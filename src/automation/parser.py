from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Dict, List, Optional
from urllib.parse import urljoin

LOGIN_ACTION = "loginsubmit"
REGISTER_KEYWORDS = ("register", "signup")


@dataclass(frozen=True)
class ParsedForm:
    action: str = ""
    method: str = "get"
    form_id: str = ""
    fields: Dict[str, str] = field(default_factory=dict)


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: List[ParsedForm] = []
        self._current: Optional[ParsedForm] = None

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "form":
            self._current = ParsedForm(
                action=attributes.get("action", ""),
                method=attributes.get("method", "get").lower(),
                form_id=attributes.get("id", ""),
            )
            self.forms.append(self._current)
            return

        if not self._current:
            return

        if tag in ("input", "textarea", "select"):
            name = attributes.get("name")
            if name:
                self._current.fields.setdefault(name, attributes.get("value", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self._current = None


def parse_forms(html: str) -> List[ParsedForm]:
    parser = FormParser()
    parser.feed(html)
    return parser.forms


def pick_login_form(forms: List[ParsedForm]) -> ParsedForm:
    for form in forms:
        if LOGIN_ACTION in form.action.lower():
            return form
    if not forms:
        raise RuntimeError("No forms found on login page")
    return forms[0]


def pick_captcha_form(forms: List[ParsedForm]) -> Optional[ParsedForm]:
    for form in forms:
        field_names = {field.lower() for field in form.fields}

        if any("captcha" in field for field in field_names):
            return form
    return None


def extract_register_url(html: str, base_url: str) -> str:
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    for href in hrefs:
        if any(keyword in href.lower() for keyword in REGISTER_KEYWORDS):
            return urljoin(base_url, href)
    return ""


def extract_response_data_keys(html: str) -> List[str]:
    match = re.search(r"var\s+submittedData\s*=\s*\{(.*?)\};", html, flags=re.DOTALL)
    if not match:
        return []

    block = match.group(1)
    keys = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*\$\(", block)
    seen = set()
    unique_keys = []
    for key in keys:
        if key not in seen:
            unique_keys.append(key)
            seen.add(key)
    return unique_keys


def extract_captcha_image_ids(text: str) -> List[str]:
    patterns = [
        r'"imageId"\s*:\s*"([^\"]+)"',
        r'"ImageId"\s*:\s*"([^\"]+)"',
        r'data-image-id\s*=\s*"([^\"]+)"',
        r'data-id\s*=\s*"([^\"]+)"',
    ]
    image_ids: List[str] = []
    seen = set()

    for pattern in patterns:
        for image_id in re.findall(pattern, text, flags=re.IGNORECASE):
            if image_id not in seen:
                image_ids.append(image_id)
                seen.add(image_id)

    if len(image_ids) < 9:
        image_ids = [str(i) for i in range(1, 10)]
    if len(image_ids) < 9 :
        raise RuntimeError(f"Not enough captcha image IDs found. Found: {len(image_ids)}")
    return image_ids[:9]


def safe_json_loads(value: str) -> Optional[dict]:
    try:
        data = json.loads(value)

    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None
