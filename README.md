# KG-RAG: Knowledge Graph-based Retrieval-Augmented Generation

A RAG system that uses a knowledge graph, instead of isolated text chunks, to give an LLM structured and connected context. This improves answer accuracy and reduces hallucinations.

Final project of the vocational Master's in AI & Big Data at Institut TIC de Barcelona, presented at **Tech Summit 2026 – AI Revolution** (StartupMat).

## The problem
Traditional RAG systems retrieve text chunks in isolation and ignore the relationships between them. This leads to incoherent answers and increases the risk of hallucinations.

## How it works
1. **Data collection:** fetches English Wikipedia articles about the Cold War (United States, Soviet Union, NATO, Berlin Wall…).
2. **Graph construction:** Mistral 7B, running locally with Ollama, extracts entities and relations from each article as semantic triples (`entityA --[RELATION]--> entityB`) and stores them in Neo4j.
3. **Retrieval:** when the user asks a question, the system extracts its key entities, resolves them against the graph (including aliases such as *USA → United States*) and retrieves their relations as structured context.
4. **Grounded answer:** the LLM answers only if the graph contains enough information. Otherwise, it says so explicitly instead of making something up.

The resulting graph contains **553 entities and 664 relations** between key concepts, events and actors of the Cold War.

## Tech stack
Python · Neo4j · Ollama · Mistral 7B · Wikipedia API

## Project structure
| File | Purpose |
|---|---|
| `get_pages.py` | Fetches Wikipedia articles and builds the knowledge graph |
| `database.py` | Neo4j connection and graph storage |
| `rag.py` | Entity resolution and context retrieval from the graph |
| `app.py` | Command-line question-answering interface |
| `utils.py` | LLM calls and helpers |
| `prompts/` | Prompts for graph extraction, entity extraction and answer generation |

## Installation and usage

### Prerequisites
- Python 3.9 or higher
- A running Neo4j instance (local or Neo4j AuraDB)

### Execute the following commands
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama serve        # in another terminal
python3 get_pages.py
python3 app.py
```
