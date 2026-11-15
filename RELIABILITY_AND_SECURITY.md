# Reliability and Security

## Failure handling

- Model timeout: bounded retry, then return a visible failure.
- Invalid structured output: reject, optionally retry once, never silently coerce.
- Invalid tool arguments: do not execute; return validation error to the model.
- Tool failure: return structured `ToolResult` and apply per-tool retry policy.
- Rate limit: bounded backoff and user-visible retryable error.
- Infinite loop: maximum tool calls and duplicate-call detection.
- Crash during side effect: use idempotency key and persisted state.

## Security controls

- Authenticate and authorize every resource access.
- Treat uploaded documents as untrusted content.
- Separate system instructions from retrieved document text.
- Never allow retrieved text to redefine tool permissions.
- Require approval for all side-effect tools.
- Redact secrets and sensitive values from logs.
- Keep provider keys in environment variables, never source control.
