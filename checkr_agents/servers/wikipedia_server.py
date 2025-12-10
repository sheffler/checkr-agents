#
# A Server that Launches a WikipediaAgent instance for each session
#

import os
import argparse
import logging

from nlip_sdk.nlip import NLIP_Message
from nlip_sdk.nlip import NLIP_Factory

from checkr_agents.agents.wikipedia_nlip_agent import WikipediaNlipAgent

from checkr_agents.http_server.nlip_session_server import NlipSessionServer
from checkr_agents.http_server.nlip_session_server import SessionManager

from checkr_agents import logger
from checkr_agents import log_to_console
import uvicorn


#
# Define a session manager that launches a new BasicAgent for each session
#

class WikipediaManager(SessionManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.myAgent = WikipediaNlipAgent(
            "Wikipedia"
        )

    async def process_nlip(self, msg: NLIP_Message) -> NLIP_Message:

        # concatenate all of the "text" parts
        text = msg.extract_text(language=None)

        try:
            results = await self.myAgent.process_query(text)
            logger.info(f"WikipediaServerResults : {results}")
            msg = NLIP_Factory.create_text(results[0])
            for res in results[1:]:
               msg.add_text(res)
            return msg
        except Exception as e:
            logger.error(f"Exception: {e}")
            error_message = f"Exception: {e}"
            return NLIP_Factory.create_text(error_message)
        
        
#
# Now configure the server
#

# app = server.app
app = NlipSessionServer("WikipediaCookie", WikipediaManager)

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Run the WikipediaServer on a specified port (default 8026")
    parser.add_argument("--port", type=int, default=8026, help="the network port to serve on")
    parser.add_argument("--uds", type=str, default=None, help="the Unix Domain Socket serve on")
    args = parser.parse_args()
    
    #
    # Configure the NLIP logger
    #

    log_to_console(logging.INFO)

    if args.uds == None:
        uvicorn.run("checkr_agents.servers.wikipedia_server:app", host="0.0.0.0", port=args.port, log_level="info", reload=True)
    else:
        uvicorn.run("checkr_agents.servers.wikipedia_server:app", uds=args.uds, log_level="info", reload=True)
        
