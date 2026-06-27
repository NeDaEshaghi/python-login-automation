from __future__ import annotations

import logging

from .client import build_session, check_proxy, select_working_proxy
from .config import PROXY_ROWS
from .stage1 import run_stage1
from .stage2 import run_stage2
from .utils import save_json

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting working proxy selection and flow execution...")
    selected_proxy = select_working_proxy()
    logger.info(f"Selected working proxy: {selected_proxy}")
    proxy_report = []

    for proxy in PROXY_ROWS:
        result = check_proxy(proxy)
        proxy_report.append(
            {
                "proxy": result.raw_proxy,
                "success": result.success,
                "status_code": result.status_code,
                "final_url": result.final_url,
                "error": result.error,
            }
        )

    save_json("proxy_test_summary.json", proxy_report)

    proxy_order = [selected_proxy, *[proxy for proxy in PROXY_ROWS if proxy != selected_proxy]]

    stage1 = None
    stage2 = None
    working_proxy = None
    last_error = None

    for proxy in proxy_order:
        logger.info(f"Trying proxy: {proxy}")
        try:
            session = build_session(proxy)
            logger.info("Running Stage 1...")
            stage1 = run_stage1(session)
            logger.info("Running Stage 2...")
            stage2 = run_stage2(session, stage1.response_text, stage1.final_url)
            working_proxy = proxy
            logger.info(f"Flow completed successfully with proxy: {proxy}")
            break
        except Exception as exc:
            logger.exception(f"Flow failed with proxy {proxy}: {exc}")
            last_error = str(exc)

    if stage1 is None or stage2 is None:
        raise RuntimeError(
            f"Login flow failed for all proxies.\nLast error: {last_error}"
        )

    summary = {
        "selected_proxy": working_proxy,
        "stage1": {
            "status_code": stage1.status_code,
            "request_url": stage1.request_url,
            "final_url": stage1.final_url,
        },
        "stage2": {
            "status_code": stage2.status_code,
            "request_url": stage2.request_url,
            "final_url": stage2.final_url,
            "expected_business_result": "Invalid captcha selection",
            "observed_business_result": stage2.business_result,
        },
    }

    save_json("run_summary.json", summary)

    logger.info("Automation flow completed successfully.")
    logger.info("Summary saved to artifacts/run_summary.json.")


if __name__ == "__main__":
    main()
