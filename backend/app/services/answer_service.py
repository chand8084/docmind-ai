
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=GEMINI_API_KEY)


class GeminiQuotaError(Exception):
    pass


class GeminiServiceError(Exception):
    pass


def generate_document_answer(question: str, retrieved_chunks: list) -> str:

    if not retrieved_chunks:
        return "The requested information was not found in the document."

    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"[Page {chunk['page_number']}]\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are DocuMind AI, a professional document question-answering assistant.

Answer the user's question using ONLY the supplied document context.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

RULES:
1. Never invent information.
2. Never use outside knowledge.
3. If the answer is missing, say:
   "The requested information was not found in the document."
4. Give a direct, complete and concise answer.
5. Include relevant page numbers.
6. Use bullet points when listing multiple items.

Return a professional answer.
"""

    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )

        if not response.text:
            raise GeminiServiceError(
                "Gemini returned an empty response."
            )

        return response.text.strip()

    except Exception as error:

        error_message = str(error).lower()

        if (
            "429" in error_message
            or "resource_exhausted" in error_message
            or "quota" in error_message
        ):
            raise GeminiQuotaError(
                "Gemini API quota exhausted. Please try again after the quota resets."
            ) from error

        raise GeminiServiceError(
            f"Gemini answer generation failed: {str(error)}"
        ) from error
