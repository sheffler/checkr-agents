#
# A Server that Launches a BasicAgent instance for each session
#

import os
import argparse

from nlip_sdk.nlip import NLIP_Message
from nlip_sdk.nlip import NLIP_Factory

from checkr_agents.agents.checkr_agent import CheckrAgent

from checkr_agents.http_server.nlip_session_server import NlipSessionServer
from checkr_agents.http_server.nlip_session_server import SessionManager

from checkr_agents import logger
import uvicorn


#
# Define a session manager that launches a new CheckrAgent for each session
#

class BasicManager(SessionManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.myAgent = CheckrAgent(
            "CheckrAgent"
        )

    async def process_nlip(self, msg: NLIP_Message) -> NLIP_Message:

        # concatenate all of the "text" parts
        text = msg.extract_text()

        try:
            results = await self.myAgent.process_query(text)
            logger.info(f"BasicServerResults: {results}")
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

app = NlipSessionServer("basic", BasicManager)

#
# If this module is run as a main, run the server and mount it on a network port of Unix Domain Socket.
#

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Run the BasicServer on a specified port (default 8020)")
    parser.add_argument("--port", type=int, default=8020, help="the network port to serve on")
    parser.add_argument("--uds", type=str, default=None, help="the Unix Domain Socket serve on")
    args = parser.parse_args()

    if args.uds == None:
        uvicorn.run("checkr_agents.servers.basic_server:app", host="0.0.0.0", port=args.port, log_level="info", reload=True)
    else:
        uvicorn.run("checkr_agents.servers.basic_server:app", uds=args.uds, log_level="info", reload=True)
