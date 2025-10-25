#
# Given a Milvus vector database, process a query and return the RAG prompt to hand to an agent.
#
# Assumes a milvus database has been created with a specified embedding and dimension.
#

import os
import json
from litellm import embedding, completion
from pymilvus import MilvusClient

# Configure Logging for LiteLLM
import litellm
# litellm._turn_on_debug()

# Load environment variables (for API keys like OPENAI_API_KEY for embedding/LLM)
from dotenv import load_dotenv
load_dotenv()


class MilvusContextGenerator:

    def __init__(self, uri: str, embedding_model: str, dim: int, collection: str):
        """
        Args:
          uri: the uri of the milvus database
          embedding_model: the embedding model
          dim: the embedding dimension
          collection: the milvus collection name
        """

        self.uri = uri
        self.embedding_model = embedding_model
        self.dim = dim
        self.collection = collection

        # Initialize milvus client
        self.milvus_client = MilvusClient(uri=self.uri)

        # For Debugging - observe that the collection is found
        # print(f"MC:{self.milvus_client.describe_collection(collection_name='pages')}")




    def retrieve_context_from_milvus(self, query: str, top_k: int = 3) -> list[str]:
        """
        1. Embeds the query using LiteLLM.
        2. Searches Milvus for the top_k relevant documents.
        3. Returns the text of the relevant documents.
        """

        # 1. Embed the query using LiteLLM
        embed_response = embedding(
            model=self.embedding_model,
            input=[ query ],
        )

        query_vector = embed_response.data[0]['embedding']

        # 2. Search Milvus
        #
        # The milvus vector database was created by llama_index MilvusVectorStore.  We need
        # to understand how it inserted the data so we can get out the documents, and
        # the field to search on (anns_field).
        #
        # Key Points (from Claude)
        # - The default collection name is "llamalection" in older versions or
        # "llamacollection" in newer versions LlamaIndex
        # - The default similarity metric is "IP" (Inner Product) LlamaIndex
        # - LlamaIndex stores additional metadata fields that you can include in
        # output_fields like _node_content, _node_type, and any custom metadata you added
        #
        # You can inspect your collection's schema first using
        # client.describe_collection(collection_name="your_collection") to see all available fields.

        search_results = self.milvus_client.search(
            collection_name=self.collection,
            data=[query_vector],
            limit=top_k,
            anns_field="embedding", # the vector field name (LlamaIndex default)
            output_fields=["text", "doc_id", "_node_content"],
            search_params={"metric_type": "IP", "params":{}}
        )

        # 3. Extract and return the text chunks
        context_chunks = []
        for hit in search_results[0]:
            # The node_content from llama_index is a json structure stored as a string
            #   Note: there are other interesting attributes and metadata in the node_content.
            node_content = json.loads(hit["entity"]["_node_content"])
            context_chunks.append(node_content["text"])
        
        return context_chunks

#
# Standalone simple test program
#

if __name__ == '__main__':

    # relative to CWD.  Must run this at ROOT of this project
    URI = "./checkr_agents/resources/rag_website_milvus.db"

    # ollama pull granite-embedding:30m
    #   (is a 62MB download)
    EMBEDDING_MODEL = 'ollama/granite-embedding:30m'
    

    EMBEDDING_LENGTH = 384
    COLLECTION_NAME = 'pages'

    mcg = MilvusContextGenerator(URI, EMBEDDING_MODEL, EMBEDDING_LENGTH, COLLECTION_NAME)

    res = mcg.retrieve_context_from_milvus("What is RTP-MIDI?")
    print(f"RES:{res}")
