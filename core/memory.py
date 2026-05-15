"""
Memory engine for Spoon Feedr, combining SQLite and ChromaDB.
Handles structured facts and vector-based semantic search.
"""

import sqlite3
import chromadb
from chromadb.config import Settings
import json
import os

class MemoryEngine:
    """Hybrid memory storage for agent-managed project context."""

    def __init__(self, db_path="db/spoon_feedr.db", chroma_path="db/chroma"):
        """Initializes the SQLite and ChromaDB clients."""
        self.db_path = db_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.init_sqlite()
        # Using a collection for project-specific knowledge
        self.collection = self.chroma_client.get_or_create_collection(name="project_memory")

    def init_sqlite(self):
        """Creates the necessary tables in SQLite for facts and interactions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def store_fact(self, key, value, category="general"):
        """Stores or updates a structured fact in SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO facts (key, value, category, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, json.dumps(value), category))
        conn.commit()
        conn.close()

    def get_fact(self, key):
        """Retrieves a fact from SQLite by its key."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM facts WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return json.loads(row[0]) if row else None

    def add_to_vector_memory(self, text, metadata=None, ids=None):
        """Adds a document to the ChromaDB vector memory."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else None,
            ids=[ids] if ids else [str(os.urandom(8).hex())]
        )

    def query_vector_memory(self, query_text, n_results=5):
        """Queries the vector memory for relevant context."""
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

def memory_agent_node(state):
    """
    Extracts facts from the last interaction and persists them.
    Used as a node in the LangGraph workflow.
    """
    # Increment current_step to avoid infinite loops in the orchestrator
    state_update = {"current_step": state["current_step"] + 1}
    from vibe_launcher import CloudLLM
    cloud = CloudLLM()
    engine = MemoryEngine()

    last_msg = state["messages"][-1].content
    # Simple fact extraction prompt
    prompt = f"Extract key project facts, technologies, or user preferences from this message as a JSON list of {{'key':..., 'value':..., 'category':...}}. MESSAGE: {last_msg}"

    try:
        resp = cloud.chat([{"role": "user", "content": prompt}], temperature=0.1)
        # Find JSON in response
        import re
        match = re.search(r'\[.*\]', resp, re.DOTALL)
        if match:
            facts = json.loads(match.group())
            for fact in facts:
                engine.store_fact(fact['key'], fact['value'], fact.get('category', 'general'))
                # Also add to vector memory
                engine.add_to_vector_memory(f"{fact['key']}: {fact['value']}", metadata={"category": fact.get('category', 'general')})
    except Exception as e:
        print(f"Memory extraction failed: {e}")

    return state_update
