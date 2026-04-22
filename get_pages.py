import requests


PROMPT = """
        You are an information extraction system.

        Your task is to extract a knowledge graph from the given text.

        Return ONLY valid JSON.

        ---

        OUTPUT FORMAT:

        {{
        "entities": [
            {{"name": "ENTITY_NAME", "type": "Person | Organization | Event | Location | Concept"}}
        ],
        "relations": [
            {{
            "source": "ENTITY_NAME",
            "relation": "RELATION_TYPE",
            "target": "ENTITY_NAME"
            }}
        ]
        }}

        ---

        RULES:
        - Only extract entities that are explicitly mentioned in the text.
        - Do not invent information.
        - Normalize entity names.
        - Use simple relation verbs.
        - If unsure, skip.

        ---

        TEXT:
        {text}
"""

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

    for i in SEED_TOPICS:

        wikipedia = fetch_wikipedia_page(i)

        if not wikipedia:
            continue

        result = ask_llm(wikipedia)
    
        print("TOPIC", i)
        print(result)
        print("----" * 50)


# ollama run mistral
