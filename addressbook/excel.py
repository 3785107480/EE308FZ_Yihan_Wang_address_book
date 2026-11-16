"""Bounded, lossless XLSX interchange with one contact per row."""

from collections import Counter
from datetime import datetime, timezone
from io import BytesIO
import re
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from .store import METHOD_TYPES, MAX_METHODS, ValidationError, validate_contact

BASE_HEADERS = ("Name", "Company", "Job Title", "Notes", "Bookmarked")
MAX_UPLOAD = 5 * 1024 * 1024
MAX_ROWS = 5000
MAX_COLUMNS = 5 + 2 * MAX_METHODS * len(METHOD_TYPES)


def write_workbook(contacts, template=False):
    """Export every method in dynamically repeated, labeled columns."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contacts"
    widths = {kind: 1 for kind in METHOD_TYPES}
    for contact in contacts:
        for kind, count in Counter(m["type"] for m in contact["methods"]).items():
            widths[kind] = max(widths[kind], count)
    headers = list(BASE_HEADERS)
    for kind in METHOD_TYPES:
        for i in range(1, widths[kind] + 1):
            headers.extend((f"{kind.title()} {i} Label", f"{kind.title()} {i} Value"))
    sheet.append(headers)
    for contact in contacts:
        values = [contact["name"], contact["company"], contact["job_title"],
                  contact["notes"], "Yes" if contact["bookmarked"] else "No"]
        for kind in METHOD_TYPES:
            methods = [method for method in contact["methods"] if method["type"] == kind]
            for i in range(widths[kind]):
                values.extend((methods[i]["label"], methods[i]["value"]) if i < len(methods) else ("", ""))
        sheet.append(values)
        for cell in sheet[sheet.max_row]:
            # Explicit strings retain leading zeros and cannot become formulas.
            cell.data_type = "s"
            cell.number_format = "@"
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for cell in sheet[1]:
        cell.fill = PatternFill("solid", fgColor="163D39")
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(vertical="center")
    sheet.row_dimensions[1].height = 28
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in sheet.columns:
        sheet.column_dimensions[column[0].column_letter].width = 28
    sheet.column_dimensions["D"].width = 42
    instructions = workbook.create_sheet("Instructions")
    for line in [
        "Yihan Wang Address Book — XLSX format v1",
        "Enter contacts on the Contacts sheet. One contact per row. Name is required.",
        "Bookmarked accepts Yes/No, True/False, or 1/0. A blank cell means No.",
        "Repeated columns use e.g. Phone 1 Label, Phone 1 Value, Phone 2 Label, Phone 2 Value.",
        "Supported types: Phone, Email, Social, Address, Website, Other.",
        "Keep phone values as text to preserve leading zeros and + prefixes.",
        "Email must be a valid address. Website must start with http:// or https://.",
        "Do not enter formulas. Unknown, duplicate or malformed column headers are rejected.",
        "At most 5000 contacts per file and 100 contact methods per contact; upload limit 5 MiB.",
        "Invalid rows reject the entire file; exact duplicate contacts are skipped.",
        "Method values, labels, notes and bookmarks are included in the export.",
        "Database IDs and timestamps are internal metadata and are not imported/exported.",
        "Method order is grouped by type; repeated methods within a type retain their order.",
        "Template: fill the Contacts sheet and save as .xlsx." if template else
        f"Exported at {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
    ]:
        instructions.append([line])
    instructions.column_dimensions["A"].width = 110
    for row in instructions:
        row[0].alignment = Alignment(wrap_text=True, vertical="top")
        instructions.row_dimensions[row[0].row].height = 30
    result = BytesIO()
    workbook.save(result)
    workbook.close()
    return result.getvalue()


def read_workbook(raw):
    if not raw or len(raw) > MAX_UPLOAD:
        raise ValidationError("Choose a non-empty .xlsx file no larger than 5 MiB.")
    try:
        with ZipFile(BytesIO(raw)) as archive:
            infos = archive.infolist()
            if len(infos) > 500 or sum(info.file_size for info in infos) > 32 * 1024 * 1024:
                raise ValidationError("The workbook expands beyond the supported size.")
            if any(info.filename.endswith("vbaProject.bin") for info in infos):
                raise ValidationError("Macro-enabled workbooks are not supported.")
            for info in infos:
                if info.filename.endswith(".xml"):
                    xml = archive.read(info).upper()
                    if b"<!DOCTYPE" in xml or b"<!ENTITY" in xml:
                        raise ValidationError("XML document declarations and entities are not supported.")
        workbook = load_workbook(BytesIO(raw), read_only=True, data_only=False, keep_links=False)
    except ValidationError:
        raise
    except Exception as error:
        raise ValidationError("The file is not a readable .xlsx workbook.") from error
    try:
        if "Contacts" not in workbook.sheetnames:
            raise ValidationError("The workbook must contain a sheet named Contacts. Download the template.")
        sheet = workbook["Contacts"]
        if (sheet.max_row or 0) > MAX_ROWS + 1 or (sheet.max_column or 0) > MAX_COLUMNS:
            raise ValidationError("The workbook contains too many rows or columns.")
        rows = sheet.iter_rows()
        first = next(rows, ())
        while first and first[-1].value is None:
            first = first[:-1]
        headers = []
        for cell in first:
            if cell.data_type == "f" or not isinstance(cell.value, str):
                raise ValidationError("Every used column needs a text header.")
            headers.append(cell.value.strip())
        if not headers or "Name" not in headers:
            raise ValidationError("The Name column is required. Download the import template.")
        if len(headers) != len(set(headers)):
            raise ValidationError("Duplicate column headers are not allowed.")
        method_columns = {}
        for i, header in enumerate(headers):
            if header in BASE_HEADERS:
                continue
            match = re.fullmatch(r"(Phone|Email|Social|Address|Website|Other) ([1-9]\d*) (Label|Value)", header)
            if not match or int(match.group(2)) > MAX_METHODS:
                raise ValidationError(f"Unsupported column: {header}")
            kind, index, part = match.groups()
            method_columns.setdefault((kind.lower(), int(index)), {})[part] = i
        if any("Value" not in parts for parts in method_columns.values()):
            raise ValidationError("Each method label column needs a matching Value column.")
        contacts = []
        for row_number, row in enumerate(rows, 2):
            if row_number > MAX_ROWS + 1:
                raise ValidationError("The worksheet exceeds 5000 data rows.")
            if not any(cell.value is not None and cell.value != "" for cell in row):
                continue
            if len(contacts) >= MAX_ROWS:
                raise ValidationError("The workbook exceeds 5000 contacts.")
            values = []
            for cell in row:
                if cell.data_type == "f":
                    raise ValidationError(f"Row {row_number}: formulas are not allowed.")
                if cell.data_type == "e":
                    raise ValidationError(f"Row {row_number}: spreadsheet error cells are not allowed.")
                if isinstance(cell.value, float) and cell.value.is_integer():
                    values.append(str(int(cell.value)))
                else:
                    values.append("" if cell.value is None else str(cell.value))
            values += [""] * max(0, len(headers) - len(values))
            if any(values[len(headers):]):
                raise ValidationError(f"Row {row_number}: data exists in an unlabeled column.")
            data = dict(zip(headers, values))
            bookmark = data.get("Bookmarked", "").strip().lower()
            if bookmark not in ("", "yes", "no", "true", "false", "1", "0"):
                raise ValidationError(f"Row {row_number}: Bookmarked must be Yes or No.")
            contact = {
                "name": data.get("Name", ""), "company": data.get("Company", ""),
                "job_title": data.get("Job Title", ""), "notes": data.get("Notes", ""),
                "bookmarked": bookmark in ("yes", "true", "1"), "methods": [],
            }
            for (kind, index), parts in sorted(method_columns.items()):
                label = values[parts["Label"]].strip() if "Label" in parts else ""
                value = values[parts["Value"]].strip()
                if label and not value:
                    raise ValidationError(f"Row {row_number}: {kind.title()} {index} has a label but no value.")
                if value:
                    contact["methods"].append({"type": kind, "label": label, "value": value})
            try:
                contacts.append(validate_contact(contact))
            except ValidationError as error:
                raise ValidationError(f"Row {row_number}: {error}") from error
        if not contacts:
            raise ValidationError("The Contacts sheet contains no contact records.")
        return contacts
    except ValidationError:
        raise
    except Exception as error:
        raise ValidationError("The workbook contains unsupported or damaged data.") from error
    finally:
        workbook.close()
