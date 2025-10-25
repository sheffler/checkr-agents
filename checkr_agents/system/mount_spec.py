#
# A Mount Specification is a declaration of how to run multiple webservers in the same process.
# Each is run by a uvicorn Server instance in the asyncio event loop.
#
# Examples of mount specifications:
#
#    (app, "http://0.0.0.0:8002/...")
#    (app, "unix://name/...)
#    (app, "mem://name/...)
#
# The second two are local to the host computer.
#
# The strings of the mount spec will also be understandable to Agent client applications, like Mach2.  It
# will be possible to "connect to unix://foo" in an Agent conversation.
#
# Unix mount names will have a uniform interpretation across implementations so that Mach2 can find the sockets.
# The current plan is that "unix://name" will use "/tmp/agent-{name}.sock".
#
# Sheffler Oct 2025
#

import asyncio
import uvicorn
from urllib.parse import urlparse
import logging

from checkr_agents import MEM_APP_TBL # global table of in-memory registered apps

logger = logging.getLogger('checkr.mount_spec')

class MountSpec:

    def __init__(self, mount_spec):
        # a list of servers to start
        self.mount_spec = mount_spec

    def unix_path(self, name:str):
        """
        Return a path where an unprivilged process can create a socket.
        """
        return f"/tmp/agent-{name}.sock"

    async def create_webserver(self, spec):
        logger.info(f"CREATE_WEBSERVER:{spec}")
        app = spec[0]
        u = urlparse(spec[1])

        logger.debug(f"SCHEME:{u.scheme}")

        if u.scheme == "http":

            if u.port == None:
                raise Exception(f"Port must be specified in:{u}")

            server_config = uvicorn.Config(app, host="0.0.0.0", port=int(u.port), log_level="info")
            server = uvicorn.Server(server_config)
            logger.debug(f"SERVER:{server}")
            return await server.serve()

        elif u.scheme == "unix":
            sockpath = self.unix_path(u.hostname)
            server_config = uvicorn.Config(app, uds=sockpath, log_level="info")
            server = uvicorn.Server(server_config)
            return await server.serve()

        elif u.scheme == "mem":
            MEM_APP_TBL[u.hostname] = app # the in-memory app table
            return None

        else:
            raise Exception("Unrecognized MountSpec Scheme:{u.scheme}")

    # Usage:
    #   asyncio.run(ms.runall())
    #

    async def runall(self):

        logger.debug(f"MountSpec: RUNALL")
        
        servers = [ ]
        for spec in self.mount_spec:
            server = self.create_webserver(spec)
            logger.debug(f"GOT SERVER:{spec} {server}")
            
            # TOM: to re-think this.  The mem part isn't really async at all
            
            if not spec[1].startswith("mem:"):
                servers.append(asyncio.create_task(server)) # create a task from a couroutine
            else:
                await server # make it yield up until the None

        done, pending = await asyncio.wait(servers, return_when=asyncio.FIRST_COMPLETED)
            
        # done, pending = await asyncio.wait(servers, return_when=asyncio.ALL_COMPLETED)

        #
        # ToDo: ^C shuts everything down, and the pending tasks receive asyncio.exception.CancelledError,
        # which is correct.  It would be nice to find where to catch this and shutdown gracefully.  No luck.

        # ToDo: clean up the socket files

        # print(f"DONE/PENDING:{done}\n===\n{pending}")

        logger.debug("================================================================")
        logger.debug("done")
        logger.debug(done)
        logger.debug("pending")
        logger.debug(pending)
        # for pending_task in pending:
        #    pending_task.cancel("Another service died, server is shutting down")

        
