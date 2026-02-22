# Project Type: REST API

Guidance for documenting REST API backends.

## Key Files to Read First

1. Entry point (`app.py`, `server.ts`, `main.go`, etc.)
2. Router/routes files — reveal the full API surface
3. Middleware files — reveal cross-cutting concerns (auth, logging, rate limiting)
4. Schema/model files — reveal the data model
5. `.env.example` — reveals required configuration
6. OpenAPI/Swagger spec if present

## Type-Specific Section: API Reference

Replace the `[Type-Specific Section(s)]` placeholder in the report with:

```markdown
## API Reference

### Endpoints

| Method | Path | Auth | Handler | Purpose |
|--------|------|------|---------|---------|
| GET | `/[path]` | [yes/no/type] | `[file:function]` | [what it returns] |
| POST | `/[path]` | [yes/no/type] | `[file:function]` | [what it creates/does] |

### Middleware Stack

[List middleware in execution order with what each does]

1. `[middleware]` — [purpose]
2. `[middleware]` — [purpose]

### Authentication

[How auth works — JWT, sessions, API keys, OAuth, etc. Where tokens are validated.]

### Data Models

| Model | File | Fields | Purpose |
|-------|------|--------|---------|
| [Name] | `[path]` | [key fields] | [what it represents] |
```

## What to Look For

**In route/router files:**
- HTTP method + path = the API contract
- Middleware applied per-route = reveals auth/validation requirements
- Handler function names = reveals intent (`createUser`, `updateOrderStatus`)

**In controller/handler files:**
- Input validation logic = reveals expected request shape
- Database calls = reveals what data is read/written
- External API calls = reveals third-party dependencies
- Error responses = reveals failure modes

**In middleware:**
- Auth middleware = how users are identified and authorized
- Rate limiting = what limits exist and why
- Logging = what is instrumented

**In models/schemas:**
- Field names and types = the data model
- Validators = business rules encoded in data
- Relationships = how entities connect

## Inferring "Why"

- Route grouping (e.g., `/admin/*`, `/v1/*`, `/internal/*`) reveals audience segmentation
- Versioned routes (`/v1/`, `/v2/`) signal a breaking change history
- `deprecated` flags or comments on routes = API evolution decisions
- Custom middleware = something the framework didn't handle out of the box
- Retry logic on external calls = known unreliable dependency
