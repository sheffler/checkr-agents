# Checkr Agents

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
    NlipAgent <|-- CoordinatorNlipAgent : inheritance
    NlipAgent <|-- RagNlipAgent : inheritance
    MilvusContextManager <.. RagNlipAgent

```
