"""
tests/test_tc_xlsx_parser.py

TC XLSX Parser & Normalizer modülü için test suite.
pipeline/tc_xlsx_parser.py → TCExcelParser, PRIORITY_NORMALIZE, CHANNEL_NORMALIZE
"""
import pytest


# ── Import ─────────────────────────────────────────────────────────────────────

def test_import():
    """Modül import edilebilmeli."""
    from pipeline.tc_xlsx_parser import TCExcelParser, PRIORITY_NORMALIZE, CHANNEL_NORMALIZE
    assert "CRITICAL" in PRIORITY_NORMALIZE
    assert "MOBILE" in CHANNEL_NORMALIZE


# ── Priority normalization ─────────────────────────────────────────────────────

class TestPriorityNormalization:

    @pytest.fixture
    def parser(self):
        from pipeline.tc_xlsx_parser import TCExcelParser
        return TCExcelParser({"meta": {}, "sheets": []})

    def test_critical(self, parser):
        assert parser._normalize_priority("CRITICAL") == "CRITICAL"

    def test_high(self, parser):
        assert parser._normalize_priority("HIGH") == "HIGH"

    def test_medium(self, parser):
        assert parser._normalize_priority("MEDIUM") == "MEDIUM"

    def test_low(self, parser):
        assert parser._normalize_priority("LOW") == "LOW"

    def test_case_insensitive_critical(self, parser):
        assert parser._normalize_priority("critical") == "CRITICAL"

    def test_case_insensitive_high(self, parser):
        assert parser._normalize_priority("high") == "HIGH"

    def test_abbreviation_med(self, parser):
        assert parser._normalize_priority("MED") == "MEDIUM"

    def test_abbreviation_h(self, parser):
        assert parser._normalize_priority("H") == "HIGH"

    def test_abbreviation_l(self, parser):
        assert parser._normalize_priority("L") == "LOW"

    def test_abbreviation_c(self, parser):
        assert parser._normalize_priority("C") == "CRITICAL"

    def test_unknown_returns_unknown(self, parser):
        result = parser._normalize_priority("PRIORTY")  # truly unknown
        assert result == "UNKNOWN"

    def test_unknown_adds_warning(self, parser):
        parser.warnings = []
        parser._normalize_priority("XYZ")
        assert any("XYZ" in w for w in parser.warnings)


# ── Channel normalization ──────────────────────────────────────────────────────

class TestChannelNormalization:

    @pytest.fixture
    def parser(self):
        from pipeline.tc_xlsx_parser import TCExcelParser
        return TCExcelParser({"meta": {}, "sheets": []})

    def test_mobile(self, parser):
        assert parser._normalize_channel("MOBILE") == "MOBILE"

    def test_web(self, parser):
        assert parser._normalize_channel("WEB") == "WEB"

    def test_api(self, parser):
        assert parser._normalize_channel("API") == "API"

    def test_android(self, parser):
        assert parser._normalize_channel("ANDROID") == "ANDROID"

    def test_ios(self, parser):
        assert parser._normalize_channel("IOS") == "iOS"

    def test_all(self, parser):
        assert parser._normalize_channel("ALL") == "ALL"

    def test_case_insensitive_mobile(self, parser):
        assert parser._normalize_channel("mobile") == "MOBILE"

    def test_unknown_returns_other(self, parser):
        result = parser._normalize_channel("FOOBAR")
        assert result == "OTHER"

    def test_unknown_adds_warning(self, parser):
        parser.warnings = []
        parser._normalize_channel("ZIGZAG")
        assert any("ZIGZAG" in w for w in parser.warnings)


# ── TC ID generation ───────────────────────────────────────────────────────────

class TestTcIdGeneration:

    @pytest.fixture
    def parser(self):
        from pipeline.tc_xlsx_parser import TCExcelParser
        return TCExcelParser({"meta": {}, "sheets": []})

    def test_basic(self, parser):
        assert parser._generate_tc_id("Login", 5) == "TC_AUTO_LOGIN_0005"

    def test_zero_padded(self, parser):
        assert parser._generate_tc_id("Login", 1) == "TC_AUTO_LOGIN_0001"

    def test_large_row(self, parser):
        assert parser._generate_tc_id("Login", 9999) == "TC_AUTO_LOGIN_9999"

    def test_special_chars_replaced(self, parser):
        result = parser._generate_tc_id("Login&Register", 1)
        assert result == "TC_AUTO_LOGIN_REGISTER_0001"

    def test_spaces_replaced(self, parser):
        result = parser._generate_tc_id("Ana Sayfa", 3)
        assert result == "TC_AUTO_ANA_SAYFA_0003"

    def test_turkish_chars_uppercased(self, parser):
        result = parser._generate_tc_id("Ürün", 2)
        # Non-ASCII chars become _ via regex sub on upper()
        assert result.startswith("TC_AUTO_")
        assert "0002" in result


# ── Clean test steps ───────────────────────────────────────────────────────────

class TestCleanTestSteps:

    @pytest.fixture
    def parser(self):
        from pipeline.tc_xlsx_parser import TCExcelParser
        return TCExcelParser({"meta": {}, "sheets": []})

    def test_strips_trailing_whitespace(self, parser):
        result = parser._clean_test_steps("1- Adım   \n2- Adım   ")
        assert not result.endswith("   ")

    def test_collapses_multiple_blank_lines(self, parser):
        result = parser._clean_test_steps("1- Adım\n\n\n\n2- Adım")
        assert "\n\n\n" not in result

    def test_preserves_single_blank_line(self, parser):
        result = parser._clean_test_steps("1- Adım\n\n2- Adım")
        assert "\n\n" in result

    def test_preserves_numbering(self, parser):
        steps = "1- App açılır\n2- Login yapılır\n3- Dashboard görünür"
        result = parser._clean_test_steps(steps)
        assert "1- App açılır" in result
        assert "2- Login yapılır" in result
        assert "3- Dashboard görünür" in result

    def test_strip_outer_whitespace(self, parser):
        result = parser._clean_test_steps("  \n1- Adım\n  ")
        assert not result.startswith(" ")
        assert not result.endswith(" ")


# ── str_or_none ─────────────────────────────────────────────────────────────────

class TestStrOrNone:

    @pytest.fixture
    def parser(self):
        from pipeline.tc_xlsx_parser import TCExcelParser
        return TCExcelParser({"meta": {}, "sheets": []})

    def test_none_returns_none(self, parser):
        assert parser._str_or_none(None) is None

    def test_empty_string_returns_none(self, parser):
        assert parser._str_or_none("") is None

    def test_whitespace_returns_none(self, parser):
        assert parser._str_or_none("   ") is None

    def test_normal_string(self, parser):
        assert parser._str_or_none("  test  ") == "test"


# ── _parse_sheet ─────────────────────────────────────────────────────────────────

class TestParseSheet:

    def test_stats_total_rows(self, sample_tc_raw):
        from pipeline.tc_xlsx_parser import TCExcelParser
        parser = TCExcelParser(sample_tc_raw)
        result = parser.parse()
        login = next(s for s in result["sheets"] if s["sheet_name"] == "Login")
        assert login["stats"]["total_rows"] == 2

    def test_tc_id_auto_generated_when_missing(self, sample_tc_raw):
        """pinarÜrünDetay sheet'inde TEST CASE ID yok → otomatik üretilmeli."""
        from pipeline.tc_xlsx_parser import TCExcelParser
        parser = TCExcelParser(sample_tc_raw)
        result = parser.parse()
        pinar = next(s for s in result["sheets"] if s["sheet_name"] == "pinarÜrünDetay")
        tc = pinar["test_cases"][0]
        # ID ya gerçek (varsa) ya da TC_AUTO_... formatında
        assert tc["test_case_id"] is not None
        assert len(tc["test_case_id"]) > 0

    def test_all_canonical_fields_present(self, sample_tc_raw):
        """Her TC dict tüm canonical field'ları içermeli (None olabilir)."""
        from pipeline.tc_xlsx_parser import TCExcelParser
        EXPECTED_FIELDS = [
            "test_case_id", "testcase_name", "test_scenario", "test_area",
            "priority", "channel", "testcase_type", "user_type",
            "test_steps", "expected_result", "precondition", "test_data",
        ]
        parser = TCExcelParser(sample_tc_raw)
        result = parser.parse()
        for sheet in result["sheets"]:
            for tc in sheet["test_cases"]:
                for field in EXPECTED_FIELDS:
                    assert field in tc, f"Missing field '{field}' in TC: {tc}"


# ── Summary hesaplama ─────────────────────────────────────────────────────────

class TestSummaryCalculation:

    def test_total_sheets(self, sample_tc_parsed):
        assert sample_tc_parsed["summary"]["total_sheets"] == 4

    def test_total_test_cases(self, sample_tc_parsed):
        # Login: 2, Sepet: 1, pinarÜrünDetay: 1, Regresyon: 1 → 5
        assert sample_tc_parsed["summary"]["total_test_cases"] == 5

    def test_by_priority_has_high(self, sample_tc_parsed):
        assert "HIGH" in sample_tc_parsed["summary"]["by_priority"]

    def test_by_priority_has_critical(self, sample_tc_parsed):
        assert "CRITICAL" in sample_tc_parsed["summary"]["by_priority"]

    def test_by_priority_has_medium(self, sample_tc_parsed):
        assert "MEDIUM" in sample_tc_parsed["summary"]["by_priority"]

    def test_by_channel_has_mobile(self, sample_tc_parsed):
        assert "MOBILE" in sample_tc_parsed["summary"]["by_channel"]

    def test_by_channel_has_web(self, sample_tc_parsed):
        assert "WEB" in sample_tc_parsed["summary"]["by_channel"]

    def test_by_type_has_functional(self, sample_tc_parsed):
        assert "Functional" in sample_tc_parsed["summary"]["by_type"]

    def test_by_test_area_exists(self, sample_tc_parsed):
        assert "Login Ekranı" in sample_tc_parsed["summary"]["by_test_area"]

    def test_summary_counts_match(self, sample_tc_parsed):
        """by_priority toplamı total_test_cases'a eşit olmalı."""
        total_by_priority = sum(
            sample_tc_parsed["summary"]["by_priority"].values()
        )
        assert total_by_priority == sample_tc_parsed["summary"]["total_test_cases"]


# ── parse() çıktı yapısı ──────────────────────────────────────────────────────

class TestParseOutputSchema:

    def test_doc_type(self, sample_tc_parsed):
        assert sample_tc_parsed["doc_type"] == "loodos_test_case"

    def test_meta_present(self, sample_tc_parsed):
        assert "meta" in sample_tc_parsed
        assert sample_tc_parsed["meta"]["project_name"] == "Kahve Dünyası"

    def test_sheets_list(self, sample_tc_parsed):
        assert isinstance(sample_tc_parsed["sheets"], list)
        assert len(sample_tc_parsed["sheets"]) > 0

    def test_warnings_list(self, sample_tc_parsed):
        assert isinstance(sample_tc_parsed["warnings"], list)

    def test_each_sheet_has_stats(self, sample_tc_parsed):
        for sheet in sample_tc_parsed["sheets"]:
            assert "stats" in sheet
            assert "total_rows" in sheet["stats"]
            assert "skipped_rows" in sheet["stats"]

    def test_priority_normalized_in_output(self, sample_tc_parsed):
        """Login sheet'teki TC'lerin priority'si normalize edilmiş olmalı."""
        login = next(s for s in sample_tc_parsed["sheets"] if s["sheet_name"] == "Login")
        priorities = {tc["priority"] for tc in login["test_cases"]}
        # Bilinmeyen değer olmamalı
        for p in priorities:
            assert p in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN", "OTHER", None}, \
                f"Unexpected priority: {p}"

    def test_channel_normalized_in_output(self, sample_tc_parsed):
        """Login sheet'teki TC'lerin channel'ı normalize edilmiş olmalı."""
        login = next(s for s in sample_tc_parsed["sheets"] if s["sheet_name"] == "Login")
        channels = {tc["channel"] for tc in login["test_cases"]}
        assert "MOBILE" in channels


# ── Özel durumlar ──────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_empty_sheets_list(self):
        """Hiç sheet yoksa parse boş list döndürmeli."""
        from pipeline.tc_xlsx_parser import TCExcelParser
        parser = TCExcelParser({"meta": {}, "sheets": []})
        result = parser.parse()
        assert result["sheets"] == []
        assert result["summary"]["total_test_cases"] == 0

    def test_none_priority_not_normalized(self):
        """None priority → _build_tc'de normalize edilmemeli, None kalmalı."""
        from pipeline.tc_xlsx_parser import TCExcelParser
        raw = {
            "meta": {},
            "sheets": [{
                "sheet_name": "Test",
                "rows": [{
                    "testcase_name": "TC", "test_steps": "1- Adım", "expected_result": "OK",
                    "priority": None, "channel": None,
                }]
            }]
        }
        parser = TCExcelParser(raw)
        result = parser.parse()
        tc = result["sheets"][0]["test_cases"][0]
        assert tc["priority"] is None

    def test_otomasyon_field_preserved(self, sample_tc_parsed):
        """Regresyon Seti sheet'inde otomasyon alanı korunmalı."""
        reg = next(s for s in sample_tc_parsed["sheets"] if s["sheet_name"] == "Regresyon Seti")
        tc = reg["test_cases"][0]
        assert tc.get("otomasyon") == "Otomasyon Hazır"


# ── build_tc_embedding_text ───────────────────────────────────────────────────

class TestEmbeddingText:

    def test_basic(self):
        from pipeline.tc_xlsx_db import build_tc_embedding_text
        tc = {
            "testcase_name": "Login Test",
            "test_scenario": "Login Kontrolü",
            "test_area": "Login Ekranı",
            "test_steps": "1- App açılır",
        }
        text = build_tc_embedding_text(tc)
        assert "Login Test" in text
        assert "Login Kontrolü" in text
        assert "Login Ekranı" in text
        assert "1- App açılır" in text

    def test_none_fields_excluded(self):
        from pipeline.tc_xlsx_db import build_tc_embedding_text
        tc = {"testcase_name": "TC", "test_scenario": None, "test_area": None, "test_steps": None}
        text = build_tc_embedding_text(tc)
        assert "TC" in text
        assert "None" not in text

    def test_separator(self):
        from pipeline.tc_xlsx_db import build_tc_embedding_text
        tc = {"testcase_name": "A", "test_scenario": "B", "test_area": "C", "test_steps": "D"}
        text = build_tc_embedding_text(tc)
        assert " | " in text


# ── Full pipeline ──────────────────────────────────────────────────────────────

class TestFullPipeline:

    def test_reader_to_parser_chain(self, sample_tc_xlsx):
        """read_tc_xlsx → TCExcelParser → parse() uçtan uca çalışmalı."""
        from pipeline.tc_xlsx_reader import read_tc_xlsx
        from pipeline.tc_xlsx_parser import TCExcelParser

        raw = read_tc_xlsx(sample_tc_xlsx)
        result = TCExcelParser(raw).parse()

        assert result["doc_type"] == "loodos_test_case"
        assert result["summary"]["total_test_cases"] >= 1
        assert len(result["sheets"]) >= 1
        assert isinstance(result["warnings"], list)

    def test_all_tcs_have_id(self, sample_tc_parsed):
        """Her TC'nin bir ID'si olmalı (gerçek veya otomatik üretilmiş)."""
        for sheet in sample_tc_parsed["sheets"]:
            for tc in sheet["test_cases"]:
                assert tc["test_case_id"] is not None
                assert len(tc["test_case_id"]) > 0, f"Empty TC ID in: {tc}"
