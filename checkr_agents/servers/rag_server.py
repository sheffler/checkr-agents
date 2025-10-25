#
# A Server that Launches a WeatherAgent instance for each session
#

import os
import argparse
import logging

from nlip_sdk.nlip import NLIP_Message
from nlip_sdk.nlip import NLIP_Factory

from checkr_agents.agents.rag_nlip_agent import RagNlipAgent

from checkr_agents.http_server.nlip_session_server import NlipSessionServer
from checkr_agents.http_server.nlip_session_server import SessionManager

from checkr_agents import logger
import uvicorn


#
# Define a session manager that launches a new RagAgent for each session
#

class RagManager(SessionManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.myAgent = RagNlipAgent(
            "McLarenLabs"
        )

    async def process_nlip(self, msg: NLIP_Message) -> NLIP_Message:

        # concatenate all of the "text" parts
        text = msg.extract_text()

        try:
            results = await self.myAgent.process_query(text)
            logger.info(f"RagServerResults : {results}")
            msg = NLIP_Factory.create_text(results[0])
            for res in results[1:]:
               msg.add_text(res)
            return msg
        except Exception as e:
            logger.error(f"Exception {e}")
            return None
        
        
#
# Now configure the server
#

# app = server.app
app = NlipSessionServer("RagCookie", RagManager)

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Run the RagServer on a specified port (default 8022)")
    parser.add_argument("--port", type=int, default=8028, help="the network port to serve on")
    parser.add_argument("--uds", type=str, default=None, help="the Unix Domain Socket serve on")
    args = parser.parse_args()
    
    #
    # Configure the NLIP logger
    #

    log_to_console(logging.INFO)

    if args.uds == None:
        uvicorn.run("checkr_agents.servers.rag_server:app", host="0.0.0.0", port=args.port, log_level="info", reload=True)
    else:
        uvicorn.run("checkr_agents.servers.rag_server:app", uds=args.uds, log_level="info", reload=True)
        
