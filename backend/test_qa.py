
from pathlib import Path

from app.services.embedding_service import embedding_service
from app.services.chroma_service import chroma_service
from app.services.answer_service import generate_document_answer


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

question = "What programming languages does the applicant know?"


try:

    print("Question:", question)

    # Step 1: Generate question embedding
    query_embedding = embedding_service.generate_embeddings(
        [question]
    )[0]

    # Step 2: Retrieve relevant chunks
    retrieved_chunks = chroma_service.search_chunks(
        query_embedding=query_embedding,
        document_id=document_id,
        n_results=3
    )

    print("\nRetrieved chunks:", len(retrieved_chunks))

    # Step 3: Generate AI answer
    answer = generate_document_answer(
        question=question,
        retrieved_chunks=retrieved_chunks
    )

    print("\n========== DOCUMIND AI ANSWER ==========")
    print(answer)

except Exception as error:
    print("\nError:", error)
