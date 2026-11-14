#!/usr/bin/env python3
"""Read and write single cells in an .xlsx without a spreadsheet library.

The kit's two workbooks are written with inline strings (``t="inlineStr"``), so a
cell can be read and replaced as plain XML. Everything else in the file — styles,
column widths, the frozen header, the second sheet — is copied through untouched,
which is why the workbooks keep their look after a scheduler update.

    from excel import Workbook
    wb = Workbook("Vintage-Motor-House-Tracker.xlsx")
    for number, row in wb.rows("Tracker"):
        print(number, row["C"])          # row 1 is the header
    wb.set("Tracker", "H2", "Scheduled")
    wb.save()                            # atomic: temp file, then os.replace

Reading is forgiving (missing cells are ``""``, numbers come back as text); writing
only touches the cells you name. A save with no changes rewrites nothing.
"""

from __future__ import annotations

import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple
from xml.etree import ElementTree as ET

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RELNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKGREL = "http://schemas.openxmlformats.org/package/2006/relationships"

ET.register_namespace("", NS)


def split_ref(ref: str) -> Tuple[str, int]:
    """``"AB12"`` -> ``("AB", 12)``."""
    match = re.fullmatch(r"([A-Z]+)(\d+)", ref.strip().upper())
    if not match:
        raise ValueError("not a cell reference: %r" % ref)
    return match.group(1), int(match.group(2))


def col_index(col: str) -> int:
    """``"A"`` -> 1, ``"L"`` -> 12 (1-based, like the XML)."""
    value = 0
    for char in col:
        value = value * 26 + (ord(char) - 64)
    return value


def col_letter(index: int) -> str:
    """1 -> ``"A"``, 28 -> ``"AB"``."""
    out = ""
    while index:
        index, rest = divmod(index - 1, 26)
        out = chr(65 + rest) + out
    return out


class Workbook:
    """One workbook, held in memory until :meth:`save`."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        with zipfile.ZipFile(self.path) as archive:
            self._entries = {name: archive.read(name) for name in archive.namelist()}
            self._order = list(archive.namelist())
            self._compress = {info.filename: info.compress_type
                              for info in archive.infolist()}
        self._sheets = self._sheet_map()
        self._shared = self._shared_strings()
        self._dirty: set[str] = set()
        self._trees = {name: ET.fromstring(self._entries[path])
                       for name, path in self._sheets.items()}

    # -- reading ---------------------------------------------------------
    def _sheet_map(self) -> Dict[str, str]:
        workbook = ET.fromstring(self._entries["xl/workbook.xml"])
        rels = ET.fromstring(self._entries["xl/_rels/workbook.xml.rels"])
        targets = {rel.get("Id"): rel.get("Target") for rel in rels.findall("{%s}Relationship" % PKGREL)}
        out: Dict[str, str] = {}
        for sheet in workbook.iter("{%s}sheet" % NS):
            target = targets.get(sheet.get("{%s}id" % RELNS), "")
            target = target.lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            out[sheet.get("name")] = target
        return out

    def _shared_strings(self) -> List[str]:
        raw = self._entries.get("xl/sharedStrings.xml")
        if not raw:
            return []
        root = ET.fromstring(raw)
        return ["".join(t.text or "" for t in item.iter("{%s}t" % NS))
                for item in root.findall("{%s}si" % NS)]

    def sheet_names(self) -> List[str]:
        return list(self._sheets)

    def rows(self, sheet: str) -> List[Tuple[int, Dict[str, str]]]:
        """``[(row_number, {column_letter: value}), ...]`` including the header."""
        root = self._trees[sheet]
        out: List[Tuple[int, Dict[str, str]]] = []
        for row in root.iter("{%s}row" % NS):
            values: Dict[str, str] = {}
            for cell in row.findall("{%s}c" % NS):
                ref = cell.get("r") or ""
                try:
                    col, _ = split_ref(ref)
                except ValueError:
                    continue
                values[col] = self._value(cell)
            out.append((int(row.get("r") or 0), values))
        return out

    def _value(self, cell: ET.Element) -> str:
        kind = cell.get("t")
        if kind == "inlineStr":
            return "".join(t.text or "" for t in cell.iter("{%s}t" % NS))
        value = cell.find("{%s}v" % NS)
        text = (value.text or "") if value is not None else ""
        if kind == "s":
            try:
                return self._shared[int(text)]
            except (ValueError, IndexError):
                return ""
        return text

    def find(self, sheet: str, column: str, needle: str, ignore_case: bool = True) -> List[int]:
        """Row numbers (excluding the header) whose *column* contains *needle*."""
        wanted = needle.strip()
        hits: List[int] = []
        for number, row in self.rows(sheet)[1:]:
            value = (row.get(column) or "").strip()
            if not value:
                continue
            if (wanted.lower() in value.lower()) if ignore_case else (wanted in value):
                hits.append(number)
        return hits

    # -- writing ---------------------------------------------------------
    def set(self, sheet: str, ref: str, value) -> bool:
        """Write one cell. Returns True when the file actually changed."""
        col, rownum = split_ref(ref)
        text = "" if value is None else str(value)
        root = self._trees[sheet]
        row = self._row(root, rownum, create=True)
        cell = row.find("{%s}c[@r='%s']" % (NS, col + str(rownum)))
        if cell is None:
            cell = ET.Element("{%s}c" % NS, {"r": col + str(rownum)})
            style = self._style_for(root, col, rownum)
            if style:
                cell.set("s", style)
            self._insert(row, cell, col)
        if self._value(cell) == text:
            return False
        for child in list(cell):
            cell.remove(child)
        cell.attrib.pop("t", None)
        if text == "":
            pass
        elif _is_number(text):
            ET.SubElement(cell, "{%s}v" % NS).text = text
        else:
            cell.set("t", "inlineStr")
            inline = ET.SubElement(cell, "{%s}is" % NS)
            node = ET.SubElement(inline, "{%s}t" % NS)
            node.text = text
            if text != text.strip() or "\n" in text:
                node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        self._dirty.add(sheet)
        return True

    def _row(self, root: ET.Element, rownum: int, create: bool):
        sheet_data = root.find("{%s}sheetData" % NS)
        for row in sheet_data.findall("{%s}row" % NS):
            if int(row.get("r") or 0) == rownum:
                return row
        if not create:
            return None
        row = ET.Element("{%s}row" % NS, {"r": str(rownum)})
        index = 0
        for existing in sheet_data.findall("{%s}row" % NS):
            if int(existing.get("r") or 0) > rownum:
                break
            index += 1
        sheet_data.insert(index, row)
        return row

    def _style_for(self, root: ET.Element, col: str, rownum: int) -> str:
        """Borrow the style of the same column in another filled row."""
        best = ""
        for row in root.iter("{%s}row" % NS):
            if int(row.get("r") or 0) == rownum:
                continue
            for cell in row.findall("{%s}c" % NS):
                ref = cell.get("r") or ""
                try:
                    name, _ = split_ref(ref)
                except ValueError:
                    continue
                if name == col and cell.get("s"):
                    if int(row.get("r") or 0) == rownum - 1:
                        return cell.get("s")
                    best = best or cell.get("s")
        return best

    def _insert(self, row: ET.Element, cell: ET.Element, col: str) -> None:
        target = col_index(col)
        index = 0
        for existing in row.findall("{%s}c" % NS):
            ref = existing.get("r") or ""
            try:
                name, _ = split_ref(ref)
            except ValueError:
                continue
            if col_index(name) > target:
                break
            index += 1
        row.insert(index, cell)

    # -- saving ----------------------------------------------------------
    def save(self, path: str | Path | None = None) -> Path:
        """Write every changed sheet back, atomically."""
        destination = Path(path) if path else self.path
        if self._dirty:
            for sheet in self._dirty:
                name = self._sheets[sheet]
                body = ET.tostring(self._trees[sheet], encoding="UTF-8", xml_declaration=True)
                self._entries[name] = body
            self._dirty.clear()
        handle, temp = tempfile.mkstemp(suffix=".xlsx", dir=str(destination.parent))
        os.close(handle)
        try:
            with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
                for name in self._order:
                    archive.writestr(name, self._entries[name],
                                     compress_type=self._compress.get(name, zipfile.ZIP_DEFLATED))
            os.replace(temp, destination)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return destination


def _is_number(text: str) -> bool:
    if text != text.strip() or not text:
        return False
    try:
        float(text)
    except ValueError:
        return False
    return True
