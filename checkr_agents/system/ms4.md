

# Multi-Agent-System-4 Dialog

This dialog shows off the capabilities of the multi-agent-system.  It illustrates how specific "NLIP Prompts" are used to implement the "NLIP Capabilities" query.

## Getting going

In one window, start the agent system.

    $ cd checkr_agents
    $ python -m checkr_agents.system.ms4
    
In another window, start `Mach2` --- the universal NLIP client.

    $ cd kivy-chat-mach2
    $ python -m mach2
    
Connect `Mach2` to the agent system by entering `http://localhost:8024` in the address bar.


## Interact with the Coordinator Agent

The coordinator agent is the front end listening at `localhost:8024`.  Let's ask it what it's NLIP Capabilities are.

> **User**: What are your NLIP Capabilities?
>
> **Agent**:  
>> AGENT:Margaret  
>> CAPABILITY1:connect to other NLIP Agents via URL, CAPABILITY2:send messages to other NLIP Agents, CAPABILITY3:retrieve NLIP capabilities from other agents, CAPABILITY4:act as an intermediary between users and other NLIP Agents  
>> I can help you communicate with other NLIP Agents by connecting to their servers and exchanging messages. Is there a specific NLIP Agent you'd like to connect with?  
>>  

We can see that the front-end agent is enabled to respond to the "NLIP Capabilities" query.  It has a name, "Margaret", and some capabilities describing how it can interact with other agents.

Cool!


## Add the Weather Agent

Because the Coordinator Agent has tools for speaking to other agents via NLIP, we can add them into our session to add capabilities.  Let's add the Weather Agent to our session.   The Weather Agent is part of our Agent System and is listening at an internal `mem://` URI.

> **User**: Please connect to mem://weather/.
>
> **Agent**: I'll connect to the weather NLIP Agent for you.
>
> > **Calling tool:connect_to_server with args:{'url': 'mem://weather/'}**  
> > Great! I've successfully connected to the weather server. Now I'll ask for its NLIP capabilities:  
> > **Calling tool:send_to_server with args:{'url': 'mem://weather/', 'msg': 'What are your NLIP Capabilities?'}**  
> > I've received the capabilities of the weather NLIP Agent. Here's what I found:  
>>  
>> Name: Weather  
>>  
>> Capabilities:  
>> 1. get_forecast_by_coordinates: The Weather agent can provide weather forecasts when given specific latitude and longitude coordinates.  
>> 2. get_weather_alerts_by_state: The Weather agent can provide weather alerts for US states when given a two-letter state code (e.g., CA, NY).  
>>  
>> You can now ask this Weather agent about weather forecasts or alerts by providing the appropriate information, and I'll relay your requests.  

