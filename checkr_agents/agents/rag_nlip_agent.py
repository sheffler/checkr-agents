#
# A RAG Agent has tools for querying about a scraped website stored in a Milvus Database.
#

import logging
import asyncio
from importlib import resources
import os

from .nlip_agent import NlipAgent
from .checkr_agent import MODEL
from ..rag.milvus_context_generator import MilvusContextGenerator

# use the default logger
from checkr_agents import logger

NLIP_INSTRUCTION = """You are an agent with specialized knowledge about the McLaren Labs website stored
in a vector database that is used to provide context to queries.
You know about RTP-MIDI and MIDI in general.  You know about Objective-C programming,
and how to access MIDI and Audio devices in LInux.
"""

DB = "rag_website_milvus.db" # in the /resources directory
EMBEDDING_MODEL = 'ollama/granite-embedding:30m'
EMBEDDING_LENGTH = 384
COLLECTION_NAME = 'pages'

#
# A helper function to locate a milvus file in checker_agents/resources/foo
# and turn it into a relative path.
#
# Milvus is not ok with absolute paths to the .db file.  It wants a path relative
# to the current working dir.
#

def find_db_path_in_resources(db:str):   
    posix_path = resources.files('checkr_agents.resources').joinpath(db)
    rel_path = posix_path.relative_to(os.getcwd())
    logger.info(f"MILVUS DB located in {rel_path}")
    return str(rel_path)

class RagNlipAgent(NlipAgent):

    def __init__(self,
                 name: str,
                 model: str = MODEL,
                 instruction: str = None,
                 ):

        super().__init__(name, model=model)

        # initialize the vector database context generator
        URI = find_db_path_in_resources(DB)
        self.mcg = MilvusContextGenerator(URI, EMBEDDING_MODEL, EMBEDDING_LENGTH, COLLECTION_NAME)

        self.add_instruction(NLIP_INSTRUCTION)

        if instruction:
            self.add_instruction(instruction)

    #
    # Override the query function to provide context from Milvus database
    #

    async def process_query(self, query: str) -> list[str]:

        chunks = self.mcg.retrieve_context_from_milvus(query)

        context_str = "\n---\n".join(chunks)

        system_prompt = (
            "You are an expert Q&A assistant. Use the provided context "
            "to answer the user's question. If the answer is not in the context, "
            "state that you cannot find the answer in the provided documents."
        )

        user_prompt = (
            f"Context: {context_str}\n\n"
            f"Question: {query}"
        )

        self.add_instruction(system_prompt)
        return await super().process_query(user_prompt)
        
    

# Test program for running with stdin
async def main():
    logger.info(f"WELCOME")
    if len(sys.argv) < 0:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    agent = RagNlipAgent(
        "McLarenLabs"
    )
    
    # agent.load_spec("checkr_agents.assertions.assertion1:mainfn")

    try:
        await agent.chat_loop()
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    import sys
    import checkr_agents
    checkr_agents.log_to_console(logging.DEBUG)

    asyncio.run(main())
