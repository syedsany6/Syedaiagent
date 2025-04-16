from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from agents.hyperwhales.task_manager import AgentTaskManager
from agents.hyperwhales.agent import HyperwhalesAgent
import click
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10000)
def main(host, port):
    try:
        if not os.getenv("API_KEY"):
            raise MissingAPIKeyError("API_KEY environment variable not set.")
        if not os.getenv("LLM_MODEL"):
            raise MissingAPIKeyError("LLM_MODEL environment variable not set.")
        
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="hyperwhales",
            name="Hyperwhales",
            description="Analyze whale trading patterns, positions, and portfolio changes over time. Provide insights and trade suggestions.",
            tags=["hyperwhales"],
            examples=["Find me some trades now based on whales data and history"],
        )
        agent_card = AgentCard(
            name="Hyperwhales",
            description="Analyze whale trading patterns, positions, and portfolio changes over time. Provide insights and trade suggestions.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=HyperwhalesAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=HyperwhalesAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=HyperwhalesAgent()),
            host=host,
            port=port,
        )
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)
    
if __name__ == "__main__":
    main()

