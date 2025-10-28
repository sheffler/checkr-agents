#
# This Network Of Agents includes Four agents mounted at the following URLs
#
#    - a user-facing coordinator at http://localhost:8024
#    - a generic agent at mem://basic/
#    - a weather agent at mem://weather/
#    - a RAG agent at mem://rag/
#    - a Wikipedia agent at mem://wikipedia/
#
# All are emitting Checkr events in the shared address space.
#
# Sheffler Oct 2025

import asyncio
import sys
import logging

from ..servers.basic_server import app as app1
from ..servers.weather_server import app as app2
from ..servers.coordinator_server import app as coord
from ..servers.rag_server import app as rag
from ..servers.wikipedia_server import app as wiki

from .mount_spec import MountSpec

from checkr_agents.agents.checkr import Checkr
from checkr_agents import log_to_console


if __name__ == "__main__":

    log_to_console(logging.DEBUG)

    #
    # The main coordinator agent has an outward network address,
    # the other three are in-memory agents.
    #
    
    mount_spec = [
        (coord, "http://0.0.0.0:8024/"),
        (app1, "mem://basic/"),
        (app2, "mem://weather/"),
        (rag, "mem://rag/"),
        (wiki, "mem://wikipedia/"),
    ]

    checkr = Checkr()
    checkr.load_spec("checkr_agents.assertions.assertion1:mainfn")

    ms = MountSpec(mount_spec)

    try:
        asyncio.run(ms.runall())
    except Exception as e:
        print(e)
        sys.exit(0)
        

