from typing import Protocol

from app.schemas.ai import Intent, IntentClassification, InvestigationRequest


class SemanticIntentClassifier(Protocol):
    def classify(self, request: InvestigationRequest) -> IntentClassification:
        """Classify ambiguous natural-language requests."""


class KeywordIntentClassifier:
    """High-precision baseline classifier for obvious requests."""

    def classify(self, request: InvestigationRequest) -> IntentClassification:
        question = request.question.casefold()

        if any(term in question for term in ("create task", "follow up", "follow-up")):
            intent = Intent.CREATE_FOLLOW_UP
        elif any(
            term in question for term in ("recommend", "what should", "next action", "suggest")
        ):
            intent = Intent.RECOMMEND_NEXT_ACTION
        elif any(
            term in question for term in ("policy", "rule", "allowed", "jurisdiction", "compliance")
        ):
            intent = Intent.POLICY_QUESTION
        elif any(
            term in question for term in ("interaction", "history", "contacted", "conversation")
        ):
            intent = Intent.INTERACTION_SUMMARY
        elif any(term in question for term in ("account", "profile", "details", "status")):
            intent = Intent.ACCOUNT_LOOKUP
        else:
            intent = Intent.UNSUPPORTED

        return IntentClassification(
            intent=intent,
            confidence=0.98 if intent is not Intent.UNSUPPORTED else 0.0,
            source="keyword",
        )


class HybridIntentClassifier:
    """Combines safety rules, exact rules, and an injectable semantic fallback."""

    _minimum_confidence = 0.85

    def __init__(self, semantic_classifier: SemanticIntentClassifier | None = None) -> None:
        self._keyword_classifier = KeywordIntentClassifier()
        self._semantic_classifier = semantic_classifier

    def classify(self, request: InvestigationRequest) -> IntentClassification:
        safety_result = self._classify_side_effect(request.question)
        if safety_result is not None:
            return safety_result

        keyword_result = self._keyword_classifier.classify(request)
        if keyword_result.intent is not Intent.UNSUPPORTED:
            return keyword_result

        if self._semantic_classifier is None:
            return keyword_result

        semantic_result = self._semantic_classifier.classify(request)
        if semantic_result.confidence >= self._minimum_confidence:
            return semantic_result

        return IntentClassification(
            intent=Intent.UNSUPPORTED,
            confidence=semantic_result.confidence,
            source="low_confidence_fallback",
        )

    @staticmethod
    def _classify_side_effect(question: str) -> IntentClassification | None:
        normalized = question.casefold()
        if any(
            term in normalized
            for term in (
                "create task",
                "follow up",
                "follow-up",
                "send email",
                "send an email",
                "update account",
            )
        ):
            return IntentClassification(
                intent=Intent.CREATE_FOLLOW_UP,
                confidence=1.0,
                source="safety_rule",
            )
        return None
