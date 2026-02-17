"""
Tests for read_docx_structured() — Adım 1: Enhanced DOCX Reader
Kahve Dünyası formatı: bullet-list tabanlı, H1-H6, bold segments, hyperlinks
"""
import io
import pytest
from docx import Document
from docx.oxml import OxmlElement

from pipeline.document_reader import read_docx_structured


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make(build_fn) -> bytes:
    doc = Document()
    build_fn(doc)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _add_hyperlink(para, url: str, text: str):
    part  = para.part
    r_id  = part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        is_external=True,
    )
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', r_id
    )
    run_el = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = text
    run_el.append(t)
    hyperlink.append(run_el)
    para._element.append(hyperlink)


def _elements(build_fn):
    return read_docx_structured(_make(build_fn))


# ---------------------------------------------------------------------------
# Heading extraction
# ---------------------------------------------------------------------------

class TestHeadingExtraction:
    def test_h1_detected(self):
        def build(doc):
            doc.add_heading('Proje Açıklaması', level=1)

        els = _elements(build)
        headings = [e for e in els if e['type'] == 'heading']
        assert len(headings) == 1
        assert headings[0]['level'] == 1
        assert headings[0]['text'] == 'Proje Açıklaması'

    def test_h2_detected(self):
        def build(doc):
            doc.add_heading('Splash', level=2)

        els = _elements(build)
        headings = [e for e in els if e['type'] == 'heading']
        assert headings[0]['level'] == 2
        assert headings[0]['text'] == 'Splash'

    def test_h3_detected(self):
        def build(doc):
            doc.add_heading('İş Akışı', level=3)

        els = _elements(build)
        headings = [e for e in els if e['type'] == 'heading']
        assert headings[0]['level'] == 3

    def test_h4_h5_detected(self):
        def build(doc):
            doc.add_heading('Level 4', level=4)
            doc.add_heading('Level 5', level=5)

        els = _elements(build)
        headings = [e for e in els if e['type'] == 'heading']
        assert len(headings) == 2
        assert headings[0]['level'] == 4
        assert headings[1]['level'] == 5

    def test_empty_heading_skipped(self):
        def build(doc):
            doc.add_heading('', level=1)
            doc.add_heading('Real Heading', level=2)

        els = _elements(build)
        headings = [e for e in els if e['type'] == 'heading']
        assert len(headings) == 1
        assert headings[0]['text'] == 'Real Heading'

    def test_multiple_headings_ordered(self):
        def build(doc):
            doc.add_heading('H1 Bölüm', level=1)
            doc.add_heading('H2 Ekran', level=2)
            doc.add_heading('H3 Alt', level=3)

        els = _elements(build)
        headings = [e for e in els if e['type'] == 'heading']
        assert [h['level'] for h in headings] == [1, 2, 3]


# ---------------------------------------------------------------------------
# List item extraction
# ---------------------------------------------------------------------------

class TestListItemExtraction:
    def test_list_items_have_level_field(self):
        """Bullet list item'lar 'level' alanı taşımalı."""
        def build(doc):
            doc.add_paragraph('Normal paragraf')

        # python-docx Document() varsayılan olarak numPr olmadan paragraf ekler.
        # Gerçek bullet list testi için numPr XML ekliyoruz.
        doc = Document()
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement as OE

        p = doc.add_paragraph('Birinci kural')
        pPr = OE('w:pPr')
        numPr = OE('w:numPr')
        ilvl = OE('w:ilvl')
        ilvl.set(qn('w:val'), '0')
        numId = OE('w:numId')
        numId.set(qn('w:val'), '1')
        numPr.append(ilvl)
        numPr.append(numId)
        pPr.append(numPr)
        p._element.insert(0, pPr)

        buf = io.BytesIO()
        doc.save(buf)
        els = read_docx_structured(buf.getvalue())

        list_items = [e for e in els if e['type'] == 'list_item']
        assert len(list_items) >= 1
        assert list_items[0]['level'] == 0

    def test_list_item_has_required_keys(self):
        """List item'lar text, bold_segments, links alanlarına sahip olmalı."""
        doc = Document()
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement as OE

        p = doc.add_paragraph('Alt detay')
        pPr = OE('w:pPr')
        numPr = OE('w:numPr')
        ilvl = OE('w:ilvl')
        ilvl.set(qn('w:val'), '1')
        numId = OE('w:numId')
        numId.set(qn('w:val'), '1')
        numPr.append(ilvl)
        numPr.append(numId)
        pPr.append(numPr)
        p._element.insert(0, pPr)

        buf = io.BytesIO()
        doc.save(buf)
        els = read_docx_structured(buf.getvalue())

        list_items = [e for e in els if e['type'] == 'list_item']
        assert len(list_items) >= 1
        li = list_items[0]
        assert 'text' in li
        assert 'bold_segments' in li
        assert 'links' in li
        assert li['level'] == 1


# ---------------------------------------------------------------------------
# Empty paragraph filtering
# ---------------------------------------------------------------------------

class TestEmptyParagraphFiltering:
    def test_empty_paragraphs_not_in_output(self):
        def build(doc):
            doc.add_paragraph('')
            doc.add_paragraph('   ')
            doc.add_paragraph('Gerçek içerik')

        els = _elements(build)
        texts = [e.get('text', '') for e in els]
        assert '' not in texts
        assert '   ' not in texts
        assert 'Gerçek içerik' in texts

    def test_mixed_empty_and_content(self):
        def build(doc):
            doc.add_heading('Başlık', level=1)
            doc.add_paragraph('')
            doc.add_paragraph('İçerik')

        els = _elements(build)
        assert len(els) == 2
        assert els[0]['type'] == 'heading'
        assert els[1]['text'] == 'İçerik'


# ---------------------------------------------------------------------------
# Hyperlink extraction
# ---------------------------------------------------------------------------

class TestHyperlinkExtraction:
    def test_hyperlink_url_extracted(self):
        url = 'https://app.lottiefiles.com/share/abc123'

        def build(doc):
            para = doc.add_paragraph('Animasyon: ')
            _add_hyperlink(para, url, 'Lottie Linki')

        els = _elements(build)
        all_links = [l for e in els for l in e.get('links', [])]
        assert url in all_links

    def test_paragraph_without_links_has_empty_list(self):
        def build(doc):
            doc.add_paragraph('Normal paragraf, link yok.')

        els = _elements(build)
        paras = [e for e in els if e['type'] == 'paragraph']
        assert paras[0]['links'] == []

    def test_multiple_hyperlinks_in_paragraph(self):
        url1 = 'https://app.lottiefiles.com/share/aaa'
        url2 = 'https://docs.google.com/document/d/xyz'

        def build(doc):
            para = doc.add_paragraph('Linkler: ')
            _add_hyperlink(para, url1, 'Lottie')
            _add_hyperlink(para, url2, 'Google Doc')

        els = _elements(build)
        all_links = [l for e in els for l in e.get('links', [])]
        assert url1 in all_links
        assert url2 in all_links

    def test_lottie_link_in_heading_paragraph(self):
        url = 'https://figma.com/file/abc/design'

        def build(doc):
            doc.add_heading('Splash', level=2)
            para = doc.add_paragraph('Tasarım: ')
            _add_hyperlink(para, url, 'Figma')

        els = _elements(build)
        paras = [e for e in els if e['type'] == 'paragraph']
        assert any(url in e.get('links', []) for e in paras)


# ---------------------------------------------------------------------------
# Bold segment extraction
# ---------------------------------------------------------------------------

class TestBoldSegmentExtraction:
    def test_bold_runs_extracted(self):
        doc = Document()
        para = doc.add_paragraph()
        run_normal = para.add_run('Normal metin ')
        run_bold   = para.add_run('BOLD_TERM')
        run_bold.bold = True

        buf = io.BytesIO()
        doc.save(buf)
        els = read_docx_structured(buf.getvalue())

        paras = [e for e in els if e['type'] == 'paragraph']
        assert len(paras) == 1
        assert 'BOLD_TERM' in paras[0]['bold_segments']

    def test_non_bold_runs_not_in_bold_segments(self):
        doc = Document()
        para = doc.add_paragraph()
        run = para.add_run('Sadece normal metin')
        run.bold = False

        buf = io.BytesIO()
        doc.save(buf)
        els = read_docx_structured(buf.getvalue())

        paras = [e for e in els if e['type'] == 'paragraph']
        assert paras[0]['bold_segments'] == []

    def test_paragraph_has_bold_segments_key(self):
        def build(doc):
            doc.add_paragraph('Herhangi bir metin')

        els = _elements(build)
        paras = [e for e in els if e['type'] == 'paragraph']
        assert 'bold_segments' in paras[0]


# ---------------------------------------------------------------------------
# Table extraction
# ---------------------------------------------------------------------------

class TestTableExtraction:
    def test_table_extracted_with_headers_and_rows(self):
        def build(doc):
            t = doc.add_table(rows=3, cols=2)
            t.cell(0, 0).text = 'Sütun A'
            t.cell(0, 1).text = 'Sütun B'
            t.cell(1, 0).text = 'Veri 1'
            t.cell(1, 1).text = 'Veri 2'
            t.cell(2, 0).text = 'Veri 3'
            t.cell(2, 1).text = 'Veri 4'

        els = _elements(build)
        tables = [e for e in els if e['type'] == 'table']
        assert len(tables) == 1
        assert tables[0]['headers'] == ['Sütun A', 'Sütun B']
        assert len(tables[0]['rows']) == 2

    def test_empty_table_handled(self):
        def build(doc):
            doc.add_table(rows=1, cols=2)

        els = _elements(build)
        tables = [e for e in els if e['type'] == 'table']
        assert len(tables) == 1
        assert tables[0]['rows'] == []


# ---------------------------------------------------------------------------
# Element order preserved
# ---------------------------------------------------------------------------

class TestElementOrderPreserved:
    def test_heading_paragraph_order(self):
        def build(doc):
            doc.add_heading('Başlık', level=1)
            doc.add_paragraph('Paragraf içerik')

        els = _elements(build)
        assert els[0]['type'] == 'heading'
        assert els[1]['type'] == 'paragraph'

    def test_heading_paragraph_table_order(self):
        def build(doc):
            doc.add_heading('Başlık', level=2)
            doc.add_paragraph('Açıklama')
            t = doc.add_table(rows=2, cols=2)
            t.cell(0, 0).text = 'H1'; t.cell(0, 1).text = 'H2'
            t.cell(1, 0).text = 'R1'; t.cell(1, 1).text = 'R2'

        els = _elements(build)
        types = [e['type'] for e in els]
        assert types == ['heading', 'paragraph', 'table']

    def test_empty_document_returns_empty_list(self):
        def build(doc):
            pass

        els = _elements(build)
        assert els == []
