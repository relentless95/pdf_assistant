"""Isolate tests from one another and from the real document database."""

import pytest

from backend import storage


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    """Use a fresh SQLite file per test; pytest restores the path afterward."""
    # tmp_path is a pytest-managed temporary folder, not the project's data folder.
    monkeypatch.setattr(storage, "DATABASE_PATH", tmp_path / "documents.db")
    storage.initialize_database()
    yield
