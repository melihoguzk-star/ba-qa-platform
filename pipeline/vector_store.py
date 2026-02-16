"""
Vector Store using ChromaDB

Persistent vector database for semantic search. Manages document chunks,
embeddings, and similarity queries.

Author: BA-QA Platform
Date: 2026-02-16
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB wrapper for document vector storage and semantic search."""

    # Collection names by document type
    COLLECTIONS = {
        'ba': 'ba_documents',
        'ta': 'ta_documents',
        'tc': 'tc_documents'
    }

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB client with persistence.

        Args:
            persist_directory: Path to ChromaDB storage (default: data/chroma_db)
        """
        self.persist_directory = persist_directory or os.getenv(
            'CHROMA_DB_PATH',
            'data/chroma_db'
        )

        self._client = None
        self._collections = {}  # Cache collection objects

    @property
    def client(self):
        """Lazy load ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                logger.info(f"Initializing ChromaDB at: {self.persist_directory}")

                # Ensure directory exists
                os.makedirs(self.persist_directory, exist_ok=True)

                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info("ChromaDB client initialized")

            except ImportError:
                raise ImportError(
                    "chromadb not installed. Run: pip install chromadb"
                )
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                raise

        return self._client

    def get_collection(self, doc_type: str):
        """
        Get or create collection for document type.

        Args:
            doc_type: Document type ('ba', 'ta', 'tc')

        Returns:
            ChromaDB collection object
        """
        if doc_type not in self.COLLECTIONS:
            raise ValueError(f"Invalid document type: {doc_type}")

        collection_name = self.COLLECTIONS[doc_type]

        # Return cached collection
        if collection_name in self._collections:
            return self._collections[collection_name]

        # Get or create collection
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "description": f"{doc_type.upper()} documents for semantic search",
                    "created_at": datetime.now().isoformat()
                }
            )
            self._collections[collection_name] = collection
            logger.info(f"Collection ready: {collection_name}")
            return collection

        except Exception as e:
            logger.error(f"Failed to get collection {collection_name}: {e}")
            raise

    def index_document(self, doc_id: int, doc_type: str, content_json: dict,
                       metadata: dict = None):
        """
        Index a document by chunking and storing embeddings.

        Args:
            doc_id: Document ID from database
            doc_type: Document type ('ba', 'ta', 'tc')
            content_json: Parsed document content
            metadata: Additional metadata (tags, jira_keys, project_id, etc.)
        """
        # Import here to avoid circular dependency
        from pipeline.chunking_strategy import get_chunker
        from pipeline.embedding_pipeline import get_embedding_pipeline

        logger.info(f"Indexing document {doc_id} (type: {doc_type})")

        try:
            # 1. Chunk document
            chunker = get_chunker()
            chunks = chunker.chunk_document(doc_id, doc_type, content_json, metadata)

            if not chunks:
                logger.warning(f"No chunks generated for document {doc_id}")
                return 0  # Return 0 chunks

            logger.info(f"Generated {len(chunks)} chunks for document {doc_id}")

            # 2. Generate embeddings
            embedding_pipeline = get_embedding_pipeline()
            chunk_texts = [chunk['chunk_text'] for chunk in chunks]
            embeddings = embedding_pipeline.embed_batch(chunk_texts)

            # 3. Prepare ChromaDB data
            ids = [f"doc{doc_id}_chunk{i}" for i in range(len(chunks))]
            documents = chunk_texts
            metadatas = []

            for chunk in chunks:
                chunk_metadata = {
                    'document_id': doc_id,
                    'chunk_index': chunk['chunk_index'],
                    'chunk_type': chunk['chunk_type'],
                    'indexed_at': datetime.now().isoformat(),
                    **chunk['metadata']
                }
                # Convert lists to JSON strings (ChromaDB requirement)
                for key, value in list(chunk_metadata.items()):
                    if isinstance(value, (list, dict)):
                        import json
                        chunk_metadata[key] = json.dumps(value)
                    elif value is None:
                        chunk_metadata[key] = ''

                metadatas.append(chunk_metadata)

            # 4. Store in ChromaDB
            collection = self.get_collection(doc_type)

            # Delete existing chunks for this document (update operation)
            self._delete_document_chunks(collection, doc_id)

            # Add new chunks
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(f"Document {doc_id} indexed with {len(chunks)} chunks")
            return len(chunks)  # Return number of chunks indexed

        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            raise

    def search(self, query_text: str, doc_type: str, top_k: int = 10,
               filter_metadata: dict = None) -> List[Dict[str, Any]]:
        """
        Semantic search for similar document chunks.

        Args:
            query_text: Search query text
            doc_type: Document type to search ('ba', 'ta', 'tc')
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {'project_id': 1})

        Returns:
            List of matching chunks with metadata and similarity scores
        """
        from pipeline.embedding_pipeline import embed_text

        logger.info(f"Searching {doc_type} documents: '{query_text[:50]}...'")

        try:
            # Generate query embedding
            query_embedding = embed_text(query_text)

            # Search collection
            collection = self.get_collection(doc_type)

            # Check collection size and limit top_k
            collection_count = collection.count()
            actual_top_k = min(top_k, collection_count) if collection_count > 0 else top_k

            if collection_count == 0:
                logger.warning(f"Collection {doc_type} is empty")
                return []

            # Build where filter if provided
            where_filter = None
            if filter_metadata:
                where_filter = filter_metadata

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_top_k,
                where=where_filter
            )

            # Format results
            matches = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    match = {
                        'id': results['ids'][0][i],
                        'document_id': results['metadatas'][0][i].get('document_id'),
                        'chunk_text': results['documents'][0][i],
                        'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i]
                    }
                    matches.append(match)

            logger.info(f"Found {len(matches)} matches")
            return matches

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete_document(self, doc_id: int, doc_type: str):
        """
        Delete all chunks for a document.

        Args:
            doc_id: Document ID to delete
            doc_type: Document type
        """
        logger.info(f"Deleting document {doc_id} from vector store")

        try:
            collection = self.get_collection(doc_type)
            self._delete_document_chunks(collection, doc_id)
            logger.info(f"Document {doc_id} deleted from vector store")

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise

    def _delete_document_chunks(self, collection, doc_id: int):
        """Delete all chunks belonging to a document."""
        try:
            # Query for all chunks with this document_id
            results = collection.get(
                where={"document_id": doc_id}
            )

            if results['ids']:
                collection.delete(ids=results['ids'])
                logger.debug(f"Deleted {len(results['ids'])} chunks for document {doc_id}")

        except Exception as e:
            logger.warning(f"Failed to delete chunks for document {doc_id}: {e}")

    def get_collection_stats(self, doc_type: str = None) -> Dict[str, Any]:
        """
        Get statistics for collections.

        Args:
            doc_type: Specific document type, or None for all

        Returns:
            Dictionary with collection statistics
        """
        stats = {}

        doc_types = [doc_type] if doc_type else ['ba', 'ta', 'tc']

        for dtype in doc_types:
            try:
                collection = self.get_collection(dtype)
                count = collection.count()
                stats[dtype] = {
                    'collection_name': self.COLLECTIONS[dtype],
                    'chunk_count': count,
                    'status': 'active'
                }
            except Exception as e:
                stats[dtype] = {
                    'collection_name': self.COLLECTIONS.get(dtype, 'unknown'),
                    'chunk_count': 0,
                    'status': 'error',
                    'error': str(e)
                }

        return stats

    def clear_all_collections(self):
        """
        Clear all collections (DANGEROUS - use only for testing).
        """
        logger.warning("Clearing all ChromaDB collections")

        for doc_type in ['ba', 'ta', 'tc']:
            try:
                collection_name = self.COLLECTIONS[doc_type]
                self.client.delete_collection(name=collection_name)
                logger.info(f"Deleted collection: {collection_name}")

                # Clear cache
                if collection_name in self._collections:
                    del self._collections[collection_name]

            except Exception as e:
                logger.error(f"Failed to delete collection {doc_type}: {e}")

        logger.warning("All collections cleared")


# Singleton instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get singleton vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
