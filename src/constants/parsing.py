from __future__ import annotations

import re

SHEET_WHITESPACE_PATTERN = re.compile(r"\s+")

COLUMN_NAME_NON_ALNUM_PATTERN = re.compile(r"[^0-9A-Za-z]+")
COLUMN_NAME_UNDERSCORE_PATTERN = re.compile(r"_+")

UNNAMED_HEADER_LABEL = "unnamed_header"
SPREADSHEET_SUFFIXES = {".xlsx", ".xls", ".xlsm", ".ods"}
