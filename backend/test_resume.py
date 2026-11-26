
from pathlib import Path

from app.services.pdf_service import extract_pdf
from app.services.resume_service import extract_resume_data

# Locate the uploads folder
UPLOAD_DIR = Path(__file__).parent / "storage" / "uploads"

# Find all uploaded PDF files
pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found in storage/uploads.")
    raise SystemExit(1)

# Select the latest uploaded PDF
PDF_PATH = max(pdf_files, key=lambda p: p.stat().st_mtime)

print("Testing PDF:", PDF_PATH.name)

try:
    pdf_bytes = PDF_PATH.read_bytes()

    pdf_result = extract_pdf(pdf_bytes)

    resume_result = extract_resume_data(
        pdf_result["pages"]
    )

    profile = resume_result["profile"]

    print("\n========== RESUME EXTRACTION ==========")

    print("Applicant:", profile["applicant_name"])
    print("Email:", profile["email"])
    print("Phone:", profile["phone"])

    print("\nSkills:")
    for skill in profile["skills"]:
        print("-", skill)

    print("\nEducation:")
    print(profile["education"])

    print("\nExperience:")
    print(profile["experience"])

    print("\nProjects:")
    print(profile["projects"])

    print("\nCertifications:")
    print(profile["certifications"])

except Exception as error:
    print("Extraction error:", error)
