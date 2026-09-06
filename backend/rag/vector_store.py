import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension):
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []

    def add(self, embedded_chunks):
        vectors = np.array(
            [chunk["embedding"] for chunk in embedded_chunks],
            dtype="float32",
        )

        self.index.add(vectors)
        self.chunks.extend(embedded_chunks)

    def search(self, query_embedding, top_k=5):
        vector = np.array(
            [query_embedding],
            dtype="float32",
        )

        distances, indices = self.index.search(vector, top_k)

        results = []

        for distance, index in zip(distances[0], indices[0]):
            if index == -1:
                continue

            results.append({
                "chunk": self.chunks[index],
                "distance": float(distance),
            })

        return results
