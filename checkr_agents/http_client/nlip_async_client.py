#
# A simple Async NLIP Client based on HTTPX
#

import httpx
from urllib.parse import urlparse

from nlip_sdk.nlip import NLIP_Message

from checkr_agents import MEM_APP_TBL # global table of in-memory registered apps

class NlipAsyncClient:

    def __init__(self, base_url: str):
        u = urlparse(base_url)
        
        if u.scheme == "unix":
            # need to adjust requests to use the url with unix->http
            new_url = u._replace(scheme="http").geturl()
            self.base_url = new_url

            transport = httpx.AsyncHTTPTransport(uds=self.unix_path(u.hostname))
            self.client = httpx.AsyncClient(transport=transport)

        elif u.scheme == "mem":
            
            new_url = u._replace(scheme="http").geturl()
            self.base_url = new_url

            app = MEM_APP_TBL.get(u.hostname, None)
            if app == None:
                raise Exception(f"App named {u.hostname} in {base_url} not found")

            transport = httpx.ASGITransport(app=app)
            self.client = httpx.AsyncClient(transport=transport)

        else:
            self.base_url = base_url
            self.client = httpx.AsyncClient()

    def unix_path(self, name):
        return f"/tmp/agent-{name}.sock"
                                                 

    @classmethod
    def create_from_url(cls, base_url:str):
        return NlipAsyncClient(base_url)

    async def async_send(self, msg:NLIP_Message) -> NLIP_Message:
        response = await self.client.post(self.base_url, json=msg.to_dict(), timeout=120.0, follow_redirects=True)
        data = response.raise_for_status().json()
        nlip_msg = NLIP_Message(**data)
        return nlip_msg
        
