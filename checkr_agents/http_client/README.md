# NLIP Async Client

Checkr Agents all use HTTP for inter-agent communication.  This is true whether the HTTP is exposed over the network (`http://` URL), over a Unix Domain Socket (`unix://` URL) or over an in-memory transfer (`mem://` URL).  HTTP is the native interface of an NLIP Agent, and using asyncio keeps everything moving smoothly.

