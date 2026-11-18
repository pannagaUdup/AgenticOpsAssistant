from app.llm.provider import LLMProvider
from app.prompts import PromptRegistry
from app.schemas.ai import IntentClassification, InvestigationRequest


class LLMIntentClassifier:
    """Uses the configured model only for requests the keyword rules cannot classify."""

    def __init__(
        self, provider: LLMProvider, prompt_registry: PromptRegistry | None = None
    ) -> None:
        self._provider = provider
        self._prompt_registry = prompt_registry or PromptRegistry()

    async def classify(self, request: InvestigationRequest) -> IntentClassification:
        prompt = self._prompt_registry.load("classification_system", "v1")
        return await self._provider.generate_structured(
            system_prompt=prompt.content,
            user_prompt=request.question,
            response_model=IntentClassification,
            tools=[],
        )
