======================================================
  KG-RAG - Guia d'instal·lació i execució
======================================================

REQUISITS PREVIS
----------------
- Python 3.9 o superior
- Neo4j en marxa


PAS 1 - Instal·lar Ollama
----------------------------------------------------

    sudo apt-get install ollama

Un cop instal·lat, descarrega el model que necessita l'app:

    ollama pull mistral


PAS 2 - Crear l'entorn virtual de Python
-----------------------------------------
Dins la carpeta RAG_graph, executa:

    python3 -m venv .venv


PAS 3 - Activar l'entorn virtual
----------------------------------
    source .venv/bin/activate


PAS 4 - Instal·lar les dependències
-------------------------------------
    pip install -r requirements.txt


PAS 5 - Iniciar Ollama
-----------------------
En un altre terminal, executa:

    ollama serve


PAS 6 - Executar l'aplicació
------------------------------

    python3 app.py


RESUM DE COMANDES (tot seguit)
--------------------------------
    sudo apt-get install ollama
    ollama pull mistral
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ollama serve
    python3 app.py