"""
ChromaDB'ye dokümanları indexle
"""

from pipeline.vector_store import get_vector_store
from data.database import get_documents_with_content
import json


def index_all_documents():
    """Tüm dokümanları ChromaDB'ye indexle."""

    print("\n" + "="*80)
    print("CHROMADB İNDEXLEME")
    print("="*80)

    # Vector store'u al
    vector_store = get_vector_store()

    # Tüm dokümanları al
    print("\n1. Dokümanlar yükleniyor...")
    documents = get_documents_with_content()
    print(f"   ✅ {len(documents)} doküman bulundu")

    if not documents:
        print("\n⚠️  Veritabanında doküman yok!")
        print("Önce create_sample_data_for_matching.py çalıştırın.")
        return

    # Her dokümanı indexle
    print("\n2. ChromaDB'ye indexleniyor...")
    indexed_count = 0
    chunk_count = 0

    for doc in documents:
        doc_id = doc['id']
        doc_title = doc['title']
        doc_type = doc['doc_type']
        content = doc.get('content_json', '{}')

        # Content'i parse et
        if isinstance(content, str):
            content_dict = json.loads(content)
        else:
            content_dict = content

        # Sections'ları extract et
        sections = content_dict.get('sections', [])

        if not sections:
            print(f"   ⚠️  {doc_title}: İçerik yok, atlanıyor")
            continue

        # VectorStore.index_document kullan
        try:
            metadata = {
                "project_name": doc.get('project_name', ''),
                "version": doc.get('current_version', 1),
                "title": doc_title
            }

            num_chunks = vector_store.index_document(
                doc_id=doc_id,
                doc_type=doc_type,
                content_json=content_dict,
                metadata=metadata
            )

            indexed_count += 1
            if num_chunks:
                chunk_count += num_chunks
                print(f"   ✅ {doc_title} ({doc_type.upper()}): {num_chunks} chunk indexlendi")
            else:
                print(f"   ✅ {doc_title} ({doc_type.upper()}): indexlendi")

        except Exception as e:
            print(f"   ❌ {doc_title}: Indexleme hatası - {e}")

    print("\n" + "="*80)
    print("✅ İNDEXLEME TAMAMLANDI")
    print("="*80)
    print(f"\nToplam: {indexed_count} doküman, {chunk_count} chunk indexlendi")

    # Collection stats
    print("\n3. ChromaDB İstatistikleri:")
    try:
        ba_stats = vector_store.get_collection_stats('ba')
        ta_stats = vector_store.get_collection_stats('ta')
        tc_stats = vector_store.get_collection_stats('tc')

        total = ba_stats.get('total_chunks', 0) + ta_stats.get('total_chunks', 0) + tc_stats.get('total_chunks', 0)

        print(f"   Total chunks: {total}")
        print(f"   BA chunks: {ba_stats.get('total_chunks', 0)}")
        print(f"   TA chunks: {ta_stats.get('total_chunks', 0)}")
        print(f"   TC chunks: {tc_stats.get('total_chunks', 0)}")
    except Exception as e:
        print(f"   ⚠️  Stats alınamadı: {e}")

    print("\n" + "="*80)
    print("ŞİMDİ TEST EDEBİLİRSİN!")
    print("="*80)
    print("\nStreamlit uygulamasında:")
    print("1. Smart Matching sayfasına git")
    print("2. Task açıklaması gir:")
    print('   "Mobil bankacılık uygulamasına Face ID ile biometric authentication ekle"')
    print("3. 'Find Matches' tıkla")
    print("\nBeklenen sonuç:")
    print("   - Mobile Banking - Authentication & Login (yüksek confidence)")
    print("   - Mobile Banking - Technical Architecture (orta confidence)")
    print("   - Mobile Banking - Login & Authentication Test Cases (orta confidence)")
    print("\n")


if __name__ == "__main__":
    index_all_documents()
