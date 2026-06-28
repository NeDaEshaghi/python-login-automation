# REPORT

## 1. Solution Overview

This project automates a two-stage login process by reproducing the HTTP requests performed by a web browser. Instead of interacting with the user interface, the application communicates directly with the server using the `requests` library while preserving the HTTP session and cookies throughout the authentication flow.

The solution is organized into small, focused modules that follow the Single Responsibility Principle. Each module is responsible for one aspect of the automation, making the code easier to understand, maintain, and test.

---

# 2. Stage 1 Request Flow

Stage 1 reproduces the initial login request.

The workflow is:

1. Create an HTTP session.
2. Download the login page.
3. Parse the HTML document.
4. Locate the login form.
5. Extract all hidden form fields.
6. Discover the dynamic keys required for the `ResponseData` object.
7. Build the POST payload by combining:

   * Hidden form fields
   * User email
   * Dynamic `ResponseData`
8. Submit the login request using the existing session.
9. Save the request and response artifacts.
10. Return the information required for Stage 2.

---

# 3. Stage 2 Request Flow

Stage 2 reproduces the captcha submission.

The workflow is:

1. Request the captcha challenge.
2. Parse the returned HTML.
3. Extract the captcha image identifiers.
4. Locate the captcha form.
5. Build the POST payload.
6. Submit the captcha request using the same session created during Stage 1.
7. Analyze the server response.
8. Save the generated artifacts.

As required by the assignment, the payload assumes that all nine captcha images are selected.

---

# 4. Session Handling

The project uses a single `requests.Session` object for the entire login workflow.

Using a shared session provides several benefits:

* Cookies are automatically preserved.
* Authentication state is maintained.
* Session identifiers remain consistent.
* Stage 2 continues exactly where Stage 1 finished.

A new session is created only if a different proxy must be selected after a connection failure.

---

# 5. Payload Generation Process

The request payloads are generated dynamically instead of being hardcoded.

## Stage 1

The login payload is built using:

* Hidden HTML form fields
* User email
* CSRF token (when available)
* Dynamically generated `ResponseData`

The `ResponseData` object is created by extracting the required field names directly from the HTML and serializing them into JSON.

## Stage 2

The captcha payload contains:

* Hidden captcha form fields
* Captcha image identifiers
* Selected image list
* CSRF token (when present)

This approach makes the automation resilient to small changes in the HTML structure.

---

# 6. Dynamic Values Discovered

Several values are discovered during execution rather than being hardcoded.

These include:

* Login form action URL
* Hidden input fields
* CSRF token
* `ResponseData` field names
* Registration URL
* Captcha form action
* Captcha image identifiers

Discovering these values dynamically improves maintainability because changes to the page structure require fewer code modifications.

---

# 7. Project Architecture

The project is divided into independent modules.

| Module      | Responsibility                               |
| ----------- | -------------------------------------------- |
| `config.py` | Load configuration and environment variables |
| `client.py` | Create HTTP sessions and manage proxies      |
| `parser.py` | Parse HTML pages and extract dynamic values  |
| `stage1.py` | Execute the first login request              |
| `stage2.py` | Execute the captcha request                  |
| `main.py`   | Coordinate the complete workflow             |

This separation keeps networking, parsing, configuration, and business logic independent.

---

# 8. Design Decisions

Several design decisions were made to improve readability and maintainability:

* **`requests.Session`** is used to preserve cookies and session state.
* **`HTMLParser`** from Python's standard library is used instead of external HTML parsing libraries because the required parsing is relatively simple.
* **Dataclasses** are used to represent structured results returned by each stage.
* **Logging** records the execution flow and simplifies debugging.
* **Configuration** is stored in a `.env` file to avoid hardcoding environment-specific values.
* **Artifacts** (HTML and JSON files) are saved to simplify debugging and allow inspection of requests and responses after execution.

---

# 9. Error Handling

The application includes basic error handling for:

* HTTP request failures
* Invalid proxy connections
* Missing configuration values
* Missing HTML forms
* JSON parsing failures
* Unexpected server responses

Exceptions are allowed to propagate when execution cannot continue, making failures visible rather than silently ignored.

---

# 10. Assumptions

The implementation makes the following assumptions:

* A valid email address is provided through the `.env` configuration.
* At least one configured proxy is available.
* The website structure remains compatible with the parsing logic.
* The assignment requirement of selecting all nine captcha images is followed exactly.

---

# Conclusion

The solution reproduces the required login workflow while maintaining session state, dynamically generating request payloads, and separating responsibilities across dedicated modules. The implementation prioritizes readability, maintainability, and resilience to minor changes in the target application's HTML structure.
