# Python Login Automation

## Overview

This project automates a two-stage login workflow by reproducing the browser's HTTP requests. It preserves the authenticated session, dynamically extracts required form values, submits the login and captcha requests, and generates debugging artifacts.


---

# Project Structure

```text
.
├── artifacts/                  # Generated HTML and JSON artifacts
├── main.py                     # Root launcher (keeps python main.py)
├── src/
│   └── automation/
│       ├── client.py           # HTTP session and proxy management
│       ├── config.py           # Application configuration
│       ├── main.py             # Application orchestrator
│       ├── parser.py           # HTML parsing utilities
│       ├── stage1.py           # Stage 1 login flow
│       ├── stage2.py           # Stage 2 captcha flow
│       ├── utils.py            # Shared file helpers
│       └── __init__.py
├── requirements.txt
├── .env.example
├── README.md
```

---

# Requirements

* Python 3.11 or newer
* Internet connection
* Valid proxy configuration

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file in the project root.

Example:

```env
BASE_URL=https://turkey.blsspainglobal.com

EMAIL=example@example.com

PROXIES=http://username:password@proxy1:port,http://username:password@proxy2:port

TIMEOUT=40
```

---

# Running the Project

Run the automation:

```bash
python main.py
```

---

# Generated Artifacts

After execution, the `artifacts/` directory contains files such as:

```text
artifacts/
├── proxy_test_summary.json
├── run_summary.json
├── stage1_login_page.html
├── stage1_request.json
├── stage1_response.json
├── stage1_post_response.html
├── stage2_challenge.html
├── stage2_payload_all9.json
├── stage2_response.json
└── stage2_post_response.html
```

These artifacts help inspect the requests, responses, and HTML pages generated during the automation process.

---

# Architecture

The project follows a modular design.

| Module      | Responsibility                               |
| ----------- | -------------------------------------------- |
| `config.py` | Load configuration and environment variables |
| `client.py` | Create HTTP sessions and manage proxies      |
| `parser.py` | Parse HTML and extract dynamic values        |
| `stage1.py` | Execute the first login request              |
| `stage2.py` | Execute the captcha request                  |
| `main.py`   | Coordinate the complete automation workflow  |

---

# Logging

The application uses Python's built-in `logging` module to record the execution flow and simplify debugging.

Example log output:

```text
INFO  Selecting a working proxy...
INFO  Running Stage 1...
INFO  Running Stage 2...
INFO  Automation completed successfully.
```

---

# Error Handling

The project includes basic error handling for:

* HTTP request failures
* Invalid proxy connections
* Missing configuration values
* JSON parsing errors
* Missing HTML forms or dynamic fields

---

# Author

NeDa and Copilot :)
