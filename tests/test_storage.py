"""Verify saved data is available to a new Python process, not just memory."""

from pathlib import Path
import subprocess
import sys

from backend import storage


def test_document_survives_a_new_process():
    """Read committed pages and searchable chunks from a fresh interpreter."""
    storage.save_document(
        "persistent-id",
        "sample.pdf",
        [{"page_number": 1, "content": "Batteries store energy."}],
        [{"chunk_id": "chunk-1", "page_number": 1, "content": "Batteries store energy."}]
    )

    # The child has no access to this process's Python objects, only the DB file.
    code = """
import sys
from pathlib import Path
from backend import storage
from backend.retrieval import search_chunks
storage.DATABASE_PATH = Path(sys.argv[1])
document = storage.load_document('persistent-id')
assert document['filename'] == 'sample.pdf'
assert document['pages'][0]['content'] == 'Batteries store energy.'
assert search_chunks(document['chunks'], 'battery energy')[0]['chunk_id'] == 'chunk-1'
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(storage.DATABASE_PATH)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, result.stdout + result.stderr
