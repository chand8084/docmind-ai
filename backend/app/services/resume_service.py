
import re


# Skills that the initial parser can recognize
KNOWN_SKILLS = [
    "Python", "Java", "JavaScript", "C", "C++", "C#",
    "HTML", "CSS", "SQL", "Django", "FastAPI",
    "Flask", "React", "Node.js", "Express",
    "REST API", "Git", "GitHub", "MySQL",
    "PostgreSQL", "Oracle", "MongoDB",
    "Machine Learning", "Deep Learning",
    "Data Analysis", "Pandas", "NumPy",
    "LangChain", "RAG", "ChromaDB",
    "AWS", "Azure", "Docker", "Linux"
]


SECTION_NAMES = {
    "education": [
        "education", "academic qualifications",
        "educational qualifications"
    ],
    "experience": [
        "experience", "work experience",
        "professional experience", "employment history"
    ],
    "projects": [
        "projects", "personal projects",
        "academic projects"
    ],
    "skills": [
        "skills", "technical skills",
        "technical expertise", "key skills"
    ],
    "certifications": [
        "certifications", "certificates",
        "professional certifications"
    ]
}


def clean_line(line):
    return re.sub(r"\s+", " ", line).strip()


def find_candidate_name(text):
    """
    Heuristic name detection.
    Returns a candidate only when a plausible
    name is found near the beginning.
    """

    lines = [clean_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    ignored = {
        "resume", "curriculum vitae", "cv",
        "profile", "personal details",
        "professional summary"
    }

    for line in lines[:12]:

        if len(line) > 55:
            continue

        if line.lower() in ignored:
            continue

        if "@" in line or re.search(r"\d", line):
            continue

        if any(char in line for char in ["|", ":", "/", "\\"]):
            continue

        words = line.split()

        if not 2 <= len(words) <= 4:
            continue

        if not all(
            re.fullmatch(r"[A-Za-z][A-Za-z.'-]*", word)
            for word in words
        ):
            continue

        return line

    return None


def extract_email(text):
    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    return match.group(0) if match else None


def extract_phone(text):
    pattern = (
        r"(?<!\d)(?:\+?91[\s-]?)?"
        r"[6-9]\d{9}(?!\d)"
    )

    match = re.search(pattern, text)

    if not match:
        return None

    return re.sub(r"[\s-]", "", match.group(0))


def extract_skills(text):
    found = []

    for skill in KNOWN_SKILLS:

        pattern = (
            r"(?<![A-Za-z0-9])"
            + re.escape(skill)
            + r"(?![A-Za-z0-9])"
        )

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def extract_sections(text):
    """
    Identify common resume sections using headings.
    """

    sections = {
        name: []
        for name in SECTION_NAMES
    }

    current_section = None

    for raw_line in text.splitlines():

        line = clean_line(raw_line)

        if not line:
            continue

        normalized = re.sub(
            r"[:\s]+$", "", line.lower()
        ).strip()

        detected_section = None

        for section, headings in SECTION_NAMES.items():

            if normalized in headings:
                detected_section = section
                break

        if detected_section:
            current_section = detected_section
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        section: "\n".join(lines)
        for section, lines in sections.items()
        if lines
    }


def extract_resume_data(pages):
    """
    Extract structured resume information
    from page-wise PDF extraction results.
    """

    full_text = "\n".join(
        page.get("text", "")
        for page in pages
    )

    sections = extract_sections(full_text)

    profile = {
        "applicant_name": find_candidate_name(full_text),
        "email": extract_email(full_text),
        "phone": extract_phone(full_text),
        "skills": extract_skills(full_text),
        "education": sections.get("education"),
        "experience": sections.get("experience"),
        "projects": sections.get("projects"),
        "certifications": sections.get("certifications")
    }

    return {
        "document_type": "resume",
        "extraction_method": "rule_based",
        "profile": profile
    }
