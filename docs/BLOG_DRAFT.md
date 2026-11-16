# Yihan Wang Address Book — Extreme Programming Assignment

> Publication draft. Replace every `[REQUIRED: ...]` item with real information
> before publishing. Repository and deployment addresses below are not evidence
> of publication until they have been opened and verified. Insert screenshots
> and a complete running video of the final version. Keep test results consistent
> with `docs/TEST_REPORT.md` and the final run; do not convert planned checks into
> passed results.

| Item | Content |
|---|---|
| Course for This Assignment | Software Engineering (FZU–MU) |
| Team Name | Yihan Wang — Individual Project |
| Assignment Requirements | [REQUIRED: link to the current Extreme Programming assignment post] |
| Objectives of This Assignment | Implement contact bookmarks, multiple contact methods, and Excel import/export; practise module design, Git version control, verification, release preparation, and technical documentation. |
| Other References | [Python documentation](https://docs.python.org/3/), [openpyxl documentation](https://openpyxl.readthedocs.io/), [SQLite documentation](https://www.sqlite.org/docs.html), [MDN Web Docs](https://developer.mozilla.org/), [PEP 8](https://peps.python.org/pep-0008/), [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html) |

Author: Yihan Wang. FZUID: 832402121. MUID: 24125393.

The assignment deadline is 17 November 2026, 23:59 Beijing time. The latest
clarification allows individual work and does not require a fork. I am submitting
an individual project. The release, pull request, minimum three commits, own CSDN
blog, demonstration video, and PSP requirements still apply.

## Table of contents

1. [Project links](#project-links)
2. [Assignment scope and responsibilities](#assignment-scope-and-responsibilities)
3. [PSP table](#psp-table)
4. [Finished application and evidence](#finished-application-and-evidence)
5. [Architecture and database design](#architecture-and-database-design)
6. [Implementation of required features](#implementation-of-required-features)
7. [Excel format and validation](#excel-format-and-validation)
8. [Installation and running instructions](#installation-and-running-instructions)
9. [Verification results](#verification-results)
10. [Git contributions release and pull request](#git-contributions-release-and-pull-request)
11. [Development challenges and learning](#development-challenges-and-learning)
12. [Optional cloud deployment](#optional-cloud-deployment)
13. [Limitations and future improvements](#limitations-and-future-improvements)

## Project links

These links identify the source, coding conventions, release, review, and evidence
for the submitted version. Verify the actual repository branch before using the
`main` links below.

| Resource | Address |
|---|---|
| GitHub repository | [REQUIRED: verify publication of https://github.com/3785107480/EE308FZ_Yihan_Wang_address_book] |
| Code standards | [REQUIRED: verify publication of https://github.com/3785107480/EE308FZ_Yihan_Wang_address_book/blob/main/codestyle.md] |
| Setup and configuration | [REQUIRED: verified README URL] |
| Release | [REQUIRED: actual GitHub release URL and version] |
| Pull request | [REQUIRED: actual pull request URL] |
| Complete running video | [REQUIRED: publicly playable video URL or CSDN video embed] |
| Public cloud application | [REQUIRED: actual public URL if deployed; otherwise state "Not deployed; optional cloud bonus not claimed"] |

## Assignment scope and responsibilities

Yihan Wang Address Book is an English browser application. Its three required
features are persistent bookmarks, multiple labeled contact methods for each
person, and genuine Excel `.xlsx` import/export. Contact creation, editing,
deletion, searching, sorting, an import template, and duplicate detection support
these features.

The interface is written in HTML, CSS, and JavaScript. A Python WSGI application
serves the interface and HTTP API. SQLite stores the data. openpyxl reads and
writes actual XLSX workbooks; the program does not rename a CSV file to `.xlsx`.

I am the only student in this project. The module plan and prospective PSP
estimates were recorded in `docs/DEVELOPMENT_PLAN.md` before feature development.
I used AI assistance for implementation, review, and documentation. I am
responsible for understanding, running, checking, and submitting the final work.

| Student | Responsibilities | Student contribution ratio |
|---|---|---:|
| Yihan Wang | Requirement analysis, module design, interface, Python API, SQLite, Excel conversion, verification, release, documentation, and submission | 100% |
| Total | Individual project | 100% |

There is no second team member. Pair-specific collaboration problems and a second
PSP table are therefore not applicable. The Git record is used to document actual
changes rather than to imply a partnership that did not take place.

## PSP table

The planned effort below was recorded prospectively. Fill the actual column using
real student work records, including review and verification. Assistant processing
time is not automatically student working time. Do not publish "To record" cells.

| Activity | Planned minutes | Actual minutes |
|---|---:|---:|
| Requirement analysis and module design | 30 | [REQUIRED: actual] |
| SQLite model and contact API | 75 | [REQUIRED: actual] |
| Excel import/export and validation | 75 | [REQUIRED: actual] |
| Browser interface and integration | 120 | [REQUIRED: actual] |
| Automated and manual verification | 75 | [REQUIRED: actual] |
| Deployment, release and pull request | 45 | [REQUIRED: actual] |
| Screenshots, video and CSDN blog | 60 | [REQUIRED: actual] |
| Total | 480 | [REQUIRED: sum of actual minutes] |

[REQUIRED: explain the largest real differences between planned and actual effort.
If any actual values are retrospective estimates, identify that explicitly.]

## Finished application and evidence

The application has a sidebar with All contacts and Bookmarks, a searchable
contact list, contact statistics, and a detail panel. The contact form provides
repeatable method rows. Import and export actions are available above the list.
The layout adapts to narrow screens.

Use fictional contacts for the demonstration. The downloadable sample explicitly
labels its records as fictional and is imported only when the user chooses it.
Do not include private contact details in screenshots or the video.

### Main interface

[INSERT IMAGE: `01-main-interface.png` — full desktop page with fictional contacts,
summary counts, search, import/export actions, and the connection indicator.]

The main page presents the address book, the number of contacts, bookmarked
contacts, and contact methods. The application begins empty until the user adds
or imports data; the screenshot shows the populated demonstration state.

### Multiple contact methods

[INSERT IMAGE: `02-multiple-method-form.png` — one contact form containing two phone
numbers, two emails, a social handle, and another supported method.]

The same person can have several methods of the same type. Each row has a type,
optional label, and value. The form does not restrict a person to one phone number
or one email address.

[INSERT IMAGE: `03-contact-details.png` — the saved contact detail panel showing
all the entered values and labels.]

The detail panel displays every saved method. A number such as `001234567890`
remains text, including its leading zeros.

### Bookmarks

[INSERT IMAGE: `04-bookmarks.png` — the dedicated Bookmarks view, selected stars,
and the corresponding count.]

Selecting a star changes the contact's saved bookmark value. The Bookmarks view
provides quick access to the bookmarked subset. Removing the star updates that
view and the count.

### Excel export and import

[INSERT IMAGE: `05-export-in-excel.png` — the actual exported workbook open in
Excel, Numbers, or LibreOffice, with Name, Bookmarked, and repeated method columns.]

The export is an XLSX workbook with a Contacts sheet. Each contact occupies one
row. Column names describe the base fields and every numbered method label/value.
Export includes all contacts, even when the current interface is filtered.

[INSERT IMAGE: `06-import-result.png` — importing the exported workbook into an
empty test address book and showing the imported count and restored contacts.]

Import reads the compatible workbook and restores its user-entered information.
Internal database IDs and timestamps are generated by the new database rather
than copied from the workbook.

[INSERT IMAGE: `07-duplicate-import.png` — repeating the same import and showing
zero new contacts and the skipped count.]

Exact duplicate records are skipped. Same-name people with different details are
allowed, and importing does not silently overwrite an existing contact.

[INSERT IMAGE: `08-invalid-import.png` — a workbook validation error, with the
contact count unchanged.]

The complete file is validated before insertion. An invalid row rejects the file
instead of leaving a partially imported address book.

### Persistence and usability

[INSERT IMAGE: `09-after-restart.png` — saved contacts and bookmarks after stopping
and restarting the application with the same database.]

SQLite persists the contacts and bookmarks independently of browser memory.
The recorded test must actually restart the server if it is described as a
server-restart test; a page reload alone demonstrates only browser reload behavior.

[INSERT IMAGE: `10-mobile-layout.png` — a narrow-screen layout showing readable
controls and contact information.]

The responsive interface supports a smaller browser viewport. Loading, empty,
validation-error, deletion-confirmation, and connection-error states are handled
explicitly rather than being shown as a blank page.

### Complete running video

[EMBED VIDEO: one continuous demonstration of opening the application, creating
and editing a contact, multiple methods, bookmarking and unbookmarking, Bookmarks,
search, Excel export opened in a spreadsheet viewer, deletion, Excel restore,
duplicate detection, invalid import, and persistence.]

Video address: [REQUIRED: playable link]. The video shows the submitted version
and its actual behavior. The recording guide is `docs/EVIDENCE_GUIDE.md`.

The assignment does not specify a minimum screenshot count in its latest version.
The images above are a suggested coverage plan; the complete video remains a
separate required deliverable.

## Architecture and database design

```text
Browser interface (HTML / CSS / JavaScript)
             | HTTP, JSON and XLSX bytes
             v
Python WSGI application: routing and response handling
             |                         |
             v                         v
Contact validation and Store       Excel converter
             |
             v
SQLite: contacts and contact_methods
```

The local entry point uses Python's development WSGI server. The optional cloud
configuration uses Gunicorn behind Nginx. Both use the same application object.

```text
Address Book
|-- Contacts: add, view, edit, delete, search and sort
|-- Bookmarks: persisted toggle and dedicated view
|-- Methods: repeated typed and labeled details
|-- Excel: template, sample, export, validation and atomic import
|-- Persistence: SQLite transactions and cascading deletion
|-- Delivery: Git history, tests, release, PR and evidence
```

The contacts table stores the name, company, job title, notes, bookmark flag, and
creation/update timestamps. The contact_methods table stores contact_id, type,
label, value, and position. Its contact_id is a foreign key to contacts with
ON DELETE CASCADE.

This one-to-many model supports multiple methods without adding a database column
for every additional phone number. The application applies a documented limit of
100 methods per contact. Updating a contact and replacing its method rows occurs
within a transaction.

## Implementation of required features

### Bookmark contacts

The browser sends `PATCH /api/contacts/{id}/bookmark` with a JSON boolean. The server
validates the value and updates the SQLite row. The bookmark survives reopening
the browser and restarting the server with the same database.

```python
cursor = db.execute(
    "UPDATE contacts SET bookmarked=?, updated_at=? WHERE id=?",
    (value, datetime.now(timezone.utc).isoformat(timespec="seconds"), record_id),
)
```

The star is rendered from the saved record. Bookmarks are therefore part of the
contact data, not only an icon state. The browser filters the loaded records for
its dedicated view, and the API also supports `bookmarked=true`.

### Multiple contact methods

The form appends method rows. Each method uses this structure:

```json
{"type":"phone","label":"Home","value":"001234567890"}
```

The supported types are phone, email, social, address, website, and other. Types
may repeat. The server validates the list independently of the browser and rejects
unsupported types, invalid email/website values, or exact duplicate methods in
the same contact. Fully empty form rows are ignored by the interface; a labeled
row without a value is rejected.

All contact details are inserted with SQL parameters. Deleting the parent contact
also removes its method rows through the enabled foreign-key cascade.

### Excel export

The converter counts the maximum number of methods of each type across the
exported contacts. It generates enough repeated columns to include every value:

```python
headers.extend((f"{kind.title()} {i} Label", f"{kind.title()} {i} Value"))
```

For example, two phone numbers produce Phone 1 Label, Phone 1 Value, Phone 2 Label,
and Phone 2 Value. This keeps one row per contact while preserving multiple values.
The export includes notes and bookmark state as well as the visible contact fields.

String cells are explicitly marked as text. This preserves leading zeros and
ensures a stored value beginning with `=` remains text rather than becoming a
spreadsheet formula. The workbook also includes an Instructions sheet.

### Excel import

The import endpoint reads XLSX bytes and validates the workbook into normalized
contact objects before calling the database import method:

```python
contacts = read_workbook(self.body(environ, MAX_UPLOAD))
return 200, {"data": self.store.import_contacts(contacts)}, []
```

The Store validates the records again and inserts them in one transaction.
Fingerprints compare base fields, bookmark state, and method type/label/value
tuples while ignoring method order. Exact duplicates are skipped within the file
and against existing records. The response reports imported, skipped, and total
data-row counts.

## Excel format and validation

The application accepts `.xlsx`, not legacy `.xls` or CSV. The required worksheet
name is Contacts, and Name is the required header. The template provides the
compatible layout.

| Column | Purpose |
|---|---|
| Name | Required contact name |
| Company | Optional organization |
| Job Title | Optional role |
| Notes | Optional notes |
| Bookmarked | Yes/No, True/False, or 1/0; blank means No |
| Phone 1 Label / Phone 1 Value | First phone label and value |
| Phone 2 Label / Phone 2 Value | Additional phone label and value |
| Email 1 Label / Email 1 Value | Labeled email, repeatable |
| Social 1 Label / Social 1 Value | Labeled social account, repeatable |
| Address 1 Label / Address 1 Value | Labeled postal address, repeatable |
| Website 1 Label / Website 1 Value | HTTP/HTTPS website, repeatable |
| Other 1 Label / Other 1 Value | Other labeled information, repeatable |

A method Value column may omit its Label column, but a Label column must have a
matching Value column. Unknown, duplicate, or malformed headers are rejected.
Phone cells should be formatted as Text before entering numbers: the importer
cannot recover leading zeros already removed by a spreadsheet editor.

The supported limits are 5 MiB per upload, 5,000 contact data rows, 100 methods
per contact, and 32 MiB of total uncompressed workbook content. Formula cells,
spreadsheet errors, macros, and unsupported XML declarations are rejected.
Invalid files produce an explanatory error; invalid contact rows include the
worksheet row number where available.

The workbook exports all user-entered fields. Internal IDs and database timestamps
are excluded. Methods are grouped by type in the workbook, so a round trip
preserves labels and values but may regroup their cross-type display order.

## Installation and running instructions

Use Python 3.10 or later and a current browser. From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

Open `http://127.0.0.1:8080`. On Windows, the README provides commands using
`.venv\Scripts\python.exe`. The macOS start.command launcher also prepares the
environment and starts the application.

SQLite initializes at data/addressbook.db. A different path can be supplied with
`--database` or ADDRESSBOOK_DB. Keep the same database when checking persistence.
There is no Node frontend build step and no external CDN requirement.

To demonstrate the workbook format, open Import Excel and download the blank
template or fictional sample. Enter data only on the Contacts sheet and save it
as XLSX. Export Excel downloads every contact regardless of the current filter.

## Verification results

[REQUIRED: insert the final observed date, version/commit, environment, test command,
pass/fail result, and genuine limitations from docs/TEST_REPORT.md. Do not submit
this placeholder or infer success merely because tests exist.]

The automated test command is:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

The tests use isolated databases and call the real WSGI application without
requiring a network socket. They cover contact persistence, bookmark changes,
method validation, deletion/cascade, search, XLSX round trips, duplicate detection,
atomic rejection, and invalid file handling. The browser verification exercises
the actual interface against that application using a test transport. It does
not independently establish that a public cloud HTTP server is reachable.

| Scenario | Expected behavior | Observed result |
|---|---|---|
| Bookmark/unbookmark | Persisted star; Bookmarks view updates | [REQUIRED: result] |
| Multiple methods | Repeated phones/emails and labels remain visible | [REQUIRED: result] |
| Export | Real XLSX; one row/contact; all user fields included | [REQUIRED: result] |
| Import round trip | Exported fields restored in an empty test book | [REQUIRED: result] |
| Duplicate import | Zero extra exact duplicates; skipped count shown | [REQUIRED: result] |
| Invalid row | Entire file rejected; no partial insertions | [REQUIRED: result] |
| Browser/server restart | Same database retains contacts/bookmarks | [REQUIRED: result] |
| Narrow screen | Readable controls with no unintended overflow | [REQUIRED: result] |
| Public application | Works from another network, if bonus claimed | [REQUIRED: result or not deployed] |

## Git contributions release and pull request

The project uses focused commits for the initial plan, persistent backend/Excel
implementation, and completed interface/documentation. Git timestamps and authors
reflect actual operations; the minimum commit count is not satisfied by fabricated
contributors or backdated changes.

[INSERT IMAGE: `11-github-commits.png` — GitHub history showing at least three real
commits in the submitted branch, with repository and branch visible.]

Final submitted commit: [REQUIRED: full or abbreviated SHA].

I counted non-merge commits reachable from the submitted main branch using:

```bash
git shortlog -sne --no-merges main
git rev-list --count --no-merges main
```

| Contributor | Actual non-merge commits in submitted main |
|---|---:|
| Yihan Wang / Git identity 3785107480 | [REQUIRED: actual count] |
| Total | [REQUIRED: actual count, at least 3] |

If the Git author label differs from the display name, explain the mapping to my
own GitHub account rather than counting the same person twice.

[INSERT IMAGE: `12-release-and-pr.png` — actual release/tag and pull request, or
use separate screenshots if needed.]

Release version: [REQUIRED: actual version]. Release URL: [REQUIRED: actual URL].
Pull request: [REQUIRED: actual URL, source branch, target branch, and status].
For individual work, a feature branch can be reviewed through a pull request into
main in the same repository. The PR must contain actual changes. The release tag
must identify the reviewed version that is demonstrated in the video.

## Development challenges and learning

The main design challenge was preserving multiple contact methods in a spreadsheet
while keeping one row per contact. A single Phone column would discard information.
Repeated, explicitly labeled method columns make the format readable and reversible.

Another challenge was reliable import behavior. Writing rows before checking the
whole file could leave partial data after a later error. Validating first and
using a transaction makes the import outcome predictable. Comparing complete
records instead of names alone also avoids rejecting different people who share
a name.

Phone numbers are identifiers rather than quantities. Storing and exporting them
as text preserves leading zeros and international prefixes. The explicit text
cell type also prevents a user-entered string from becoming an Excel formula.

I separated routing, validation/persistence, and workbook conversion so that the
same validation rules apply to both form submissions and imports. The code
standards and README document these boundaries and the setup requirements.

[REQUIRED: add your own specific review, coding, debugging, or Git experience.
Describe the actual trigger, observation, correction, and result. Do not invent
pair communication problems for this individual project.]

## Optional cloud deployment

[REQUIRED: retain ONE truthful version of this section.]

If deployed: The application is publicly available at [REQUIRED: actual URL].
The host runs Ubuntu with Gunicorn behind Nginx. The database is kept at
/var/lib/yihan-addressbook/addressbook.db outside the source checkout. I verified
the public page and required actions from [REQUIRED: actual external network/date].
The service will remain available for assessment. [INSERT IMAGE: public page with
address bar.] This installation shares one address book; demonstration records
are fictional.

If not deployed: The application can be installed locally using the instructions
above. Public cloud deployment has not been completed, and I do not claim the
optional 15-point cloud deployment bonus. Localhost is not presented as a public
cloud address.

## Limitations and future improvements

The current installation has one shared address book. It does not provide separate
accounts or independent per-user data. An optional HTTP Basic gate can be configured
externally over HTTPS, but that is not a full account system.

Future improvements include independent accounts, authenticated sharing, import
previews and conflict resolution, pagination for larger datasets, and automated
deployment. A public installation should use HTTPS and maintain database backups.

The submitted evidence should match the released version. Before submission I
will verify every final link, video playback, image caption, PSP entry, commit
count, and CSDN table-of-contents anchor.
