
from pathlib import Path

from app.services.pdf_service import extract_pdf
from app.services.chunking_service import create_document_chunks


UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"

pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found.")
    raise SystemExit(1)

PDF_PATH = max(
    pdf_files,
    key=lambda file: file.stat().st_mtime
)

print("Testing:", PDF_PATH.name)

try:
    pdf_result = extract_pdf(PDF_PATH.read_bytes())

    chunks = create_document_chunks(
        pdf_result["pages"],
        chunk_size=1000,
        overlap=150
    )

    print("\n========== CHUNKING RESULTS ==========")
    print("Total pages:", pdf_result["page_count"])
    print("Total chunks:", len(chunks))

    for chunk in chunks[:5]:
        print("\nChunk ID:", chunk["chunk_id"])
        print("Page:", chunk["page_number"])
        print("Characters:", chunk["character_count"])
        print("Text:", chunk["text"][:250])

except Exception as error:
    print("Chunking error:", error)
