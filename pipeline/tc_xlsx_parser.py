"""
Test Case Excel verilerini parse ve normalize eder.
Reader'dan gelen raw dict'leri, platform'un beklediği JSON yapısına çevirir.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Optional

# ---------------------------------------------------------------------------
# Normalization tables
# ---------------------------------------------------------------------------

PRIORITY_NORMALIZE: dict[str, str] = {
    "CRITICAL": "CRITICAL",
    "HIGH":     "HIGH",
    "MEDIUM":   "MEDIUM",
    "LOW":      "LOW",
    # Common abbreviations / variants
    "MED":  "MEDIUM",
    "MID":  "MEDIUM",
    "H":    "HIGH",
    "L":    "LOW",
    "C":    "CRITICAL",
    "CRIT": "CRITICAL",
    "HI":   "HIGH",
}

CHANNEL_NORMALIZE: dict[str, str] = {
    "MOBILE":  "MOBILE",
    "WEB":     "WEB",
    "API":     "API",
    "ANDROID": "ANDROID",
    "IOS":     "iOS",
    "iOS":     "iOS",
    "ALL":     "ALL",
}

# Multiple blank lines → single blank line
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


# ---------------------------------------------------------------------------
# Parser class
# ---------------------------------------------------------------------------

class TCExcelParser:
    """Test Case Excel dokümanı parser."""

    def __init__(self, raw_data: dict):
        """
        Args:
            raw_data: read_tc_xlsx() çıktısı
                      {"meta": {...}, "sheets": [...], "skip_sheets": [...]}
        """
        self.raw = raw_data
        self.warnings: list[str] = []

    # -----------------------------------------------------------------------
    # Public
    # -----------------------------------------------------------------------

    def parse(self) -> dict:
        """
        Tüm sheet'leri parse eder.

        Returns:
            {
                "doc_type": "loodos_test_case",
                "meta": {...},
                "sheets": [{"sheet_name", "test_cases", "stats"}, ...],
                "summary": {...},
                "warnings": [...]
            }
        """
        self.warnings = []
        parsed_sheets: list[dict] = []

        for sheet_raw in self.raw.get("sheets", []):
            parsed = self._parse_sheet(sheet_raw)
            parsed_sheets.append(parsed)

        summary = self._calc_summary(parsed_sheets)

        return {
            "doc_type": "loodos_test_case",
            "meta":     self.raw.get("meta", {}),
            "sheets":   parsed_sheets,
            "summary":  summary,
            "warnings": self.warnings,
        }

    # -----------------------------------------------------------------------
    # Sheet level
    # -----------------------------------------------------------------------

    def _parse_sheet(self, sheet_data: dict) -> dict:
        """
        Tek bir sheet'in raw satırlarını parse eder.
        """
        sheet_name = sheet_data.get("sheet_name", "")
        raw_rows   = sheet_data.get("rows", [])

        test_cases: list[dict] = []
        skipped    = 0
        missing_required = 0

        for row_idx, row in enumerate(raw_rows, start=1):
            tc = self._build_tc(row, sheet_name, row_idx)
            if tc is None:
                skipped += 1
                continue

            # Check required fields
            if not tc.get("testcase_name"):
                missing_required += 1

            test_cases.append(tc)

        return {
            "sheet_name": sheet_name,
            "test_cases": test_cases,
            "stats": {
                "total_rows":             len(test_cases),
                "parsed_rows":            len(test_cases),
                "skipped_rows":           skipped,
                "missing_required_fields": missing_required,
            },
        }

    def _build_tc(self, row: dict, sheet_name: str, row_idx: int) -> Optional[dict]:
        """
        Raw row dict'ini normalize edilmiş TC dict'ine çevirir.
        """
        # TC ID — auto-generate if missing
        tc_id = row.get("test_case_id")
        if not tc_id or not str(tc_id).strip():
            tc_id = self._generate_tc_id(sheet_name, row_idx)

        # Priority
        priority_raw = row.get("priority")
        priority = self._normalize_priority(priority_raw) if priority_raw else None

        # Channel
        channel_raw = row.get("channel")
        channel = self._normalize_channel(channel_raw) if channel_raw else None

        # Test steps
        steps_raw = row.get("test_steps")
        test_steps = self._clean_test_steps(steps_raw) if steps_raw else None

        return {
            "test_case_id":    tc_id,
            "testcase_name":   self._str_or_none(row.get("testcase_name")),
            "test_scenario":   self._str_or_none(row.get("test_scenario")),
            "test_area":       self._str_or_none(row.get("test_area")),
            "priority":        priority,
            "channel":         channel,
            "testcase_type":   self._str_or_none(row.get("testcase_type")),
            "user_type":       self._str_or_none(row.get("user_type")),
            "test_steps":      test_steps,
            "expected_result": self._str_or_none(row.get("expected_result")),
            "precondition":    self._str_or_none(row.get("precondition")),
            "test_data":       self._str_or_none(row.get("test_data")),
            "postcondition":   self._str_or_none(row.get("postcondition")),
            "actual_result":   self._str_or_none(row.get("actual_result")),
            "existence":       self._str_or_none(row.get("existence")),
            "date":            self._str_or_none(row.get("date")),
            "app_bundle":      self._str_or_none(row.get("app_bundle")),
            "br_id":           self._str_or_none(row.get("br_id")),
            "tr_id":           self._str_or_none(row.get("tr_id")),
            "status":          self._str_or_none(row.get("status")),
            "regression":      self._str_or_none(row.get("regression")),
            "main_business_case": self._str_or_none(row.get("main_business_case")),
            "comments":        self._str_or_none(row.get("comments")),
            "created_by":      self._str_or_none(row.get("created_by")),
            "module":          self._str_or_none(row.get("module")),
            "otomasyon":       self._str_or_none(row.get("otomasyon")),
        }

    # -----------------------------------------------------------------------
    # Normalization helpers
    # -----------------------------------------------------------------------

    def _normalize_priority(self, val: str) -> str:
        """PRIORTY/PRIORITY → normalized value. Bilinmeyen → 'UNKNOWN' + warning."""
        key = str(val).strip().upper()
        normalized = PRIORITY_NORMALIZE.get(key)
        if normalized is None:
            self.warnings.append(f"Bilinmeyen priority değeri: '{val}' → UNKNOWN")
            return "UNKNOWN"
        return normalized

    def _normalize_channel(self, val: str) -> str:
        """CHANNEL normalize. Bilinmeyen → 'OTHER' + warning."""
        key = str(val).strip().upper()
        # Try exact match first
        normalized = CHANNEL_NORMALIZE.get(key) or CHANNEL_NORMALIZE.get(str(val).strip())
        if normalized is None:
            self.warnings.append(f"Bilinmeyen channel değeri: '{val}' → OTHER")
            return "OTHER"
        return normalized

    def _clean_test_steps(self, val: str) -> str:
        """
        Test adımlarını temizle:
        - Strip leading/trailing whitespace per line
        - Collapse 3+ consecutive blank lines to single blank line
        - Preserve numbering format (1- Adım, 2- Adım)
        """
        lines = val.splitlines()
        cleaned = [line.rstrip() for line in lines]
        result = "\n".join(cleaned)
        result = _MULTI_BLANK_RE.sub("\n\n", result)
        return result.strip()

    def _generate_tc_id(self, sheet_name: str, row_idx: int) -> str:
        """TC ID yoksa üret: TC_AUTO_{SHEET_NAME}_{ROW:04d}"""
        safe_name = re.sub(r"[^A-Z0-9]", "_", sheet_name.upper())
        return f"TC_AUTO_{safe_name}_{row_idx:04d}"

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    def _calc_summary(self, parsed_sheets: list) -> dict:
        """
        Tüm sheet'lerdeki TC'leri toplayarak summary hesapla.
        """
        total_tc = 0
        by_priority: Counter = Counter()
        by_channel:  Counter = Counter()
        by_type:     Counter = Counter()
        by_test_area: Counter = Counter()

        for sheet in parsed_sheets:
            tcs = sheet.get("test_cases", [])
            total_tc += len(tcs)
            for tc in tcs:
                if tc.get("priority"):
                    by_priority[tc["priority"]] += 1
                if tc.get("channel"):
                    by_channel[tc["channel"]] += 1
                if tc.get("testcase_type"):
                    by_type[tc["testcase_type"]] += 1
                if tc.get("test_area"):
                    by_test_area[tc["test_area"]] += 1

        # Top 20 test areas
        top_test_areas = dict(by_test_area.most_common(20))

        return {
            "total_sheets":     len(parsed_sheets),
            "total_test_cases": total_tc,
            "by_priority":      dict(by_priority),
            "by_channel":       dict(by_channel),
            "by_type":          dict(by_type),
            "by_test_area":     top_test_areas,
        }

    # -----------------------------------------------------------------------
    # Utility
    # -----------------------------------------------------------------------

    @staticmethod
    def _str_or_none(val) -> Optional[str]:
        """None/boş string → None, diğerleri strip edilmiş string."""
        if val is None:
            return None
        s = str(val).strip()
        return s if s else None
