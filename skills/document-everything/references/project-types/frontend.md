# Project Type: Frontend Application

Standard: **Component Story Format 3 (CSF3) + Storybook Autodocs** for component libraries; **Diataxis framework** for app-level documentation.

Reference: https://storybook.js.org/docs/writing-docs/autodocs

---

## Type-Specific Section: UI Structure

Replace `[Type-Specific Section(s)]` in the report with:

```markdown
## UI Structure

### Pages / Routes

| Route | Component | Auth Required | Purpose |
|-------|-----------|--------------|---------|
| `/` | `pages/Home` | No | Landing page / dashboard |
| `/[resource]` | `pages/[Resource]List` | Yes | Resource listing with filters |
| `/[resource]/:id` | `pages/[Resource]Detail` | Yes | Detail view |
| `/settings` | `pages/Settings` | Yes | User preferences |

### Component Hierarchy

[Top-level layout and composition]

```
Layout
├── Header (navigation, auth state, notifications)
├── Sidebar (if applicable)
├── Page Components
│   └── Feature Components
│       └── UI Primitives (Button, Input, etc.)
└── Footer
```

### State Management

| Store / Context | File | What it manages |
|----------------|------|----------------|
| `[AuthStore]` | `stores/auth` | Current user, session token, permissions |
| `[UIStore]` | `stores/ui` | Theme, sidebar open/close, modal state |

### API Integration

| Service / Hook | File | Endpoints consumed |
|---------------|------|--------------------|
| `use[Resource]` | `hooks/use[Resource]` | `GET /[resource]`, `POST /[resource]` |
```

---

## Diataxis Documentation Structure

For frontend apps, organize docs following the Diataxis framework — keep these four types strictly separate:

| Type | What to write | Example |
|------|--------------|---------|
| **Tutorial** | Step-by-step walkthrough for a new developer | "Set up the dev environment and add a new page" |
| **How-to Guide** | Recipe for a specific task | "How to add a new form field", "How to add a route" |
| **Reference** | Factual component API docs | Props table, event list, slot names |
| **Explanation** | Background and rationale | "Why we chose Zustand over Redux", "How auth flow works" |

---

## Storybook Component Documentation (if component library)

If the project includes a component library or design system, document components using Storybook CSF3 conventions:

For each component, document:
1. **Purpose** — what UI problem it solves
2. **Props / API** — name, type, required, default, description for each prop
3. **Variants** — what visual states exist (primary/secondary, sizes, disabled, loading)
4. **Usage guidance** — when to use vs alternatives
5. **Accessibility** — keyboard behavior, ARIA roles, focus management

---

## What to Look For

**In page/route components:**
- Data fetching patterns (`useEffect`, `getServerSideProps`, `loader`, `useQuery`) → what data drives each page
- User interaction handlers → what actions are available on each page
- Auth guards/route protection → which pages require authentication

**In shared components:**
- Props interface / TypeScript types → the component's contract
- Internal `useState` → what the component manages independently
- Context consumption → what global state it depends on
- Forwarded refs → designed for programmatic control by parents

**In state management:**
- State shape → what data lives globally vs locally
- Side effects (`useEffect`, actions, middleware) → what triggers state changes
- Selectors / derived state → computed values and their performance implications

**In API service files / hooks:**
- Base URL → which backends are called
- Auth headers → how requests are authenticated
- Cache/stale settings (React Query, SWR) → freshness strategy
- Optimistic updates → UX decisions that need documentation

## Inferring "Why"

- Component named `Legacy`, `V2`, `Redesigned` → evolution history; document what it replaced
- Feature flag checks → gradual rollout; document what the flag controls
- `// TODO: move to server component` (Next.js) → performance optimization planned
- Duplicated components in separate directories → A/B test or multi-team ownership
- Custom hooks wrapping native browser APIs → browser inconsistency workaround
- `memo()` / `useMemo` / `useCallback` on a component → known performance issue
