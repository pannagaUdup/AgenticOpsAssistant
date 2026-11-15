# API Contracts

## Create investigation

`POST /api/v1/investigations`

```json
{
  "account_id": "acct_001",
  "question": "What should we do next about the billing issue?",
  "include_policy": true,
  "requested_action": null
}
```

The response contains `investigation_id`, status, recommendation, evidence references, and approval information when applicable.

## Approval

`POST /api/v1/approvals/{approval_id}`

```json
{
  "status": "approved",
  "decided_by": "user_001",
  "comment": "Reviewed and approved."
}
```

## Error classes

- `400`: invalid request or tool arguments.
- `401`: unauthenticated.
- `403`: unauthorized tool or resource access.
- `404`: account, investigation, or approval not found.
- `409`: duplicate or invalid state transition.
- `422`: schema validation failure.
- `502`: invalid upstream/model response.
- `503`: unavailable dependency.
- `504`: dependency timeout.
