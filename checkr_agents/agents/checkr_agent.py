#
# A Checkr Agent implements a converation with an LLM, augmented with tools and prompt instructions.
# It emits Oroboro events at major points in its lifecycle using an instance of a Checkr.
#
# The Checkr Agent maintains the conversation history with the LLM, and provides the logic for
# calling Tools and incorporating their results.
#
# A new user query is sent to the agent with the process_query() method.  The result of the query
# is a list of messages.
#


import logging
import asyncio
import time
from typing import Optional, List, Dict, Any
from typing import Callable

from .checkr import Checkr

from checkr_agents import logger

# from pydantic import schema_of, schema_json_of
from pydantic import TypeAdapter
import json

# Pydantic v2 is deprecating schema_of.  This is how to do it in Pydantic v3.
def schema_of(thing):
    adapter = TypeAdapter(thing)
    return adapter.json_schema()

from litellm import completion
from dotenv import load_dotenv

# Configure Logging for LiteLLM
import litellm
# litellm._turn_on_debug()

# Load .env for vars like ANTHROPIC_API_KEY, etc
load_dotenv()

#
# Configure the default MODEL for this project
#

# MODEL = 'llama3.2:latest'
# MODEL = 'ollama_chat/llama3.2:latest'
# MODEL = 'ollama_chat/llama3-groq-tool-use:latest'
# MODEL = "anthropic/claude-3-7-sonnet-20250219"
MODEL = "cerebras/llama-4-scout-17b-16e-instruct"

#
# PROMPTS
#

TOOLS_INSTRUCTION = """
You are an agent with tools.  When calling a tool, make sure to match the type signature of the tool.
"""

class CheckrAgent:
    """
    LLM-based Agent capable of invoking tools.

    Args:
        name (str): REQUIRED - the agent's name
        model (str): the LLM model to use
        instruction (str): the system instruction
        tools (list): the initial set of tools
    """
        

    def __init__(self,
                 name: str,
                 model: str = 'ollama_chat/llama3.2:latest',
                 instruction: str = None,
                 tools: list[Callable] = [ ]
                 ):

        # start time
        self.tstart = time.time()

        # create the checkr
        self.checkr = Checkr()
        self.define_checkr_events()

        # self.name: str = name
        self.model: str = model
        self.instruction: str = instruction

        # the conversation history
        self.messages: list[Any] = [
            {
                "role": "system",
                "content": TOOLS_INSTRUCTION
            }
        ]

        # Every agent knows its name
        self.add_instruction(f"Your NAME is {name}.")

        # Add other instructions
        if instruction:
            self.add_instruction(instruction)

        # tools is a list of dict
        self.tools: list[Dict] = [ ]

        # map from tool name to Callable
        self.fnmap: Dict(str, Callable) = { }

        # final_text is what is returned to the user after a turn
        self.final_text: list[str] = [ ]

        # build the initial tools from a list of python callables
        for fn in tools:
            self.add_tool(fn)
    
    #
    # relative time since agent birth
    #
    def _trel(self):
        return time.time() - self.tstart

    #
    # the events that define the lifecycle of a query
    #
    def define_checkr_events(self):

        # agent set up events
        self.on_add_tool = self.checkr.define_observer_event("on_add_tool")
        self.on_add_instruction = self.checkr.define_observer_event("on_add_instruction")

        # query lifecycle events
        self.on_query_received = self.checkr.define_observer_event("on_query_received")
        self.on_query_analyzed = self.checkr.define_observer_event("on_query_analyzed")
        self.on_one_tool_called = self.checkr.define_observer_event("on_one_tool_called")
        self.on_all_tools_called = self.checkr.define_observer_event("on_all_tools_called")
        self.on_tool_calls_analyzed = self.checkr.define_observer_event("on_tool_calls_analyzed")
        self.on_query_handled = self.checkr.define_observer_event("on_query_handled")

    #
    # Load an assertion
    #
    def load_spec(self, modspec:str):
        logger.info(f"LOADING THE ASSERTION {modspec}")
        self.checkr.load_spec(modspec)

    #
    # Tools MUST be Async Callable (for now).  Do use doc strings for the function and
    # the arguments as this helps the LLM understand the tool and its arguments.
    #
    
    def add_tool(self, fn: Callable):
        """Add a tool to the agent.  Its name and schema are generated using introspection."""
        name = fn.__name__

        # this is the tool description passed to the LLM
        self.tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": fn.__doc__,
                "parameters": schema_of(fn)
            }
        })

        # when the LLM requests a tool invocation this is where we find the Py function to call
        self.fnmap[name] = fn

        self.checkr.post_and_run(self._trel(), self.on_add_tool, name)

    def list_tools(self):
        return self.tools

    #
    # Add a system instruction to refine the Agent's behavior
    #

    def add_instruction(self, instruction: str):
        self.messages.append(
            {
                "role": "system",
                "content": instruction
            }
        )

        self.checkr.post_and_run(self._trel(), self.on_add_instruction, instruction)
            

    #
    # Helper for main loop
    #

    async def _call_tool(self, name: str, args: Dict, tool_call_id: str) -> bool:
        """Call tool by name return True if it is found.
            ToDo: consider error handling ...
        """
        isFound = False

        fn = self.fnmap[name]
        if fn:
            isFound = True
            logger.info(f"Invoking tool:{name} with args:{args}")
            result = await fn(**args)
            logger.info(f"Got tool result:{result}")

            self.final_text.append(f"Calling tool:{name} with args:{args}")

            # NOTE: this solves a strange problem with ollama only
            # if type(result) == int:
            #    result = str(result)

            # serialize to json unless it is already a string
            content = result
            if type(content) != str:
                content = json.dumps(content)

            self.messages.append(
                {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": name,
                    "content": content
                }
            )

            # attach tool name, args and result to event
            self.checkr.post_and_run(self._trel(), self.on_one_tool_called, (name, args, result))

        return isFound


    #
    # Record the response message appropriately in both self.messages and self.final_response
    #
    
    def _handle_response(self, response_message):

        # to be shown to the user at the end of this turn
        if response_message.content is not None:
            self.final_text.append(response_message.content)

        tool_calls = response_message.tool_calls

        # NOTE: model_dump() is not mentioned in the documentation, but without
        # it pydantic complains about serializing messages on the following calls to completion().
        # The response is a Message with tool_calls[] containing a
        # ChatCompletionMessageToolCall object.  Pydantic does not know how to serialize properly.
        # Explicit serialization takes care of it.
        
        # to record in the conversation history
        if tool_calls:
            self.messages.append(response_message.model_dump())
        else:
            self.messages.append(response_message)


    #
    # Process a user query.  Return a message.
    #
            
    async def process_query(self, query: str) -> list[str]:
        print(f"Processing query")

        # checkr.postAndRun(on_query)

        # reset the result text
        self.final_text = [ ]

        # add to the conversation history
        self.messages.append({"role": "user", "content": query})

        # attach query to the event
        self.checkr.post_and_run(self._trel(), self.on_query_received, query)

        # call the LLM with the conversation
        response = completion(
            model=self.model, messages=self.messages, tools=self.tools
        )

        response_message = response.choices[0].message

        if response_message is None:
            import sys
            print(f"RESPONSE:{response_message}")
            sys.exit(1)

        # Save the response
        self._handle_response(response_message)

        # attach raw response
        self.checkr.post_and_run(self._trel(), self.on_query_analyzed, response_message)

        # Are there tool calls?
        tool_calls = response_message.tool_calls

        while tool_calls:

            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id # a uniqe id

                self.checkr.set_flag(tool_name)

                if await self._call_tool(tool_name, tool_args, tool_call_id) == False:
                    self.messages.append({"role": "user", "content": "Tool '{tool_name}' not found"})

            # for now, attach no values to the event
            self.checkr.post_and_run(self._trel(), self.on_all_tools_called)
            self.checkr.clear_all_flags()

            # Now call the LLM again with the tool result
            response = completion(
                model=self.model, messages=self.messages, tools=self.tools
            )

            # Get the final response.
            response_message = response.choices[0].message

            # Save the response in the converation and add it to the text result
            self._handle_response(response_message)

            # attach response message
            self.checkr.post_and_run(self._trel(), self.on_tool_calls_analyzed, response_message)

            # Are there more tool calls?
            tool_calls = response_message.tool_calls

        self.checkr.post_and_run(self._trel(), self.on_query_handled)

        return self.final_text

    #
    # Provide a simple console based command loop for testing
    #
    
    async def chat_loop(self):
        logger.info("Agent Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                responses = await self.process_query(query)
                # response = "\n".join(responses)
                response = "\n".join([str(item) for item in responses])
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        pass
    
################################################################
#
# Some simple tools for testing in the main() program below
#

async def echo(input: str) -> str:
    """This tool returns its argument as an echo"""
    logger.info(f"Echoing {input}")
    return f"Echoed Output is {input}"

# print(schema_json_of(echo, title="Echo", indent=2))

async def add2(val: int) -> int:
    """Add 2 to the argument and return the result."""
    return int(val) + 2

async def secret1(input: str) -> str:
    """Compute a secret given an input string"""
    import random
    letters = "abcdefghijklmnopqrstuvwxyz"
    c0 = random.choice(letters)
    c1 = random.choice(letters)
    secret = f"{input}{c0}{c1}"
    logger.info(f"The secret of {input} is {secret}")
    return secret

async def secret2(input: str) -> str:
    """Compute a secret given an input string"""
    import random
    letters = "abcdefghijklmnopqrstuvwxyz"
    c0 = random.choice(letters)
    c1 = random.choice(letters)
    c2 = random.choice(letters)
    secret = f"{input}{c0}{c1}{c2}"
    logger.info(f"The secret of {input} is {secret}")
    return secret


#
# Test program for trying out a simple agent with the console
#

async def main():
    logger.info(f"WELCOME")
    if len(sys.argv) < 0:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    agent = CheckrAgent(
        name="Pronda",
        model=MODEL,
        instruction="You are a simple agent.  Answer each query as best as possible."
    )
    
    agent.add_tool(echo)
    agent.add_tool(add2)
    agent.add_tool(secret1)
    agent.add_tool(secret2)

    print(f"LOADING THE ASSERTION")
    agent.load_spec("checkr_agents.assertions.assertion1:mainfn")
    agent.load_spec("checkr_agents.assertions.assertion2:mainfn2")

    try:
        await agent.chat_loop()
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    import sys
    import checkr_agents
    checkr_agents.log_to_console(logging.DEBUG)

    asyncio.run(main())
