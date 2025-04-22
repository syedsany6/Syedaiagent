from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from agents.autogen.task_manager import AgentTaskManager
from agents.autogen.agent import Agent
from autogen_ext.tools.mcp import SseServerParams
import click
import os
import logging
import asyncio
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=10002)
def main(host, port):
    url = os.getenv('DOMAIN_URL', f'http://{host}:{port}/')
    print(f"URL: {url}")
    try:
        if not os.getenv("API_KEY"):
            raise MissingAPIKeyError("API_KEY environment variable not set.")
        if not os.getenv("LLM_MODEL"):
            raise MissingAPIKeyError("LLM_MODEL environment variable not set.")

        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="YieldStable",
            name="YieldStableAgent",
            description="Analyze trades on defillama and provide insights on the best stablecoin farming strategies",
            tags=["yieldstable"],
            examples=["Find me some trades now based on whales data and history"],
        )
        agent_card = AgentCard(
            name="YieldStableAgent",
            description="Analyze trades on defillama and provide insights on the best stablecoin farming strategies",
            url=url,
            version="1.0.0",
            defaultInputModes=["text", "text/plain"],
            defaultOutputModes=["text", "text/plain"],
            capabilities=capabilities,
            skills=[skill],
        )
        agent = Agent(
            label="YieldStableAgent",
            system_instruction="You are an expert AI Stablecoin Yield Consultant. Your role is to research, verify, and recommend highest-yield stablecoin farming strategies based on user preferences, investment horizon, and risk tolerance—using tools such as yield aggregators (DefiLlama preferred), web search, and social sentiment.",
            supported_content_types=["text", "text/plain"],
        )
        asyncio.run(
            agent.initialize(
                mcp_server_params=[
                    # SseServerParams(url="http://15.235.225.246:8054/sse"),
                    SseServerParams(url="http://15.235.225.246:5000/sse"),
                    # SseServerParams(url="http://15.235.225.246:8058/sse"),
                ]
            )
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=agent),
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
