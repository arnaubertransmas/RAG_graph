import requests
import json


def load_prompt(file_path):
    with open(f"prompts/{file_path}", "r", encoding="utf-8") as f:
        return f.read()
    

def ask_llm(text, prompt_file_name, context=None):
    extract_entities_prompt = load_prompt(prompt_file_name)
    if context:
        prompt = extract_entities_prompt.format(text=context, question=text)
    else:
        prompt = extract_entities_prompt.format(text=text)
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


def safe_json_load(text):

    try:
        return json.loads(text)
    except:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            return None

        cleaned = text[start:end+1]

        return json.loads(cleaned)

    except:
        return None