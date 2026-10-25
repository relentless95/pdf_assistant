"""Check answer validation and provider failures without real API requests."""

import json
from types import SimpleNamespace

import httpx
import pytest
from pydantic import SecretStr

import answering


@pytest.fixture
def passages():
    return [{
        "chunk_id": "battery-chunk",
        "page_number": 2,
        "content": "Batteries store energy for later use."
    }]


@pytest.fixture
def fake_provider(monkeypatch):
    """Replace settings and route HTTP requests through an in-memory handler."""
    settings = SimpleNamespace(
        openrouter_api_key=SecretStr("test-key"),
        openrouter_model="test-model"
    )
    monkeypatch.setattr(answering, "get_settings", lambda: settings)
    original_client = httpx.Client

    def install(handler):
        monkeypatch.setattr(
            answering.httpx,
            "Client",
            lambda **kwargs: original_client(
                transport=httpx.MockTransport(handler), **kwargs
            )
        )

    return install


def provider_response(answer, source_ids, insufficient_evidence):
    return httpx.Response(200, json={"choices": [{
        "finish_reason": "stop",
        "message": {"content": json.dumps({
            "answer": answer,
            "source_ids": source_ids,
            "insufficient_evidence": insufficient_evidence
        })}
    }]})


def test_answer_uses_supplied_source(fake_provider, passages):
    def handler(request):
        body = json.loads(request.content)
        evidence = json.loads(body["messages"][1]["content"])
        assert evidence["question"] == "How is energy stored?"
        assert evidence["excerpts"][0]["source_id"] == "battery-chunk"
        return provider_response(
            "Batteries store energy for later use.", ["battery-chunk"], False
        )

    fake_provider(handler)
    result = answering.generate_answer("How is energy stored?", passages)
    assert result["insufficient_evidence"] is False
    assert result["sources"] == [{
        "chunk_id": "battery-chunk",
        "page_number": 2,
        "content": passages[0]["content"]
    }]


def test_unsupported_question_returns_no_sources(fake_provider, passages):
    fake_provider(lambda request: provider_response(
        "The excerpts do not explain bicycle brakes.", [], True
    ))
    result = answering.generate_answer("How do bicycle brakes work?", passages)
    assert result["insufficient_evidence"] is True
    assert result["sources"] == []


def test_invented_source_is_rejected(fake_provider, passages):
    fake_provider(lambda request: provider_response(
        "Batteries store energy.", ["invented-chunk"], False
    ))
    with pytest.raises(answering.AnsweringError):
        answering.generate_answer("How is energy stored?", passages)


def test_timeout_is_handled(fake_provider, passages):
    def handler(request):
        raise httpx.ReadTimeout("Simulated timeout", request=request)

    fake_provider(handler)
    with pytest.raises(answering.AnsweringError, match="timed out"):
        answering.generate_answer("How is energy stored?", passages)


def test_provider_rejection_is_handled(fake_provider, passages):
    fake_provider(lambda request: httpx.Response(
        429, json={"error": {"message": "Rate limit exceeded"}}
    ))
    with pytest.raises(answering.AnsweringError, match="rejected"):
        answering.generate_answer("How is energy stored?", passages)


def test_invalid_answer_is_rejected(fake_provider, passages):
    fake_provider(lambda request: httpx.Response(200, json={"choices": [{
        "finish_reason": "stop",
        "message": {"content": "Not valid JSON"}
    }]}))
    with pytest.raises(answering.AnsweringError, match="invalid answer"):
        answering.generate_answer("How is energy stored?", passages)
