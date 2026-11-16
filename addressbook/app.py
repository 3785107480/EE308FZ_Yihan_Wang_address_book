"""Same-origin WSGI JSON API and static file application."""

import base64
import hmac
import json
import logging
import mimetypes
import os
from pathlib import Path
import re
import sqlite3
from urllib.parse import parse_qs, urlsplit

from .demo import SAMPLE_CONTACTS
from .excel import MAX_UPLOAD, read_workbook, write_workbook
from .store import Store, ValidationError

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
MAX_JSON = 256 * 1024
LOGGER = logging.getLogger(__name__)


class Application:
    def __init__(self, database=None):
        self.store = Store(database or os.environ.get("ADDRESSBOOK_DB", ROOT / "data" / "addressbook.db"))

    def __call__(self, environ, start_response):
        try:
            status, payload, headers = self.dispatch(environ)
        except ValidationError as error:
            status, payload, headers = 400, {"error": str(error)}, []
        except sqlite3.Error:
            LOGGER.exception("Database operation failed")
            status, payload, headers = 500, {"error": "Database unavailable. Please retry."}, []
        except Exception:
            LOGGER.exception("Unhandled request error")
            status, payload, headers = 500, {"error": "Unexpected server error. Please retry."}, []
        if isinstance(payload, (dict, list)):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers.append(("Content-Type", "application/json; charset=utf-8"))
        else:
            body = payload
        phrases = {200: "OK", 201: "Created", 400: "Bad Request", 401: "Unauthorized",
                   403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed", 500: "Internal Server Error"}
        headers += [
            ("Content-Length", str(len(body))), ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "same-origin"),
            ("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"),
        ]
        start_response(f"{status} {phrases[status]}", headers)
        return [body]

    def body(self, environ, limit):
        try:
            length = int(environ.get("CONTENT_LENGTH", "0") or "0")
        except ValueError as error:
            raise ValidationError("Invalid request length.") from error
        if length <= 0 or length > limit:
            raise ValidationError(f"Request body must be between 1 and {limit} bytes.")
        data = environ["wsgi.input"].read(length)
        if len(data) != length:
            raise ValidationError("Incomplete request body.")
        return data

    def json_body(self, environ):
        if environ.get("CONTENT_TYPE", "").split(";")[0] != "application/json":
            raise ValidationError("Use Content-Type: application/json.")
        try:
            payload = json.loads(self.body(environ, MAX_JSON))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValidationError("The request must contain valid JSON.") from error
        if not isinstance(payload, dict):
            raise ValidationError("The request must contain a JSON object.")
        return payload

    def dispatch(self, environ):
        path, method = environ.get("PATH_INFO", "/"), environ["REQUEST_METHOD"]
        # Optional access gate for a cloud demo. Keep the password out of Git.
        password = os.environ.get("ADDRESSBOOK_PASSWORD", "")
        if password and path != "/api/health":
            expected = "Basic " + base64.b64encode(f"reviewer:{password}".encode()).decode()
            if not hmac.compare_digest(environ.get("HTTP_AUTHORIZATION", ""), expected):
                return 401, {"error": "Sign in with the evaluation credentials."}, [("WWW-Authenticate", 'Basic realm="Address Book"')]
        if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            return 405, {"error": "Method not allowed."}, []
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = environ.get("HTTP_ORIGIN")
            if origin and urlsplit(origin).netloc != environ.get("HTTP_HOST", ""):
                return 403, {"error": "Cross-origin writes are not allowed."}, []
            if environ.get("HTTP_SEC_FETCH_SITE") == "cross-site":
                return 403, {"error": "Cross-site writes are not allowed."}, []
        if path == "/api/health" and method == "GET":
            # Query SQLite as well as the process to make this an actual readiness check.
            with self.store.connection() as db:
                db.execute("SELECT 1 FROM contacts LIMIT 1").fetchall()
            return 200, {"status": "ok", "version": "1.0.0"}, []
        if path == "/api/contacts":
            if method == "GET":
                records = self.store.list_contacts()
                params = parse_qs(environ.get("QUERY_STRING", ""))
                query = params.get("q", [""])[0].strip().casefold()
                if query:
                    records = [c for c in records if query in " ".join(
                        [c["name"], c["company"], c["job_title"], c["notes"]]
                        + [m["value"] + " " + m["label"] for m in c["methods"]]
                    ).casefold()]
                if params.get("bookmarked", [""])[0] == "true":
                    records = [c for c in records if c["bookmarked"]]
                return 200, {"data": records}, []
            if method == "POST":
                return 201, {"data": self.store.create(self.json_body(environ))}, []
        match = re.fullmatch(r"/api/contacts/([1-9]\d*)(/bookmark)?", path)
        if match:
            record_id = int(match.group(1))
            if match.group(2) and method == "PATCH":
                record = self.store.bookmark(record_id, self.json_body(environ).get("bookmarked"))
            elif not match.group(2) and method == "GET":
                record = self.store.get(record_id)
            elif not match.group(2) and method == "PUT":
                record = self.store.update(record_id, self.json_body(environ))
            elif not match.group(2) and method == "DELETE":
                if self.store.delete(record_id):
                    return 200, {"message": "Contact deleted."}, []
                return 404, {"error": "Contact not found."}, []
            else:
                return 405, {"error": "Method not allowed."}, []
            return (200, {"data": record}, []) if record else (404, {"error": "Contact not found."}, [])
        if path in ("/api/export", "/api/template", "/api/sample") and method == "GET":
            template = path == "/api/template"
            records = SAMPLE_CONTACTS if path == "/api/sample" else [] if template else self.store.list_contacts()
            filename = "address-book-sample.xlsx" if path == "/api/sample" else "address-book-template.xlsx" if template else "address-book-contacts.xlsx"
            return 200, write_workbook(records, template), [
                ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("Content-Disposition", f'attachment; filename="{filename}"'),
            ]
        if path == "/api/import" and method == "POST":
            contacts = read_workbook(self.body(environ, MAX_UPLOAD))
            return 200, {"data": self.store.import_contacts(contacts)}, []
        if method == "GET" and path in ("/", "/index.html", "/app.js", "/styles.css", "/icon.svg"):
            file = STATIC / ("index.html" if path == "/" else path[1:])
            if file.is_file():
                mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                return 200, file.read_bytes(), [("Content-Type", mime + "; charset=utf-8")]
        return 404, {"error": "Endpoint not found."}, []
