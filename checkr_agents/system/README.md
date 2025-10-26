# Checkr Agent System

An Agent Server, as defined in this project, is a FastAPI application server with an NLIP endpoint at a standard URL.
By definition, all NLIP agent servers expose an `/nlip` endpoint, but individual servers can be run at different addresses.  An Agent Server address can be a network address, a unix pipe name or a named in-memory channel.

Agent servers can be run as individual processes or can be combined into a multi-agent "system" that is run in a single process.  Such a multi-agent system is described by a "Mount Specification" which lists the collection of agent servers and their addresses.

An example below shows a mount specification example.  In it, three servers are created.  Each of which is a FastAPI server "app" serving an NLIP endpoint for an agent.

``` python

agent_server1 = ...
agent_server2 = ...
agent_server3 = ...

mount_spec = [
  (agent_server1, "http://localhost:8024")
  (agent_server2, "unix://pipename")
  (agent_server1, "mem://channelname")
]

```

- The first line mounts "agent_server1" at the network address "http://localhost:8024".
- The second line mounts "agent_server2" at the Unix Socket Domain named "pipename".  By convention, Agent Server unix sockets are mounted at "/tmp/agent-{pipename}.sock".
- The third line mounts "agent_server3" with the in-memory pipe name "channelname."

The nice thing about the mount names is that they are used consistently across the NLIP Agent Servers in this project.  For example, if using the Mach2 NLIP chat agent, you can connect directly to "http://localhost:8024" to interact with it.

Mach2 also understands the Unix Domain Socket convention of Agent Servers so that if you type "unix://pipename" into the address bar of Mach2, it will find the Unix Domain Socket "/tmp/agent-{pipename}.sock" and open a session there.

In-Memory addresses are slightly different: they exist only within the Unix process of the running servers.  This feature becomes very useful for inter-agent communication using HTTP clients.  For example, in the `CoordinatorNlipAgent` if you type:

>> **Can you please connect to mem://channelname/.**

the Coordinator NLIP Agent will use its HTTP client to open a connection to the Agent at the in-memory channel with name "channelname".  Then that second agent will be available for use by the front-end the coordinator agent.

Channel-specifications are a consistent way to facilitate inter-agent communication across NLIP Agent Servers.


### Protection Domains

The three different mount domains (network, unix socket, in-memory channel) have different security characteristics.

- Network addresses may be reachable from other computers on the network.
- Unix Domain Sockets are only reachable by other processes on the same computer.
- In-Memory channels are reachable by other agents in the same process.

These different kinds of mount addresses allow some flexibility in designing multi-agent systems, and give means to restrict access to sensitive agents by keeping them in-memory, or by configuring Unix Sockets with appropriate permissions.
