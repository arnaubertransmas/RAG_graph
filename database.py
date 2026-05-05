from neo4j import GraphDatabase

def connection():
    URI = "neo4j+s://63503d8c.databases.neo4j.io"
    USER = "63503d8c"
    PASSWORD = "gqviLR21bIDLRTZtN9teKT2I90zxZeElMGd1Ybc34og"

    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    return driver

def save_graph(data, driver):

    with driver.session() as session:

        # entitats
        for entity in data["entities"]:
            session.run("""
                MERGE (n:Entity {name:$name})
                SET n.type = $type
            """,
            name=entity["name"],
            type=entity["type"])

        # relacions
        for rel in data["relations"]:
            rel_type = rel["relation"].upper().replace(" ", "_")
            session.run(f"""
                MATCH (a:Entity {{name:$source}})
                MATCH (b:Entity {{name:$target}})
                MERGE (a)-[r:{rel_type}]->(b)
            """,
            source=rel["source"],
            target=rel["target"])


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
# unmark_processed("NATO", conn)