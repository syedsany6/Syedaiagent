# Prerequisites

Since Mem0 requires postgresql to store the vector database, you need to have it installed and running on your machine. You can install it using the following commands:

## MacOS
```bash
brew install postgresql
```

# Installation

1. Create venv and activate

```bash
uv venv --python 3.12
source .venv/bin/activate  # On Unix/macOS
```

2. Install deps

```bash
uv pip install -r pyproject.toml
```

# Start A2A server

```bash
uv run agents/autogen/oraichain/__main__.py
```