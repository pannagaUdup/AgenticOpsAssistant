# System Architecture

```mermaid
flowchart TB
    User --> API[FastAPI API]
    API --> Service[Investigation Service]
    Service --> Router[Deterministic Router]
    Router --> Prompts[Versioned Prompt Registry]
    Service --> LLM[LLM Provider Adapter]
    Service --> Tools[Validated Tool Registry]
    Tools --> PostgreSQL[(PostgreSQL)]
    Tools --> Retriever[Policy Retriever]
    Retriever --> VectorStore[(Vector Store)]
    Documents[Policy Documents] --> Ingestion[Ingestion Pipeline]
    Ingestion --> VectorStore
    Service --> Approval[Approval Service]
    Approval --> PostgreSQL
```

Initial implementation uses one general reasoning model, one embedding model, deterministic routing, PostgreSQL, and a fake provider for tests. Redis, background workers, and multi-agent orchestration are deferred until the workflow baseline is measured.
