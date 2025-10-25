# Checkr Agents

``` mermaid

class Diagram
    class CheckrAgent {
	}
	
	class NlipAgent {
	}

	class WeatherNlipAgent {
	}

	class CoordinatorNlipAgent {
	}

	class RagNlipAgent {
	}
	
	CheckrAgent <|-- NlipAgent : inheritance
	NlipAgent <|-- WeatherNlipAgent : inheritance
	NlipAgent <|-- CoordinatorNlipAgent : inheritance
	NlipAgent <|-- RagNlipAgent : inheritance
```
