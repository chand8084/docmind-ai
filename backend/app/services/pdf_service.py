
import pymupdf


def extract_pdf(file_bytes: bytes) -> dict:
    """
    Extract text and metadata from a PDF.
    Preserve page numbers and identify pages
    that may require OCR.
    """

    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF file signature.")

    try:
        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        if document.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported yet."
            )

        if len(document) == 0:
            raise ValueError("The PDF contains no pages.")

        if len(document) > 200:
            raise ValueError(
                "PDF exceeds the maximum limit of 200 pages."
            )

        pages = []
        full_text = []

        empty_pages = []
        low_text_pages = []
        scanned_candidates = []

        for index, page in enumerate(document):

            page_number = index + 1

            text = page.get_text(
                "text",
                sort=True
            ).strip()

            image_count = len(page.get_images())

            page_data = {
                "page_number": page_number,
                "text": text,
                "character_count": len(text),
                "image_count": image_count
            }

            pages.append(page_data)
            full_text.append(
                f"\n--- Page {page_number} ---\n{text}"
            )

            if not text:
                empty_pages.append(page_number)

                if image_count > 0:
                    scanned_candidates.append(page_number)

            elif len(text) <= 30:
                low_text_pages.append(page_number)

        metadata = document.metadata or {}

        result = {
            "metadata": {
                "title": metadata.get("title"),
                "author": metadata.get("author"),
                "subject": metadata.get("subject"),
                "creator": metadata.get("creator"),
                "producer": metadata.get("producer")
            },
            "page_count": len(document),
            "total_characters": sum(
                page["character_count"] for page in pages
            ),
            "pages": pages,
            "full_text": "\n".join(full_text),
            "empty_pages": empty_pages,
            "low_text_pages": low_text_pages,
            "scanned_candidates": scanned_candidates,
            "requires_ocr": len(scanned_candidates) > 0
        }

        document.close()

        return result

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            f"Unable to process PDF: {str(error)}"
        ) from error
