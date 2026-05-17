---
title: "Chapter 11: Spec 004 — Adding Batch Execution"
part: "Part III: DevSpark in Action"
---

# Chapter 11: Spec 004 — Adding Batch Execution

## The Starting Point

Three specifications in, WebSpark.HttpClientUtility was well-documented, cleanly structured, and null-safe. Spec 004 was the first one adding new user-facing capability rather than improving what was already there.

The feature request came from my own usage. I had written the same pattern in three different projects:

```csharp
var results = new List<ApiResult>();
var errors = new List<(string Id, Exception Error)>();

foreach (var item in items)
{
    try
    {
        var url = $"https://api.example.com/v1/resources/{item.Id}";
        var result = await httpClientUtility.GetAsync<ApiResult>(url);
        results.Add(result);
        
        // Rate limit: stay under 10 req/sec
        await Task.Delay(100);
    }
    catch (Exception ex)
    {
        errors.Add((item.Id, ex));
    }
}
```

The pattern was always: build a URL per item, call the API, collect results and errors, throttle. The throttling parameters changed. The URL template changed. The error handling changed slightly. But the structure was always the same.

This is the signal that something belongs in a library: when you find yourself writing the same structural pattern repeatedly, and the only variation is in the parameters.

## The Specification

```text
/devspark.specify Add a batch execution API to WebSpark.HttpClientUtility. 
The API should accept a list of items, a URL template with placeholder 
substitution, and configuration for throttling and error handling. 
It should return a result collection separating successes from failures. 
Consider real-time progress reporting.
```

The intake classifier routed this to `full-spec`, and it's worth pausing on why. The "consider real-time progress reporting" clause implied SignalR or Server-Sent Events — which are significantly more complex than batch HTTP calls and carry meaningful dependency consequences for a library that targets .NET broadly. That single clause was enough to flag the spec for full treatment rather than a lightweight pass.

## Designing Batch Execution

I needed throttling, templating, and error collection to coexist without creating a leaky abstraction. Each decision I made about one of those concerns imposed a constraint on the next, so it's worth tracing them in sequence rather than treating them as independent choices.

**Template substitution syntax.** URL templates need a way to substitute item properties into the URL. The options were `{placeholder}` (simple, readable, familiar from C# string formatting and URI templates), `{{placeholder}}` (double-brace style, avoids ambiguity with C# string interpolation), or a custom lambda where the caller provides a `Func<TItem, string>` to build the URL. I chose `{placeholder}` token syntax. The double-brace style is harder to read. The lambda approach is more flexible but adds complexity to the API surface and doesn't compose cleanly with configuration. That choice — reflection-based token substitution — meant the API would accept a `string` template rather than a delegate, which immediately constrained how throttling configuration could be expressed: it had to be a separate parameter, not folded into the URL-building logic.

**Throttling model.** With the template syntax settled as a string, throttling had to live in configuration. The question was whether to use delay-based throttling (wait N milliseconds between requests) or rate-based throttling (maintain a target rate using a token bucket or sliding window). Delay-based is simpler to implement and reason about; rate-based is more accurate but requires a concurrent data structure. I chose delay-based for the initial implementation. The common use case is "don't exceed X requests per second on an external API," and a delay of `1000 / maxRequestsPerSecond` milliseconds achieves that without concurrency complexity. That decision, in turn, constrained error handling: since requests were sequential with delays rather than concurrent, I didn't need to worry about thread-safety in the error collection.

**Error handling.** Three options: fail-fast (stop on first error, throw), collect-all (continue on errors, collect all errors, report at end), or configurable (caller chooses). I chose collect-all as the default, with fail-fast available as a configuration option. The most common batch use case is "process as many as I can, report what failed" — stopping on first error is the exception, not the rule. But fail-fast is a legitimate mode for cases where any single failure invalidates the entire batch. Making this configurable rather than hardcoded was the right call, but it raised a question about how results would be validated across retries — which is what led to the integrity check.

During PR review, a teammate asked how batch results would be validated when a caller retried a subset of failed items. That question prompted the SHA-256 content integrity feature: an optional check that computes a hash of the response body and compares it against an expected value. This is useful when calling APIs that serve signed content or when detecting unexpected response changes. The implementation uses `System.Security.Cryptography.SHA256`, part of the .NET BCL — no external dependency:

```csharp
private static string ComputeSha256(string content)
{
    var bytes = Encoding.UTF8.GetBytes(content);
    var hash = SHA256.HashData(bytes);
    return Convert.ToHexString(hash).ToLowerInvariant();
}
```

`SHA256.HashData()` is the BCL method introduced in .NET 5, avoiding the `using` pattern required by the older `SHA256.Create()` / `ComputeHash()` / `Dispose()` sequence. Since the package targets .NET 8, this is available cleanly.

**Registration model.** The batch execution API could be part of standard service registration (`AddWebSparkHttpClient()` registers everything including batch) or opt-in (`AddWebSparkBatchExecution()` as a separate call). I chose opt-in. Users who don't need batch execution shouldn't pay for registering its infrastructure, and opt-in signals explicitly that batch execution is an additional capability rather than part of the core. This also kept the registration footprint consistent with the package split from Spec 003.

**Real-time progress.** My initial inclination was to add SignalR support to the extensions package — it's optional, it belongs with other optional features, and users who want it can install the extensions. I put that in the spec and moved forward. By the time the critic questioned SignalR, the API shape was already determined by these earlier trade-offs.

## What the Critic Found About SignalR

`/devspark.critic` ran before implementation. The SignalR finding was its highest-priority SHOWSTOPPER:

```
SHOWSTOPPER: SignalR dependency in the extensions package creates a dependency 
that forces ASP.NET Core references into non-web contexts.

WebSpark.HttpClientUtility targets .NET 8 broadly — it's used in console 
applications, worker services, and web APIs. SignalR (via 
Microsoft.AspNetCore.SignalR) is designed for ASP.NET Core web applications. 
Adding it to the extensions package forces ASP.NET Core transitive references 
into projects that may not be web applications.

The batch execution use case — calling external APIs for a list of items — 
is frequently a background job or worker service, not a web application. 
A worker service that wants batch execution but not real-time progress would 
be forced to take the ASP.NET Core dependency anyway.

Recommendation: Move SignalR progress reporting to the demo application, 
not the library. The demo application (which is an ASP.NET Core web project) 
is the appropriate home for this feature. The library can provide a progress 
callback interface that any caller can implement, including one that publishes 
to SignalR — but the SignalR implementation stays outside the library.
```

My initial reaction was that this was an overstatement. The extensions package already had other dependencies that implied specific hosting models. SignalR wasn't *that* different.

I re-read the finding two days later, after I'd had time to think about it.

The critic was right.

The key insight is "worker service." I use WebSpark.HttpClientUtility in several worker services — long-running background processes that consume APIs and process data. Those are exactly the context where batch execution is most useful: long-running jobs against rate-limited APIs. And worker services have no use for SignalR. Adding SignalR to the extensions package would force every worker service that wants batch execution to carry a web framework dependency it doesn't need.

The critic was right, and the finding had a direct consequence for the API shape: real-time progress reporting was out of scope for this release, so the batch API would accept a simple callback for completion only, no streaming updates. That decision made the implementation trivial and the API contract clear. The progress callback interface approach was cleaner: define an `IBatchProgressReporter` interface in the library, accept it as an optional parameter, and let callers implement it however they want — including with SignalR if they're in a web context. This is the reason the critic exists: to ask uncomfortable questions about decisions that seem fine until they're interrogated.

## The Revised Design

After conceding the critic's SignalR finding, the architecture changed:

**In the library**: `IBatchProgressReporter` interface, with a default `NullBatchProgressReporter` implementation (does nothing). The batch executor accepts an optional `IBatchProgressReporter`.

**In the demo application**: `SignalRBatchProgressReporter` implementing `IBatchProgressReporter`, pushing progress events to a SignalR hub. This is a complete, working example that demonstrates the pattern — it just lives in the demo, not the library.

**Not in the library**: Any direct SignalR dependency.

## The 50-Request Demo Cap

The demo application includes a public endpoint that allows visitors to run a sample batch execution against a public API (JSONPlaceholder, a free mock API). The endpoint was constrained to 50 requests per batch.

The 50-request limit is arbitrary in the sense that 47 or 60 would have been equally defensible. But the cap forces users to opt into unlimited requests explicitly, preventing accidental request storms from misconfigured throttling — without it, a user could believe they had set up throttling correctly and inadvertently spawn thousands of concurrent requests. The spec's clarification question had asked: "What is the demo cap, and why?" My answer defined both the number (50) and the reasoning: rate-limiting the public JSONPlaceholder API as a good citizen, keeping the demo fast enough that visitors see results quickly, and preventing accidental or intentional abuse of the public demo endpoint.

The implementation:

```csharp
const int MaxDemoBatchSize = 50;

if (request.Items.Count > MaxDemoBatchSize)
{
    return BadRequest(new {
        error = "Demo batch size limit exceeded",
        limit = MaxDemoBatchSize,
        received = request.Items.Count,
        message = "The public demo is limited to 50 items per batch. " +
                  "Install the package to run unlimited batches."
    });
}
```

The error message is explicit about the reason and points users to the library. A user who wants to run larger batches has a clear next step.

## The PR Review

`/devspark.pr-review` found two HIGH findings and one MEDIUM:

**HIGH**: The `SubstituteTokens` method throws `InvalidOperationException` when a property isn't found, but the exception type is wrong for this context. The caller provided a template with a token that doesn't match any property — this is a usage error that should be an `ArgumentException` (or a derived type like `ArgumentOutOfRangeException`), not an `InvalidOperationException`. In .NET conventions, `InvalidOperationException` means "the object is in an invalid state for this operation"; `ArgumentException` means "the argument value is wrong."

Fix: Changed to `ArgumentException` with a clear message. Updated the relevant tests.

**HIGH**: The `IBatchProgressReporter` interface has no documentation. It's a public extension point that users are expected to implement, and there's no guidance on what the implementation contract is — whether it should be thread-safe, whether it can throw, whether it's called on the calling thread or a thread pool thread.

Fix: Added XML documentation to the interface and its single method, documenting the contract: implementations should be thread-safe (calls may come from multiple threads if the batch uses concurrency), should not throw (exceptions in the reporter are silently swallowed to avoid disrupting the batch), and are called on thread pool threads.

**MEDIUM**: The reflection-based property lookup caches by `Type` but not by `string template`. If the same type is used with different URL templates (which could happen if a caller changes the template between calls), the cache is per-type but the token set is per-template. The cache stores `PropertyInfo` objects by property name, not by which properties are referenced in the template — so the cache behavior is correct, but it's not obvious why without reading the implementation. Needs a comment.

Fix: Added a comment explaining the cache is property-name-keyed, not template-keyed, and why that's correct.

## What the Specification Caught — The Honest Accounting

The SignalR finding is the definitive example of the critic's value in this specification. I was wrong about the placement. The critic was right. The library is better for not having a SignalR dependency, and the `IBatchProgressReporter` interface is better API design than a built-in SignalR integration would have been.

The 50-request demo cap is an example of a different kind of specification value: making explicit decisions that would otherwise be implicit. The cap was going to exist regardless — the question was whether it would be a number I picked at implementation time without thinking about why, or a number documented in the spec with a stated rationale.

The PR review's finding about `InvalidOperationException` vs `ArgumentException` is a small but real correctness issue. Exception type selection is a detail that's easy to get wrong and that matters for callers who catch specific exception types. The constitution's principle "public APIs must follow .NET design guidelines" is what motivated the reviewer to flag it.

## The Running Example: What Four Specifications Accomplished

Looking across all four specifications on WebSpark.HttpClientUtility:

- Users now have a documentation site where they couldn't find conceptual guidance before
- The codebase has zero compiler warnings and a verified null safety contract
- Core users have a 40% smaller package footprint with the same capabilities
- Batch HTTP execution is now a library feature rather than copy-paste boilerplate

Each specification built on the previous one. The compiler discipline from Spec 002 made the package split in Spec 003 safer. The package split in Spec 003 made the batch execution architecture in Spec 004 cleaner. The documentation site from Spec 001 gave each subsequent spec a place to publish its user-facing documentation changes.

That compounding is the argument for running DevSpark specifications consecutively rather than treating each one in isolation. Isolation misses the compounding; sequence captures it.

Part IV covers the advanced architecture — the tiered prompt model, autonomy levels, the harness runtime — that underlies everything in the case studies. Part V returns to the first-person account of what six months of real use teaches you that no case study can.
