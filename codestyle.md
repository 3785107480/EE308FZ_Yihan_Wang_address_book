# Code Standards

## Sources

Python conventions derive from [PEP 8](https://peps.python.org/pep-0008/) and
[PEP 257](https://peps.python.org/pep-0257/). JavaScript conventions derive from
the [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html).
HTML follows the [HTML Living Standard](https://html.spec.whatwg.org/), with
accessibility informed by [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

## Project conventions

- Use UTF-8, English interface text, comments and documentation.
- Use four-space indentation in Python and two spaces in JavaScript, HTML and CSS.
- Use snake_case Python names, lowerCamelCase JavaScript names, and descriptive
  identifiers. Keep one statement per line and document non-obvious decisions.
- Keep HTTP routing, SQLite operations and Excel processing in separate modules.
- Validate data on the server. Use SQL parameters, transactions and foreign keys.
- Render contact text with textContent, never interpolated untrusted HTML.
- Bound upload size and workbook dimensions; reject formulas in import data.
- Never commit personal contacts, credentials, databases or machine-specific paths.
- Test behavior and persistence with isolated databases; do not test deletion on
  a public dataset containing real personal information.
- Update README and tests when the API or spreadsheet contract changes.
- Keep commits focused and descriptive; record actual contributions honestly.
