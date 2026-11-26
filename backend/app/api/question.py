
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.services.embedding_service import embedding_service
from app.services.chroma_service import chroma_service

from app.services.answer_service import (
    generate_document_answer,
    GeminiQuotaError,
    GeminiServiceError
)

router = APIRouter(
    prefix="/api/documents",
    tags=["Document Question Answering"]
)


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=1000
    )


@router.post("/{document_id}/ask")
async def ask_document(
    document_id: str,
    request: QuestionRequest
):

    try:
        # 1. Generate question embedding
        query_embedding = await run_in_threadpool(
            embedding_service.generate_embeddings,
            [request.question]
        )

        # 2. Retrieve relevant chunks
        retrieved_chunks = await run_in_threadpool(
            chroma_service.search_chunks,
            query_embedding[0],
            document_id,
            3
        )

        if not retrieved_chunks:
            raise HTTPException(
                status_code=404,
                detail="No relevant information found for this document."
            )

        # 3. Generate answer using Gemini
        answer = await run_in_threadpool(
            generate_document_answer,
            request.question,
            retrieved_chunks
        )

        # 4. Return answer with source pages
        source_pages = sorted({
            chunk["page_number"]
            for chunk in retrieved_chunks
        })

        return {
            "status": "success",
            "document_id": document_id,
            "question": request.question,
            "answer": answer,
            "source_pages": source_pages,
            "retrieved_chunks": len(retrieved_chunks)
        }

    except HTTPException:
        raise

    except GeminiQuotaError as error:
        raise HTTPException(
            status_code=429,
            detail=str(error)
        ) from error

    except GeminiServiceError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Question processing failed: {str(error)}"
        ) from error