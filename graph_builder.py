import json
import re
from neo4j_connection import Neo4jConnection

def parse_affiliations_from_bio(bio):
    return re.findall(r'[A-Z][a-z]+(?: & [A-Z][a-z]+| [A-Z][a-z]+)+ LLP', bio)

def add_person_to_graph(name, bio, person_type):
    conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "welcome123")
    
    conn.query("MERGE (p:Person {name: $name}) SET p.bio = $bio, p.type = $type", {
        "name": name.strip(),
        "bio": bio.strip(),
        "type": person_type
    })

    affiliations = parse_affiliations_from_bio(bio)
    for org in affiliations:
        conn.query("MERGE (o:Org {name: $org})", {"org": org.strip()})
        conn.query("""
            MATCH (p:Person {name: $pname}), (o:Org {name: $oname})
            MERGE (p)-[:AFFILIATED_WITH]->(o)
        """, {"pname": name.strip(), "oname": org.strip()})

    conn.close()


def extract_affiliations(bio):
    return re.findall(r'[A-Z][a-z]+(?: & [A-Z][a-z]+| [A-Z][a-z]+)+ LLP', bio)

def detect_collaboration(bio, other_name):
    return other_name in bio

def detect_cases(bio):
    return re.findall(r'\b20[0-9]{2} .*? arbitration', bio, re.IGNORECASE)

def build_graph(conn, bio_file_path="data/sample_bios.json"):
    with open(bio_file_path) as f:
        bios = json.load(f)

    conn.query("MATCH (n) DETACH DELETE n")  # Reset

    names = {k: v["name"] for k, v in bios.items()}

    for ptype, person in bios.items():
        name = person["name"]
        bio = person["bio"]

        conn.query("CREATE (:Person {name: $name, type: $type, bio: $bio})", {
            "name": name.strip(),
            "type": ptype,
            "bio": bio.strip()
        })

        affiliations = extract_affiliations(bio)
        for org in affiliations:
            conn.query("MERGE (:Org {name: $name})", {"name": org.strip()})
            conn.query("""
                MATCH (p:Person {name: $pname}), (o:Org {name: $oname})
                CREATE (p)-[:AFFILIATED_WITH]->(o)
            """, {"pname": name.strip(), "oname": org.strip()})

        for other_type, other_name in names.items():
            if other_name != name and detect_collaboration(bio, other_name):
                conn.query("""
                    MATCH (a:Person {name: $a}), (b:Person {name: $b})
                    MERGE (a)-[:WORKED_WITH]->(b)
                """, {"a": name.strip(), "b": other_name.strip()})

        for case in detect_cases(bio):
            conn.query("MERGE (:Event {name: $case})", {"case": case.strip()})
            conn.query("""
                MATCH (p:Person {name: $p}), (e:Event {name: $case})
                MERGE (p)-[:PARTICIPATED_IN]->(e)
            """, {"p": name.strip(), "case": case.strip()})
