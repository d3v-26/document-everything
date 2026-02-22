# Project Type: REST API

Standard: **OpenAPI Specification 3.1** — the industry standard maintained by the OpenAPI Initiative.

Reference: https://spec.openapis.org/oas/v3.1.0.html

---

## Type-Specific Section: API Reference

Replace `[Type-Specific Section(s)]` in the report with:

```markdown
## API Reference

### Servers

| Environment | Base URL |
|-------------|---------|
| Production | `https://api.example.com/v1` |
| Staging | `https://staging-api.example.com/v1` |

### Authentication

[How auth works — JWT Bearer, API Key, OAuth 2.0, sessions. Where tokens are validated, how to obtain credentials.]

### Endpoints

| Method | Path | Auth | Handler | Purpose |
|--------|------|------|---------|---------|
| `GET` | `/resource` | Bearer | `handlers/resource.get` | Returns paginated list |
| `POST` | `/resource` | Bearer | `handlers/resource.create` | Creates new resource |
| `GET` | `/resource/:id` | Bearer | `handlers/resource.getById` | Returns single item |
| `PUT` | `/resource/:id` | Bearer | `handlers/resource.update` | Full update |
| `DELETE` | `/resource/:id` | Bearer | `handlers/resource.delete` | Soft-deletes |

### Request / Response Schemas

[Key data models — fields, types, required/optional, constraints]

| Model | Used In | Key Fields |
|-------|---------|-----------|
| `[ModelName]` | POST/PUT body | `id` (uuid), `name` (string, required), `createdAt` (ISO 8601) |

### Error Responses

| Status | Code | Meaning |
|--------|------|---------|
| 400 | `VALIDATION_ERROR` | Request body failed schema validation |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Valid token but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

### Middleware Stack

[In execution order]

1. `[middleware]` — [purpose, e.g. request logging]
2. `[middleware]` — [e.g. JWT validation]
3. `[middleware]` — [e.g. rate limiting]
```

---

## OpenAPI 3.1 Structure to Document

When an `openapi.yaml` or `swagger.yaml` exists, use it as the authoritative source and document:

- **`info`**: title, version, description, contact, license
- **`servers`**: base URLs per environment
- **`paths`**: each operation with summary, description, parameters, requestBody, responses
- **`components/schemas`**: all reusable data models
- **`components/securitySchemes`**: auth mechanisms defined
- **`tags`**: logical groupings of endpoints

If no OpenAPI spec exists, generate documentation from the route/controller code and note that a spec should be created.

---

## What to Look For

**In router/route files:**
- HTTP method + path = the API contract; document all combinations
- Middleware applied per-route = auth/validation requirements
- Handler function names reveal intent (`createUser`, `updateOrderStatus`)
- Versioned paths (`/v1/`, `/v2/`) = API evolution history

**In controller/handler files:**
- Input validation logic → expected request shape
- Database calls → what data is read/written
- External API calls → third-party dependencies
- Error responses → failure modes; document them all

**In middleware:**
- Auth middleware → how users are identified and authorized
- Rate limiting middleware → limits (document requests-per-minute)
- CORS config → which origins are allowed

**In model/schema files:**
- Fields and types → data model
- Validators → business rules encoded in data
- Required vs optional fields → API contract

## Inferring "Why"

- Route grouping (`/admin/*`, `/v2/*`, `/internal/*`) → audience segmentation
- `deprecated: true` on routes → API evolution; document what replaced it
- Custom middleware → something the framework didn't handle by default
- Retry logic on external calls → known unreliable upstream dependency
- `idempotencyKey` field → distributed system concern, safe retries
- `softDelete` pattern → regulatory / audit trail requirement
