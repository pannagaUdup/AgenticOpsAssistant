# Functional Requirements

1. The system accepts an account ID and natural-language investigation question.
2. The router identifies the intent and allowed tools.
3. Tool arguments are validated before execution.
4. Account and interaction tools read PostgreSQL data.
5. Policy search returns traceable evidence references.
6. The model returns a validated recommendation schema.
7. Insufficient evidence is represented explicitly.
8. Recommendations may propose a task but cannot execute it.
9. Task creation requires explicit human approval.
10. Tool calls are bounded, logged, and safe to retry.
