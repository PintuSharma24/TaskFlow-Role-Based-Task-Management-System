
import asyncio

from app.services.ollama_service import generate_response


async def main():

    print("Connecting to TaskFlow AI...")

    response = await generate_response(
        "Introduce yourself as the AI assistant for TaskFlow."
    )

    print("\nOllama Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
