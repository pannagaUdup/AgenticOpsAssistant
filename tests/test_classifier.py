from app.schemas.ai import Intent, IntentClassification, InvestigationRequest
from app.services.classifier import HybridIntentClassifier
from app.services.router import RequestRouter


def make_request(question: str) -> InvestigationRequest:
    return InvestigationRequest(account_id="acct_001", question=question)


class StubSemanticClassifier:
    def __init__(self, result: IntentClassification) -> None:
        self.result = result

    def classify(self, request: InvestigationRequest) -> IntentClassification:
        del request
        return self.result


def test_hybrid_classifier_uses_semantic_fallback_for_synonym() -> None:
    classifier = HybridIntentClassifier(
        StubSemanticClassifier(
            IntentClassification(
                intent=Intent.INTERACTION_SUMMARY,
                confidence=0.94,
                source="semantic_stub",
            )
        )
    )

    result = classifier.classify(make_request("Tell me what happened with this customer recently"))

    assert result.intent is Intent.INTERACTION_SUMMARY
    assert result.source == "semantic_stub"


def test_hybrid_classifier_uses_safety_rule_for_side_effect() -> None:
    classifier = HybridIntentClassifier(
        StubSemanticClassifier(
            IntentClassification(
                intent=Intent.ACCOUNT_LOOKUP,
                confidence=0.99,
                source="semantic_stub",
            )
        )
    )

    result = classifier.classify(make_request("Please send an email to the customer"))

    assert result.intent is Intent.CREATE_FOLLOW_UP
    assert result.source == "safety_rule"


def test_hybrid_classifier_rejects_low_confidence_semantic_result() -> None:
    classifier = HybridIntentClassifier(
        StubSemanticClassifier(
            IntentClassification(
                intent=Intent.POLICY_QUESTION,
                confidence=0.60,
                source="semantic_stub",
            )
        )
    )

    result = classifier.classify(make_request("Could you look into this for me?"))

    assert result.intent is Intent.UNSUPPORTED
    assert result.source == "low_confidence_fallback"


def test_router_uses_hybrid_classifier() -> None:
    router = RequestRouter(
        StubSemanticClassifier(
            IntentClassification(
                intent=Intent.ACCOUNT_LOOKUP,
                confidence=0.91,
                source="semantic_stub",
            )
        )
    )

    decision = router.route(make_request("Who is this customer?"))

    assert decision.intent is Intent.ACCOUNT_LOOKUP
