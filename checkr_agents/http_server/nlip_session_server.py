#
# An HTTP Server with session management.
#

from fastapi import FastAPI, Body, Request, Response, Depends, HTTPException
from typing import Dict, Annotated
from uuid import uuid4
import traceback
import sys

from nlip_sdk.nlip import NLIP_Message

#
# Session-oriented NLIP handler
#

class SessionManager:

    async def process_nlip(self, msg: NLIP_Message) -> NLIP_Message:
        raise NotImplementedError("Subclasses must implement this method")
    
#
# A fast api server with two predefined routes
class NlipSessionServer(FastAPI):

    def __init__(self, suffix:str, session_manager_class):

        super().__init__()

        self.suffix = suffix
        self.session_manager_class = session_manager_class

        self.session_cookie_name = f"session_id_{suffix}"
        self.sessions: Dict[str, SessionManager] = { }

        app = self

        @app.post("/nlip")
        async def process_nlip_request(
                message: Annotated[NLIP_Message, Body(examples=examples)],
                manager: SessionManager = Depends(self.get_session_manager)
        ):
            try:
                response = await manager.process_nlip(message)
                return response
            except Exception as e:
                print(f"NlipSessionServer:{e}")
                traceback.print_exc(file=sys.stdout)
                raise HTTPException(status_code=400, detail=str(e))


        @app.get("/health")
        async def health_check():
            return {"status": "healthy"}
        
    # A dependency function to get or create a session
    def get_session_manager(self, request: Request, response: Response) -> SessionManager:
        """
        Retrieves the Session manager instance associated with the current session.
        A new session and manager are created if not exists.
        """

        session_id = request.cookies.get(self.session_cookie_name)

        if not session_id or session_id not in self.sessions:
            # Create a new session and manager
            session_id = str(uuid4())
            self.sessions[session_id] = self.session_manager_class()

            # Set cookie to remember this session
            response.set_cookie(
                key=self.session_cookie_name,
                value=session_id,
                httponly=True,
                samesite="lax",
            )
            print(f"Created new session and agent for session_id: {session_id}")

        return self.sessions[session_id]

# Provide examples of simple NLIP messages that are displayed in the docs UI
examples = [
    {
        "format": "text",
        "subformat":"english",
        "content": "How are you today?"
    },
    {
        "format": "text",
        "subformat":"english",
        "content": "Is there a weather alert for CA?"
    },
    {
        "format": "text",
        "subformat":"english",
        "content": "Describe your NLIP Capabilities."
    },
]

