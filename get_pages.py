import requests
from database import connection, save_graph, is_processed, mark_processed
from utils import load_prompt, safe_json_load

SEED_TOPICS = [
    "United_States",
    "Cold_War",
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
    # url = f"https://ca.wikipedia.org/w/api.php"
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
    return text[:8000]

# for i in SEED_TOPICS:
#     a = fetch_wikipedia_page(i)
#     print(a)


# def stream_wikipedia_dump_ca(dump_path):
#     import bz2
#     import xml.etree.ElementTree as ET
#     xml namespace
#     NS = "http://www.mediawiki.org/xml/schema/export-0.10/"
    
#     with bz2.open(dump_path, 'rb') as f:
#         context = ET.iterparse(f, events=('end',))
#         for event, elem in context:
#             if elem.tag == f"{{{NS}}}page":
#                 title = elem.findtext(f"{{{NS}}}title")
#                 text_elem = elem.find(f".//{{{NS}}}text")
#                 text = text_elem.text if text_elem is not None else ''
                
#                 if title and ':' not in title:  # Salta Talk:, Usuari:, etc.
#                     yield title, text[:3000]
                
#                 elem.clear()

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


if __name__ == "__main__":

    connection_neo4j = connection()

    # for title, text in stream_wikipedia_dump_ca("cawiki-latest-pages-articles-multistream.xml.bz2"):
    #     if is_processed(title, connection_neo4j):
    #         print("Skipping", title)
    #         continue
    
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