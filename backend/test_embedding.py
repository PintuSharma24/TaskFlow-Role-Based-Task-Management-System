
import asyncio

from app.services.ollama_service import (
    generate_embedding,
    generate_embeddings
)


async def main():
    print("Testing single embedding...")

    text = "Employee completed API testing and documentation."

    embedding = await generate_embedding(text)

    print("Single embedding generated successfully!")
    print("Dimensions:", len(embedding))
    print("First five values:", embedding[:5])

    print("\nTesting batch embeddings...")

    documents = [
        "Employee completed API testing.",
        "Manager assigned a new sales report.",
        "Employee worked on database validation."
    ]

    embeddings = await generate_embeddings(documents)

    print("Batch embeddings generated successfully!")
    print("Number of documents:", len(embeddings))

    for index, vector in enumerate(embeddings):
        print(f"Document {index + 1}: {len(vector)} dimensions")


if __name__ == "__main__":
    asyncio.run(main())

