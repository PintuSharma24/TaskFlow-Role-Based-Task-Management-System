
import httpx


# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"

OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_EMBED_URL = f"{OLLAMA_BASE_URL}/api/embed"

# Models
LLM_MODEL = "llama3.2:latest"
EMBEDDING_MODEL = "nomic-embed-text:latest"

# Expected embedding dimensions
EMBEDDING_DIMENSIONS = 768


async def generate_response(
    user_message: str,
    system_message: str = "You are TaskFlow AI, an intelligent assistant for a task management system."
) -> str:
    """
    Send a message to Ollama and return the LLM response.
    """

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_CHAT_URL,
                json=payload
            )

            response.raise_for_status()

            result = response.json()

            return result["message"]["content"]

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Check whether the Docker container is running."
        ) from error

    except httpx.TimeoutException as error:
        raise RuntimeError(
            "Ollama response timed out. Please try again."
        ) from error

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"Ollama returned HTTP {error.response.status_code}."
        ) from error


async def generate_embedding(text: str) -> list[float]:
    """
    Convert a single text into a 768-dimensional embedding.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_EMBED_URL,
                json=payload
            )

            response.raise_for_status()

            result = response.json()

            embedding = result["embeddings"][0]

            if len(embedding) != EMBEDDING_DIMENSIONS:
                raise RuntimeError(
                    f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
                    f"received {len(embedding)}."
                )

            return embedding

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Check whether the Docker container is running."
        ) from error

    except httpx.TimeoutException as error:
        raise RuntimeError(
            "Embedding generation timed out."
        ) from error

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"Ollama embedding API returned HTTP {error.response.status_code}."
        ) from error


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts in one request.
    """

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("All texts must contain non-empty content.")

    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_EMBED_URL,
                json=payload
            )

            response.raise_for_status()

            result = response.json()

            embeddings = result["embeddings"]

            if len(embeddings) != len(texts):
                raise RuntimeError(
                    "The number of generated embeddings does not match "
                    "the number of input texts."
                )

            for embedding in embeddings:
                if len(embedding) != EMBEDDING_DIMENSIONS:
                    raise RuntimeError(
                        f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
                        f"received {len(embedding)}."
                    )

            return embeddings

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Check whether the Docker container is running."
        ) from error

    except httpx.TimeoutException as error:
        raise RuntimeError(
            "Batch embedding generation timed out."
        ) from error

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"Ollama embedding API returned HTTP {error.response.status_code}."
        ) from error
