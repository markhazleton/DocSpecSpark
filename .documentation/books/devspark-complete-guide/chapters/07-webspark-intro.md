---
title: "Chapter 7: Introducing WebSpark.HttpClientUtility — The Running Example"
part: "Part III: DevSpark in Action"
---

# Chapter 7: Introducing WebSpark.HttpClientUtility — The Running Example

> **What you'll learn in this chapter:**
> - What WebSpark.HttpClientUtility is and why it was chosen as the running example
> - The state of the package before the DevSpark specifications began
> - How four consecutive specifications transformed it
> - What to expect from Chapters 8 through 11

The next four chapters document four consecutive production specifications on a real project. Not a tutorial project. Not a cleaned-up example. A live NuGet package with actual users, published on NuGet.org, with a version history that reflects real decisions made under real constraints.

I chose WebSpark.HttpClientUtility as this book's running example for three reasons. First, it's a project I know intimately — I built it, maintain it, and use it in other projects. I can speak to the decisions with authority rather than reconstructing them from documentation. Second, the four specifications form a natural progression that demonstrates the full range of DevSpark's capabilities: a major feature addition, a discipline-enforcement refactor, a structural split, and an API extension. Third, the specifications were run consecutively over a period of several months, which means the output of each one informed the input of the next — the kind of compounding that makes DevSpark most valuable.

## What WebSpark.HttpClientUtility Does

WebSpark.HttpClientUtility is a .NET library for making HTTP requests with resilience, observability, and consistent error handling built in. It wraps `HttpClient` — .NET's standard HTTP client — with a set of utilities that address the common pain points:

- **Retry policies**: Configurable exponential backoff with jitter for transient failures
- **Circuit breaking**: Polly-based circuit breaker to prevent cascade failures
- **Structured logging**: Request/response logging at appropriate verbosity levels with correlation IDs
- **Response caching**: In-memory response caching for GET requests with configurable TTL
- **Error normalization**: Consistent exception handling that surfaces useful context rather than raw HTTP errors
- **Timeout management**: Per-request and per-client timeout configuration

The package targets .NET developers building applications that consume external HTTP APIs — whether those are REST services, internal microservices, or third-party integrations. The core problem it solves is that getting `HttpClient` right — thread-safe, lifetime-managed, properly configured for production use — involves enough subtle complexity that most developers either do it wrong or copy and paste boilerplate they don't fully understand. WebSpark.HttpClientUtility does it correctly so you don't have to.

## The State of the Package Before DevSpark

Before the four specifications in this part, WebSpark.HttpClientUtility was functional but accumulating technical debt in a few specific areas.

**Documentation**: The package had XML documentation comments for the public API but no user-facing documentation — no getting-started guide, no examples, no conceptual explanation of when to use which features. Users who found the package on NuGet had to read the source code or experiment to understand how to use it effectively.

**Compiler warnings**: The codebase had accumulated a set of compiler warnings that weren't treated as errors. Some were genuine nullability issues introduced as the code was updated for newer .NET versions. Others were informational warnings that had been present so long they'd become invisible. None were catastrophic, but collectively they represented unacknowledged risk.

**Package structure**: The package had grown to include features with varying levels of dependency weight. The core HTTP utility functionality required a handful of lightweight packages (Polly, Microsoft.Extensions.Http), but some optional features pulled in heavier dependencies that not every user needed. Users who only wanted the basic retry and circuit-breaking behavior were paying a dependency cost for features they'd never use.

**Batch execution**: As I used the package in projects, I found myself repeatedly writing the same pattern: calling an external API for a list of items, handling rate limits, collecting results and errors. This pattern was user-side boilerplate that belonged in the library.

Each of these became a specification. The order they were run reflects the priority I assigned to them at the time — documentation was the gap most visible to users; compiler warnings were the gap most visible to code quality; package structure was architectural housekeeping; batch execution was a genuine new capability.

## Why This Order Matters

The sequencing of these specifications is pedagogically useful because each one builds on the previous.

Spec 001 (documentation site) establishes what the package does and how it's used — clarity that made Spec 002 possible. You can't sensibly define compiler discipline for a codebase you don't fully understand.

Spec 002 (compiler warnings) cleaned up the nullability model and established the `TreatWarningsAsErrors` configuration that would make Spec 003 safer. Splitting a package when the code has unresolved nullability issues means the split propagates those issues into both halves.

Spec 003 (package split) reorganized the code into a cleaner dependency graph — which clarified exactly what belonged in the core package versus extensions. That clarity informed the design of the new batch execution API in Spec 004, which needed to integrate cleanly with both halves.

The specifications are not independent. They're a thread. Each one left the codebase in a better state for the next one. That compounding is one of DevSpark's core value propositions, and it's more visible when you can see four consecutive specifications on the same project than when you read about individual specifications in isolation.

## The Four Specifications at a Glance

Here is a summary of what each specification accomplished:

**Spec 001 — Documentation Site**: Built an Eleventy 3.0 static site documenting the package, published to GitHub Pages. The specification grew to 37KB as the scope was clarified. The most important thing it caught: a path resolution assumption in the build configuration that would have silently failed at deployment time rather than build time. The spec caught it at spec time.

**Spec 002 — Compiler Discipline**: Enabled `TreatWarningsAsErrors` across the codebase. Required resolving 23 existing warnings before the flag could be set. Replaced `?.` with `ArgumentNullException.ThrowIfNull()` in 11 locations. Established a policy of maximum 5 suppressions with documented justification in code. The test suite grew from 340 to 711 tests as nullability edge cases were addressed. Eight clarification questions had to be answered before the plan could be written.

**Spec 003 — Package Split**: Separated the monolithic package into `WebSpark.HttpClientUtility` (core, minimal dependencies) and `WebSpark.HttpClientUtility.Extensions` (optional features, heavier dependencies). Reduced core dependencies from 13 to 9. Reduced core package size by approximately 40%. Established lockstep versioning (both packages always share the same version number) and atomic GitHub Actions publishing (both packages publish in a single pipeline run or neither publishes). Zero breaking changes for users of the core package.

**Spec 004 — Batch Execution**: Added an opt-in batch execution API with template-based URL generation, per-request result collection, and built-in rate limit handling. Template substitution uses `{placeholder}` token syntax. SHA-256 hashing for content integrity uses the .NET BCL implementation — no external dependency. The SignalR real-time progress feature, originally planned for the core package, was moved to the demo application after the critic raised a scope concern that turned out to be correct. A 50-request demo cap was established for the public demonstration endpoint.

## How to Read the Next Four Chapters

Each specification chapter follows the same structure:

1. **The starting point**: Where the codebase and the project stood before the specification
2. **The specification process**: How `/devspark.specify` → `/devspark.clarify` → `/devspark.plan` → `/devspark.tasks` played out for this particular feature
3. **The quality gates**: What `/devspark.analyze`, `/devspark.critic`, and `/devspark.checklist` found — including findings that changed the implementation
4. **The implementation**: What was built, key decisions made during implementation
5. **The PR review**: What `/devspark.pr-review` found and how it was resolved
6. **What the specification caught**: The honest accounting — what would have been different without the DevSpark workflow

This structure is intentional. I want you to see the workflow, not just the output. The output is interesting. The workflow is what you can replicate on your own projects.

One more note before we begin: I've edited some of the specification artifacts for length and readability, but I haven't changed the substance of the decisions. The clarification questions are real questions that I had to answer. The critic findings are real findings — including the one about SignalR that I initially disagreed with and later conceded. The PR review findings are real findings. Where I say something was caught at spec time, it was caught at spec time.

The goal is to show you DevSpark working on a real project, with the honesty that requires.
