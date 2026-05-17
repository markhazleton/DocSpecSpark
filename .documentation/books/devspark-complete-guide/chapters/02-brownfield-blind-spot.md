---
title: "Chapter 2: The Brownfield Blind Spot — Why I Actually Built DevSpark"
part: "Part I: Why DevSpark Exists"
---

# Chapter 2: The Brownfield Blind Spot — Why I Actually Built DevSpark

> **What you'll learn in this chapter:**
> - The specific failure that revealed DevSpark's original design gap
> - What "brownfield blindness" means in the context of AI-assisted development
> - How the hotfix incident changed the framework's architecture
> - Why the most dangerous deviation from process is the one that works

I'm going to tell you about a hotfix I shipped that violated everything I'd built into DevSpark.

It worked. The bug got fixed. The customer never noticed anything had gone wrong. From a purely operational standpoint, the incident was invisible.

That's why it was dangerous.

## The System

The system in question was a legacy ASP.NET application — call it the "contract management system" — that had been in production for eleven years. It was a brownfield project: not something I'd built from scratch but something I'd inherited, extended, and maintained. The original developers were long gone. The documentation was sparse. The test coverage was somewhere between minimal and insulting.

I'd been using DevSpark on greenfield projects for several months at this point and had been gradually applying it to the contract management system where I could. The project had a constitution that covered the parts I'd worked on directly. It did not cover the legacy core — the parts that predated my involvement and that I tried not to touch unless absolutely necessary.

The legacy core was where the bug appeared.

## The Incident

A client reported that contract documents were being generated with incorrect date formatting — a four-digit year rendered as two digits. The bug was intermittent, triggered by a specific combination of locale settings and date field configurations that the original developers hadn't anticipated.

I diagnosed the bug in about twenty minutes. It was in a date formatting utility method that had been there since 2014. The fix was four lines of code: replace a format string with an explicit format that didn't depend on locale, add a guard for null values, update the affected unit test.

I shipped the fix the same evening.

I did not use DevSpark. I did not open a spec. I did not run `/devspark.specify`. I wrote four lines, verified the behavior manually, committed, and pushed. The fix was in production in under two hours.

## What I Skipped

Let me be specific about what I bypassed.

**No specification.** The "spec" for this fix existed only in my head. I understood the problem, I understood the fix, and I didn't write any of it down.

**No clarification.** I didn't ask any of the questions that `/devspark.clarify` would have surfaced. Was the bug isolated to this utility method, or was the same format string used elsewhere? Were there other locale-dependent behaviors in the same code path? What were the edge cases for null handling in callers of this method?

**No quality gates.** The constitution for this project required that any change touching date handling include integration tests covering the affected locale combinations. I ran the existing unit test. I did not add an integration test. The constitution was violated.

**No PR review.** I pushed directly to main. The PR review would have caught the missing integration test as a CRITICAL finding.

**Commit message quality.** My commit message was `fix: date formatting bug`. The DevSpark commit convention required the bug ID, the affected component, and the test coverage added. Mine had none of that.

In the DevSpark terminology: I ran a one-off fix without using `/devspark.quickfix`. Even quickfix — the lightest-weight DevSpark workflow — requires a tracking record and a constitution check.

## The Constitution Violation

The constitution violation is the part that bothered me most, for a specific reason.

The integration test requirement existed because of an earlier incident — a different date-related bug that had been fixed in unit tests but not caught until production because the unit tests used a fixed culture and the production environment had a different default. That earlier incident cost several hours of emergency investigation. The integration test requirement was the lesson learned.

I knew this. I wrote the requirement myself. And when the next date-related bug appeared and I was under time pressure, I skipped the requirement anyway. The very lesson I'd enshrined in the constitution was the one I violated.

This is not a moral failing. It's a design failure. I had built a framework with excellent governance for greenfield work and almost no governance for emergency repairs. The constitution existed; the enforcement pathway for a two-hour hotfix did not.

## What the Post-Mortem Found

Three weeks later, I ran the site audit on the contract management system: `/devspark.site-audit`.

The audit found the missing integration test. It also found three other places in the codebase where the same date formatting pattern — the vulnerable one I'd "fixed" — still existed. I had fixed one instance and left three others.

This is exactly the kind of thing the specification process catches. When you write a spec for "fix date formatting in the contract generation path," the spec forces you to define the scope — which means asking how many places the pattern appears. I hadn't asked. I'd assumed "the bug" was localized and fixed "the bug" without verifying the assumption.

The three remaining instances were time bombs. Two used the same locale-dependent format string I'd replaced. One used a completely different approach that happened to work but for wrong reasons. None of them would have failed the existing unit tests.

## The Lesson and the Response

The incident revealed what I came to call the brownfield blind spot: the tendency for AI-assisted development frameworks to assume greenfield conditions. You have a clean spec, a defined architecture, a constitution that covers the code you're writing. The AI follows the workflow, the gates catch the problems, and the output is governed.

But most real development doesn't happen in greenfield conditions. It happens in systems with history — with legacy code that predates the framework, with inherited decisions that no one fully understands, with emergency situations where process feels like friction.

DevSpark's response to the brownfield blind spot was threefold.

**First, the quickfix command was redesigned.** The original quickfix was a lightweight path for small, clear changes. After the incident, it was extended to include a mandatory constitution check — even a four-line fix has to answer: "Which constitution principles apply to this change?" The check doesn't have to take long. It has to happen.

**Second, the site audit was made scope-aware.** The audit can now be targeted at specific directories or file patterns, making it practical to run against legacy code that you're touching rather than requiring a full-codebase scan every time. The command `/devspark.site-audit Scope to src/contracts/utilities/ only` audits exactly what you need audited without the overhead of scanning everything.

**Third, the constitution template for inherited/legacy projects got explicit guidance on brownfield patterns.** A constitution that only covers new code isn't a constitution for the whole project — it's a constitution for the ideal version of the project. Effective constitutions acknowledge legacy zones: areas with known technical debt, explicit exceptions to the standard rules, and a documented migration path.

## The Hotfix That Works

Here is the thing about hotfixes that violate process: the most dangerous ones are the ones that work.

If my date formatting fix had introduced a regression, I'd have caught the process violation immediately. The regression would have been the signal. I'd have investigated, found the missing integration test, added it, realized I'd missed the other three instances, and fixed all of them. The violation would have been its own corrective.

Instead it worked. The bug got fixed. The customer was satisfied. And I moved on to the next thing, leaving behind three time bombs I didn't know about.

The audit caught them. If I hadn't run the audit, I wouldn't have found them until one of them failed in production — probably in a different locale, with a different customer, at a different time. By then, the connection to the date formatting work I'd done three weeks earlier would have been less obvious.

This is the real argument for structured AI-assisted development: not that it prevents you from shipping bad code, but that it surfaces the problems you don't know you've created. The AI is not the quality gate. The workflow is the quality gate. The AI executes the workflow.

## Four Extensions Built on the Lesson

The brownfield incident led directly to four extensions I built into DevSpark that weren't in the original design.

**`/devspark.quickfix`** — redesigned to be genuinely usable for emergency repairs without sacrificing the constitution check. The command asks one diagnostic question before anything else: "Does this change touch code covered by the constitution?" If yes, it runs the relevant constitution checks. If no, it documents the reason the change is outside constitution scope.

**`/devspark.site-audit` scoping** — the ability to target the audit at a specific directory or file set, making it practical to run against the code you just touched rather than everything.

**Legacy zone guidance in the constitution template** — explicit patterns for documenting inherited technical debt and the rules that apply (or don't apply) to it.

**`/devspark.commit-audit`** — a command that analyzes git history for workflow compliance. The commit audit on the contract management system showed me that the hotfix wasn't the only time I'd bypassed the workflow. There were four other commits in the past six months with similar patterns: direct-to-main pushes, vague commit messages, no associated spec. I hadn't noticed any of them at the time. The audit made the pattern visible.

## The Honest Accounting

I want to be direct about something: DevSpark didn't prevent the brownfield incident. I had the framework. I had the constitution. I had the tools. And I still shipped a hotfix that violated the constitution and left three bugs behind.

What DevSpark did was make the incident findable. The audit surfaced what I'd missed. The constitution violation was documentable. The missing tests could be added.

That's a different claim than "DevSpark prevents you from making mistakes." The claim is: "DevSpark makes your mistakes visible and correctable."

After six months of real use, that turns out to be the more valuable property. You can't prevent all mistakes in a complex system. You can build a system that surfaces them quickly and provides a clear path to correction.

The next chapter begins the technical foundation — how DevSpark actually works. The brownfield blind spot is the reason some of that foundation looks the way it does.
