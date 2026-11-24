
import asyncio

from sqlalchemy import select, func

from app.database.connection import SessionLocal
from app.models.rag_document import RAGDocument
from app.services.rag_service import index_manager_documents


async def main():

    manager_id = 3

    db = SessionLocal()

    try:
        print("Starting RAG indexing...")
        print(f"Manager ID: {manager_id}")

        # Index documents for this Manager
        indexed_count = await index_manager_documents(
            db=db,
            manager_id=manager_id
        )

        print("\nIndexing completed!")
        print("Documents indexed:", indexed_count)

        # Verify total documents
        total_documents = db.scalar(
            select(func.count())
            .select_from(RAGDocument)
            .where(RAGDocument.manager_id == manager_id)
        )

        print("Total stored documents:", total_documents)

        # Verify document types
        results = db.execute(
            select(
                RAGDocument.source_type,
                func.count(RAGDocument.id)
            )
            .where(RAGDocument.manager_id == manager_id)
            .group_by(RAGDocument.source_type)
        ).all()

        print("\nDocuments by source type:")

        for source_type, count in results:
            print(f"{source_type}: {count}")

        # Verify embedding dimensions
        sample = db.scalar(
            select(RAGDocument)
            .where(RAGDocument.manager_id == manager_id)
            .limit(1)
        )

        if sample:
            print("\nSample document:")
            print("Source type:", sample.source_type)
            print("Source ID:", sample.source_id)
            print("Embedding dimensions:", len(sample.embedding))

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
