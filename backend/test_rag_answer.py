import asyncio

from app.database.connection import SessionLocal
from app.services.rag_service import ask_manager_question


async def main():

    db = SessionLocal()

    try:
        manager_id = 2

        question = "Which employees worked on customer feedback tasks?"

        print("Testing TaskFlow RAG Answer Generation...")
        print("Question:", question)

        result = await ask_manager_question(
            db=db,
            manager_id=manager_id,
            question=question,
            top_k=5
        )

        print("\nAI GENERATED ANSWER:")
        print(result["answer"])

        print("\nRETRIEVED SOURCES:")

        for source in result["sources"]:
            print(
                source["source_type"],
                "| Source ID:",
                source["source_id"]
            )

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())