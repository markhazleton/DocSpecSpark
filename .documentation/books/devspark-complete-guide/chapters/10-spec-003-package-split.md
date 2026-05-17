---
title: "Chapter 10: Spec 003 — Splitting the Package"
part: "Part III: DevSpark in Action"
---

# Chapter 10: Spec 003 — Splitting the Package

> **What you'll learn in this chapter:**
> - When a monolithic package needs to be split — and when it doesn't
> - How lockstep versioning preserves the simplicity of a multi-package ecosystem
> - What atomic publishing means and why it matters for NuGet packages
> - The 40% size reduction that required zero breaking changes for core users

## The Starting Point

After Spec 002 cleared the compiler warnings and established the null safety baseline, the codebase was in the cleanest state it had been in for over a year. That cleanliness made the package's structural problem more visible.

WebSpark.HttpClientUtility had grown from a focused HTTP utility library into something broader. The core functionality — retry policies, circuit breaking, structured logging, response caching — was lightweight: it depended on Polly, Microsoft.Extensions.Http, and Microsoft.Extensions.Logging. These were packages any .NET project using `HttpClient` would already have.

But the package also included optional extensions: an OpenTelemetry integration, a custom health check endpoint format, and a set of Prometheus metric exporters. These depended on OpenTelemetry.Api, Microsoft.Extensions.Diagnostics.HealthChecks, and the Prometheus .NET client. Together, those optional extension dependencies added roughly 40% to the installed size of the package.

A developer who wanted retry-and-circuit-breaker for their `HttpClient` calls was paying the dependency cost of OpenTelemetry and Prometheus, even if they never used those features.

## The Problem with Monolithic Package Growth

This is a common evolution pattern for utility libraries. You start with a focused core. Users ask for related features. You add them to the existing package because creating a new package is overhead — it requires separate projects, separate NuGet metadata, separate versioning decisions, and coordination when publishing. The convenience of the monolithic package outweighs the cost of the growing dependency footprint, until it doesn't.

The tipping point for WebSpark.HttpClientUtility was when a user opened an issue noting that adding the package to a minimal API project caused the project's startup time to increase measurably, traced to the OpenTelemetry SDK initialization. The user didn't need OpenTelemetry. They needed the retry behavior. But the package forced the dependency.

That issue became the trigger for Spec 003.

## The Specification

```text
/devspark.specify Split WebSpark.HttpClientUtility into a core package (minimal 
dependencies, retry/circuit-breaking/logging/caching) and an extensions package 
(OpenTelemetry, HealthChecks, Prometheus). Existing users of the core features 
should not need to change their code. Version both packages together. Publish 
atomically.
```

The intake classifier routed this to `full-spec`. The reasons were clear: the split involves multiple NuGet packages, CI pipeline changes, versioning decisions with long-term implications, and a zero-breaking-changes requirement that needed careful verification.

## Clarification: The Hard Questions

Three clarification questions shaped the entire architecture of the split:

**Question 1: Lockstep or independent versioning?**

Two options:
- **Lockstep**: Both packages always have the same version number. `WebSpark.HttpClientUtility 2.3.0` and `WebSpark.HttpClientUtility.Extensions 2.3.0` are always released together.
- **Independent**: Each package versions independently based on what changed in that package.

Independent versioning is theoretically correct — if only the extensions package changes, incrementing the core package's version is misleading. But in practice, independent versioning for closely related packages creates compatibility questions: "Does `Extensions 2.4.0` work with `Core 2.3.0`?" Users have to track two version numbers and understand their compatibility relationship.

My answer: Lockstep. The packages are closely related and always released together. The simplicity of a single version number for both packages outweighs the theoretical precision of independent versioning. This is the same approach used by popular package families like Serilog and its sinks.

**Question 2: What is the exact boundary between core and extensions?**

This question required inventorying every public type in the package and assigning it to one of three categories:
- Core (stays in `WebSpark.HttpClientUtility`)
- Extension (moves to `WebSpark.HttpClientUtility.Extensions`)
- Shared (types that both packages need — goes in core, referenced by extensions)

The inventory produced surprises. The `IHttpRequestLogger` interface was used by both the core logging infrastructure and the OpenTelemetry integration. It needed to stay in core and be referenced by extensions rather than moved.

The `CircuitBreakerOptions` configuration class was used by the core circuit breaker and by the Prometheus exporter (which exported circuit breaker state as a metric). Same decision: stays in core.

The boundary turned out to be cleaner than expected: the dependency-heavy code was mostly in self-contained classes that didn't share types with the core. The six classes in the OpenTelemetry integration and the four in the Prometheus exporter could be moved without pulling core types with them.

**Question 3: How does atomic publishing work?**

"Atomic" here means: either both packages publish successfully or neither publishes. A partial publish — where the core package publishes but the extensions package fails — would leave users in a state where `WebSpark.HttpClientUtility 2.3.0` exists but `WebSpark.HttpClientUtility.Extensions 2.3.0` does not. Lockstep versioning with a partial publish breaks the version promise.

The implementation required a GitHub Actions workflow design where both packages are built and validated first, then both are pushed to NuGet in a single job that either completes successfully or fails entirely — not two separate jobs that could succeed independently.

My answer: Single-job publication with explicit dependency validation before push.

## The Plan

The technical plan organized the work into five phases:

**Phase 1 — Project structure**: Create `WebSpark.HttpClientUtility.Extensions` as a new .NET class library project. Set up the solution to include both projects. Configure the extensions project to reference the core project.

**Phase 2 — Dependency migration**: Move the 10 classes (6 OpenTelemetry, 4 Prometheus) to the extensions project. Update namespaces. Remove the heavy dependencies from the core `.csproj`; add them to the extensions `.csproj`.

**Phase 3 — Verification**: Run the full test suite against both projects. Verify that the core project builds with only its declared dependencies. Verify that the extensions project builds and that its tests pass.

**Phase 4 — NuGet metadata**: Create the `WebSpark.HttpClientUtility.Extensions.csproj` NuGet metadata (package ID, description, dependency declarations). Update the core package's README to mention the extensions package.

**Phase 5 — CI pipeline**: Update the GitHub Actions workflow to build both packages, run all tests, and publish both atomically on release tag.

## What the Quality Gates Found

`/devspark.analyze` found a consistency issue: the task list included a task for "Create migration guide for users who use extensions features" but the specification said "existing users of the core features should not need to change their code" — it said nothing about users of the extensions features.

This surfaced an ambiguity in the spec: what about users of the OpenTelemetry and Prometheus features? For them, the package split *is* a breaking change — they need to add `WebSpark.HttpClientUtility.Extensions` as a dependency. The spec had treated them as out of scope ("zero breaking changes for core users") but hadn't addressed them directly.

The spec was amended: extension feature users require a one-time dependency change. A migration guide (not just a note in the README but a dedicated migration page on the documentation site) would document the change. The NuGet release notes would flag this as a breaking change for extension users.

`/devspark.critic` raised one SHOWSTOPPER that required a genuine decision:

**SHOWSTOPPER: The atomic publication approach has a race condition window.** Both packages are built and validated in the same CI job. They're pushed to NuGet sequentially, not simultaneously (NuGet doesn't support batch publication). Between the first push and the second push, there's a window — typically a few seconds — where one package exists on NuGet and the other does not. A user who installs during that window gets an inconsistent state.

This is a real risk. The window is short, but it's non-zero.

My response: The risk is accepted. The window is small (NuGet push is fast, typically 2-5 seconds per package). The lockstep version number means a user who installs during the window will find the second package is missing and get an error — they will not silently get an incompatible combination. The mitigation is: retry. Documented in the release notes: "If you encounter a NuGet restore failure during the first minutes after a new release, wait 60 seconds and retry."

## The Implementation

The migration of the 10 classes to the extensions project was mechanical. The interesting work was in the CI pipeline.

### Atomic Publishing in GitHub Actions

The naive approach — two separate `dotnet nuget push` commands, one for each package — fails the atomicity requirement because they're independent steps that can fail independently.

The solution was a single step with explicit dependency validation:

```yaml
- name: Publish packages (atomic)
  run: |
    # Validate both packages exist before pushing either
    CORE_PKG=$(ls dist/WebSpark.HttpClientUtility.*.nupkg | head -1)
    EXT_PKG=$(ls dist/WebSpark.HttpClientUtility.Extensions.*.nupkg | head -1)
    
    if [ -z "$CORE_PKG" ] || [ -z "$EXT_PKG" ]; then
      echo "Error: One or both packages not found. Aborting."
      exit 1
    fi
    
    echo "Publishing $CORE_PKG..."
    dotnet nuget push "$CORE_PKG" --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
    
    echo "Publishing $EXT_PKG..."
    dotnet nuget push "$EXT_PKG" --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
    
    echo "Both packages published successfully."
```

If the core package push fails, the step fails and the extensions package is never pushed. If the core package push succeeds and the extensions push fails, we have a partial publish — but this is the same race condition window identified by the critic. The mitigation (documented in release notes) applies.

### Dependency Count

After the split, the dependency graphs were:

**Core package** (9 dependencies, down from 13):
- Polly 8.x
- Microsoft.Extensions.Http
- Microsoft.Extensions.Http.Polly
- Microsoft.Extensions.Logging.Abstractions
- Microsoft.Extensions.Caching.Memory
- Microsoft.Extensions.Options
- System.Text.Json
- Microsoft.IO.RecyclableMemoryStream
- System.Runtime.CompilerServices.Unsafe

**Extensions package** (4 additional, all transitive through the 3 new direct dependencies):
- OpenTelemetry.Api
- Microsoft.Extensions.Diagnostics.HealthChecks
- prometheus-net

The core package size on disk dropped from approximately 420KB to 250KB — a 40% reduction. For a NuGet package, this is the footprint that gets downloaded and cached by every developer machine and CI runner that uses the package.

## The PR Review

`/devspark.pr-review` found two MEDIUM findings and one LOW:

**MEDIUM**: The extensions project doesn't have its own test project. The extensions classes are tested via the core test project's integration tests, which reference both packages. This is structurally fragile — the extensions tests are in the wrong project and will be confused if anyone tries to run only the core tests.

Fix: Created `WebSpark.HttpClientUtility.Extensions.Tests` as a separate test project. Moved the relevant integration tests.

**MEDIUM**: The migration guide on the documentation site doesn't cover users who are using the OpenTelemetry integration via dependency injection (using `AddOpenTelemetryInstrumentation()`). The guide documents the namespace change but not the DI registration change.

Fix: Added a DI registration section to the migration guide.

**LOW**: The core package's README doesn't mention what's in the extensions package or link to it. A user who discovers the core package won't know the extensions exist.

Fix: Added an "Extensions" section to the core README.

## The Honest Accounting

The zero-breaking-changes requirement for core users was met. No user who was using only the retry, circuit-breaking, logging, or caching features needed to change anything. Their code compiled without changes. Their dependency footprint shrank by 40%.

The breaking change for extension users was discovered during `devspark.analyze` — the spec's scope ambiguity was caught by the cross-artifact consistency check. Without the analyze gate, the migration guide might have been incomplete or absent.

The critic's race-condition finding was the most valuable quality gate output. It didn't block the implementation, but it forced a documented decision rather than an unexamined assumption. The race condition was known and accepted, with a documented mitigation, rather than unknown and silently present.

Spec 003 left the codebase in its cleanest structural state: two packages with clear responsibilities, minimal dependencies, atomic versioning, and atomic publishing. Spec 004 built on that foundation.
