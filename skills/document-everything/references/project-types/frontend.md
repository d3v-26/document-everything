# Project Type: Frontend Application

Guidance for documenting frontend web applications (React, Vue, Svelte, Next.js, etc.).

## Key Files to Read First

1. Entry point (`index.html`, `main.ts`, `_app.tsx`, `app.vue`)
2. Router config — reveals page/route structure
3. State management store files (Redux, Pinia, Zustand, etc.)
4. `package.json` — reveals framework and key libraries
5. Build config (`vite.config.ts`, `next.config.js`, etc.)
6. `.env.example` — reveals required API endpoints and feature flags

## Type-Specific Section: UI Structure

Replace the `[Type-Specific Section(s)]` placeholder in the report with:

```markdown
## UI Structure

### Pages / Routes

| Route | Component | Auth Required | Purpose |
|-------|-----------|--------------|---------|
| `/[path]` | `[file]` | [yes/no] | [what the user does here] |

### Component Hierarchy

[Top-level layout and key shared components]

```
Layout
├── Header (navigation, auth state)
├── [Page components]
│   └── [Feature components]
└── Footer
```

### State Management

| Store / Context | File | What it manages |
|----------------|------|----------------|
| [name] | `[path]` | [what state lives here] |

### API Integration

| Service / Hook | File | Endpoints consumed |
|---------------|------|--------------------|
| [name] | `[path]` | `[METHOD /path]` |
```

## What to Look For

**In page/route components:**
- What data is fetched on load (`useEffect`, `getServerSideProps`, `loader`)
- What user interactions are handled
- What sub-components are composed

**In shared components:**
- Props interface = the component's contract
- Internal state = what the component manages independently
- Context consumption = what global state it depends on

**In state stores:**
- State shape = what data lives globally
- Actions/mutations = what can change and how
- Selectors = what derived data is computed

**In API service files:**
- Base URL patterns = which backends are called
- Auth headers = how requests are authenticated
- Error handling = how failures surface to users

## Inferring "Why"

- Component naming (`Legacy`, `V2`, `Redesigned`) = evolution history
- Feature flag checks = what is in gradual rollout
- `// TODO: move to server component` (Next.js) = performance optimization in progress
- Duplicated components in different directories = multi-team ownership or A/B testing
- Custom hooks wrapping native APIs = abstraction over browser inconsistencies
