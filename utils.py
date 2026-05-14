import requests
import json


def load_prompt(file_path):
    with open(f"prompts/{file_path}", "r", encoding="utf-8") as f:
        return f.read()
    

def ask_llm(question, prompt_file_name, context=None):
    prompt_template = load_prompt(prompt_file_name)
    
    if context is not None:
        prompt = prompt_template.format(context=context, text=question)
    else:
        prompt = prompt_template.format(text=question)
    
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "temperature": 0,
        }
    )
    return res.json()["response"]


def safe_json_load(text):
    ''' netejem json '''

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