---
title: "Appendix B: Constitution Templates"
---

# Appendix B: Constitution Templates

These templates are starting points for common project types. Each template should be reviewed and adjusted to match your project's actual requirements before use. Use `/devspark.constitution` to generate a personalized constitution, or paste these templates as a starting point and refine.

## Template 1: Web API (REST/HTTP)

```markdown
# [Project Name] Constitution

## I. Security (MANDATORY)

- No hardcoded secrets, credentials, API keys, or connection strings in source code (MUST)
  *Store all secrets in environment variables or a secrets manager*
- All user-supplied input MUST be validated and sanitized before processing
- SQL queries MUST use parameterized statements or an ORM that handles parameterization
  *Never concatenate user input into SQL strings*
- Authentication MUST use established libraries — no hand-rolled auth logic
- Error responses MUST NOT expose internal stack traces, database details, or file paths
- Rate limiting MUST be applied to authentication endpoints and write operations
- CORS configuration MUST explicitly list allowed origins — wildcard (*) prohibited on production

## II. Testing (MANDATORY)

- Tests MUST be written before implementation (Red-Green-Refactor)
- Unit test coverage MUST meet or exceed 80%
- Integration tests MUST NOT mock the database — use a test database instance
- All public API endpoints MUST have integration tests covering:
  - Happy path (valid input → expected response)
  - Validation failure (invalid input → 400)
  - Authentication failure (unauthenticated → 401)
  - Authorization failure (authenticated but unauthorized → 403)

## III. Architecture

- HTTP handlers MUST NOT contain business logic
  *Business logic belongs in service classes or domain functions*
- Services MUST NOT access the database directly
  *Data access belongs in repository classes or data access layers*
- Dependencies MUST be injected, not created inside functions or classes
- All database schema changes MUST be versioned migrations
  *Never modify production schemas without a reversible migration*
- Migrations MUST be reversible (every up() MUST have a down())

## IV. Code Quality

- Functions MUST NOT exceed 50 lines (excluding comments and blank lines)
- Files MUST NOT exceed 500 lines
- All public endpoints MUST be documented (OpenAPI/Swagger spec MUST be current)
- No `console.log`, `print()`, or debug output in production code (MUST NOT)
- No `// TODO` or `# TODO` comments in merged code (SHOULD NOT)
  *Open tasks belong in the issue tracker*

## V. Documentation

- Every significant architectural decision MUST be recorded as an ADR in `.documentation/decisions/`
- CHANGELOG MUST be updated in every release PR
- New external dependencies MUST be documented with their purpose

## Governance

- This constitution supersedes all other guidance
- Amendments require team review via PR (at least two reviewers for MANDATORY sections)
- Violations of MUST requirements are CRITICAL findings in PR review
- **Version**: 1.0.0 | **Ratified**: [date]
```

---

## Template 2: React / Frontend Application

```markdown
# [Project Name] Constitution

## I. Security

- No API keys or secrets in client-side code (MUST NOT)
  *All sensitive data MUST go through a backend proxy*
- All user input MUST be sanitized before rendering to prevent XSS
- MUST NOT use `dangerouslySetInnerHTML` without documented security review
- All external URLs in links MUST use `rel="noopener noreferrer"` for target="_blank"
- Content Security Policy headers MUST be configured in production

## II. Performance

- Lighthouse performance score MUST be ≥ 90 on desktop, ≥ 75 on mobile
- Initial bundle size MUST NOT exceed 250KB gzipped
- All images MUST have `width` and `height` attributes or use lazy loading
- Web Vitals targets: LCP < 2.5s, FID < 100ms, CLS < 0.1

## III. Accessibility (MANDATORY)

- All interactive elements MUST be keyboard accessible
- All images MUST have descriptive `alt` text (not empty for decorative images)
- Color contrast MUST meet WCAG 2.1 AA minimum (4.5:1 for normal text)
- Forms MUST have properly associated labels for all inputs
- Focus management MUST be handled correctly for modals and route changes
- ARIA attributes MUST be used correctly — incorrect ARIA is worse than no ARIA

## IV. Testing

- Unit tests required for all utility functions and custom hooks
- Component tests MUST cover render, user interaction, and error states
- No production code commits without corresponding test updates
- Snapshot tests MUST be reviewed when they change — do not auto-accept snapshots

## V. Code Quality

- Components MUST be functional components with TypeScript
- Props MUST be typed — no `any` type in component props (MUST NOT)
- State management MUST follow the established pattern (do not introduce new state libraries)
- CSS MUST use the established styling system — no inline styles except for dynamic values
- Files MUST NOT exceed 300 lines — components exceeding this SHOULD be split

## VI. Documentation

- All reusable components MUST have Storybook stories
- Complex state management flows MUST have data flow diagrams or documentation
- Breaking API contract changes MUST be communicated to the backend team before implementation

## Governance

- This constitution supersedes all other guidance
- **Version**: 1.0.0 | **Ratified**: [date]
```

---

## Template 3: Python / Data Pipeline

```markdown
# [Project Name] Constitution

## I. Data Quality (MANDATORY)

- All input data MUST be validated against a schema before processing
- Data transformations MUST be idempotent when possible
  *Running the same transformation twice MUST produce the same result*
- All data loss operations (delete, overwrite, drop) MUST require explicit confirmation
  and be logged with timestamp, user, and reason
- MUST NOT commit to main branch while a data pipeline is actively running against production

## II. Security

- Database credentials MUST be loaded from environment variables or secrets manager (MUST NOT hardcode)
- Pipeline logs MUST NOT contain PII, credentials, or sensitive data values
- All external API calls MUST use authenticated connections — no anonymous access to data sources

## III. Testing

- All transformation functions MUST have unit tests with sample data
- Integration tests MUST run against a test database, never production
- Data quality checks MUST be automated — no manual data validation before releases
- Test datasets MUST be representative of edge cases (empty inputs, null values, max values)

## IV. Code Quality

- Functions MUST NOT exceed 50 lines
- All public functions MUST have type annotations (Python 3.10+ syntax)
- All modules MUST have docstrings describing their purpose
- Dependencies MUST be pinned to specific versions in requirements files

## V. Observability

- All pipeline runs MUST log: start time, end time, records processed, records failed
- Failures MUST include: error type, failed record identifier, and actionable context
- Alerting MUST be configured for failure rates exceeding 1% of records
- Data lineage MUST be trackable from source to output

## VI. Performance

- Pipeline steps MUST NOT load entire datasets into memory if batch processing is possible
- External API calls MUST implement retry logic with exponential backoff
- Long-running operations (>5 minutes) MUST emit progress logs

## Governance

- This constitution supersedes all other guidance
- Data-destructive changes require two-developer sign-off
- **Version**: 1.0.0 | **Ratified**: [date]
```

---

## Template 4: .NET / C# Enterprise Application

```markdown
# [Project Name] Constitution

## I. Security (MANDATORY)

- No hardcoded connection strings, secrets, or credentials (MUST)
  *Use Azure Key Vault or IConfiguration with user secrets in development*
- All user input MUST be validated using model annotations and/or FluentValidation
- Entity Framework queries MUST use parameterized queries (LINQ expressions, not raw SQL strings)
- Authentication MUST use ASP.NET Core Identity or an established OAuth library
- OWASP Top 10 protections MUST be implemented for all web-facing endpoints

## II. Architecture

- MUST follow Clean Architecture layering: Domain → Application → Infrastructure → Presentation
  *Dependencies flow inward — Infrastructure MUST NOT be referenced by Domain*
- All database access MUST go through repository classes (MUST NOT access DbContext directly from controllers)
- Business logic MUST live in Application layer services, not controllers or infrastructure
- Cross-cutting concerns (logging, caching, validation) MUST use middleware or decorators, not inline code

## III. Testing (MANDATORY)

- Test-First development required — no production code without a failing test first
- Unit tests MUST use xUnit and mock infrastructure dependencies with Moq or NSubstitute
- Integration tests MUST use a real database (SQL Server LocalDB or PostgreSQL in Docker)
- All HTTP endpoints MUST have integration tests using WebApplicationFactory
- Minimum 80% line coverage required, measured in CI

## IV. Code Quality

- Classes MUST follow Single Responsibility Principle — one primary responsibility per class
- Methods MUST NOT exceed 30 lines
- Classes MUST NOT exceed 200 lines
- All public APIs MUST have XML documentation comments
- Async/await MUST be used consistently — no blocking calls in async context (MUST NOT use .Result or .Wait())

## V. Observability

- Structured logging MUST use ILogger<T> with Serilog as the underlying provider
- All unhandled exceptions MUST be logged with context at Error level
- Health check endpoints MUST be implemented and monitored
- Performance-sensitive operations MUST use Activity/DiagnosticSource for distributed tracing

## Governance

- This constitution supersedes all other guidance
- **Version**: 1.0.0 | **Ratified**: [date]
```

---

## Constitution Anti-Patterns

These are common mistakes in constitution writing. Avoid them.

### Anti-Pattern 1: Vague Principles

❌ Bad:
```markdown
- Write clean, readable code
- Follow best practices
- Be security-minded
```

✅ Good:
```markdown
- Functions MUST NOT exceed 50 lines
- No `eval()`, `exec()`, or `Function()` constructor calls (MUST NOT)
- All user input MUST be validated against a Zod schema before use
```

### Anti-Pattern 2: Implementation Details in the Constitution

The constitution defines principles, not implementation choices.

❌ Bad:
```markdown
- Use the `axios` library for all HTTP requests
- Store session data in Redis
- Use Tailwind CSS for styling
```

These belong in agent instruction files or coding standards documents.

✅ Good:
```markdown
- HTTP requests to external services MUST include timeout configuration
- Session data MUST be stored server-side — client-side session storage is prohibited
- UI components MUST conform to the established design system
```

### Anti-Pattern 3: Too Many MUST Requirements

When everything is a MUST, nothing is.

❌ Bad:
```markdown
- Code MUST be readable (MUST)
- Comments MUST be clear (MUST)
- Variable names MUST be descriptive (MUST)
- Functions MUST be well-structured (MUST)
```

These generate constant noise in reviews and obscure the things that truly matter.

✅ Better:
Reserve MUST for things you would actually reject a PR over. Promote the rest to SHOULD or remove them.

### Anti-Pattern 4: Undatable Principles

Principles that cannot be enforced because they require subjective human judgment with no objective criteria.

❌ Bad:
```markdown
- Code MUST be elegant
- Architectture MUST be scalable
- Design MUST be future-proof
```

✅ Good:
```markdown
- Functions with cyclomatic complexity > 10 MUST have a justification comment
- All services MUST expose health check endpoints that can be monitored independently
- New data storage decisions MUST be documented as ADRs with scalability considerations
```
