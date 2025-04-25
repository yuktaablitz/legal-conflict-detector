from neo4j_connection import Neo4jConnection
from conflict_classifier import classify_conflict_with_llama

# 1. Connect to your Neo4j database
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "welcome123")

# 2. Fetch bios of arbitrator and lawyer from Neo4j
def get_bios_from_graph():
    result = conn.query("MATCH (p:Person) RETURN p.name AS name, p.type AS type, p.bio AS bio")
    bios = {}
    for row in result:
        bios[row['type']] = {
            "name": row['name'],
            "bio": row['bio']
        }
    return bios

# 3. Get bios
bios = get_bios_from_graph()
arbitrator_bio = bios.get('arbitrator', {}).get('bio', 'No bio found')
lawyer_bio = bios.get('lawyer', {}).get('bio', 'No bio found')

# 4. Send to OpenAI
print("\n=== 🧠 Sending to OpenAI for Conflict Analysis ===\n")
result = classify_conflict_with_llama(arbitrator_bio, lawyer_bio)
print("\n📊 Conflict Assessment:\n")
print(result)

conn.close()
