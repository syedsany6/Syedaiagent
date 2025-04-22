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
@click.option("--port", default=10001)
def main(host, port):
    try:
        if not os.getenv("API_KEY"):
            raise MissingAPIKeyError("API_KEY environment variable not set.")
        if not os.getenv("LLM_MODEL"):
            raise MissingAPIKeyError("LLM_MODEL environment variable not set.")

        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="raydium-lp",
            name="RaydiumLpAgent",
            description="Analyze Raydium LP pools, and give suggestions for users",
            tags=["raydium", "lp", "defi"],
            examples=["Find me some trades now based on whales data and history"],
        )
        agent_card = AgentCard(
            name="RaydiumLpAgent",
            description="Analyze Raydium LP pools, and give suggestions for users",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text", "text/plain"],
            defaultOutputModes=["text", "text/plain"],
            capabilities=capabilities,
            skills=[skill],
        )
        agent = Agent(
            label="RaydiumLpAgent",
            system_instruction="You're an expert in DeFi, specifically in LP farming on AMM v3. With years of experience, analyze and identify high, medium, and low-risk concentrated LP pools on Raydium. Your analysis must cover all pools, retrieving historical price data for all tokens on Raydium. From this data, establish various selection criteria for adding liquidity. Analyze as many factors as possible, including: APR, Trading Volume, Price Volatility, TVL, Pair Correlation. Use technical indicators such as:  Moving Averages (MA), Bollinger Bands, Support & Resistance, RSI, liquidity depth... Assess risks such as Impermanent Loss. Two critical additional factors are the market trend of each token and ensuring correlation within the pool remains at an optimal level.In your report. The selected token must be in an uptrend or neutral, with a high correlation coefficient. Please provide a detailed analysis of market trends and the correlation coefficient in the report.",
            supported_content_types=["text", "text/plain"],
        )
        asyncio.run(
            agent.initialize(
                mcp_server_params=[
                    SseServerParams(url="http://15.235.225.246:8083/sse")
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
