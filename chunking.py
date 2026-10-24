

def chunk_text(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> list[str]:
    """Return nonblank text slices, with sizes measured in characters.

    Defaults: up to 1,000 characters per slice, with 200 characters of overlap
    before stripping edge whitespace. Overlap repeats boundary context between
    neighboring slices. Return an empty list for empty or whitespace-only text.
    Raise ValueError for a nonpositive size or overlap outside [0, chunk_size).
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    # Chained comparison: overlap must be >= 0 AND < chunk_size.
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be non-negative and less than chunk_size")

    chunks = []
    step = chunk_size - chunk_overlap

    # With the defaults, starting positions are 0, 800, 1600, and so on.
    for start in range(0, len(text), step):
        # Slicing includes start and excludes the end; strip removes edge whitespace.
        chunk = text[start : start + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

        # Once a slice reaches the end, avoid another slice of only repeated text.
        if start + chunk_size >= len(text):
            break

    return chunks
