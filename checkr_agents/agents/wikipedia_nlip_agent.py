#
# A Wikipedia Agent has a tool for retrieving a Wikipedia page by name.

import logging
from checkr_agents import logger

import asyncio
from .nlip_agent import NlipAgent

from typing import Any
import httpx

# Constants
WIKIPEDIA_API_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
USER_AGENT = "wikipedia-app/1.0"


#MODEL = 'ollama_chat/llama3.2:latest'
# MODEL = "anthropic/claude-3-7-sonnet-20250219"
MODEL = "cerebras/llama3.3-70b"   # 2025-12-09 Cerebras is fine calling this tool

async def make_wikipedia_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Wikipedia API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"WikipediaException:{e}"


# TOOL definition
async def get_wikipedia_page_by_title(title: str) -> Any:
    """ Get wikipedia page summary given the page title
    Args:
        title: The title of the Wikipedia article
    """

    url = WIKIPEDIA_API_BASE.format(title=title)
    data = await make_wikipedia_request(url)

    return data


class WikipediaNlipAgent(NlipAgent):

    def __init__(self,
                 name: str,
                 model: str = MODEL,
                 instruction: str = None,
                 tools = [get_wikipedia_page_by_title]
                 ):

        super().__init__(name, model=model, tools=tools)

        self.add_instruction("You are an agent with tools for retrieving page summaries from Wikipedia given a page title."
                             "Use wikipedia as a helpful encyclopedia with many kinds of knowledge."
                             )

        if instruction:
            self.add_instruction(instruction)
    

# Test program for running with stdin
async def main():
    logger.info(f"WELCOME")
    if len(sys.argv) < 0:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    agent = WikipediaNlipAgent(
        "Wikipedia"
    )
    
    agent.load_spec("checkr_agents.assertions.assertion1:mainfn")

    try:
        await agent.chat_loop()
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    import sys
    import checkr_agents
    checkr_agents.log_to_console(logging.DEBUG)

    asyncio.run(main())
