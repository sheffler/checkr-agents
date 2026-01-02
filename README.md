# Checkr Agent Networks

See the following reference for an early version of this work.

- *An Approach to Checking Correctness for Agentic Systems*: https://arxiv.org/abs/2509.20364


## Introduction

This project introduces two new capabilities.

1.  Composable NLIP Agents.  One executable may now consist of multiple agents that communicate amongst themselves to respond to queries.  An "Agent System" is a collection of Agents with a well-defined mechanism for sending messages to each other via a specified "address."  (See the [./checkr_agents/system](./checkr_agents/system) directory.)

2.  Checkr Agents.  The lifecycle of an Agent, and its handling of a query, is defined by a series of events.  These events are emitted to a cooperative thread that is running one or more "assertions."  An assertion can verify the correctness of a temporal expression over time, or otherwise check the correctness of the event trace of an Agent in a non-invasive way.

## Networks of Agents: a System

An NLIP Agent exposes its front-end via an HTTP (or HTTPS) server with a designated endoint (`/nlip`) receiving and sending JSON messages of a specified format (NLIP Message Format).  When deployed, an HTTP server is mounted at an address.  Most often, the address is a "network address" at a specific IP address, or a hostname.  The combination of the `scheme` and the address identify the protocol the server understands and where it is listening.

- `http://10.0.0.20`
- `http://example-host.ai`

This project defines two new mount notations.

- `unix://agent-name`
- `mem://agent-name`

The first is a mount notation that indicates an NLIP Agent server listening at a Unix Domain Socket on the current host.  The second is a mount notation that indicates an NLIP Agent server listening at an in-memory channel.

Mounts agents of of various types may be specified in a simple declarative way and the "System" mount machinery figures out to run the various agents, listening at the different types of addresses.   This means that it is easy to decompose problems into networks of agents, with each specialized for a specific task.  Specialization helps keep agents compact and performant.

The significance of the different types of address is that they have different security profiles.  A network address may be reachable by other computers.  A Unix Domain Socket may be reachable by other processes on the same computer.  Agents mounted at `mem://` URIs are only reachable by the other agents it was launched with.


![Network of Agents](./pics/Slide2.png)

Coordinator NLIP Agents are agents that have *tools* to send and receive messages to other NLIP Agents via an address.  A `mem://` address is entirely local to an Agent System.  This makes it very useful for the composition of specialized agents into a single system, where only one (the Coordinator) has a network exposed address.

The significance of this scheme is that it universally uses the NLIP Agent as the unit of agent composibility independent of whether the NLIP Agent is exposed on the network, or whether it is one of a collection of cooperatively-multithreaded agents residing in one process.  An NLIP Agent has an address, and it may be public or private, but it behaves the same either way.


## Launching a System and communicating between agents

A collection of agents is specified with a "Launch Specfication."  An example is shown below.   In it, three servers are created.  Each of which is a FastAPI server "app" serving an NLIP endpoint for an agent.

``` python

agent_server1 = ...
agent_server2 = ...
agent_server3 = ...

mount_spec = [
  (agent_server1, "http://localhost:8024")
  (agent_server2, "unix://pipename")
  (agent_server3, "mem://channelname")
]

```

Agents that have been enabled for NLIP communication will have two "Tools" at their disposal.

- `connect_to_server(url)`
- `send_to_server(url, message)`

With these two tools a Coordinator Agent can establish a connection to another agent with `connect_to_server(url)` - whether it is local or across the network.  Once a connection is established, the Coordinator Agent can use the `send_to_server(url, message)` tool to send an NLIP message.

The significance of this approach is that helper agents can be dynamically added to a main agent session to help or provide specialized knowlege.  Examples in this project show dialogs that can exercise this functionality.



## Checkers and Assertions

All agents in this project derive from the base class `CheckrAgent`.  A CheckrAgent emits events at well-defined points in its lifetime.  For example, some of the key events of handling of a query are shown below.

- `on_query_received`
- `on_query_analyzed`
- `on_all_tools_called`
- `on_query_handled`

When launched, an Agent System may start one or more "assertions."  An assertion is a coroutine that verifies a statement of truth about an Agent System.  An assertion may run at a single point in time, or it may consider a sequence of events over time.


## A Universal Chat Agent

Agents with NLIP interfaces can be reached by other agents, or by users employing a chat agent.  One such universal chat agent is the [Mach2 Chat App](https://github.com/sheffler/kivy-client-mach2).  A screenshot is shown below.

![Agent-to-Agent](pics/mach2-2.png)

In the figure you can observe the address bar where an agent URL can be entered.  Candidates include network addresses (`http://localhost:8024`) as well as Unix Domain Sockets serving up NLIP Agents (`unix://my-agent`).

You can also observe the dynamic addition of a helper agent to the coordinator agent.


## Installation and Build


We recommend checking out the Oroboro dependency and NLIP-SDK dependency in a directory adjacent to this project's directory.

    $ mkdir git
	$ cd git
	$ git clone https://github.com/nlip-project/nlip_sdk
	$ git clone https://github.com/sheffler/Oroboro
	$ git clone https://github.com/sheffler/checkr-agents
	

This project works well with `uv`.

1. Create a virtual environment.

        $ cd git/checkr-agents
        $ uv venv
    	$ . .venv/bin/activate
		
2. Synchronize the project dependencies

        $ uv sync


## Put secrets in the .env file

This project uses LiteLLM to connect to various LLMs.  If using a paid or remote LLM that requires a key, you can place it in the `.env` file in the root of the project.

For example, if you are using Anthropic and Cerebras models, you would copy your API KEYs into it.

    ANTHROPIC_API_KEY=sk-ant-api03-b2R1absad...
    CEREBRAS_API_KEY=csk-54kvefnr5evdtrk...
	
If you have enabled LANGFUSE integration, put your LANGFUSE environment variables in it.

	LANGFUSE_OTEL_HOST="https://us.cloud.langfuse.com"
	LANGFUSE_PUBLIC_KEY=pk-lf-5fd47dda-7f5e-4a1c-0000-c5960234d2b2
	LANGFUSE_SECRET_KEY=sk-lf-fac0f7e0-fc19-4015-2222-b950128916e9



## Running the Multi-Agent Agent-to-Agent Demonstration

See the complete explanation of a session with detailed screenshots in [./checkr_agents/system](./checkr_agents/system).
