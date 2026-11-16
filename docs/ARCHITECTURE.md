# Design and Implementation

## Responsibilities

```text
Browser HTML / CSS / JavaScript
      | same-origin HTTP + JSON / XLSX bytes
      v
Application (WSGI router and response/error handling)
      |                         |
      v                         v
Store + validation         Excel converter (openpyxl)
      |
      v
SQLite contacts + contact_methods
```

`store.py` validates input and owns database transactions. `excel.py` translates
spreadsheet rows into the same validated contact model. `app.py` serves the UI and
API. The development server uses wsgiref; production uses Gunicorn behind Nginx.

## Functional structure

```text
Address Book
├── Contacts: add / view / edit / delete / search / sort
├── Bookmarks: toggle / dedicated filter / counts
├── Contact methods: type / label / value / repeated entries
├── Excel: blank template / fictional sample / export / atomic import
├── Persistence: SQLite / foreign keys / transactions
└── Delivery: tests / local setup / cloud deployment / documentation
```

## Schema

`contacts`: id (primary key), name, company, job_title, notes, bookmarked (boolean
constraint), created_at, updated_at. `contact_methods`: id (primary key), contact_id
(foreign key with ON DELETE CASCADE), type (allowlisted), label, value, position.
The one-to-many relationship avoids a fixed number of phone/email fields in the
database. Method order is retained within a contact; spreadsheet export groups
methods by type and retains within-type ordering.

All input values are parameterized in SQL. Updating a contact and replacing its
methods occurs in one transaction. Reading both tables uses a consistent snapshot.
Deleting a contact deletes its methods through the foreign-key cascade.

## Feature decisions

Bookmark: a boolean field toggled through PATCH, persisted in SQLite; browser
filters current data into a dedicated Bookmarks view. No computed star-only state.

Multiple methods: every method has type, optional label, and required value. All
six supported types can occur repeatedly. Empty UI rows are ignored; labeled rows
without values are rejected. Server validation is independent of browser checks.

Excel: one contact per row, with explicit columns `Phone 1 Label`, `Phone 1 Value`,
`Phone 2 Label`, etc. Counts are dynamic based on exported data, not truncated to
one phone number. Base fields and bookmark state are included. IDs/timestamps are
database metadata, not imported. Text data is explicitly exported as text so `=`
does not create a formula, and leading-zero phone strings remain strings.

Import validates file size, archive expansion, XML declarations, sheet name,
headers, row count, cell types and contact values. Only after all rows validate
does a single transaction write the records. Exact duplicates compare all contact
fields and method values/labels; same-name contacts with different information
are retained. A report shows imported and skipped counts. This avoids silently
discarding distinct contacts or creating partial imports after invalid rows.

## Errors and interface

Handled invalid input returns HTTP 400 with `error`, missing records 404, blocked
cross-origin writes 403, unexpected server/database failures 500 with non-sensitive
messages. Successful creation returns 201 and `data`; other reads/writes return
200. XLSX endpoints return the actual workbook MIME type and attachment filename.

UI text uses textContent, so a contact named `<img ...>` is displayed literally.
Website links accept HTTP/HTTPS only; external links use noopener/noreferrer.
No external scripts, fonts, framework CDN or build step is required. Dialogs have
accessible names, keyboard controls, form labels and visible validation messages.
Native dialogs provide focus containment. Reduced-motion preferences are respected.

The page is responsive, but browser layout and interactions require browser QA;
static code review alone is not a claim that every viewport has been verified.

## Deployment limits

One shared address book, no independent users. The optional HTTP Basic gate is
configured externally and should only be used with HTTPS. This app is suitable for
assignment/demo scale, not a privacy-sensitive multi-user production directory.
