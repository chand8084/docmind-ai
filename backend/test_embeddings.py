
from pathlib import Path

from app.services.pdf_service import extract_pdf
from app.services.chunking_service import create_document_chunks
from app.services.embedding_service import embedding_service


UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"

pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found.")
    raise SystemExit(1)

pdf_path = max(
    pdf_files,
    key=lambda file: file.stat().st_mtime
)

print("Processing:", pdf_path.name)

try:

    # Step 1: Extract PDF text
    pdf_result = extract_pdf(pdf_path.read_bytes())

    # Step 2: Create chunks
    chunks = create_document_chunks(
        pdf_result["pages"]
    )

    print("Total chunks:", len(chunks))

    # Step 3: Generate embeddings
    texts = [chunk["text"] for chunk in chunks]

    embeddings = embedding_service.generate_embeddings(texts)

    print("\n========== EMBEDDING RESULTS ==========")

    print("Total embeddings:", len(embeddings))

    if embeddings:
        print("Vector dimensions:", len(embeddings[0]))
        print("First vector preview:", embeddings[0][:10])

    print("\nEmbedding generation successful!")

except Exception as error:
    print("Embedding error:", error)
