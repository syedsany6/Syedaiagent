# Marvin Contact Extractor Agent

This example demonstrates how to implement an agent using the Marvin framework to extract structured contact information from text and integrate it with the A2A framework.

## Overview

This example showcases Marvin's strengths in structured data extraction and multi-turn interactions:

- **Multi-Turn Interaction** - Agent asks for missing information when extraction is incomplete
- **Type-Safe Extraction** - Uses `result_type=ContactInfo` to get structured data
- **Custom Tools** - Validates emails and formats phone numbers
- **State Management** - Maintains extraction state across conversation turns

## How It Works

1. User sends text containing potential contact information
2. Marvin agent extracts structured data using `agent.run(result_type=ContactInfo)`
3. If information is incomplete, agent identifies missing fields and asks specific questions
4. User provides additional information in subsequent messages
5. Agent merges new information with previously extracted data
6. When contact information is complete, agent returns final structured data
7. A2A sends back both a text summary and structured JSON data

## Architecture

The implementation follows the A2A architecture pattern:

1. **ExtractorAgent (agent.py)** - Core agent with multi-turn extraction logic
2. **AgentTaskManager (task_manager.py)** - A2A integration layer handling task state transitions
3. **Server Entry Point (__main__.py)** - Sets up and runs the A2A server

## Files

- `agent.py` - Core agent implementation with multi-turn extraction
- `task_manager.py` - A2A integration using DataPart for structured data
- `__main__.py` - Server entry point
- `example.py` - Standalone example (without A2A)

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

## Example Multi-Turn Interactions

**Interaction 1: Partial Information**
- User: "John's email is john@example.com"
- Agent: "Thanks for providing John's email. Could you also share John's full name and any other contact details like a phone number or organization?"
- User: "His name is John Smith and he works at Acme Corp"
- Agent: "Thank you! I've recorded the contact information for John Smith who works at Acme Corp with email john@example.com."

**Interaction 2: Missing Contact Method**
- User: "Sarah Jones is the new marketing director"
- Agent: "I see that Sarah Jones is the marketing director. To complete the contact record, could you provide an email address or phone number where she can be reached?"
- User: "You can reach her at (555) 123-4567"
- Agent: "Great! I've saved the contact information for Sarah Jones, marketing director, with phone number (555) 123-4567."

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

## Contact Validation

The agent includes validation capabilities for contact information:
- Phone number formatting for consistency
- Email validation to ensure correct format
- Completeness checking to ensure essential fields are present

## Why Marvin?

This example showcases how Marvin simplifies building conversational AI applications:

1. **Type-Safe Outputs** - Get structured data directly with `result_type=ContactInfo`
2. **Thread Context** - Maintain conversation context across multiple turns
3. **Tool Integration** - Easily add validation tools to enhance extraction
4. **Simple Multi-Turn** - Natural handling of stateful conversations

## Learn More

- [marvin repo](https://github.com/prefecthq/marvin)
- [marvin docs](https://www.askmarvin.ai)
