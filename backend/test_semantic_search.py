
from pathlib import Path

from app.services.embedding_service import embedding_service
from app.services.chroma_service import chroma_service


UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"

pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No uploaded PDF found.")
    raise SystemExit(1)

pdf_path = max(
    pdf_files,
    key=lambda file: file.stat().st_mtime
)

document_id = pdf_path.stem

# Ask a question about the uploaded resume
question = "Which programming languages does the applicant know?"

try:

    print("Question:", question)

    # Step 1: Convert question into an embedding
    query_embedding = embedding_service.generate_embeddings(
        [question]
    )[0]

    # Step 2: Search ChromaDB
    results = chroma_service.search_chunks(
        query_embedding=query_embedding,
        document_id=document_id,
        n_results=3
    )

    # Step 3: Display retrieved information
    print("\n========== SEMANTIC SEARCH RESULTS ==========")

    if not results:
        print("No relevant information found.")

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("Chunk ID:", result["chunk_id"])
        print("Page:", result["page_number"])
        print("Distance:", round(result["distance"], 4))
        print("Content:", result["text"])

except Exception as error:
    print("Search error:", error)
