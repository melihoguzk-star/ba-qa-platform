"""
TC XLSX Database Integration

Parse edilmiş Test Case Excel verisini platforma kaydeder:
  1. SQLite documents tablosuna dosya bazlı üst kayıt
  2. Duplicate tespiti (aynı başlık/kaynak → yeni versiyon)
  3. ChromaDB'ye semantik arama için embedding indexleme
     (TC adı + test scenario + test steps → chunk text)

Kullanım:
    from pipeline.tc_xlsx_db import save_tc_import
    result = save_tc_import(parsed_data, source_file="file.xlsx",
                            project_id=1, title="Kahve Dünyası TC")
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Tag applied to all XLSX imports for easy filtering
XLSX_IMPORT_TAG = "xlsx_import"
TC_TAG = "test_case"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_tc_import(
    parsed_data: dict,
    source_file: str,
    project_id: int,
    title: Optional[str] = None,
    index_chromadb: bool = True,
) -> dict:
    """
    Parse edilmiş TC verisini veritabanına kaydet ve ChromaDB'ye index et.

    Args:
        parsed_data:    TCExcelParser.parse() çıktısı
        source_file:    Orijinal dosya adı (duplicate tespiti + description için)
        project_id:     Hedef proje ID'si
        title:          Doküman başlığı (None ise source_file'dan türetilir)
        index_chromadb: ChromaDB indexlemesi yapılsın mı?

    Returns:
        {
            "imported":   int,   # yeni kayıt sayısı
            "updated":    int,   # güncellenen kayıt sayısı
            "skipped":    int,   # atlanan kayıt sayısı
            "doc_id":     int | None,
            "chunks":     int,   # ChromaDB'ye eklenen chunk sayısı
            "errors":     [str]
        }
    """
    stats = {"imported": 0, "updated": 0, "skipped": 0, "doc_id": None,
             "chunks": 0, "errors": []}

    # ── Başlık ──────────────────────────────────────────────────────────────
    if not title:
        title = source_file.rsplit(".", 1)[0]  # dosya adı, uzantısız

    # ── Duplicate kontrolü ──────────────────────────────────────────────────
    existing_doc = _find_existing_doc(project_id, title, source_file)

    try:
        if existing_doc:
            doc_id = existing_doc["id"]
            _update_existing(doc_id, parsed_data, source_file)
            stats["updated"] = 1
            stats["doc_id"] = doc_id
            logger.info("TC import: updated doc_id=%d ('%s')", doc_id, title)
        else:
            doc_id = _create_new(project_id, title, parsed_data, source_file)
            stats["imported"] = 1
            stats["doc_id"] = doc_id
            logger.info("TC import: created doc_id=%d ('%s')", doc_id, title)
    except Exception as exc:
        logger.error("TC import save failed: %s", exc)
        stats["errors"].append(f"Kayıt hatası: {exc}")
        return stats

    # ── ChromaDB indexleme ──────────────────────────────────────────────────
    if index_chromadb and doc_id:
        try:
            chunks = _index_to_chromadb(doc_id, parsed_data, project_id, title)
            stats["chunks"] = chunks
        except Exception as exc:
            logger.warning("ChromaDB indexing failed (non-fatal): %s", exc)
            stats["errors"].append(f"ChromaDB index hatası: {exc}")

    return stats


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def _find_existing_doc(project_id: int, title: str, source_file: str) -> Optional[dict]:
    """
    Aynı proje + başlık veya kaynak dosya eşleşmesi olan mevcut TC belgesini döndürür.
    """
    from data.database import get_db

    conn = get_db()
    try:
        # 1. Exact title match in same project
        row = conn.execute(
            """
            SELECT id, title, current_version
            FROM documents
            WHERE project_id = ? AND doc_type = 'tc' AND title = ? AND status != 'archived'
            LIMIT 1
            """,
            (project_id, title),
        ).fetchone()

        if row:
            return dict(row)

        # 2. Same source file (stored in description)
        row = conn.execute(
            """
            SELECT id, title, current_version
            FROM documents
            WHERE project_id = ? AND doc_type = 'tc'
              AND description LIKE ? AND status != 'archived'
            LIMIT 1
            """,
            (project_id, f"%{source_file}%"),
        ).fetchone()

        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Create / Update
# ---------------------------------------------------------------------------

def _create_new(project_id: int, title: str, parsed_data: dict, source_file: str) -> int:
    """Yeni TC belgesi oluştur, ilk versiyonu kaydet, doc_id döndür."""
    from data.database import create_document

    summary = parsed_data.get("summary", {})
    sheet_count = summary.get("total_sheets", 0)
    tc_count = summary.get("total_test_cases", 0)
    description = (
        f"XLSX import: {source_file} | "
        f"{sheet_count} sheet | {tc_count} test case"
    )

    doc_id = create_document(
        project_id=project_id,
        doc_type="tc",
        title=title,
        content_json=parsed_data,
        description=description,
        tags=[XLSX_IMPORT_TAG, TC_TAG],
        created_by="xlsx_upload",
    )
    return doc_id


def _update_existing(doc_id: int, parsed_data: dict, source_file: str) -> None:
    """Mevcut belgeye yeni versiyon ekle ve updated_at'ı güncelle."""
    from data.database import get_db, create_document_version

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT current_version FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
        current_ver = row["current_version"] if row else 1
        new_ver = current_ver + 1

        # Yeni versiyon oluştur
        create_document_version(
            doc_id=doc_id,
            content_json=parsed_data,
            change_summary=f"XLSX re-import: {source_file} @ {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            created_by="xlsx_upload",
        )

        # Versiyon numarasını güncelle
        conn.execute(
            "UPDATE documents SET current_version = ?, updated_at = ? WHERE id = ?",
            (new_ver, datetime.now().isoformat(), doc_id),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ChromaDB indexing
# ---------------------------------------------------------------------------

def _index_to_chromadb(doc_id: int, parsed_data: dict, project_id: int, title: str) -> int:
    """
    Parsed TC verisini ChromaDB 'tc_documents' koleksiyonuna index eder.

    Her sheet için birleşik chunk text:
        {sheet_name} | {testcase_name} | {test_scenario} | {test_steps}
    Bu sayede semantik arama TC bazında çalışır.
    """
    from pipeline.vector_store import VectorStore

    metadata = {
        "project_id": project_id,
        "title": title,
        "doc_type": "tc",
        "source": "xlsx_import",
        "imported_at": datetime.now().isoformat(),
    }

    vs = VectorStore()
    chunk_count = vs.index_document(
        doc_id=doc_id,
        doc_type="tc",
        content_json=parsed_data,
        metadata=metadata,
    )
    return chunk_count or 0


# ---------------------------------------------------------------------------
# Convenience: build TC text for embedding (also used in tests)
# ---------------------------------------------------------------------------

def build_tc_embedding_text(tc: dict) -> str:
    """
    Tek bir TC satırı için embedding metni oluşturur.
    Format: "{testcase_name} | {test_scenario} | {test_area} | {test_steps}"
    """
    parts = [
        tc.get("testcase_name") or "",
        tc.get("test_scenario") or "",
        tc.get("test_area") or "",
        tc.get("test_steps") or "",
    ]
    return " | ".join(p for p in parts if p).strip()
