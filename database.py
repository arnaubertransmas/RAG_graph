from neo4j import GraphDatabase

def connection():
    # per full wikipedia -->
    # URI = neo4j+s://20209bc2.databases.neo4j.io
    # USER = 20209bc2
    # PASSWORD = X_BMnvtplEig2sJnOmtkE08Qrfm7LAsEosDalBdzhU
    URI = "neo4j+s://63503d8c.databases.neo4j.io"
    USER = "63503d8c"
    PASSWORD = "gqviLR21bIDLRTZtN9teKT2I90zxZeElMGd1Ybc34og"

    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    return driver

def save_graph(data, driver):
    ''' guardem graph a Neo4j Aura '''
    # build entity map from declared entities
    entities = {e["name"]: e.get("type", "Unknown") for e in data.get("entities", [])}

    # auto-add any source/target referenced in relations but missing from entities
    for rel in data.get("relations", []):
        for key in ("source", "target"):
            name = rel[key]
            if name not in entities:
                print(f"  [WARN] auto-adding missing entity: '{name}'")
                entities[name] = "Unknown"

    with driver.session() as session:
        # entitats
        for name, etype in entities.items():
            session.run("""
                MERGE (n:Entity {name: $name})
                SET n.type = $type
            """, name=name, type=etype)

        # relacions
        for rel in data.get("relations", []):
            rel_type = rel["relation"].upper().replace(" ", "_")
            session.run(f"""
                MATCH (a:Entity {{name: $source}})
                MATCH (b:Entity {{name: $target}})
                MERGE (a)-[r:{rel_type}]->(b)
            """, source=rel["source"], target=rel["target"])
            print(f"  [REL] {rel['source']} --[{rel_type}]--> {rel['target']}")


def is_processed(title, driver):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Page {title:$title, processed:true})
            RETURN p
            LIMIT 1
        """, title=title)

        return result.single() is not None 


def mark_processed(title, driver):
    with driver.session() as session:
        session.run("""
            MERGE (p:Page {title:$title})
            SET p.processed = true
        """, title=title)

def unmark_processed(title, driver):
    with driver.session() as session:
        session.run("""
            MATCH (p:Page {title:$title})
            SET p.processed = false
        """, title=title)


# conn = connection()
# SEED_TOPICS = [
#     "United_States",
#     "Cold_War",
#     "Soviet_Union",
#     "NATO",
#     "Warsaw_Pact",
#     "Cuban_Missile Crisis",
#     "Korean_War",
#     "Vietnam_War",
#     "Berlin_Wall",
#     "Mikhail_Gorbachev",
#     "Ronald_Reagan"
# ]

# for topic in SEED_TOPICS:
#     unmark_processed(topic, conn)