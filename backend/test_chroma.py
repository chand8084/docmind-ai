
from pathlib import Path

from app.services.pdf_service import extract_pdf
from app.services.chunking_service import create_document_chunks
from app.services.embedding_service import embedding_service
from app.services.chroma_service import chroma_service


UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"

pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found.")
    raise SystemExit(1)

pdf_path = max(
    pdf_files,
    key=lambda file: file.stat().st_mtime
)

document_id = pdf_path.stem

try:
    print("Processing:", pdf_path.name)

    # Extract PDF text
    pdf_result = extract_pdf(pdf_path.read_bytes())

    # Create text chunks
    chunks = create_document_chunks(pdf_result["pages"])

    print("Total chunks:", len(chunks))

    # Generate embeddings
    texts = [chunk["text"] for chunk in chunks]

    embeddings = embedding_service.generate_embeddings(texts)

    print("Total embeddings:", len(embeddings))

    # Store in ChromaDB
    stored_count = chroma_service.store_chunks(
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings
    )

    print("\n========== CHROMADB RESULTS ==========")
    print("Document ID:", document_id)
    print("Chunks stored:", stored_count)
    print("Total chunks in database:", chroma_service.get_collection_count())

    print("\nChromaDB storage successful!")

except Exception as error:
    print("ChromaDB error:", error)
