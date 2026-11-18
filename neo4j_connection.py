import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    @classmethod
    def from_env(cls):
        """Build a connection from NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD (see .env.example)."""
        return cls(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "welcome123"),
        )

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            return list(session.run(query, parameters or {}))
