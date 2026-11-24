import asyncio

from app.database.connection import SessionLocal
from app.services.rag_service import search_similar_documents


async def main():

    db = SessionLocal()

    try:
        manager_id = 2

        question = "Which employees worked on customer feedback tasks?"

        print("Testing RAG Semantic Search...")
        print("Manager ID:", manager_id)
        print("Question:", question)

        results = await search_similar_documents(
            db=db,
            manager_id=manager_id,
            query=question,
            top_k=5
        )

        print("\nRetrieved Documents:", len(results))

        for index, document in enumerate(results, start=1):

            print(f"\nDocument {index}")
            print("Source Type:", document.source_type)
            print("Source ID:", document.source_id)
            print("Manager ID:", document.manager_id)
            print("Content:")
            print(document.content)
            print("-" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())