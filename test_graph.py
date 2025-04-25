from graph_builder import build_graph
from neo4j_connection import Neo4jConnection

conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "welcome123")

build_graph(conn)

print("Graph populated.")
conn.close()
