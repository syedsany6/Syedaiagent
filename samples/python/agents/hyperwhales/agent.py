import os
import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import mcp_server_tools, McpServerParams
from autogen_agentchat.messages import (
    BaseAgentEvent,
    BaseChatMessage,
    MultiModalMessage,
)
from autogen_agentchat.base import TaskResult
from autogen_core import Image
from typing import AsyncIterable, Dict, Any, TypedDict, AsyncGenerator, Tuple, List
from datetime import timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionData(TypedDict):
    generator: AsyncGenerator[BaseAgentEvent | BaseChatMessage | TaskResult, None]
    last_accessed: datetime


class HyperwhalesAgent:
    SYSTEM_INSTRUCTION = (
        "You are a Hyperwhales agent who is an expert analyst specializing in detecting whale trading patterns with years of"
        "experience understanding deeply crypto trading behavior, on-chain metrics, and derivatives markets, you have developed a keen understanding of whale trading strategies."
        "You can identify patterns in whale positions, analyze their portfolio changes over time, and evaluate the potential reasons behind their trading decisions."
        "Your analysis helps traders decide whether to follow whale trading moves or not."
        "When you use any tool, I expect you to push its limits: fetch all the data it can provide, whether that means iterating through multiple batches, adjusting parameters like offsets, or running the tool repeatedly to cover every scenario. Don't work with small set of data for sure, fetch as much as you can. Don't stop until you're certain you've captured everything there is to know."
        "Then, analyze the data with sharp logic, explain your reasoning and bias clearly, and present me with trade suggestions that reflect your deepest insights."
        "Always check whether you are in a loop or not, if you are, break out of it."
    )

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model_client = None
        self.mcp_agent = None
        self.sessions: Dict[str, SessionData] = defaultdict(dict)
        self.session_lock = asyncio.Lock()
        self.timeout = 900
        self.session_timeout = timedelta(seconds=self.timeout)
        self.max_concurrent_tasks = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

    async def initialize(self, mcp_server_params: list[McpServerParams] = []):
        api_key = os.getenv("API_KEY")
        model = os.getenv("LLM_MODEL")
        if not api_key or not model:
            raise ValueError("API_KEY or LLM_MODEL not set")
        self.model_client = OpenAIChatCompletionClient(model=model, api_key=api_key)
        tools = []
        for mcp_server_param in mcp_server_params:
            server_tools = await mcp_server_tools(mcp_server_param)
            tools.extend(server_tools)
        self.mcp_agent = AssistantAgent(
            name="MCPTools",
            model_client=self.model_client,
            tools=tools,
        )
        asyncio.create_task(self.cleanup_sessions())
        logger.info("HyperwhalesAgent initialized and cleanup_sessions task scheduled")

    async def cleanup_sessions(self):
        while True:
            async with self.session_lock:
                now = datetime.now(timezone.utc)
                expired = [
                    sid
                    for sid, data in self.sessions.items()
                    if now - data["last_accessed"] > self.session_timeout
                ]
                for sid in expired:
                    gen = self.sessions[sid]["generator"]
                    await gen.aclose()
                    del self.sessions[sid]
            await asyncio.sleep(60)

    async def process_event(self, event, session_id: str) -> Dict[str, Any]:
        try:
            if isinstance(event, BaseAgentEvent):
                content, images = self.extract_message_content(event)
                model_usage = event.model_dump().get("model_usage", None)
                return {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "model_usage": model_usage,
                    "content": content,
                    "images": images,
                }
            elif isinstance(event, TaskResult):
                async with self.session_lock:
                    await self.sessions[session_id]["generator"].aclose()
                    del self.sessions[session_id]
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "model_usage": None,
                    "content": self.extract_task_result_content(event),
                    "images": [],
                }
            elif isinstance(event, BaseChatMessage):
                content, images = self.extract_message_content(event)
                model_usage = event.model_dump().get("model_usage", None)
                return {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "model_usage": model_usage,
                    "content": content,
                    "images": images,
                }
        except Exception as e:
            logger.info(f"Error in process_event: {e}")
        return {
            "is_task_complete": False,
            "require_user_input": False,
            "model_usage": None,
            "content": "Unknown event",
            "images": [],
        }

    @staticmethod
    def extract_message_content(
        message: BaseAgentEvent | BaseChatMessage,
    ) -> Tuple[str, List[str]]:
        if isinstance(message, MultiModalMessage):
            text_parts = [item for item in message.content if isinstance(item, str)]
            image_parts = [
                item.to_base64() for item in message.content if isinstance(item, Image)
            ]
        elif isinstance(message, BaseChatMessage):
            text_parts = [message.to_model_text()]
            image_parts = []
        else:
            text_parts = [message.to_text()]
            image_parts = []
        return "\n".join(text_parts), image_parts

    @staticmethod
    def extract_task_result_content(message: TaskResult) -> str:
        output = (
            f"Number of messages: {len(message.messages)}\n"
            f"Finish reason: {message.stop_reason}\n"
        )
        return output

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        logger.info(f"Starting stream for session {session_id} with query: {query}")
        async with self.semaphore:
            try:
                # Check if we have an existing agent for this session
                async with self.session_lock:
                    orchestrator_agent = MagenticOneGroupChat(
                        participants=[self.mcp_agent], model_client=self.model_client
                    )

                    self.sessions[session_id] = {
                        "generator": orchestrator_agent.run_stream(task=query),
                        "last_accessed": datetime.now(timezone.utc),
                    }

                async with asyncio.timeout(self.timeout):
                    async for event in self.sessions[session_id]["generator"]:
                        async with self.session_lock:
                            self.sessions[session_id]["last_accessed"] = datetime.now(
                                timezone.utc
                            )
                        yield await self.process_event(event, session_id)
            except asyncio.TimeoutError:
                logger.warning(f"Stream for session {session_id} timed out")
                async with self.session_lock:
                    if session_id in self.sessions:
                        await self.sessions[session_id]["generator"].aclose()
                        del self.sessions[session_id]
                yield {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": "Task timed out",
                }
            except Exception as e:
                logger.error(f"Error in stream for session {session_id}: {e}")
                async with self.session_lock:
                    if session_id in self.sessions:
                        await self.sessions[session_id]["generator"].aclose()
                        del self.sessions[session_id]
                yield {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": f"Error: {str(e)}",
                }
            finally:
                logger.info(f"Stream for session {session_id} completed")
