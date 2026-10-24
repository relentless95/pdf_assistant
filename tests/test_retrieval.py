from retrieval import search_chunks


def test_search_chunks_ranks_relevant_passages_first():
    """Rank multiple matches by relevance, preserving their source metadata."""
    # Put the strongest match last so the test requires actual reordering.
    chunks = [
        {
            "chunk_id": "solar",
            "page_number": 1,
            "content": "Solar energy comes from sunlight and solar panels."
        },
        {
            "chunk_id": "football",
            "page_number": 2,
            "content": "Football players score goals on a pitch."
        },
        {
            "chunk_id": "battery",
            "page_number": 3,
            "content": "Battery storage stores energy for later use."
        }
    ]

    results = search_chunks(chunks, "battery storage energy", top_k=2)

    assert [result["chunk_id"] for result in results] == ["battery", "solar"]
    assert results[0]["page_number"] == 3
    assert results[0]["content"] == chunks[2]["content"]
    assert results[0]["score"] > results[1]["score"] > 0
