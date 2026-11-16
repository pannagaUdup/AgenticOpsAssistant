from app.api.dependencies import get_llm_provider
from app.main import app


def test_investigation_route_can_be_reached() -> None:
    # The route wiring is tested separately from database-backed execution.
    # The dependency override prevents an external model call in this smoke test.
    app.dependency_overrides[get_llm_provider] = lambda: None  # type: ignore[assignment]
    try:
        assert "/api/v1/investigations" in app.openapi()["paths"]
    finally:
        app.dependency_overrides.clear()
