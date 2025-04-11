# Marvin Contact Extractor Agent

This example demonstrates how to implement an agent using the Marvin framework to extract structured contact information from text and integrate it with the A2A framework.

## Overview

This example showcases Marvin's strengths in structured data extraction and type-safe outputs:

- Uses Marvin's `Agent` class with `result_type` parameter to get structured data
- Returns both human-readable text and structured contact information
- Passes structured data through A2A's DataPart
- Uses `marvin.Thread` to manage the agent's context by `sessionId`

## How It Works

1. User sends text containing potential contact information
2. Marvin agent extracts structured data using `agent.run(result_type=ContactInfo)`
3. A2A sends back both a text summary and structured JSON data
4. Client can use either the human-readable text or process the structured data

## Architecture

The implementation follows the A2A architecture pattern:

1. **ExtractorAgent (agent.py)** - Core agent using Marvin's type-safe extraction capabilities
2. **AgentTaskManager (task_manager.py)** - A2A integration that handles both text and structured data
3. **Server Entry Point (__main__.py)** - Sets up and runs the A2A server

## Files

- `agent.py` - Core agent implementation using Marvin's `Agent` class and `result_type`
- `task_manager.py` - A2A integration that passes structured data with `DataPart`
- `__main__.py` - Server entry point

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- OpenAI API Key (or appropriate API key for the model you're using)

## Setup & Running

1. Navigate to the samples directory:

   ```bash
   cd samples/python
   ```

2. Create an environment file with your API key:

   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. Set up the Python environment:

   ```bash
   uv python pin 3.12
   uv venv
   source .venv/bin/activate
   ```

4. Run the agent:

   ```bash
   # Basic run
   uv run agents/marvin

   # On custom host/port
   uv run agents/marvin --host 0.0.0.0 --port 8080
   ```

5. In a separate terminal, run the A2A client:

   ```bash
   uv run hosts/cli --agent http://localhost:10001
   ```

## Example Inputs

- "My name is Jane Smith, email jane.smith@example.com, phone (555) 123-4567"
- "Contact our sales team at sales@company.com"
- "John Doe is the CEO of TechCorp and can be reached at john@techcorp.com"

## Structure of the Extracted Data

The agent returns structured contact information in this format:

```json
{
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "phone": "(555) 123-4567",
  "organization": "TechCorp",
  "role": "Software Engineer"
}
```

## Why Marvin?

This example showcases how Marvin simplifies working with LLMs:

1. **Type-Safe Outputs** - Get structured data directly with `result_type=ContactInfo`
2. **Minimal Code** - Simple implementation with Marvin's clean API
3. **Broad Model Support** - Marvin supports a wide range of models via [`pydantic-ai`](https://github.com/pydantic/pydantic-ai)
4. **Focus on Core Logic** - No need for complex prompt engineering

## Learn More

- [marvin repo](https://github.com/prefecthq/marvin)
- [marvin docs](https://www.askmarvin.ai)
