"""Shared setup and cleanup automatically discovered by pytest."""

import pytest

from main import documents


@pytest.fixture(autouse=True)
def clear_document_storage():
    """Give each test empty storage and remove its uploads afterward."""
    documents.clear()
    yield  # Pytest runs the test here, then resumes cleanup below.
    documents.clear()
