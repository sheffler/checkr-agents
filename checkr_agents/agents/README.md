# Checkr Agents

``` mermaid

classDiagram
    class CheckrAgent {
	  - messages[]
	  - tools[]

	  - process_query(q)
	}
	
	class NlipAgent {
	}

	class WeatherNlipAgent {
	}

	class CoordinatorNlipAgent {
	  - connect_to_server(url)
	  - send_to_server(url, msg)
	}

	class RagNlipAgent {
	  - milvus_context_manager
	}
	
	CheckrAgent <|-- NlipAgent : inheritance
	NlipAgent <|-- WeatherNlipAgent : inheritance
	NlipAgent <|-- CoordinatorNlipAgent : inheritance
	NlipAgent <|-- RagNlipAgent : inheritance
```
