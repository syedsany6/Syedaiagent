from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "hyperwhales",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 768,  # Change this according to your local model's dimensions
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5-coder:32b",
            "temperature": 0,
            "max_tokens": 2000,
            "ollama_base_url": "https://ollama.orai.network",
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text:latest",
            "ollama_base_url": "https://ollama.orai.network",
        },
    },
}


class MemoryManager:
    def __init__(self):
        self.memory = Memory.from_config(config)

    def get_memory(self):
        return self.memory

    def add_memory(self, session_id: str, messages: list[dict]):
        self.memory.add(messages=messages, user_id=session_id)

    def relevant_memories(self, session_id: str, query: str):
        return self.memory.search(query, user_id=session_id).get("results")

    def delete_session(self, session_id: str):
        self.memory.delete_all(user_id=session_id)
