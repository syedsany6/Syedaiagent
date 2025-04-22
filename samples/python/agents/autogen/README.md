# Prerequisites

Since Mem0 requires postgresql to store the vector database, you need to have it installed and running on your machine. You can install it using the following commands:

## MacOS
```bash
brew install postgresql
```

# Installation

1. Create venv and activate

```bash
# enter A2A sample dirs
cd samples/python

uv venv --python 3.12
source .venv/bin/activate  # On Unix/macOS
```

2. Install deps

```bash
# install deps for the overall workspace
uv pip install -r pyproject.toml
# install deps for autogen workspace member
uv pip install -e agents/autogen
```

3. Create an .env file

```bash
cp .env.example .env
```

Then, fill the .env with your keys and appropriate MCP servers:

```bash
LLM_MODEL=o3-mini
API_KEY=sk-proj-H30rO7vd...
MCP_SERVER_URL=http://localhost:4000/sse
```

# Start A2A server

```bash
uv run agents/autogen/oraichain/__main__.py
```