# Yihan Wang Address Book v1.0.0

Release-note template. Publish it only for the final reviewed commit and replace
all pending fields. A local document or tag is not a published GitHub release.

## Features

- English responsive contact interface with creation, editing, detail view,
  deletion confirmation, search, sorting, and visible loading/error/empty states.
- Persistent contact bookmarks and a dedicated Bookmarks view.
- Multiple labeled phone, email, social, address, website, and other methods per
  contact, including repeated methods of the same type.
- Genuine XLSX export with one row per contact and explicit columns for all
  user-entered fields, bookmark state, method labels, and values.
- Compatible XLSX import, a blank template, and an explicitly fictional sample.
- Whole-file validation, transactional import, row-specific errors where
  applicable, and exact-duplicate skipping.
- SQLite persistence with automatic initialization and cascading method deletion.
- README, coding standards, prospective PSP plan, architecture, evidence guide,
  individual blog draft, automated tests, and optional cloud configuration.

## Run

Python 3.10+ and a current browser are required. Create a virtual environment,
install requirements.txt, and run `python server.py` from the source root.
Open `http://127.0.0.1:8080`. See README for Windows and macOS launcher instructions.
Node.js is needed only for optional browser verification, not for the application.

## Verification

- Final source commit: [REQUIRED: SHA].
- Application test command: `python -m unittest discover -s tests -p 'test_*.py' -v`.
- Observed application test result: [REQUIRED: actual result/environment/date].
- Browser verification result: [REQUIRED: actual result or not run].
- Spreadsheet-viewer/manual result: [REQUIRED: actual result or not completed].
- Evidence/report: [REQUIRED: verified link to docs/TEST_REPORT.md and/or video].

## Known limits

One shared address book; no independent user accounts. XLSX only, up to 5 MiB,
5,000 contact data rows and 100 methods per contact. Import rejects formulas and
invalid files, skips exact duplicates, and adds rather than updates contacts.
Export excludes internal database IDs/timestamps and groups methods by type.

The local Python WSGI server is for development. Optional public hosting uses
the provided Gunicorn/systemd/Nginx configuration. Public URL:
[REQUIRED: verified actual URL, or "Not deployed; cloud bonus not claimed"].

Author/student: Yihan Wang (FZUID 832402121, MUID 24125393). Individual project with
AI assistance for implementation, review, and documentation; responsibility for
understanding, verification, and submission remains with the student.
