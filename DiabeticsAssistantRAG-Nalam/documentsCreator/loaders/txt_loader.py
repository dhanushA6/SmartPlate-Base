from pathlib import Path
from typing import Dict


def load_txt(path: Path) -> Dict[str, str]:
    """
    Load a TXT file and return a simple dict with title and content.

    This mirrors the behavior of the main project's txt_loader, but
    avoids returning LangChain Documents to keep this module independent.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    title = path.stem
    return {
        "title": title,
        "content": text,
    }

