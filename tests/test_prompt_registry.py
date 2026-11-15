from pathlib import Path

import pytest

from app.prompts.registry import PromptNotFoundError, PromptRegistry


def test_registry_loads_versioned_recommendation_prompt() -> None:
    prompt = PromptRegistry().load("recommendation_system", "v1")

    assert prompt.name == "recommendation_system"
    assert prompt.version == "v1"
    assert "evidence_sufficient" in prompt.content


def test_registry_rejects_missing_prompt(tmp_path: Path) -> None:
    with pytest.raises(PromptNotFoundError):
        PromptRegistry(tmp_path).load("recommendation_system", "v1")


def test_registry_rejects_invalid_identifiers() -> None:
    registry = PromptRegistry()

    with pytest.raises(ValueError, match="prompt name"):
        registry.load("Recommendation System", "v1")

    with pytest.raises(ValueError, match="prompt version"):
        registry.load("recommendation_system", "1")


def test_registry_rejects_empty_prompt(tmp_path: Path) -> None:
    (tmp_path / "empty_v1.md").write_text("  \n", encoding="utf-8")

    with pytest.raises(PromptNotFoundError, match="empty"):
        PromptRegistry(tmp_path).load("empty", "v1")
