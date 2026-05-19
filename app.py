from database import connection
from utils import ask_llm
from rag import get_context


def main():
    driver = connection()

    while True:
        print("-" * 50)
        text = input("How can I help you? ")

        if text.lower() == ":q" or text.lower() == "bye":
            break

        entities = ask_llm(text, "extract_entities.txt")
        print("Entities:", entities)

        context = get_context(entities, driver)
        print("Context:\n", context)

        if not context.strip():
            print("Answer: I don't have enough information to answer that.")
            continue

        answer = ask_llm(text, "generate_final_response.txt", context=context)
        print("Answer:", answer)

    driver.close()


if __name__ == "__main__":
   main()