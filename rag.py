from utils import safe_json_load

EQUIVALENCE_RELATIONS = {"WAS_OFFICIAL_NAME_OF", "ALSO_KNOWN_AS", "IS_ALSO_CALLED", "KNOWN_AS"}

def parse_entities(text):
    ''' retorna json net amb les entitats '''
    return safe_json_load(text)


def resolve_names_in_graph(names, driver):
    ''' busca names semblants 
        USA -> United States of America
    '''

    if not names:
        return []

    resolved = set(names)

    with driver.session() as session:
        for name in names:
            if not name.strip():
                continue
            
            # busquem nodes similars
            # returns node 'Cold War' → score 2.99
            result = session.run("""
                CALL db.index.fulltext.queryNodes('entity_name_index', $search)
                YIELD node, score
                RETURN node.name AS name, score
                LIMIT 5
            """, search=name)
            # de neo4j cursor a list per poder iterar fàcilment
            rows = list(result)
            resolved.update(r["name"] for r in rows if r["name"])

        # busca relacions d'equivelence_relations
        result = session.run("""
            MATCH (a:Entity)-[r]-(b:Entity)
            WHERE a.name IN $names
              AND type(r) IN $relations
            RETURN b.name AS name
        """, names=list(resolved), relations=list(EQUIVALENCE_RELATIONS))

        resolved.update(r["name"] for r in result if r["name"])

    return list(resolved)


def get_context(entities_json, driver):
    ''' agafa les relacions per passar-les al model 
        returns context
    '''

    names = parse_entities(entities_json)

    if not names:
        return ""

    names = resolve_names_in_graph(names, driver)
    # print("Buscant:", names)

    # A --[RELATION]--> B
    triples = set()

    with driver.session() as session:
        search_query = " OR ".join(f'"{n}"' for n in names if n.strip())

        if search_query:
            # busquem nodes
            result = session.run("""
                CALL db.index.fulltext.queryNodes('entity_name_index', $search)
                YIELD node AS a
                MATCH (a)-[r]->(b)
                RETURN a.name AS origen, type(r) AS relacio, b.name AS desti
            """, search=search_query)
            rows = list(result)
            
            for r in rows:
                triples.add(f"{r['origen']} --[{r['relacio']}]--> {r['desti']}")

        # relacions entre entitats
        result = session.run("""
            MATCH (a:Entity)-[r]-(b:Entity)
            WHERE a.name IN $names AND b.name IN $names
            RETURN a.name AS origen, type(r) AS relacio, b.name AS desti
        """, names=names)
        for r in result:
            triples.add(f"{r['origen']} --[{r['relacio']}]--> {r['desti']}")

    return "\n".join(triples)