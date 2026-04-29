import requests
import json
from get_pages import load_prompt
from database import connection

# INTENTAR FER QUE TINGUI MEMÒRI + SIMILARITY FALLBACK

driver = connection()

EQUIVALENCE_RELATIONS = {"WAS_OFFICIAL_NAME_OF", "ALSO_KNOWN_AS", "IS_ALSO_CALLED", "KNOWN_AS"}

def extract_entities(question):
    extract_entities_prompt = load_prompt("extract_entities.txt")
    prompt = extract_entities_prompt.format(text=question)
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "temperature": 0
        }
    )
    return res.json()["response"]

def parse_entities(text):
    return json.loads(text)

def resolve_names_in_graph(names: list[str]):
    resolved = set(names)

    with driver.session() as session:

        # Entity matching
        for name in names:
            acronym_pattern = f"(?i){'.*'.join(name)}"

            result = session.run("""
                MATCH (n:Entity)
                WHERE toLower(n.name) CONTAINS toLower($name)
                   OR toLower($name) CONTAINS toLower(n.name)
                   OR n.name =~ $pattern
                RETURN n.name AS name
                LIMIT 2
            """, name=name, pattern=acronym_pattern)

            resolved.update(r["name"] for r in result if r["name"])

        # NO graph expansion
        result = session.run("""
            MATCH (a:Entity)-[r]-(b:Entity)
            WHERE a.name IN $names
              AND type(r) IN $relations
            RETURN b.name AS name
        """, names=list(resolved), relations=list(EQUIVALENCE_RELATIONS))

        resolved.update(r["name"] for r in result if r["name"])

    return list(resolved)


def get_context(entities_json: str):
    names = parse_entities(entities_json)
    names = resolve_names_in_graph(names)
    print("Buscant:", names)
    
    triples = set()
    with driver.session() as session:
        for name in names:
            result = session.run("""
                MATCH (a:Entity)-[r]->(b)
                WHERE toLower(a.name) CONTAINS toLower($name)
                   OR toLower($name) CONTAINS toLower(a.name)
                RETURN a.name AS origen, type(r) AS relacio, b.name AS desti
            """, name=name)
            for r in result:
                triples.add(f"{r['origen']} --[{r['relacio']}]--> {r['desti']}")

        result = session.run("""
            MATCH (a:Entity)-[r]-(b:Entity)
            WHERE any(name IN $names WHERE toLower(a.name) CONTAINS toLower(name)
                                       OR toLower(name) CONTAINS toLower(a.name))
              AND any(name IN $names WHERE toLower(b.name) CONTAINS toLower(name)
                                       OR toLower(name) CONTAINS toLower(b.name))
            RETURN a.name AS origen, type(r) AS relacio, b.name AS desti
        """, names=names)
        for r in result:
            triples.add(f"{r['origen']} --[{r['relacio']}]--> {r['desti']}")

    return "\n".join(triples)

def answer_question(context, question):
    answer = load_prompt("generate_final_response.txt")
    prompt = answer.format(text=context, question=question)
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "temperature": 0
        }
    )
    return res.json()["response"]

if __name__ == "__main__":
    while True:
        question = input("Question: ")
        
        if question.lower() == ":q":
            break

        entities = extract_entities(question)
        print("Entities:", entities)

        context = get_context(entities)
        print("Context:\n", context)
        
        answer = answer_question(context, question)
        print("Answer:", answer)


    driver.close()