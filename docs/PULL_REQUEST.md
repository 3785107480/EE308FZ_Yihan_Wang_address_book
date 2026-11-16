# Complete the address book interface, deployment and verification

The persistent contacts and Excel API need a browser interface for the assignment
workflow. This change adds contact forms and details, bookmark access, search and
sorting, Excel download/upload, and visible request feedback in an English
responsive page.

It also adds a macOS launcher, browser integration runner, CI configuration,
Gunicorn/systemd/Nginx deployment files, and detailed setup and submission
documentation. The shared-server deployment listens publicly on port 8081 and
proxies to the address book on localhost:8080.

Validation: all 9 WSGI/SQLite/Excel test methods passed on Python 3.12.14 with
openpyxl 3.1.5. JavaScript syntax checks passed. The tests cover repeated methods
of all six types, 100-method round trips, bookmark persistence, import atomicity,
duplicate handling and rejected input. A consistent SQLite read transaction keeps
contacts and their methods in the same snapshot.

Browser execution remains pending: Chrome aborted at launch in the development
environment. Clean dependency installation, manual UI/workbook checks and public
cloud access must be recorded after running on the student's computer/server.
