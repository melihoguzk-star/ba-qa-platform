#!/usr/bin/env python3
"""
Bulk Reindex Script for ChromaDB

Reindex all existing documents from SQLite into ChromaDB vector store.
Supports incremental processing, checkpoint resume, and dry-run mode.

Usage:
    python scripts/reindex_all.py --doc-type ba --batch-size 50
    python scripts/reindex_all.py --doc-type ta --batch-size 50
    python scripts/reindex_all.py --doc-type tc --batch-size 50
    python scripts/reindex_all.py --all  # Reindex all document types

Author: BA-QA Platform
Date: 2026-02-16
"""
import argparse
import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.database import get_db
from pipeline.vector_store import get_vector_store

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReindexProgress:
    """Track reindexing progress with checkpoint support."""

    def __init__(self, checkpoint_file='data/reindex_checkpoint.json'):
        self.checkpoint_file = checkpoint_file
        self.progress = self._load_checkpoint()

    def _load_checkpoint(self):
        """Load checkpoint from file."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return {}

    def save_checkpoint(self, doc_type, last_doc_id, stats):
        """Save checkpoint to file."""
        self.progress[doc_type] = {
            'last_doc_id': last_doc_id,
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        }
        try:
            os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def get_last_doc_id(self, doc_type):
        """Get last processed document ID for resume."""
        return self.progress.get(doc_type, {}).get('last_doc_id', 0)

    def clear_checkpoint(self, doc_type=None):
        """Clear checkpoint for doc type or all."""
        if doc_type:
            if doc_type in self.progress:
                del self.progress[doc_type]
        else:
            self.progress = {}

        if os.path.exists(self.checkpoint_file):
            try:
                if self.progress:
                    with open(self.checkpoint_file, 'w') as f:
                        json.dump(self.progress, f, indent=2)
                else:
                    os.remove(self.checkpoint_file)
            except Exception as e:
                logger.error(f"Failed to clear checkpoint: {e}")


def reindex_documents(doc_type, batch_size=50, dry_run=False, resume=False):
    """
    Reindex documents of a specific type.

    Args:
        doc_type: Document type to reindex ('ba', 'ta', 'tc', or 'all')
        batch_size: Number of documents per batch
        dry_run: If True, only count documents without indexing
        resume: If True, resume from last checkpoint

    Returns:
        Dictionary with reindexing statistics
    """
    stats = {
        'total_documents': 0,
        'indexed': 0,
        'failed': 0,
        'skipped': 0,
        'start_time': datetime.now().isoformat()
    }

    # Initialize progress tracker
    progress = ReindexProgress()

    # Get last processed doc ID if resuming
    start_doc_id = 0
    if resume:
        start_doc_id = progress.get_last_doc_id(doc_type)
        if start_doc_id > 0:
            logger.info(f"Resuming from document ID: {start_doc_id}")

    try:
        # Query documents from database
        conn = get_db()
        query = """
            SELECT d.id, d.doc_type, d.project_id, d.title, d.description,
                   d.tags, d.jira_keys, d.current_version,
                   dv.content_json
            FROM documents d
            JOIN document_versions dv ON d.id = dv.document_id
                AND d.current_version = dv.version_number
            WHERE d.doc_type = ? AND d.status = 'active' AND d.id > ?
            ORDER BY d.id ASC
        """

        rows = conn.execute(query, (doc_type, start_doc_id)).fetchall()
        conn.close()

        stats['total_documents'] = len(rows)

        if dry_run:
            logger.info(f"DRY RUN: Would reindex {len(rows)} {doc_type} documents")
            return stats

        if not rows:
            logger.info(f"No documents found for type: {doc_type}")
            return stats

        logger.info(f"Reindexing {len(rows)} {doc_type} documents...")

        # Get vector store
        vector_store = get_vector_store()

        # Process documents in batches
        try:
            from tqdm import tqdm
            progress_bar = tqdm(rows, desc=f"Indexing {doc_type}", unit="doc")
        except ImportError:
            progress_bar = rows
            logger.warning("tqdm not installed. Install for progress bar: pip install tqdm")

        batch_count = 0
        last_doc_id = start_doc_id

        for row in progress_bar:
            doc_id = row['id']
            last_doc_id = doc_id

            try:
                # Parse content JSON
                content_json = json.loads(row['content_json'])

                # Prepare metadata
                metadata = {
                    'project_id': row['project_id'],
                    'title': row['title'],
                    'description': row['description'] or '',
                    'tags': json.loads(row['tags'] or '[]'),
                    'jira_keys': json.loads(row['jira_keys'] or '[]'),
                    'version_number': row['current_version']
                }

                # Index document
                vector_store.index_document(
                    doc_id=doc_id,
                    doc_type=doc_type,
                    content_json=content_json,
                    metadata=metadata
                )

                stats['indexed'] += 1
                batch_count += 1

                # Save checkpoint every batch
                if batch_count >= batch_size:
                    progress.save_checkpoint(doc_type, last_doc_id, stats)
                    batch_count = 0

            except Exception as e:
                logger.error(f"Failed to index document {doc_id}: {e}")
                stats['failed'] += 1

        # Save final checkpoint
        progress.save_checkpoint(doc_type, last_doc_id, stats)

        stats['end_time'] = datetime.now().isoformat()

        # Calculate duration
        start = datetime.fromisoformat(stats['start_time'])
        end = datetime.fromisoformat(stats['end_time'])
        duration = (end - start).total_seconds()
        stats['duration_seconds'] = duration

        # Clear checkpoint after successful completion
        if not resume or stats['indexed'] == stats['total_documents']:
            progress.clear_checkpoint(doc_type)

        return stats

    except Exception as e:
        logger.error(f"Reindexing failed: {e}")
        raise


def print_statistics(doc_type, stats):
    """Print reindexing statistics."""
    print("\n" + "=" * 60)
    print(f"REINDEXING STATISTICS - {doc_type.upper()}")
    print("=" * 60)
    print(f"Total Documents:     {stats['total_documents']}")
    print(f"Successfully Indexed: {stats['indexed']}")
    print(f"Failed:              {stats['failed']}")
    print(f"Skipped:             {stats['skipped']}")

    if 'duration_seconds' in stats:
        duration = stats['duration_seconds']
        print(f"Duration:            {duration:.2f}s")

        if stats['indexed'] > 0:
            rate = stats['indexed'] / duration
            print(f"Indexing Rate:       {rate:.2f} docs/sec")

    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Bulk reindex documents into ChromaDB vector store'
    )
    parser.add_argument(
        '--doc-type',
        choices=['ba', 'ta', 'tc', 'all'],
        default='all',
        help='Document type to reindex (default: all)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Batch size for checkpointing (default: 50)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Count documents without indexing'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint'
    )
    parser.add_argument(
        '--clear-checkpoint',
        action='store_true',
        help='Clear checkpoint and start fresh'
    )

    args = parser.parse_args()

    # Clear checkpoint if requested
    if args.clear_checkpoint:
        progress = ReindexProgress()
        if args.doc_type == 'all':
            progress.clear_checkpoint()
            logger.info("Cleared all checkpoints")
        else:
            progress.clear_checkpoint(args.doc_type)
            logger.info(f"Cleared checkpoint for {args.doc_type}")
        return

    # Determine which document types to process
    doc_types = ['ba', 'ta', 'tc'] if args.doc_type == 'all' else [args.doc_type]

    overall_stats = {
        'total_documents': 0,
        'indexed': 0,
        'failed': 0,
        'skipped': 0
    }

    # Process each document type
    for doc_type in doc_types:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {doc_type.upper()} documents")
        logger.info(f"{'='*60}")

        try:
            stats = reindex_documents(
                doc_type=doc_type,
                batch_size=args.batch_size,
                dry_run=args.dry_run,
                resume=args.resume
            )

            print_statistics(doc_type, stats)

            # Update overall stats
            overall_stats['total_documents'] += stats['total_documents']
            overall_stats['indexed'] += stats['indexed']
            overall_stats['failed'] += stats['failed']
            overall_stats['skipped'] += stats['skipped']

        except Exception as e:
            logger.error(f"Failed to process {doc_type}: {e}")
            overall_stats['failed'] += 1

    # Print overall statistics if processing multiple types
    if len(doc_types) > 1:
        print("\n" + "=" * 60)
        print("OVERALL STATISTICS")
        print("=" * 60)
        print(f"Total Documents:     {overall_stats['total_documents']}")
        print(f"Successfully Indexed: {overall_stats['indexed']}")
        print(f"Failed:              {overall_stats['failed']}")
        print(f"Skipped:             {overall_stats['skipped']}")
        print("=" * 60 + "\n")

    # Print vector store statistics
    try:
        vector_store = get_vector_store()
        vstore_stats = vector_store.get_collection_stats()

        print("\n" + "=" * 60)
        print("VECTOR STORE STATUS")
        print("=" * 60)
        for doc_type, stats in vstore_stats.items():
            print(f"{doc_type.upper()}: {stats['chunk_count']} chunks ({stats['status']})")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Failed to get vector store stats: {e}")

    logger.info("Reindexing complete!")


if __name__ == '__main__':
    main()
