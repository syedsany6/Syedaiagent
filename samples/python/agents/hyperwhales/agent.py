import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, mcp_server_tools
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.base import TaskResult
import asyncio
from typing import AsyncGenerator, Any, AsyncIterable, Dict

class HyperwhalesAgent:
  SYSTEM_INSTRUCTION = (
    "You are a Hyperwhales agent who is an expert analyst specializing in detecting whale trading patterns with years of"
    "experience understanding deeply crypto trading behavior, on-chain metrics, and derivatives markets, you have developed a keen understanding of whale trading strategies."
    "You can identify patterns in whale positions, analyze their portfolio changes over time, and evaluate the potential reasons behind their trading decisions."
    "Your analysis helps traders decide whether to follow whale trading moves or not."
    "When you use any tool, I expect you to push its limits: fetch all the data it can provide, whether that means iterating through multiple batches, adjusting parameters like offsets, or running the tool repeatedly to cover every scenario. Don't work with small set of data for sure, fetch as much as you can. Don't stop until you're certain you've captured everything there is to know."
    "Then, analyze the data with sharp logic, explain your reasoning and bias clearly, and present me with trade suggestions that reflect your deepest insights."
  )

  SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

  def __init__(self):
    tools = []
    tools_url = f"http://{"0.0.0.0"}:{"4000"}/sse"
    print(f"Setting up tools with SSE URL: {tools_url}")
    
    async def setup_tools():
        return await mcp_server_tools(SseServerParams(url=tools_url))
    
    # Run the async function in an event loop
    tools_list = asyncio.run(setup_tools())
    for tool in tools_list:
        tools.append(tool)    

    api_key = os.getenv('API_KEY')
    if not api_key:
        print("API_KEY not found in environment variables.")
        return None
    self.model_client = OpenAIChatCompletionClient(model="o3-mini", api_key=api_key)
    self.mcp_agent = AssistantAgent(name="MCPTools", model_client=self.model_client, tools=tools, system_message=self.SYSTEM_INSTRUCTION)
    self.sessions: dict[str, AsyncGenerator[Any, None]] = {}

  async def stream(self, query: str, session_id: str) -> AsyncIterable[Dict[str, Any]]:
    print(f"Running stream for session {session_id} with query: {query}")
    orchestrator_agent = MagenticOneGroupChat(participants=[self.mcp_agent], model_client=self.model_client)
    self.sessions[session_id] = orchestrator_agent.run_stream(task=query)
    
    async for event in self.sessions[session_id]:
      print(f"Event: {event}")
      result = {}
      if isinstance(event, BaseAgentEvent):
          result = { "is_task_complete": False, "require_user_input": False, "content": event.model_dump_json() }
      elif isinstance(event, TaskResult):
          result = { "is_task_complete": True, "require_user_input": False,  "content": event.stop_reason }
          del self.sessions[session_id]
      elif isinstance(event, BaseChatMessage):
          result = { "is_task_complete": False, "require_user_input": False, "content": event.model_dump_json() }
      yield result


