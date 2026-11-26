
from pathlib import Path
import chromadb


BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "storage" / "chroma_db"


class ChromaService:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(DB_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name="documind_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def store_chunks(
        self,
        document_id: str,
        chunks: list,
        embeddings: list
    ):

        if not chunks:
            return 0

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:

            ids.append(
                f"{document_id}_{chunk['chunk_id']}"
            )

            documents.append(chunk["text"])

            metadatas.append({
                "document_id": document_id,
                "chunk_id": chunk["chunk_id"],
                "page_number": int(chunk["page_number"])
            })

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(ids)

    def search_chunks(
        self,
        query_embedding: list,
        document_id: str,
        n_results: int = 3
    ):
        """
        Retrieve relevant chunks from a specific document.
        """

        total_chunks = self.collection.count()

        if total_chunks == 0:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, total_chunks),
            where={"document_id": document_id},
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            retrieved_chunks.append({
                "text": document,
                "chunk_id": metadata["chunk_id"],
                "page_number": metadata["page_number"],
                "distance": distance
            })

        return retrieved_chunks

    def get_collection_count(self):
        return self.collection.count()


chroma_service = ChromaService()
