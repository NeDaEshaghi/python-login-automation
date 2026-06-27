from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


import requests

from .config import LOGIN_URL, PROXY_ROWS, RUNTIME

logger = logging.getLogger(__name__)


@dataclass
class ProxyCheckResult:
    raw_proxy: str
    success: bool
    status_code: Optional[int] = None
    final_url: str = ""
    error: str = ""


def parse_proxy_row(proxy: str) -> str:
    host, port, username, password = proxy.strip().split(":")
    return f"http://{username}:{password}@{host}:{port}"


def build_session(raw_proxy: str) -> requests.Session:
    session = requests.Session()

    proxy_url = parse_proxy_row(raw_proxy)
    session.proxies.update({"http": proxy_url, "https": proxy_url})
    session.headers.update(
        {
            "User-Agent": RUNTIME.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def check_proxy(raw_proxy: str) -> ProxyCheckResult:
    session = build_session(raw_proxy)
    try:
        resp = session.get(LOGIN_URL, timeout=RUNTIME.timeout, allow_redirects=True)
        return ProxyCheckResult(
            raw_proxy=raw_proxy,
            success=True,
            status_code=resp.status_code,
            final_url=str(resp.url),
        )
    except requests.RequestException as exc:
        logger.warning(f"Proxy check failed for {raw_proxy}: {exc}")
        return ProxyCheckResult(raw_proxy=raw_proxy, success=False, error=str(exc))


def select_working_proxy() -> str:
    results = [check_proxy(proxy) for proxy in PROXY_ROWS]

    for result in results:
        if result.success and result.status_code == 200:
            logger.info("Selected proxy: %s", result.raw_proxy)
            return result.raw_proxy

    for result in results:
        if result.success:
            logger.info("Selected proxy: %s", result.raw_proxy)
            return result.raw_proxy

    raise RuntimeError("No working proxy was found.")