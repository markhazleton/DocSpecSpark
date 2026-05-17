---
title: "Chapter 8: Spec 001 — Building the Documentation Site"
part: "Part III: DevSpark in Action"
---

# Chapter 8: Spec 001 — Building the Documentation Site

> **What you'll learn in this chapter:**
> - How a documentation gap becomes a full DevSpark specification
> - Why the spec grew to 37KB before implementation began
> - The single most valuable thing the specification process caught
> - What a real PR review looks like for a documentation project

## The Starting Point

WebSpark.HttpClientUtility had been published on NuGet for several months before Spec 001. The package had XML documentation comments throughout the public API — the triple-slash comments that generate IntelliSense help in IDEs. But it had nothing a user could find through a web browser: no getting-started guide, no architecture explanation, no examples showing the most common patterns.

The feedback I was getting from the few developers who had found the package followed a consistent pattern: "I can see from the code what this does, but I'm not sure when I should use the circuit breaker versus just increasing the retry count" and "Is there a way to configure this globally or does it have to be per-request?" These were not questions about bugs. They were questions about understanding, and they pointed to a documentation gap that IntelliSense comments couldn't fill.

The decision to build a documentation site was straightforward. The implementation — which static site generator, what hosting approach, how to integrate the build into the CI pipeline — was less obvious.

## Running the Specification

I opened the specification with:

```text
/devspark.specify Build a documentation site for WebSpark.HttpClientUtility 
that explains what the package does, how to get started, and covers the main 
configuration scenarios. Should be static, hosted on GitHub Pages, integrated 
with the existing GitHub Actions pipeline.
```

The intake classifier routed this to `full-spec` rather than `quick-spec`. That was the right call, even though a documentation site might sound simple. The integration with GitHub Actions meant there were architectural decisions to make (separate workflow file? job in the existing release workflow?), and the "covers the main configuration scenarios" was vague enough that it needed to be made concrete before implementation.

## The Clarification Phase

`/devspark.clarify` produced five questions before the spec was approved for planning:

**Question 1: Which static site generator?**

Several options were viable: Eleventy, Docusaurus, VitePress, or simple hand-written HTML. Each had tradeoffs — Docusaurus is well-suited for API documentation and has strong ecosystem support, but adds a React dependency; Eleventy is lightweight and gives more control over output; VitePress is designed for Vite-based projects; hand-written HTML is the minimum viable path.

My answer: Eleventy 3.0. The package itself is not a JavaScript project, and I didn't want to introduce a React/Node dependency on the documentation side that would imply JavaScript expertise to maintain. Eleventy's build output is plain HTML and CSS with no client-side framework requirement.

**Question 2: Content scope — API reference or conceptual guide?**

There are two distinct types of documentation: API reference (what each method does, what its parameters are) and conceptual guide (when to use each feature, how to think about the configuration). API reference can be generated from XML comments; a conceptual guide requires human authorship.

My answer: Primarily conceptual guide. The API reference is available in the XML comments via IntelliSense. What's missing is the conceptual layer — the "why" and "when" — that can only be written, not generated.

**Question 3: Versioning approach?**

The package is versioned semantically. The documentation could either be version-specific (separate docs for each release) or always-current (docs for the latest stable release). Version-specific documentation is significantly more complex to maintain.

My answer: Always-current. At this stage, with a relatively young package and a single maintainer, the overhead of versioned documentation isn't justified.

**Question 4: Search functionality?**

A static site can include client-side search (using tools like Pagefind) or omit it and rely on browser Ctrl+F and external search engines.

My answer: Include Pagefind-based search. The documentation site will have enough content that users should be able to search it.

**Question 5: Integration with CI — deploy on every push or only on release?**

The documentation site should reflect the current state of the package. It could deploy on every push to main (always current but potentially showing unreleased changes) or only on release tags (always stable but potentially lagging behind recent changes).

My answer: Deploy on release tags. The documentation should reflect the released package, not unreleased work in progress.

## The Specification Grows

After the clarification phase, the specification document began to accumulate detail. This is normal — the spec is where decisions get made, and making decisions requires working through their implications.

The Eleventy 3.0 decision led to decisions about the site structure, the template system, the markdown pipeline, and the output configuration. The GitHub Pages integration led to decisions about the GitHub Actions workflow, the repository settings required, and the custom domain configuration. Each decision revealed two or three more decisions that needed to be made.

By the time the specification was approved for planning, it was 37KB. That's large for a documentation project. It includes:

- Site structure (directory layout, navigation hierarchy)
- Eleventy 3.0 configuration (template engine, markdown plugins, passthrough file copy)
- Content inventory (list of every page to be written, with outline)
- GitHub Actions workflow (triggers, steps, artifact paths, deployment target)
- GitHub Pages configuration (branch, directory, custom domain)
- Pagefind integration (build step, index location, UI configuration)
- Build validation (what checks must pass before deployment is allowed)

The content inventory alone — the list of every page with its outline — was ten pages of the specification. Writing it forced me to define the complete information architecture before writing a line of content.

## What the Specification Caught

Here is the thing the specification caught that would have been painful to discover later.

When I specified the GitHub Actions workflow, I wrote out the build steps in detail:

```yaml
- name: Build documentation site
  run: cd docs-site && npx @11ty/eleventy
  
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs-site/_site
```

The `publish_dir` value — `./docs-site/_site` — is a path relative to the repository root. The Eleventy build step uses `cd docs-site && npx @11ty/eleventy`, which changes to the `docs-site` directory and builds there. Eleventy's default output directory is `_site`, relative to where it runs — so the output goes to `docs-site/_site`.

That's correct: `./docs-site/_site` is the right path from the repository root.

But I had initially written the Eleventy configuration with an explicit output directory override:

```javascript
// .eleventy.js
module.exports = function(eleventyConfig) {
  return {
    dir: {
      output: "site"  // ← override: output goes to docs-site/site
    }
  };
};
```

With the explicit output override, the actual output goes to `docs-site/site` — but the deployment step is pointing at `docs-site/_site`. The deployment would silently find an empty directory (or fail with a directory-not-found error, depending on how `peaceiris/actions-gh-pages` handles it) and deploy nothing — or deploy nothing useful.

The mismatch between the output directory in the Eleventy config and the publish directory in the workflow was caught while writing the specification, before any code was written. The specification required me to write out both the Eleventy config and the Actions workflow in enough detail that the inconsistency became visible.

This is the most valuable thing a specification can do: force consistency across decisions that will be implemented separately but need to work together.

If the spec hadn't caught it, the error would have appeared after: writing the Eleventy config, writing the Actions workflow, committing both, pushing, watching the CI run, seeing it pass (because the build step succeeds), and then finding the deployed site is empty. Investigation would have required understanding the directory structure, reading the Eleventy documentation about output paths, tracing the Actions workflow step by step. Probably two hours of debugging to find a four-word error.

The spec found it in fifteen minutes of writing.

## The Planning Phase

`/devspark.plan` translated the specification into a technical plan. The key architectural decisions:

**Eleventy 3.0, not 2.x**: Eleventy 3.0 had just entered general availability. Its module system was cleaner for new projects, but its ecosystem of plugins was slightly less mature than 2.x. Given that I was starting fresh, 3.0 was the right choice.

**Nunjucks templates**: Eleventy supports multiple template languages. I chose Nunjucks for its familiar syntax (similar to Jinja2, liquid) and its strong support for layouts and macros.

**Tailwind CSS via CDN**: For a documentation site with a single maintainer, a CDN-loaded Tailwind CSS was simpler than a build-step integration. Performance was acceptable; the documentation site is not a web application.

**GitHub Actions using `peaceiris/actions-gh-pages`**: A well-maintained action for GitHub Pages deployment that handles the branch management correctly.

## The Quality Gates

`/devspark.analyze` ran cross-artifact consistency checks across the spec, plan, and task list. It found one issue: the task list included a task for "Configure custom domain" but the specification said custom domain was out of scope for the initial deployment. The task was removed.

`/devspark.critic` found two SHOWSTOPPER items that I reviewed carefully:

**SHOWSTOPPER 1**: The documentation site content is manually authored and will drift from the actual package behavior as the package evolves. There is no automated mechanism to detect when documentation is out of date.

This is a real risk. My mitigation: the content inventory (in the spec) becomes a review checklist for each release. Before each version release, the documentation review is a checklist item.

**SHOWSTOPPER 2**: GitHub Pages deployment from a private repository requires a paid GitHub account. If the repository is ever made private, the documentation deployment will fail.

This was not a risk I needed to mitigate — the repository was and would remain public — but it was worth acknowledging. Documented as: "Repository is public by design; this risk is accepted for public repositories."

## The Implementation

The implementation followed the task list closely. Eleventy 3.0 was configured, the Nunjucks templates were written, the content pages were authored, Pagefind was integrated, and the GitHub Actions workflow was set up.

Two notable implementation decisions:

**Syntax highlighting**: I added Prism.js for code block syntax highlighting after discovering that the default Eleventy markdown rendering was outputting code blocks without language hints. The specification hadn't mentioned syntax highlighting — an omission. I added it during implementation and noted it in the task list as a scope addition. It wasn't complex enough to require a spec amendment, but it was explicitly tracked.

**Navigation structure**: The specified navigation hierarchy had five top-level sections (Getting Started, Configuration, Features, Examples, API Reference). During content authoring, it became clear that "Configuration" and "Features" overlapped significantly — you configure features by understanding the features. They were merged into "Configuration & Features" with a section-level introduction explaining the overlap. This changed the navigation structure from the spec but improved the information architecture. Documented in the PR description.

## The PR Review

`/devspark.pr-review` found three items:

**MEDIUM**: The GitHub Actions workflow file doesn't pin action versions to SHA hashes. Using `@v3` means the workflow will use whatever the action author publishes as v3, including potentially breaking changes. Recommendation: pin to SHA.

I agreed with this finding. Fixed before merge.

**LOW**: The Eleventy configuration doesn't have a `.eleventy.js` return statement for the `dir` configuration — it's relying on Eleventy's defaults. This is technically correct but fragile; if Eleventy changes its defaults in a future version, the output path changes silently.

I agreed with this finding too. Fixed by making the `dir` configuration explicit even when using default values.

**LOW**: The content pages use relative links for cross-page navigation. Relative links break when the GitHub Pages base URL has a path prefix. Should use site-root-relative links or Eleventy's `url` filter.

Fixed. This was another thing the specification hadn't anticipated — the GitHub Pages URL structure and its implications for link handling.

All three findings were straightforward fixes. The PR was approved without additional review cycles.

## What the Specification Caught — The Honest Accounting

The path resolution mismatch between the Eleventy output directory and the Actions publish directory is the clearest example of specification value in this project. The spec caught a configuration error at spec-writing time that would have been a deployment-time debugging problem otherwise.

The five clarification questions made five decisions explicit that I would have made implicitly during implementation. Making them explicit at spec time rather than implementation time means they're documented — the decisions are in the spec, reviewable, changeable before any code is written. If I'd answered any of those questions differently than I did (say, choosing Docusaurus instead of Eleventy), I would have been changing a spec rather than refactoring an implementation.

What the specification didn't catch: the syntax highlighting gap, the navigation structure overlap, and the link handling issue. All three appeared during implementation and were handled appropriately (tracked, documented, or raised in PR review). Not everything can be caught at spec time — the goal isn't perfection, it's systematic reduction of downstream surprises.

In the next chapter, Spec 002 enforces a discipline I'd been deferring for months.
