"""Persist document metadata, extracted pages, and chunks in a local SQLite file.

Initialize tables by running this module directly before starting the API.
Original PDF bytes are not stored. Each operation closes its own connection.
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "data" / "documents.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection with named rows and foreign-key enforcement enabled."""
    DATABASE_PATH.parent.mkdir(
        parents=True, exist_ok=True
    )  # Ensure the directory exists

    connection = sqlite3.connect(DATABASE_PATH)
    # Required on every connection for relationship checks and cascading deletion.
    connection.execute("PRAGMA foreign_keys = ON")

    connection.row_factory = sqlite3.Row  # Enable named column access

    return connection


def initialize_database() -> None:
    """Create all three related tables if absent; preserve existing data."""

    connection = get_connection()

    try:
        with connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pages (
                    document_id TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    PRIMARY KEY (document_id, page_number),
                    FOREIGN KEY (document_id)   
                        REFERENCES documents(id) 
                        ON DELETE CASCADE
                );


                CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (document_id, page_number) 
                    REFERENCES pages(document_id, page_number) 
                    ON DELETE CASCADE
                );
                """)

    finally:
        connection.close()


def save_document(document_id: str, filename: str, pages: list[dict], chunks: list[dict]) -> None:
    """Insert document, pages, and chunks atomically; roll back if an insert fails."""
    connection = get_connection()

    try:
        with connection:
            # Insert parents first; ? placeholders safely bind the supplied values.
            connection.execute(
                "INSERT INTO documents (id, filename) VALUES (?, ?)",
                (document_id, filename),
            )

            # Each tuple supplies values for one page; executemany repeats the insert.
            connection.executemany(
                "INSERT INTO pages (document_id, page_number, content) VALUES (?, ?, ?)",
                [(document_id, page["page_number"], page["content"]) for page in pages],
            )

            # Insert the chunks
            connection.executemany(
                "INSERT INTO chunks (id, document_id, page_number, content) VALUES (?, ?, ?, ?)",
                [
                    (chunk["chunk_id"], document_id, chunk["page_number"], chunk["content"])
                    for chunk in chunks
                ],
            )



    finally:
        connection.close()

def list_documents() -> list[dict]:
    """Return the ID and filename of every saved document."""
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT id, filename FROM documents ORDER BY id"
        ).fetchall()

        return [
            {
                "document_id": row["id"],
                "filename": row["filename"]
            }
            for row in rows
        ]
    finally:
        connection.close()


def load_document(document_id: str) -> dict | None:
    """Rebuild a document dictionary from saved rows, or return None if unknown."""
    connection = get_connection()

    try:
        document = connection.execute(
            "SELECT id, filename FROM documents WHERE id = ?",
            (document_id,)
        ).fetchone()

        if document is None:
            return None

        pages = connection.execute(
            """
            SELECT page_number, content
            FROM pages
            WHERE document_id = ?
            ORDER BY page_number
            """,
            (document_id,)
        ).fetchall()

        chunks = connection.execute(
            """
            SELECT id AS chunk_id, document_id, page_number, content
            FROM chunks
            WHERE document_id = ?
            ORDER BY page_number, rowid
            """,
            (document_id,)
        ).fetchall()

        # Convert named SQLite rows into ordinary dictionaries for the API.
        return {
            "document_id": document["id"],
            "filename": document["filename"],
            "pages": [dict(page) for page in pages],
            "chunks": [dict(chunk) for chunk in chunks]
        }
    finally:
        connection.close()


def delete_document(document_id: str) -> bool:
    """Delete a document; cascades remove pages/chunks. Return False if unknown."""
    connection = get_connection()

    try:
        with connection:
            cursor = connection.execute(
                "DELETE FROM documents WHERE id = ?",
                (document_id,)
            )

        return cursor.rowcount > 0
    finally:
        connection.close()

if __name__ == "__main__":
    initialize_database()
