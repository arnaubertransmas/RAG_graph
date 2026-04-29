import requests
from database import connection, save_graph, is_processed, mark_processed, safe_json_load

SEED_TOPICS = [
    "Cold_War",
    "United_States",
    "Soviet_Union",
    "NATO",
    "Warsaw_Pact",
    "Cuban_Missile Crisis",
    "Korean_War",
    "Vietnam_War",
    "Berlin_Wall",
    "Mikhail_Gorbachev",
    "Ronald_Reagan"
]


def load_prompt(file_path):
    with open(f"prompts/{file_path}", "r", encoding="utf-8") as f:
        return f.read()


def fetch_wikipedia_page(title):
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts",
        "exintro": False,
        # Text pla, sense HTML
        "explaintext": True,
        "format": "json"
    }
    headers = {"User-Agent": "RAGgraph/1.0 (arnau@gmail.com)"}
    res = requests.get(url=url, params=params, headers=headers)
    
    pages = res.json()["query"]["pages"]
    page = next(iter(pages.values()))
    text = page.get("extract", "")
    
    # ~3000 caràcters, context max de Mistral
    return text[:3000]

# for i in SEED_TOPICS:
#     a = fetch_wikipedia_page(i)
#     print(a)


def create_graph_structure(text):

    stucture_graph_prompt = load_prompt("structure_graph.txt")
    prompt = stucture_graph_prompt.format(text=text)

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

# print(ask_llm("return the entities"))

if __name__ == "__main__":

    connection_neo4j = connection()

    for topic in SEED_TOPICS:

        if is_processed(topic, connection_neo4j):
            print("Skipping", topic)
            continue

        wikipedia = fetch_wikipedia_page(topic)

        if not wikipedia:
            continue

        result = create_graph_structure(wikipedia)
        data = safe_json_load(result)

        if not data:
            print("INVALID JSON:", topic)
            continue

        print("TOPIC", topic)
        print(result)
        print("----" * 50)

        try:
            save_graph(data, connection_neo4j)
        except Exception as e:
            print("ERROR,", e)

        mark_processed(topic, connection_neo4j)


# # ollama run mistral