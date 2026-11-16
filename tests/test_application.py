"""Behavioral API, persistence and Excel tests; no listening socket required."""

from io import BytesIO
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from openpyxl import Workbook, load_workbook

from addressbook.app import Application
from addressbook.excel import MAX_UPLOAD, read_workbook, write_workbook
from addressbook.store import fingerprint, ValidationError


def contact(name="Alice Chen", bookmarked=False):
    return {
        "name": name, "company": "FZU–MU", "job_title": "Student",
        "notes": "Project partner\nPrefers email", "bookmarked": bookmarked,
        "methods": [
            {"type": "phone", "label": "Mobile", "value": "0013800123456"},
            {"type": "phone", "label": "Home", "value": "+44 20 1234 5678"},
            {"type": "email", "label": "University", "value": "alice@example.com"},
            {"type": "social", "label": "WeChat", "value": "alice_chen"},
            {"type": "address", "label": "Campus", "value": "Fuzhou, China"},
            {"type": "website", "label": "Portfolio", "value": "https://example.com"},
            {"type": "other", "label": "Office", "value": "Building A, room 12"},
        ],
    }


def workbook_bytes(rows, title="Contacts"):
    workbook = Workbook()
    workbook.active.title = title
    for row in rows:
        workbook.active.append(row)
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    return output.getvalue()


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "contacts.db"
        self.app = Application(self.database)

    def request(self, method, path, payload=None, raw=None, **extra):
        body = raw if raw is not None else json.dumps(payload).encode() if payload is not None else b""
        path, _, query = path.partition("?")
        environ = {
            "REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
            "CONTENT_TYPE": "application/json" if raw is None else
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "CONTENT_LENGTH": str(len(body)), "wsgi.input": BytesIO(body),
            "HTTP_HOST": "localhost:8080", **extra,
        }
        response = {}
        def start(status, headers):
            response["status"] = int(status.split()[0])
            response["headers"] = dict(headers)
        response["body"] = b"".join(self.app(environ, start))
        if response["headers"].get("Content-Type", "").startswith("application/json"):
            response["json"] = json.loads(response["body"])
        return response

    def create(self, payload=None):
        response = self.request("POST", "/api/contacts", payload or contact())
        self.assertEqual(response["status"], 201, response)
        return response["json"]["data"]

    def test_contact_crud_multiple_methods_and_persistence(self):
        created = self.create()
        self.assertEqual(len(created["methods"]), 7)
        self.assertTrue(created["created_at"])
        self.app = Application(self.database)
        restored = self.request("GET", f'/api/contacts/{created["id"]}')["json"]["data"]
        self.assertEqual(created, restored)
        updated = contact("Alice Wang", True)
        updated["methods"] = [updated["methods"][2]]
        response = self.request("PUT", f'/api/contacts/{created["id"]}', updated)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["json"]["data"]["methods"], updated["methods"])
        self.assertEqual(self.request("DELETE", f'/api/contacts/{created["id"]}')["status"], 200)
        self.assertEqual(self.request("GET", "/api/contacts")["json"], {"data": []})
        self.assertEqual(self.request("DELETE", f'/api/contacts/{created["id"]}')["status"], 404)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM contact_methods").fetchone()[0], 0)

    def test_bookmarks_search_and_casefold(self):
        alice = self.create()
        self.create(contact("Bob Lee", True))
        result = self.request("PATCH", f'/api/contacts/{alice["id"]}/bookmark', {"bookmarked": True})
        self.assertEqual(result["status"], 200)
        self.assertEqual(len(self.request("GET", "/api/contacts?bookmarked=true")["json"]["data"]), 2)
        self.request("PATCH", f'/api/contacts/{alice["id"]}/bookmark', {"bookmarked": False})
        self.assertEqual(len(self.request("GET", "/api/contacts?bookmarked=true&q=bOb")["json"]["data"]), 1)
        self.assertEqual(len(self.request("GET", "/api/contacts?q=0013800123456")["json"]["data"]), 2)
        self.assertEqual(self.request("GET", "/api/contacts?q=missing")["json"], {"data": []})

    def test_bad_contact_validation_does_not_write(self):
        cases = [[], {"name": " "}, {"name": "A", "bookmarked": "false"},
                 {"name": "A", "methods": [{"type": "email", "value": "bad"}]},
                 {"name": "A", "methods": [{"type": "website", "value": "javascript:alert(1)"}]},
                 {"name": "A", "methods": [{"type": "alien", "value": "123"}]},
                 {"name": "A", "methods": contact()["methods"] * 2}]
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertEqual(self.request("POST", "/api/contacts", payload)["status"], 400)
        self.assertEqual(self.request("GET", "/api/contacts")["json"], {"data": []})

    def test_excel_export_import_round_trip_all_data(self):
        original = self.create(contact("王奕涵 Yihan", True))
        dangerous = contact("=1+1")
        dangerous["notes"] = "=HYPERLINK(\"https://example.com\")"
        other = self.create(dangerous)
        exported = self.request("GET", "/api/export")
        self.assertEqual(exported["status"], 200)
        self.assertTrue(exported["body"].startswith(b"PK"))
        workbook = load_workbook(BytesIO(exported["body"]), data_only=False)
        sheet = workbook["Contacts"]
        self.assertEqual(sheet.max_row, 3)
        headers = [c.value for c in sheet[1]]
        self.assertIn("Phone 2 Value", headers)
        for row in sheet.iter_rows(min_row=2):
            self.assertTrue(all(cell.data_type != "f" for cell in row))
        workbook.close()
        # Empty the local test store, then restore the actual exported file.
        self.request("DELETE", f'/api/contacts/{original["id"]}')
        self.request("DELETE", f'/api/contacts/{other["id"]}')
        imported = self.request("POST", "/api/import", raw=exported["body"])
        self.assertEqual(imported["json"]["data"], {"imported": 2, "skipped": 0, "total_rows": 2})
        restored = self.request("GET", "/api/contacts")["json"]["data"]
        self.assertEqual({fingerprint(c) for c in restored}, {fingerprint(original), fingerprint(other)})
        phone = next(m for c in restored for m in c["methods"] if m["label"] == "Mobile")
        self.assertEqual(phone["value"], "0013800123456")
        again = self.request("POST", "/api/import", raw=exported["body"])
        self.assertEqual(again["json"]["data"]["skipped"], 2)

    def test_import_atomicity_duplicate_policy_and_same_name(self):
        invalid = workbook_bytes([
            ["Name", "Email 1 Value"], ["Valid", "valid@example.com"], ["Invalid", "bad"],
        ])
        response = self.request("POST", "/api/import", raw=invalid)
        self.assertEqual(response["status"], 400)
        self.assertIn("Row 3", response["json"]["error"])
        self.assertEqual(self.app.store.list_contacts(), [])
        alice = contact()
        different = contact()
        different["company"] = "Different organization"
        raw = write_workbook([alice, alice, different])
        result = self.request("POST", "/api/import", raw=raw)["json"]["data"]
        self.assertEqual(result, {"imported": 2, "skipped": 1, "total_rows": 3})

    def test_invalid_workbooks_rejected(self):
        files = [b"not xlsx", workbook_bytes([["Name"]], "Wrong"),
                 workbook_bytes([["Phone 1 Value"], ["123"]]),
                 workbook_bytes([["Name", "Name"], ["A", "B"]]),
                 workbook_bytes([["Name", "Favorite"], ["A", "Yes"]]),
                 workbook_bytes([["Name", "Bookmarked"], ["A", "maybe"]]),
                 workbook_bytes([["Name", "Phone 1 Label"], ["A", "Mobile"]]),
                 workbook_bytes([["Name", "Phone 1 Label", "Phone 1 Value"], ["A", "Mobile", ""]]),
                 workbook_bytes([["Name", "Notes"], ["A", "=1+1"]]),
                 write_workbook([], True)]
        for raw in files:
            with self.subTest(size=len(raw)):
                self.assertEqual(self.request("POST", "/api/import", raw=raw)["status"], 400)
        self.assertEqual(self.app.store.list_contacts(), [])

    def test_limits_routing_security_and_health(self):
        self.assertEqual(self.request("GET", "/api/health")["json"]["status"], "ok")
        self.assertEqual(self.request("GET", "/../server.py")["status"], 404)
        self.assertEqual(self.request("PATCH", "/api/contacts/999/bookmark", {"bookmarked": True})["status"], 404)
        self.assertEqual(self.request("POST", "/api/contacts", contact(), HTTP_ORIGIN="https://other.example")["status"], 403)
        self.assertEqual(self.request("POST", "/api/contacts", contact(), HTTP_SEC_FETCH_SITE="cross-site")["status"], 403)
        self.assertEqual(self.request("POST", "/api/contacts", raw=b"{}")["status"], 400)
        self.assertEqual(self.request("POST", "/api/import", raw=b"x", CONTENT_LENGTH=str(MAX_UPLOAD + 1))["status"], 400)
        self.assertEqual(self.request("POST", "/api/contacts", contact(), CONTENT_LENGTH="-1")["status"], 400)
        with patch.dict(os.environ, {"ADDRESSBOOK_PASSWORD": "test-only-secret"}):
            self.assertEqual(self.request("GET", "/api/contacts")["status"], 401)
            self.assertEqual(self.request("GET", "/api/health")["status"], 200)


if __name__ == "__main__":
    unittest.main()
