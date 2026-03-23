from pathlib import Path
from typing import Dict, List
import json


def load_json_sections(path: Path) -> List[Dict[str, str]]:
    """
    Load a structured JSON knowledge module and return a list of
    simple {title, content} dicts, one per section when possible.
    Falls back to a single big document when there is no sections list.
    """
    data = json.loads(path.read_text(encoding="utf-8"))

    base_title = data.get("title") or path.stem
    sections: List[Dict[str, str]] = []

    raw_sections = data.get("sections")

    if isinstance(raw_sections, list) and raw_sections:
        for idx, section in enumerate(raw_sections, start=1):
            if not isinstance(section, dict):
                # If section is not a dict, just stringify it.
                content_text = json.dumps(section, ensure_ascii=False, indent=2)
                sections.append(
                    {
                        "title": f"{base_title} – Section {idx}",
                        "content": content_text,
                    }
                )
                continue

            section_title = (
                section.get("section_title")
                or section.get("title")
                or f"Section {idx}"
            )

            content_obj = section.get("content", section)

            if isinstance(content_obj, str):
                content_text = content_obj
            else:
                content_text = json.dumps(
                    content_obj,
                    ensure_ascii=False,
                    indent=2,
                )

            sections.append(
                {
                    "title": f"{base_title} – {section_title}",
                    "content": content_text,
                }
            )
    else:
        # No structured sections, just dump the whole JSON document.
        content_text = json.dumps(data, ensure_ascii=False, indent=2)
        sections.append(
            {
                "title": base_title,
                "content": content_text,
            }
        )

    return sections

