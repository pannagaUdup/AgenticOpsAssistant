# Database Schema

## Existing entities

- `users`: authenticated users.
- `accounts`: synthetic customer accounts.
- `interactions`: account interaction history.
- `follow_up_tasks`: approved operational tasks.

## Planned AI entities

- `investigations`: request, routing decision, status, and final response.
- `tool_executions`: tool name, arguments, result status, duration, and errors.
- `evidence_references`: retrieved source IDs and citation metadata.
- `approvals`: pending, approved, rejected, or expired side-effect requests.

Every execution record must be associated with an investigation and account where applicable. Sensitive arguments and raw prompts must be redacted according to the security policy.
