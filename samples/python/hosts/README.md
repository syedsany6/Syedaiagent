## Hosts

Sample apps or agents that are A2A clients that work with A2A servers. 

* [CLI](/samples/python/hosts/cli)  
  Command line tool to interact with an A2A server. Specify the server location on the command line. The CLI client looks up the agent card and then performs task completion in a loop based on command line inputs. 

* [Orchestrator Agent](/samples/python/hosts/multiagent)  
An Agent that speaks A2A and can delegate tasks to remote agents. Built on the Google ADK for demonstration purposes. Includes a "Host Agent" that maintains a collection of "Remote Agents". The Host Agent is itself an agent and can delegate tasks to one or more Remote Agents. Each RemoteAgent is an A2AClient that delegates to an A2A Server. You need to create a `.env` file in this folder with `GOOGLE_API_KEY` environment variable, as it uses an LLM to figure out which remote agent to delegate a task to.

  ```bash
  cd samples/python/hosts/multiagent
  echo "GOOGLE_API_KEY=your_api_key_here" > .env
  ```

* [MultiAgent Web Host](/demo/README.md)  
*This lives in the [demo](/demo/README.md) directory*  
A web app that visually shows A2A conversations with multiple agents (using the [Orchestrator Agent](/samples/python/hosts/multiagent)). Will render text, image, and webform artifacts. Has a separate tab to visualize task state and history as well as known agent cards. You need to make sure `.env` file exists with your `GOOGLE_API_KEY` in the folder `samples/python/hosts/multiagent` before starting the Web Host.