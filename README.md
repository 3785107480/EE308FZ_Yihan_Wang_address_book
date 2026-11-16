# Yihan Wang Address Book

An English-language address book for the EE308FZ Extreme Programming assignment.
Individual project by Yihan Wang (FZUID 832402121, MUID 24125393).

The browser interface supports contact CRUD, quick bookmarks, multiple labeled
contact methods, search, and real Excel `.xlsx` import/export. SQLite persists
contacts independently of the browser. No Node build step or frontend CDN is required.

## Quick start

Requirements: Python 3.10+ and a current Chrome, Edge, Firefox or Safari browser.
Install Python from [python.org](https://www.python.org/downloads/) if needed.

From the project root on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

From PowerShell on Windows:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080). The app starts empty; add a contact,
or open **Import Excel**, download the fictional sample, select it and import it.
Sample data is never added silently. Stop the development server with Ctrl+C.

On macOS, double-clicking `start.command` also creates the environment, installs
dependencies if needed and starts the local app. The first run requires internet.
If that file is not executable after downloading a ZIP, run `chmod +x start.command`.

## Features

- Add, edit, view and delete contacts; search names, organizations and method details.
- Star/unstar any contact and access a dedicated **Bookmarks** view.
- Multiple phone numbers, emails, social handles, addresses, websites and other
  methods per contact, each with its own label. Limit: 100 methods per contact.
- Export **all contacts**, including their notes, bookmark state, method labels
  and values; export is independent of the current search/bookmark filter.
- Import a compatible `.xlsx` workbook, validate it before any database write,
  report the row causing a validation error, and skip exact duplicate records.
- Preserve leading zeros and `+` in phone numbers; export text beginning with `=`
  as text, not an executable Excel formula.
- Responsive English UI, native accessible dialogs, keyboard controls, visible
  error/loading/empty states, deletion confirmation and connection refresh.

## Configuration and persistence

SQLite initializes automatically at `data/addressbook.db`. No manual schema import
is needed. The directory must be writable. Existing data survives app/browser/server
restarts. Database files are excluded from Git; back them up separately.

```bash
python server.py --host 127.0.0.1 --port 8080 --database /path/to/addressbook.db
```

Alternatively set `ADDRESSBOOK_DB` to an absolute database path. The browser and API
are served from the same origin, so no separate frontend URL configuration is needed.

For a LAN demonstration, `--host 0.0.0.0` accepts other devices on the network;
allow the chosen port in the computer firewall. Use the computer's LAN address,
not localhost, on another device.

An optional `ADDRESSBOOK_PASSWORD` environment variable enables HTTP Basic access
with username `reviewer`. Only use this over HTTPS; credentials are sent with each
request. Share evaluation credentials privately with teaching staff, never commit
them. This installation otherwise has **one shared address book**, not user accounts.
Use fictional data for a public demonstration.

## Excel contract

Use **Import Excel → Download blank template**. The workbook must contain a
`Contacts` sheet. One contact occupies one row.

| Column | Meaning |
|---|---|
| `Name` | Required name |
| `Company` | Optional organization |
| `Job Title` | Optional role |
| `Notes` | Optional notes |
| `Bookmarked` | Yes/No, True/False or 1/0; blank means No |
| `Phone 1 Label`, `Phone 1 Value` | First labeled phone number |
| `Phone 2 Label`, `Phone 2 Value` | Second phone number, and so on |
| `Email 1 Label`, `Email 1 Value` | Labeled email |
| `Social 1 Label`, `Social 1 Value` | Labeled social account |
| `Address 1 Label`, `Address 1 Value` | Labeled postal address |
| `Website 1 Label`, `Website 1 Value` | HTTP/HTTPS website |
| `Other 1 Label`, `Other 1 Value` | Other labeled detail |

Repeat numbered columns to add methods. A Value column can omit its matching Label
column, but a Label column needs a Value column. Required/optional column names are
case-sensitive. Unknown or duplicate headers are rejected rather than silently lost.

Limits: `.xlsx` only, 5 MiB upload, 5,000 contact data rows, 100 methods per contact,
32 MiB total uncompressed ZIP content. Formulas, spreadsheet error cells and macros
are rejected. Keep phone cells formatted as Text before entering values: importing
cannot restore zeros already removed by Excel. Simple email validation requires a
single `@` and a dotted domain; it does not verify deliverability.

All valid contacts are inserted in one transaction. Invalid input imports nothing.
Exact duplicates compare all contact fields, bookmark state, labels and values,
ignoring method order; they are skipped both within a file and against existing
contacts. Different contacts with the same name are allowed. Import does not update
existing contacts. Export retains every user-entered field but not internal database
IDs/timestamps; methods are grouped by type and ordered within each type.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Readiness and version |
| GET | `/api/contacts` | Contacts; optional `q` and `bookmarked=true` |
| POST | `/api/contacts` | Create contact |
| GET / PUT / DELETE | `/api/contacts/{id}` | View, replace or delete contact |
| PATCH | `/api/contacts/{id}/bookmark` | Set boolean `bookmarked` |
| GET | `/api/export` | Download all contacts as XLSX |
| GET | `/api/template` | Download empty XLSX template |
| GET | `/api/sample` | Download fictional sample XLSX |
| POST | `/api/import` | Upload raw XLSX request body |

JSON writes use `Content-Type: application/json`. Successful record/list/import
responses use `data`; deletion uses `message`; handled errors use `error` with
HTTP 400, 403, 404 or 500. POST creation returns 201. XLSX import sends binary file
bytes, not multipart form data. See [architecture](docs/ARCHITECTURE.md).

## Verification

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Tests call the real WSGI application, HTTP handlers and isolated SQLite databases.
They verify status codes and response bodies without needing a network socket.
They cover persistence, deletion/cascades, bookmarks, search, Excel round trips,
atomic import, duplicates, Unicode, leading zeros and invalid workbook rejection.

Optional full browser verification (requires Node.js 20+, npm and Chrome/Chromium):

```bash
npm install
npx playwright install chromium
npm run test:browser
```

On Windows set `ADDRESSBOOK_PYTHON` to `.venv\Scripts\python.exe` for the browser
runner if Python is not available as `python3`. The browser runner uses an isolated
temporary database and a test transport to the real WSGI application. This verifies
UI integration but does not prove a public HTTP server is reachable. It saves desktop
and mobile images under the ignored `artifacts/` directory.

Read [test status](docs/TEST_REPORT.md) for observed results and limitations.

## Cloud deployment and assignment submission

- [New Ubuntu server deployment](deploy/README.md)
- [Reuse the existing Alibaba Cloud server](deploy/EXISTING_SERVER_ZH.md)
- [Step-by-step Chinese guide](docs/NEXT_STEPS_ZH.md)
- [Evidence and complete video script](docs/EVIDENCE_GUIDE.md)
- [Requirement-by-requirement checklist](docs/ACCEPTANCE_CHECKLIST.md)
- [English individual blog draft](docs/BLOG_DRAFT.md)
- [Code standards](codestyle.md)
- [Prospective plan and PSP table](docs/DEVELOPMENT_PLAN.md)

This source package is prepared for repository name
`EE308FZ_Yihan_Wang_address_book`. The repository, cloud URL, GitHub release, pull
request, demo video and CSDN blog must be published and verified before submission.
Their links are **not yet claimed as live**. Publication requires the student's
authenticated GitHub session and cloud console/SSH access. The cloud plan reuses
the existing Alibaba Cloud server with a separate public port.

## Structure

```text
addressbook/     WSGI API, validation, SQLite repository, XLSX interchange, demo data
static/          English HTML, CSS and JavaScript interface
tests/           Real application tests and browser verification
deploy/          Gunicorn/systemd/Nginx configuration and shared-server guide
docs/            Plan, architecture, tests, evidence guide and blog draft
server.py        Local development server
wsgi.py          Production Gunicorn entry point
```
