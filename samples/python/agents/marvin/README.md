# Marvin Contact Extractor Agent

This example demonstrates how to implement an agent using the Marvin framework for a specific task - contact information extraction - and integrate it with the A2A framework.

## Overview

This example showcases Marvin's strengths in natural language processing and structured extraction:

- Uses Marvin's Agent class for simple, streamlined agent creation
- Extracts structured contact information from unstructured text
- Provides clear, conversational responses
- Integrates with the A2A protocol for interoperability

## Architecture

The implementation follows the A2A architecture pattern:

1. **ExtractorAgent (agent.py)** - Core agent built with Marvin that extracts contact information
2. **AgentTaskManager (task_manager.py)** - Wrapper that integrates the agent with the A2A framework
3. **Server Entry Point (__main__.py)** - Sets up and runs the A2A server

## Files

- `agent.py` - Core agent implementation using Marvin's Agent class
- `task_manager.py` - A2A integration layer
- `__main__.py` - Server entry point
- `example.py` - Standalone example (without A2A)

## Running the Agent

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key

# Start the server
uv run agents/marvin
```

## Using with an A2A Client

```bash
# Run the CLI client
uv run hosts/cli --agent http://localhost:10001
```

## Example Inputs

- "My name is Jane Smith, email jane.smith@example.com, phone (555) 123-4567"
- "Contact our sales team at sales@company.com"
- "John Doe is the CEO of TechCorp and can be reached at john@techcorp.com"

## Why Marvin?

This example showcases how Marvin simplifies working with AI through:

1. **Simple Agent Interface** - Create powerful agents with minimal code
2. **Task Execution** - Run tasks directly using `agent.run()`
3. **Clean Integration** - Easily connect Marvin agents to other systems
4. **Structured Data** - Extract information from unstructured text

## Requirements

- marvin
- pydantic
- Python 3.13+

## Installation

```
pip install marvin pydantic
``` 