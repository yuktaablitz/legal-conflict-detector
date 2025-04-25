from pyvis.network import Network
import networkx as nx
from neo4j_connection import Neo4jConnection

def generate_interactive_graph(html_path="graph.html"):
    conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "welcome123")

    # Build graph from Neo4j
    records = conn.query("MATCH (a)-[r]->(b) RETURN a.name AS from, TYPE(r) AS rel, b.name AS to")
    conn.close()

    G = nx.DiGraph()
    for record in records:
        G.add_node(record['from'])
        G.add_node(record['to'])
        G.add_edge(record['from'], record['to'], label=record['rel'])

    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    net.toggle_physics(True)  # This makes nodes float/move when hovered!

    net.save_graph(html_path)
    return html_path
