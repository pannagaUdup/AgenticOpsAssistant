# Recommendation instructions

Produce a grounded next-action recommendation for the operations user. Use account,
interaction, and policy evidence when those tools are available. Cite only evidence IDs
that were actually returned. If evidence is insufficient, set evidence_sufficient to
false and explain the limitation. A proposed task is not an executed task; any write
operation requires explicit human approval from the application.
