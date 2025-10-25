# Checkr Agents

``` mermaid

classDiagram
    class CheckrAgent {
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
	}
	
	CheckrAgent <|-- NlipAgent : inheritance
	NlipAgent <|-- WeatherNlipAgent : inheritance
	NlipAgent <|-- CoordinatorNlipAgent : inheritance
	NlipAgent <|-- RagNlipAgent : inheritance
```
