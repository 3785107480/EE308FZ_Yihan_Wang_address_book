# Address Book Development Plan

Author: Yihan Wang (individual project). Course: Software Engineering (FZU–MU).

Planning recorded before feature implementation on 16 November 2026 (Beijing time).
Deadline supplied by the student: 17 November 2026, 23:59 Beijing time.

## Scope and acceptance criteria

The student clarified that a fork is no longer required and individual work is allowed.
Retain the release, pull request, minimum three commits, individual CSDN blog,
screenshots, complete running video, and PSP requirements unless teaching staff
issue a further change. Cloud deployment is optional bonus work.

1. Create, read, edit, delete and search persistent contacts.
2. Toggle a contact bookmark and provide a dedicated Bookmarks view.
3. Store multiple labeled phone, email, social, address, website and other methods
   per contact without a fixed method-count limit.
4. Export a real XLSX workbook with one row per contact, explicit column labels,
   and all method values. Reimport the exported format without losing data.
5. Validate an entire import before writing. Report row-specific errors and import
   nothing when invalid; skip exact duplicates while retaining different people
   with the same name. Include an import template.
6. Provide an English, keyboard-usable responsive interface with loading, empty,
   success, error and confirmation states.
7. Supply source, dependency versions, setup instructions, code standards,
   meaningful automated tests and deployment configuration.

## Design and ownership

Yihan Wang owns all modules (100% individual contribution). AI assistance is used
for implementation, review and documentation. The student must run, understand,
verify and submit the work; this plan does not claim another contributor.

Modules: browser UI (HTML/CSS/JavaScript), Python WSGI HTTP API, SQLite repository,
XLSX conversion using openpyxl, tests and submission documentation. Use in-process
WSGI integration tests so endpoint/database verification does not require sockets.
Production hosting uses Gunicorn behind Nginx; the local WSGI server is for development.

## Planned meaningful commits

1. Record architecture, acceptance criteria, coding conventions and PSP plan.
2. Implement and test persistent contacts and lossless Excel import/export.
3. Implement and verify the complete browser interface and submission materials.

Commits reflect actual changes. Do not backdate commits or manufacture human work.

## PSP planned effort

| Activity | Planned minutes | Actual minutes |
|---|---:|---:|
| Requirement analysis and module design | 30 | To record |
| SQLite model and contact API | 75 | To record |
| Excel import/export and validation | 75 | To record |
| Browser interface and integration | 120 | To record |
| Automated and manual verification | 75 | To record |
| Deployment, release and pull request | 45 | To record |
| Screenshots, video and CSDN blog | 60 | To record |
| Total | 480 | To record |

These are prospective estimates, not a promise of completion time. Record actual
student effort as it occurs; assistant elapsed time is not human working time.

## External information still needed

- A GitHub repository in the student's account and authenticated publication access.
- Assignment post URL for the blog information table.
- Optional cloud host access/configuration, keeping the older calculator service intact.
- Student-recorded complete video, screenshots and final CSDN publication/submission.
