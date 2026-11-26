
from pathlib import Path

from app.services.embedding_service import embedding_service
from app.services.chroma_service import chroma_service

UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"

pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF found.")
    raise SystemExit(1)

pdf_path = max(
    pdf_files,
    key=lambda file: file.stat().st_mtime
)

document_id = pdf_path.stem

questions = [
    "What is the applicant's full name?",
    "Which programming languages does the applicant know?",
    "What is the applicant's educational qualification?",
    "Which college did the applicant attend?",
    "What projects has the applicant developed?",
    "What is the applicant's CGPA?"
]

for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:", question)

    query_embedding = embedding_service.generate_embeddings(
        [question]
    )[0]

    results = chroma_service.search_chunks(
        query_embedding=query_embedding,
        document_id=document_id,
        n_results=3
    )

    if not results:
        print("No relevant information found.")
        continue

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("Page:", result["page_number"])
        print("Distance:", round(result["distance"], 4))
        print("Content:")
        print(result["text"])