
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool

from app.services.pdf_service import extract_pdf
from app.services.chunking_service import create_document_chunks
from app.services.embedding_service import embedding_service
from app.services.chroma_service import chroma_service


router = APIRouter(
    prefix="/api/documents",
    tags=["Document Processing"]
)

MAX_FILE_SIZE = 15 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_path = None

    try:
        # 1. Validate file extension
        if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # 2. Read and validate file size
        file_bytes = await file.read(MAX_FILE_SIZE + 1)

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds the 15 MB limit."
            )

        # 3. Extract PDF text
        result = await run_in_threadpool(
            extract_pdf,
            file_bytes
        )

        if result["total_characters"] == 0:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found. This PDF may require OCR."
            )

        # 4. Generate document ID
        document_id = str(uuid.uuid4())

        # 5. Split extracted text into chunks
        chunks = await run_in_threadpool(
            create_document_chunks,
            result["pages"]
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="Unable to create text chunks from this PDF."
            )

        # 6. Generate embeddings locally
        chunk_texts = [
            chunk["text"] for chunk in chunks
        ]

        embeddings = await run_in_threadpool(
            embedding_service.generate_embeddings,
            chunk_texts
        )

        # 7. Store chunks and embeddings in ChromaDB
        stored_count = await run_in_threadpool(
            chroma_service.store_chunks,
            document_id,
            chunks,
            embeddings
        )

        # 8. Save original PDF
        file_path = UPLOAD_DIR / f"{document_id}.pdf"

        await run_in_threadpool(
            file_path.write_bytes,
            file_bytes
        )

        # 9. Return upload information
        return {
            "status": "success",
            "message": "PDF uploaded and indexed successfully.",
            "document_id": document_id,
            "filename": file.filename,
            "file_size": len(file_bytes),
            "page_count": result["page_count"],
            "total_characters": result["total_characters"],
            "total_chunks": len(chunks),
            "stored_chunks": stored_count,
            "requires_ocr": result["requires_ocr"],
            "metadata": result["metadata"]
        }

    except HTTPException:
        raise

    except Exception as error:

        # Remove the saved PDF if processing fails afterward
        if file_path and file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        ) from error

    finally:
        await file.close()
