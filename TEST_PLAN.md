# Test Plan

## Unit tests

- Pydantic request, routing, tool, evidence, and recommendation schemas.
- Prompt selection and versioning.
- Tool argument validation.
- Approval state transitions.
- Idempotency-key behavior.

## Integration tests

- Account and interaction tools against PostgreSQL.
- Policy retrieval against a test corpus.
- Model provider adapter with mocked responses.
- API error mapping for dependency failures.

## Workflow tests

- Read-only account investigation.
- Policy-grounded recommendation with citations.
- Insufficient-evidence response.
- Malformed tool call.
- Duplicate tool call.
- Tool timeout and retry exhaustion.
- Approval approval, rejection, and expiration.
- Crash recovery before and after a side effect.

## Evaluation criteria

- Routing accuracy.
- Tool-call validity.
- Retrieval hit rate.
- Citation validity.
- Recommendation correctness.
- Latency and token cost.
- No unapproved side effects.
