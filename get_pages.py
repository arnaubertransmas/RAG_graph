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


def load_prompt():
    with open("prompts/structure_graph.txt", "r", encoding="utf-8") as f:
        return f.read()

PROMPT = load_prompt()


def fetch_wikipedia_page(title):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + title

    headers = {
        "User-Agent": "RAGgraph/1.0 (arnau@gmail.com)"
    }

    res = requests.get(url=url, headers=headers)
    # print(url)
    # print(res.status_code)

    if res.status_code != 200:
        return None
    
    data = res.json()
    return data.get("extract", "")

# for i in SEED_TOPICS:
#     a = fetch_wikipedia_page(i)
#     print(a)


def ask_llm(text):

    prompt = PROMPT.format(text=text)

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

        result = ask_llm(wikipedia)

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


# ollama run mistral