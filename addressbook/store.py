"""Validated contacts and transactional SQLite persistence."""

from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3

METHOD_TYPES = ("phone", "email", "social", "address", "website", "other")
MAX_METHODS = 100


class ValidationError(ValueError):
    """A user-readable input validation error."""


def clean_text(value, field, limit, required=False):
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be text.")
    value = value.strip()
    if required and not value:
        raise ValidationError(f"{field} is required.")
    if len(value) > limit:
        raise ValidationError(f"{field} must contain at most {limit} characters.")
    if any((ord(char) < 32 and char not in "\n\r\t") or
           0xD800 <= ord(char) <= 0xDFFF or ord(char) in (0xFFFE, 0xFFFF)
           for char in value):
        raise ValidationError(f"{field} contains unsupported control characters.")
    return value


def validate_contact(payload):
    """Return normalized, bounded input, independent of frontend validation."""
    if not isinstance(payload, dict):
        raise ValidationError("Contact must be a JSON object.")
    contact = {
        "name": clean_text(payload.get("name", ""), "Name", 120, True),
        "company": clean_text(payload.get("company", ""), "Company", 160),
        "job_title": clean_text(payload.get("job_title", ""), "Job title", 160),
        "notes": clean_text(payload.get("notes", ""), "Notes", 5000),
    }
    bookmarked = payload.get("bookmarked", False)
    if not isinstance(bookmarked, bool):
        raise ValidationError("Bookmarked must be true or false.")
    contact["bookmarked"] = bookmarked
    methods = payload.get("methods", [])
    if not isinstance(methods, list) or len(methods) > MAX_METHODS:
        raise ValidationError(f"Methods must be a list of at most {MAX_METHODS} items.")
    contact["methods"] = []
    seen = set()
    for index, method in enumerate(methods, 1):
        if not isinstance(method, dict):
            raise ValidationError(f"Contact method {index} must be an object.")
        kind = method.get("type")
        if kind not in METHOD_TYPES:
            raise ValidationError(f"Contact method {index} has an unsupported type.")
        label = clean_text(method.get("label", ""), "Method label", 80)
        value = clean_text(method.get("value", ""), "Method value", 1000, True)
        if kind == "email" and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValidationError(f"Invalid email address: {value}")
        if kind == "website" and not re.fullmatch(r"https?://[^\s]+", value, re.I):
            raise ValidationError("Website values must start with http:// or https://.")
        key = (kind, label, value)
        if key in seen:
            raise ValidationError("A contact cannot contain duplicate contact methods.")
        seen.add(key)
        contact["methods"].append({"type": kind, "label": label, "value": value})
    return contact


def fingerprint(contact):
    """Exact data duplicate detection, insensitive to contact method order."""
    data = {key: contact[key] for key in
            ("name", "company", "job_title", "notes", "bookmarked")}
    data["methods"] = sorted(
        (m["type"], m["label"], m["value"]) for m in contact["methods"]
    )
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    company TEXT NOT NULL DEFAULT '',
                    job_title TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    bookmarked INTEGER NOT NULL DEFAULT 0 CHECK(bookmarked IN (0, 1)),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS contact_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
                    type TEXT NOT NULL CHECK(type IN ('phone', 'email', 'social', 'address', 'website', 'other')),
                    label TEXT NOT NULL,
                    value TEXT NOT NULL,
                    position INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS methods_contact ON contact_methods(contact_id);
            """)

    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return closing(db)

    def _all(self, db):
        contacts = {}
        for row in db.execute("SELECT * FROM contacts ORDER BY name COLLATE NOCASE, id"):
            record = dict(row)
            record["bookmarked"] = bool(record["bookmarked"])
            record["methods"] = []
            contacts[row["id"]] = record
        for row in db.execute(
            "SELECT contact_id, type, label, value FROM contact_methods ORDER BY contact_id, position"
        ):
            contacts[row["contact_id"]]["methods"].append(
                {key: row[key] for key in ("type", "label", "value")}
            )
        return list(contacts.values())

    def list_contacts(self):
        with self.connection() as db:
            return self._all(db)

    def get(self, record_id):
        return next((row for row in self.list_contacts() if row["id"] == record_id), None)

    def _insert(self, db, contact):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cursor = db.execute(
            "INSERT INTO contacts(name, company, job_title, notes, bookmarked, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            tuple(contact[key] for key in ("name", "company", "job_title", "notes", "bookmarked"))
            + (now, now),
        )
        self._methods(db, cursor.lastrowid, contact["methods"])
        return cursor.lastrowid

    def _methods(self, db, record_id, methods):
        db.executemany(
            "INSERT INTO contact_methods(contact_id, type, label, value, position) VALUES (?, ?, ?, ?, ?)",
            [(record_id, m["type"], m["label"], m["value"], i) for i, m in enumerate(methods)],
        )

    def create(self, payload):
        contact = validate_contact(payload)
        with self.connection() as db, db:
            record_id = self._insert(db, contact)
        return self.get(record_id)

    def update(self, record_id, payload):
        contact = validate_contact(payload)
        with self.connection() as db, db:
            cursor = db.execute(
                "UPDATE contacts SET name=?, company=?, job_title=?, notes=?, bookmarked=?, updated_at=? WHERE id=?",
                tuple(contact[key] for key in ("name", "company", "job_title", "notes", "bookmarked"))
                + (datetime.now(timezone.utc).isoformat(timespec="seconds"), record_id),
            )
            if not cursor.rowcount:
                return None
            db.execute("DELETE FROM contact_methods WHERE contact_id=?", (record_id,))
            self._methods(db, record_id, contact["methods"])
        return self.get(record_id)

    def bookmark(self, record_id, value):
        if not isinstance(value, bool):
            raise ValidationError("Bookmarked must be true or false.")
        with self.connection() as db, db:
            cursor = db.execute(
                "UPDATE contacts SET bookmarked=?, updated_at=? WHERE id=?",
                (value, datetime.now(timezone.utc).isoformat(timespec="seconds"), record_id),
            )
            if not cursor.rowcount:
                return None
        return self.get(record_id)

    def delete(self, record_id):
        with self.connection() as db, db:
            return bool(db.execute("DELETE FROM contacts WHERE id=?", (record_id,)).rowcount)

    def import_contacts(self, contacts):
        """Validate everything and insert in one transaction; skip exact duplicates."""
        contacts = [validate_contact(contact) for contact in contacts]
        with self.connection() as db, db:
            db.execute("BEGIN IMMEDIATE")
            seen = {fingerprint(contact) for contact in self._all(db)}
            added = 0
            for contact in contacts:
                key = fingerprint(contact)
                if key not in seen:
                    self._insert(db, contact)
                    added += 1
                    seen.add(key)
        return {"imported": added, "skipped": len(contacts) - added, "total_rows": len(contacts)}
