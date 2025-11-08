# Checkr Agents

This directory contains the base agent of this project (the `CheckrAgent`), and a number of agents that derive from it.  The collection of agents form a shallow class hierarchy, as shown in the figure below.  A short description of each follows.

- `CheckrAgent` - a base agent class that contains most of the logic for handling a query with an LLM, keeping the conversation history, managing tool calls, and formatting results.  The `CheckrAgent` also keeps a `Checkr` which is an object that is used to emit trace events.

- `NlipAgent` - the `NlipAgent` derives from the base agent class and adds NLIP-aware context in the form of a prompt.  Any `NlipAgent` will contain an instruction that teaches it how to respond when it is asked to describe its "NLIP Capabilities."  This instruction is the basis for how NLIP Agents learn of each others' capabilities.

- `WeatherNlipAgent` - an agent that has tools to gather information about weather forecasts and alerts.

- `WikipediaNlipAgent` - an agent with a tool to retrieve information from Wikipedia.

- `RagNlipAgent` - this agent intercepts the initial query and adds context to the session using a vector database.  This project includes a database that has been constructed by scaping a website (https://mclarenlabs.com) that contains information about MIDI.

- `CoordinatorNlipAgent` - this is a very special NLIP agent that has been given tools for connecting to other NLIP agents, establishing their capabilities and sending messages to those agents.  NLIP Agent URLS can include network addresses (`http://my-agent.com`), Unix Domain Socket addresses (`unix://a-different-agent`), or in-memory addresses of agents in the same system (`mem://cooperative-agent`).

    The `CoordinatorNlipAgent` is an example of the **Router** Agent Design Pattern.


``` mermaid

classDiagram
direction TB
    class CheckrAgent {
	    - messages[]
	    - tools[]
	    - process_query(q)
    }

    class NlipAgent {
	    + NLIP_PROMPT
    }

    class WeatherNlipAgent {
	    + WEATHER_PROMPT
	    - tool: make_nws_request()
	    - tool: format_alert()
    }

    class WikipediaNlipAgent {
	    + WIKIPEDIA_PROMPT
	    - tool: make_wikipedia_request()
    }

    class CoordinatorNlipAgent {
	    + NLIP_COORDINATOR_PROMPT
	    - tool: connect_to_server(url)
	    - tool: send_to_server(url, msg)
    }

    class RagNlipAgent {
	    + RAG_PROMPT
	    - milvus_context_manager
	    - process_query(q)
    }

    class MilvusContextManager {
	    - milvus_website.db
    }

    CheckrAgent <|-- NlipAgent : inheritance
    NlipAgent <|-- WeatherNlipAgent : inheritance
    NlipAgent <|-- WikipediaNlipAgent : inheritance
    NlipAgent <|-- CoordinatorNlipAgent : inheritance
    NlipAgent <|-- RagNlipAgent : inheritance
    MilvusContextManager <.. RagNlipAgent

```


## Running these agents in isolation

Normally, NLIP agents are run in the context of an NLIP HTTP Server.  However, these agents have been enabled with a text-based terminal interface for exercising each of them in isolation.

Having built and installed the project, any of these can be run from the root of the project directory as follows.

``` console
$ python -m checkr_agents.agents.checkr_agent
$ python -m checkr_agents.agents.nlip_agent
$ python -m checkr_agents.agents.weather_nlip_agent
$ python -m checkr_agents.agents.wikipedia_nlip_agent
$ python -m checkr_agents.agents.rag_nlip_agent
$ python -m checkr_agents.agents.coordinator_nlip_agent
```
