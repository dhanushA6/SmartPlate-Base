from pathlib import Path
from typing import Dict, List

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def extract_pdf_text(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf not installed. Run: pip install pypdf")

    reader = PdfReader(str(path))
    texts: List[str] = []

    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""

        if txt.strip():
            texts.append(txt)

    return "\n".join(texts)


def load_pdf(path: Path) -> Dict[str, str]:
    content = extract_pdf_text(path)

    if len(content.strip()) < 50:
        raise RuntimeError(f"PDF content too short: {path}")

    return {
        "title": path.stem,
        "content": content,
    }
