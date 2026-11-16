# Verification Report

Project: Yihan Wang Address Book. Verification recorded on 16 November 2026
(Beijing time). This report distinguishes observed checks from remaining
publication and deployment work.

## Automated backend and workbook verification

Command from the repository root:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Observed result: **9 test methods passed**, including parameterized subcases.
The observed runtime was Python 3.12.14 with openpyxl 3.1.5. This used the bundled
verification runtime, not a fresh installation from `requirements.txt`; the clean
installation check remains part of the student setup verification.
The test runner invokes the actual WSGI application, response handlers, workbook
converter and SQLite repository. Each test uses a temporary database. No listening
socket or cloud service is required, and the demonstration database is untouched.

| Test | Observed result | Behavior covered |
|---|---|---|
| `test_contact_crud_multiple_methods_and_persistence` | Passed | Create/view/update/delete; seven labeled methods; application recreation with the same SQLite file; deletion cascade |
| `test_bookmarks_search_and_casefold` | Passed | Bookmark/unbookmark, bookmark filter, case-insensitive search and empty search results |
| `test_bad_contact_validation_does_not_write` | Passed | Invalid contact shape/name/bookmark/type/email/website/duplicate methods rejected without records |
| `test_excel_export_import_round_trip_all_data` | Passed | Genuine XLSX attachment; one row per contact; Unicode; notes; bookmark and method labels/values; leading zeros; formula-like text stays text; reimport and exact duplicate skipping |
| `test_repeated_methods_of_every_type_survive_excel_round_trip` | Passed | Two methods of each of six types; labeled dynamic columns; 12 methods retained; bookmark survives application recreation and XLSX round trip |
| `test_method_limit_exports_without_truncation` | Passed | All 100 supported methods exported and restored; 101-method update rejected without changing the original record |
| `test_import_atomicity_duplicate_policy_and_same_name` | Passed | Invalid row rejects entire import; row-specific error; exact duplicates skipped; different same-name contacts retained |
| `test_invalid_workbooks_rejected` | Passed | Corrupt input; wrong sheet; missing/duplicate/unknown headers; invalid bookmark; labels without values; formula cells; empty template rejected as an import |
| `test_limits_routing_security_and_health` | Passed | Database readiness check; missing records; blocked traversal and cross-site writes; content type and body limits; optional access gate |

The importer and exporter use `openpyxl`. Round-trip assertions compare all
user-entered fields using the same normalized contact model, including method
labels and values. Internal database IDs and timestamps are deliberately not
part of the spreadsheet contract. Method order is grouped by type in Excel,
while the order within each type is retained.

## Browser verification

The optional browser runner is `tests/browser_test.cjs`:

```bash
npm install
npx playwright install chromium
npm run test:browser
```

It exercises browser interactions against the real Python WSGI application and
an isolated SQLite database through a test transport. Its intended coverage
includes create/edit/delete, multiple methods, bookmarks, reload persistence,
search, actual XLSX download/upload, duplicate import, safe text rendering and
desktop/mobile layout checks. It writes review images into `artifacts/`.

The browser runner was attempted in the development environment on 16 November
2026. Chrome terminated with SIGABRT during launch, before opening the application.
No browser assertions or screenshot inspections completed; the UI verification
therefore remains pending. JavaScript syntax checks passed for `static/app.js`
and `tests/browser_test.cjs`. The backend result above alone is not evidence that
the UI was visually inspected or that a real network endpoint is reachable.

Starting a listening development server was also blocked by this environment's
socket restrictions (`PermissionError` at bind). This does not establish a failure
on the student's computer or cloud host. Check the actual installation there.

## Remaining evaluation evidence

- Run the documented setup on the student's computer and confirm the application
  opens in a normal browser over the local HTTP server.
- Open an exported workbook in Excel or Numbers and demonstrate readable headers,
  one row per contact and every contact method, then import it in the application.
- Capture the final interface and required features, including an invalid-import
  error and successful import/export.
- Record a complete running demonstration video and verify playback permissions.
- If claiming cloud bonus points, deploy to the actual public host and verify it
  from another network. Local or simulated browser URLs do not establish this.
- Verify the final GitHub repository, commit history, release asset, pull request
  and published CSDN article independently after publication.

No public deployment, GitHub publication, video publication or CSDN submission is
claimed complete by this report.
