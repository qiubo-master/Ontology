# HTTP API

All payloads are JSON. The demo server listens on `127.0.0.1:8000`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Service and adapter mode |
| GET | `/api/catalog` | Intents, capabilities, objects, relations and rules |
| POST | `/api/intent/preview` | Debounced intent preview while the user is typing |
| POST | `/api/chat` | Execute one ontology runtime turn |
| POST | `/api/actions/{id}/confirm` | Confirm a proposed Action |
| GET | `/api/reviews` | Human-review queue |
| POST | `/api/reviews/{id}/decision` | Approve or reject a review |
| GET | `/api/audits` | Audit event stream |
| GET | `/api/metrics` | Demo operating metrics |
| GET | `/api/sessions/{id}` | Session replay payload |
| POST | `/api/config/publish` | Publish a demo config version |

## Chat example

```json
{
  "session_id": "demo-001",
  "user_id": "C1001",
  "message": "取消预约 AP20260001"
}
```

The response contains `trace_id`, intent prediction, capability, object references, Function results, evidence, risk and an optional Action proposal. Clients must not execute write operations directly; they confirm the returned `action.id` through the Action endpoint.
