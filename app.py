from database import connection
from utils import ask_llm
from rag import get_context


def main():
    driver = connection()
    while True:
        text = input("Question: ")

        if text.lower() == ":q":
            break

        entities = ask_llm(text, "extract_entities.txt")
        print("Entities:", entities)

        context = get_context(entities, driver)
        print("Context:\n", context)

        answer = ask_llm(text, "generate_final_response.txt", context=context)
        print("Answer:", answer)

    driver.close()


if __name__ == "__main__":
   main()