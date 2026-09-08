import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


def create_embeddings(chunks):
    if not chunks:
        return []

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    texts = [chunk["content"] for chunk in chunks]

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
    )

    embeddings = response.embeddings

    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunks.append({
            **chunk,
            "embedding": embedding.values,
        })

    return embedded_chunks