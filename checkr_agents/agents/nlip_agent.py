#
# An NLIP Agent knows how to respond to the request for NLIP Capabilities
#

import asyncio
import logging
from typing import Callable

from .checkr_agent import CheckrAgent
from .checkr_agent import MODEL


logger = logging.getLogger("NLIP")

NLIP_INSTRUCTION = """
You are an NLIP Agent.

NLIP is an acronym for "Natural Language Interaction Protocol."  The NLIP project aims to define a protocol for the following use cases.
- Agent to Agent interactions in Natural Language
- User-Agent to Agent protocol

An NLIP Agent, when defined, is given a system instruction that describes its unique capabilities.

One of the first requests an NLIP Agent will be asked to fulfill is to describe its NLIP Capabilities.
When you are asked to describe your NLIP Capabilities, you should respond with a response of the format:
    AGENT:NAME
    CAPABILITY1:description, CAPABILITY2:description, CAPABILITY3:description, ...
- where NAME is your name
- CAPABILITITY1, CAPABILITY2 and CAPABILITY3 are dictionary keys.  The description associated with each should be unique.
- it is important that you include your NAME
- it is important that the capabilities are described in a means that another LLM can understand them

"""


class NlipAgent(CheckrAgent):

    def __init__(self,
                 name: str,
                 model: str = MODEL,
                 instruction: str = None,
                 tools: list[Callable] = [ ]
                 ):

        super().__init__(name, model, NLIP_INSTRUCTION, tools)

        # any additional instructions
        if instruction:
            self.add_instruction(instruction)




#
# Test program for trying out a simple agent with the console
#

async def main():
    logger.info(f"WELCOME")
    if len(sys.argv) < 0:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    agent = NlipAgent(
        name="Bart"
    )
    
    try:
        await agent.chat_loop()
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    import sys
    import checkr_agents
    checkr_agents.log_to_console(logging.DEBUG)

    asyncio.run(main())
