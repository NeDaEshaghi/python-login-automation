from __future__ import annotations

import json
from dataclasses import dataclass
import logging
from urllib.parse import urljoin
import requests

from .config import BASE_URL, CAPTCHA_ENDPOINT, CSRF_FIELD, CSRF_HEADER, RUNTIME
from .parser import extract_captcha_image_ids, parse_forms, pick_captcha_form
from .utils import save_html, save_json

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Stage2Result:
    status_code: int
    final_url: str
    request_url: str
    payload: dict
    response_text: str
    business_result: str


def build_captcha_payload(captcha_fields: dict, images_ids: list[str]) -> dict:
    payload = dict(captcha_fields)

    payload["selectedImages"] = json.dumps(images_ids, separators=(",", ":"))
    payload["SelectedImages"] = ",".join(images_ids)
    payload["SelectedImageIds"] = json.dumps(images_ids, separators=(",", ":"))

    return payload


def find_stage2_endpoint(base_url: str, html: str, fallback_url: str) -> str:
    forms = parse_forms(html)
    captcha_form = pick_captcha_form(forms)
    if captcha_form and captcha_form.action:
        return urljoin(base_url, captcha_form.action)
    return fallback_url


def detect_business_result(response_text: str) -> str:

    text = response_text.lower()

    if "invalid" in text and "captcha" in text:
        return "Invalid captcha selection"

    if "captcha" in text and "error" in text:
        return "Captcha rejected"

    return "Captcha result not explicit in body"


def run_stage2(
    session: requests.Session, stage1_response_html: str, stage1_final_url: str
) -> Stage2Result:
    logger.info("Downloading captcha challenge ....")
    challenge_url = urljoin(BASE_URL, CAPTCHA_ENDPOINT)
    challenge_resp = session.get(
        challenge_url, timeout=RUNTIME.timeout, allow_redirects=True
    )

    challenge_text = challenge_resp.text or ""

    save_html("stage2_challenge.html", challenge_text)
    logger.info("Extracting captcha image IDs ...")

    image_ids = extract_captcha_image_ids(challenge_text)

    forms = parse_forms(challenge_text)
    captcha_form = pick_captcha_form(forms)
    captcha_fields = captcha_form.fields if captcha_form else {}

    post_url = find_stage2_endpoint(
        str(challenge_resp.url),
        challenge_text,
        urljoin(stage1_final_url, "/Global/account/LoginSubmit"),
    )
    payload = build_captcha_payload(captcha_fields, image_ids)

    csrf_tocken = payload.get(CSRF_FIELD)
    headers = {}
    if csrf_tocken:
        headers[CSRF_HEADER] = csrf_tocken
    logger.info("Submitting captcha selection ...")
    post_resp = session.post(
        post_url,
        data=payload,
        headers=headers,
        timeout=RUNTIME.timeout,
        allow_redirects=True,
    )

    business_result = detect_business_result(
        post_resp.text,
    )

    save_json(
        "stage2_payload_all9.json",
        {
            "request_url": post_url,
            "image_ids": image_ids,
            "payload": payload,
        }
    )

    save_json(
        "stage2_response.json",
        {
            "status_code": post_resp.status_code,
            "final_url": str(post_resp.url),
            "business_result": business_result,
            "snippet": post_resp.text[:4000],
        }
    )

    save_html("stage2_post_response.html", post_resp.text)

    logger.info(f"Stage 2 completed successfully {post_resp.status_code}")


    return Stage2Result(
        status_code=post_resp.status_code,
        final_url=str(post_resp.url),
        request_url=post_url,
        payload=payload,
        response_text=post_resp.text,
        business_result=business_result,
    )
