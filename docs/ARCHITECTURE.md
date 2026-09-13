# Architecture

## Runtime sequence

```text
Query
  -> ModelAdapter.classify
  -> IntentDefinition
  -> CapabilityDefinition
  -> ToolAdapter.call (read-only Functions)
  -> KnowledgeAdapter.search (object-scoped evidence)
  -> deterministic risk and action policy
  -> ModelAdapter.compose
  -> user confirmation
  -> human review when L4
  -> ToolAdapter.execute_action
  -> AuditRecord for every stage
```

## Important boundaries

- Intent predicts the entry point; it does not contain business workflow code.
- Capability defines a stable contract composed of objects, Functions, knowledge, rules and Actions.
- Function is read-only. Action mutates state and therefore carries permission, confirmation, precondition, idempotency and compensation semantics.
- Runtime holds per-request instances and evidence. The ontology catalog stores schemas and policy; it does not duplicate every source-system row.
- Adapters isolate external services. Replace them individually without changing chat, review or configuration clients.

## Production replacement order

1. Replace `MemoryStore` with PostgreSQL and Redis.
2. Add enterprise OIDC/SSO, RBAC/ABAC and tenant isolation.
3. Replace `MockToolAdapter` reads with source-system connectors.
4. Replace write Actions one at a time behind idempotent gateways.
5. Replace `MockKnowledgeAdapter` with versioned hybrid retrieval.
6. Replace `MockModelAdapter` with the selected intent model and LLM gateway.
7. Move orchestration into LangGraph while preserving the runtime state contract.
8. Add queues, tracing, evaluation, alerting, secret management and disaster recovery.

