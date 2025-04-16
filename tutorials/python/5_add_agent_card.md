# Agent Card

Now that we have defined our skills, we can create an Agent Card.

Remote Agents are required to publish an Agent Card in JSON format describing the agent's capabilities and skills in addition to authentication mechanisms. In other words, this lets the world know about your agent and how to interact with it. You can find more details in the [documentation](documentation?id=agent-card).

## Implementation <!-- {docsify-ignore} -->

First lets add some helpers for parsing command line arguments. This will be helpful later for starting our server

```bash
uv add click
```

And update our code

```python
import logging

import click
from dotenv import load_dotenv
import google_a2a
from google_a2a.common.types import AgentSkill, AgentCapabilities, AgentCard

logging.basicConfig(level=logging.Info)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
  skill = AgentSkill(
    id="my-project-echo-skill"
    name="Echo Tool"
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"]
  )
  logging.info(skill)

if __name__ == "__main__":
  main()

```

Next we'll add our Agent Card

```python
# ...
def main(host, port):
  # ...
  capabilities = AgentCapabilities()
  agent_card = AgentCard(
    name="Echo Agent",
    description="This agent echos the input given",
    url=f"http://{host}:{port}/",
    version="0.1.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=capabilities,
    skills=[skill]
  )
  logging.info(agent_card)

if __name__ == "__main__":
  main()
```


## Test Run <!-- {docsify-ignore} -->

Let's give this a run.

```bash
uv run my-project
```

The output should look something like this.

```bash

```

<div class="bottom-buttons" style="flex flex-row">
  <a href="#/tutorials/python/4_agent_skills.md" class="back-button">Back</a>
  <a href="#/tutorials/python/6_start_server.md" class="next-button">Next</a>
</div>
