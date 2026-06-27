from __future__ import annotations

import json

from .config import OUTPUT_DIR


def save_json(filename: str, data: dict | list) -> None:
    """Save data as formatted JSON to OUTPUT_DIR."""
    output_file = OUTPUT_DIR / filename
    output_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_html(filename: str, html: str) -> None:
    """Save HTML content to OUTPUT_DIR for debugging."""
    output_file = OUTPUT_DIR / filename
    output_file.write_text(
        html,
        encoding="utf-8",
        errors="ignore",
    )
