from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urljoin
import requests

from .config import CREDENTIALS, CSRF_FIELD, CSRF_HEADER, LOGIN_URL, RUNTIME
from .parser import (
    extract_register_url,
    extract_response_data_keys,
    parse_forms,
    pick_login_form,
)
from .utils import save_html, save_json

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Stage1Result:
    status_code: int
    final_url: str
    request_url: str
    payload: Dict[str, str]
    response_text: str
    register_url: str


def _build_login_payload(
    form_fields: Dict[str, str], response_keys: List[str]
) -> Dict[str, str]:

    if not CREDENTIALS.email.strip():
        raise ValueError("Email is not configured. Please set EMAIL in the .env file.")

    email = CREDENTIALS.email.strip()

    payload = dict(form_fields)

    for key in response_keys:
        payload[key] = email

    if response_keys:

        response_data = {key: email for key in response_keys}

        payload["ResponseData"] = json.dumps(
            response_data,
            separators=(",", ":"),
        )

    return payload


def run_stage1(session: requests.Session) -> Stage1Result:
    logger.info(f"Fetching login page: {LOGIN_URL}")
    login_resp = session.get(LOGIN_URL, timeout=RUNTIME.timeout)
    login_resp.raise_for_status()

    save_html("stage1_login_page.html", login_resp.text)

    logger.info("Parsing login form and response data keys...")

    forms = parse_forms(login_resp.text)
    login_form = pick_login_form(forms)
    response_keys = extract_response_data_keys(login_resp.text)

    logger.info("Building login payload ...")

    payload = _build_login_payload(login_form.fields, response_keys)
    post_url = urljoin(str(login_resp.url), login_form.action or str(login_resp.url))

    headers = {}

    csrf_token = payload.get(CSRF_FIELD)
    if csrf_token:
        headers[CSRF_HEADER] = csrf_token

    post_resp = session.post(
        post_url,
        data=payload,
        headers=headers,
        timeout=RUNTIME.timeout,
        allow_redirects=True,
    )

    register_url = extract_register_url(login_resp.text, str(login_resp.url))

    save_json(
        "stage1_request.json",
        {
            "url": post_url,
            "method": "POST",
            "payload_keys": list(payload.keys()),
            "response_data_keys": response_keys,
            "headers": headers,
        }
    )

    save_json(
        "stage1_response.json",
        {
            "status_code": post_resp.status_code,
            "final_url": str(post_resp.url),
            "snippet": post_resp.text[:30000],
        }
    )

    save_html("stage1_response.html", post_resp.text)

    logger.info(f"Stage 1 completed. Final URL: {post_resp.url}, Status Code: {post_resp.status_code}")

    return Stage1Result(
        status_code=post_resp.status_code,
        final_url=str(post_resp.url),
        request_url=post_url,
        payload=payload,
        response_text=post_resp.text,
        register_url=register_url,
    )