#
# An NLIP Coordinator Agent has tools for communicating with other NLIP Agents.
# An additional system instruction helps refine its behavior.

import logging

import asyncio
from .nlip_agent import NlipAgent

from typing import Any
import httpx
import json

# Import NLIP
from checkr_agents.http_client.nlip_async_client import NlipAsyncClient
from nlip_sdk.nlip import NLIP_Factory, NLIP_Message
from urllib.parse import urlparse

from pydantic import AnyHttpUrl
from pydantic import AnyUrl
from pydantic import validate_call

# map host->session
sessions = { }

# Use the NLIP logger in this package
logger = logging.getLogger("checkr")

# MODEL = 'llama3.2:latest'
# MODEL = 'ollama_chat/llama3.2:latest'
# MODEL = 'ollama_chat/llama3-groq-tool-use:
MODEL = "anthropic/claude-3-7-sonnet-20250219"

# Cerebras is having trouble generating a send_to_message tool call
# MODEL = "cerebras/llama-4-scout-17b-16e-instruct"   # Nov 3, 2025: deprecated by cerebras
# MODEL = "cerebras/llama3.3-70b"



# Configure Logging for LiteLLM
import litellm
litellm._turn_on_debug()

#
# Make a connection and return a status string
#
    
async def OLDconnect_to_server(url: str):
    """Connect to the server and return a message.
    Args:
      url: a url-formatted string
    """
     
    try:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
    except Exception as e:
        text = f"Exception: {e}"
        logger.error(f"Exception: {e}")
        return text

    # Establish the URL and return a connection message
    await asyncio.sleep(1.0)
    client = NlipAsyncClient.create_from_url(f"{scheme}://{netloc}/nlip/")

    # Remember this client for this server
    hashkey = f"{scheme}://{netloc}"
    sessions[hashkey] = client

    logger.info(f"Saved {netloc} with client {client}")
    return f"Connected to {scheme}://{netloc}/"


#
# Make a connection and return a status string.
#   Use strongly typed url - may be too hard for some LLMs, like Cerebras
#

async def connect_to_server(url: AnyUrl):
    scheme = url.scheme
    host = url.host
    port = url.port
    netloc = url.host if url.port == None else f"{host}:{port}"
    
    # Establish the URL and return a connection message
    await asyncio.sleep(1.0)
    client = NlipAsyncClient.create_from_url(f"{scheme}://{netloc}/nlip/")

    # Remember this client for this server
    hashkey = f"{scheme}://{netloc}"
    sessions[hashkey] = client

    logger.info(f"Saved {netloc} with client {client}")
    return f"Connected to {scheme}://{netloc}/"

#
# Send a message to a server
#
async def OLDsend_to_server(url: str, msg: str) -> dict:
    """Connect to the server and send a message.
    Args:
      url: a url-formatted string
      msg: a message string to send to the agent at the url
    """
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc

    # Look up the client for this server
    hashkey = f"{scheme}://{netloc}" # netloc includes host and port, if specified
    client = sessions[hashkey]

    nlip_message = NLIP_Factory.create_text(msg)
    logger.info(f"Sending message: {msg}")
    nlip_resp = await client.async_send(nlip_message)
    logger.info(f"Received: {nlip_resp.model_dump()}")
    # return nlip_resp.model_dump() # did not work
    # return nlip_resp.extract_text() # worked
    return str(nlip_resp.model_dump())
    

#
# Send an NLIP message to a server
#   Use strongly typed url - may be too hard for some LLMs, like Cerebras
#   LLM must also generate complex structure NLIP message
#
async def send_to_server(url: AnyUrl, nlip_message: NLIP_Message) -> dict:

    scheme = url.scheme
    host = url.host
    port = url.port
    netloc = url.host if url.port == None else f"{host}:{port}"

    # Look up the client for this server
    hashkey = f"{scheme}://{netloc}" # netloc includes host and port, if specified
    client = sessions[hashkey]

    logger.info(f"Sending message: {nlip_message}")
    nlip_resp = await client.async_send(nlip_message)
    logger.info(f"Received: {nlip_resp.model_dump()}")
    # return nlip_resp.model_dump() # did not work
    # return nlip_resp.extract_text() # worked
    return str(nlip_resp.model_dump())


NLIP_COORDINATOR_PROMPT = """
You are an advanced NLIP Agent with the capability to speak to other NLIP Agents.
You have two tools for this purpose:
- connect_to_server
- send_to_server

When you are asked to connect to a server at a specific URL, use the connect_to_server tool with that URL to establish a connection.
If the response to that tool begins with: "Connected to ", then the connection is valid.  Otherwise, it is not.
For a valid connection, you should follow the connect_to_server tool call with a tool call of send_to_server to the same URL with the string: "What are your NLIP Capabilities?"
The remote Agent will respond with its [NAME] and capabilities.  Take note of this information, especially the NAME.  In future requests, if a user asks for you to send a request to NAME you should use the send_to_server tool with the URL that was associated with NAME and use the request as the msg: argument.
"""

class CoordinatorNlipAgent(NlipAgent):

    def __init__(self,
                 name: str,
                 model: str = MODEL,
                 instruction: str = None,
                 tools = [connect_to_server, send_to_server]
                 ):

        super().__init__(name, model=model, tools=tools)

        self.add_instruction("You are an agent with tools for querying other NLIP Agent Servers")
        self.add_instruction(NLIP_COORDINATOR_PROMPT)

        if instruction:
            self.add_instruction(instruction)
    

# Test program for running with stdin
async def main():
    logger.info(f"WELCOME")
    if len(sys.argv) < 0:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    agent = CoordinatorNlipAgent(
        "Margaret"
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
