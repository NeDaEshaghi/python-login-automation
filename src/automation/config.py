from dataclasses import dataclass
from pathlib import Path
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

BASE_URL = os.getenv("BASE_URL", "https://turkey.blsspainglobal.com")
LOGIN_URL = f"{BASE_URL}/Global/account/login"
REGISTER_URL = f"{BASE_URL}/Global/account/RegisterUser"

PROXY_ROWS = [
    proxy.strip() for proxy in os.getenv("PROXIES", "").split(";") if proxy.strip()
]

OUTPUT_DIR = Path("artifacts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CSRF_FIELD = "__RequestVerificationToken"
CSRF_HEADER = "RequestVerificationToken"
CAPTCHA_ENDPOINT = "/Global/CaptchaPublic/GenerateCaptcha?"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class RuntimeConfig:
    timeout: int = int(os.getenv("TIMEOUT", "40"))
    user_agent: str = DEFAULT_USER_AGENT


@dataclass
class Credentials:
    email: str = os.getenv("EMAIL", "")


RUNTIME = RuntimeConfig()
CREDENTIALS = Credentials()
