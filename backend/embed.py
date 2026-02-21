import os
import random
from hashlib import sha256
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "false").lower() == "true"
OPENAI_EMBEDDINGS_AVAILABLE = True


def _local_embedding(text: str, dim: int = 3072) -> list[float]:
    # Deterministic fallback so vector search still works without OpenAI quota/network.
    seed = int.from_bytes(sha256(text.encode("utf-8")).digest()[:8], "big")
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(dim)]


def embed_text(text: str) -> list[float]:
    global OPENAI_EMBEDDINGS_AVAILABLE

    if USE_LOCAL_EMBEDDINGS or not OPENAI_EMBEDDINGS_AVAILABLE:
        return _local_embedding(text)

    try:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
        )
        return response.data[0].embedding
    except Exception as exc:
        OPENAI_EMBEDDINGS_AVAILABLE = False
        print(f"Embedding fallback enabled ({type(exc).__name__}): using local embeddings.")
        return _local_embedding(text)
