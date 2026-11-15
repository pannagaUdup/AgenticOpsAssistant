# Agent Workflow

```mermaid
stateDiagram-v2
    [*] --> Received
    Received --> Routed
    Routed --> Investigating
    Investigating --> ToolCall
    ToolCall --> Investigating: tool result
    ToolCall --> Recovery: timeout or failure
    Recovery --> ToolCall: bounded retry
    Recovery --> Failed: retry limit reached
    Investigating --> RecommendationReady: model returns final output
    RecommendationReady --> ApprovalPending: side effect proposed
    RecommendationReady --> Completed: read-only answer
    ApprovalPending --> Executing: approved
    ApprovalPending --> Completed: rejected or expired
    Executing --> Completed: idempotent task creation
    Executing --> Recovery: execution failure
```

Rules:

- Maximum tool calls are defined by the routing decision.
- Duplicate tool calls are detected before execution.
- Only the application, not the model, can authorize a side effect.
- Every terminal state is observable and persisted where appropriate.
