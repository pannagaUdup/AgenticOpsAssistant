import re
from dataclasses import dataclass
from pathlib import Path


class PromptNotFoundError(FileNotFoundError):
    """Raised when a requested prompt name and version do not exist."""


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    name: str
    version: str
    content: str


class PromptRegistry:
    """Loads immutable, versioned prompt files from the repository prompt directory."""

    _name_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    _version_pattern = re.compile(r"^v[0-9]+$")

    def __init__(self, root: Path | str = "prompts") -> None:
        self._root = Path(root)

    def load(self, name: str, version: str) -> PromptTemplate:
        self._validate_identifier(name, self._name_pattern, "prompt name")
        self._validate_identifier(version, self._version_pattern, "prompt version")

        path = self._root / f"{name}_{version}.md"
        if not path.is_file():
            raise PromptNotFoundError(
                f"Prompt '{name}' version '{version}' was not found at {path}"
            )

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise PromptNotFoundError(f"Prompt '{name}' version '{version}' is empty")

        return PromptTemplate(name=name, version=version, content=content)

    @staticmethod
    def _validate_identifier(value: str, pattern: re.Pattern[str], label: str) -> None:
        if not pattern.fullmatch(value):
            raise ValueError(f"Invalid {label}: {value!r}")
