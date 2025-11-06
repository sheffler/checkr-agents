# Checkr Agents Python Package

Files in this folder define a Python Package.  A brief description of each of the subfolders here follows.

- [agents](./agents) - the base agent class of this project as well as example agents with specialized tools or capabilities.

- [assertions](./assertions) - tasks that run alongside an agent or agent system.  (These are not very fully developed yet.)

- [http_client](./http_client) - an HTTP client for talking with NLIP Agent Servers that may be mounted at various locations.  The HTTP client understands addresses like `http://localhost:8024`, `unix://agent-one` and `mem://cooperative-agent` and does the right thing.

- [http_server](./http_server) - defines the class `NlipSessionServer` which establishes an NLIP Server using the FastAPI package.  The `NlipSessionServer` sets up cookie and session management for an agent.

- [rag](./rag) - this is a helper.  It defines a class called `MilvusContextGenerator` that can receive a query and generate additional textual context for it using a vector database.  Its implementation is not specific to NLIP agent types.

- [resources](./resources) - non-code files that are used by this project.

- [servers](./servers) - this directory is important.  For each agent type in the [agents](./agents) directory, there is a corresponding file here for serving that agent over an HTTP interface with the NLIP protocol.

- [system](./system) - this directory contains the `MountSpec` class, which is responsible for runnning collections of agents together as a group called a "System."  A number of examples show how multi-agent systems are defined and launched.
