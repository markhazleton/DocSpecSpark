---
title: "Chapter 20: Six Months Later — What the Ledger Actually Shows"
part: "Part V: Living with DevSpark"
---

# Chapter 20: Six Months Later — What the Ledger Actually Shows

> **What you'll learn in this chapter:**
> - The honest overhead accounting — where the front-loading cost is real
> - The confidence trap and why it's DevSpark's subtlest failure mode
> - Why the critic's value only becomes visible over multiple sprints
> - What constitution staleness looks like and how to prevent it
> - The single-model trap and how to avoid it

## The Premise of This Chapter

I want to write the chapter that the marketing version of this book would omit.

Most framework documentation tells you about the wins. This chapter is about the ledger — both sides. The overhead is real. The failure modes are real. The lessons in this chapter are the ones I learned by making mistakes, not by designing the framework carefully in advance.

Six months of DevSpark on real projects, including the brownfield contract management system, the WebSpark.HttpClientUtility specifications, and the DevSpark repository itself, produced a picture that's more complicated than "the framework makes everything better." The framework makes some things better consistently, some things better conditionally, and a few things harder in ways that require active management.

Here is what the ledger shows.

## The Overhead Is Front-Loaded and Real

Before using DevSpark, I estimated that adding a structured workflow would add about 10% overhead to the development process — a small tax for large gains.

That estimate was wrong. The overhead is closer to 30–40% on a typical full-spec feature — but it's concentrated in the first third of the work.

The specification and clarification phases take time. Writing a spec for a feature that I could have started implementing in an hour takes two to three hours. Answering eight clarification questions before the plan is written takes another hour. For a feature that I could have coded in an afternoon, the spec-and-plan phase takes a full morning.

This feels inefficient when you're in it. You know roughly what needs to be built. You're writing documentation about the thing instead of building the thing. The overhead is real and it's visceral.

But the back end is faster. Implementation follows a clear task list. The quality gates catch problems before they reach PR review. The PR review is faster because the review context (the spec, the plan, the gates) is available. The feedback-and-rework cycle is shorter because the implementation matches the spec rather than diverging from an unspecified mental model.

The total time — from "I need to build this" to "it's merged" — is comparable for features that would otherwise have encountered significant rework. For features that would have shipped cleanly without a spec, total time is longer with DevSpark.

The honest framing: DevSpark is most valuable for features where implementation risk is high — where you might build the wrong thing, or build the right thing incorrectly. For features where implementation risk is low and you have high confidence in the approach, the overhead isn't justified by the return.

The hard part is that "high confidence" and "actually correct" are not the same thing. The brownfield incident happened in a context where I had very high confidence in a four-line fix.

## The Confidence Trap

This is DevSpark's subtlest failure mode, and the one I've observed most consistently across the developers I know who use the framework.

The confidence trap is: you use DevSpark on the features where you're uncertain, you succeed, and you build confidence that you can identify uncertain features. Then you classify a feature as "low risk" and skip the workflow. The feature turns out to be more complex than it looked.

The trap is self-reinforcing. Every time you skip the workflow and it works out, you get more confident that your risk classification is accurate. Until the time it doesn't work out — and by then, you've built a habit of selective workflow application.

I fell into this trap with the brownfield hotfix. I'd been using DevSpark for months. I'd developed a good intuition for "this is complex enough to warrant a spec." And then I misclassified a four-line fix that left three bugs behind.

The framework's defense against the confidence trap is the quickfix command — a lightweight path that's fast enough to use on genuinely small changes while still running the constitution check. The constitution check is the minimum viable verification: "does this change touch anything the constitution covers?" That question alone would have caught the date formatting violation.

The practical advice: if you find yourself reasoning "this doesn't need a spec because X," write that reasoning down and look at it. If X is "this is a small change," that's not a good reason to skip the workflow. Small changes can be wrong. If X is "this change has no architectural implications and I've done exactly this before," that's a better reason.

## The Critic's Value Is a Lagging Indicator

The critic command produces alarming output. It over-flags intentionally. Early users — and I was one of them — respond to critic output with frustration: "This is overkill. Half of these findings are theoretical risks that will never materialize."

That reaction is correct. Half the findings often are theoretical. The frustration is valid.

But the critic's real value is not in individual findings. It's in the pattern across multiple critic runs on multiple specs.

After six months of critic output on the WebSpark specifications and the DevSpark repository, I started to notice which categories of findings I'd been dismissing — "this won't happen in practice" — and then which of those had actually occurred.

The SignalR finding on Spec 004 is the clearest example: a finding I initially dismissed as "overstatement," which turned out to be correct within two days of reflection. The dependency impact on non-web contexts was a real problem that the critic identified and I initially rationalized away.

Not all critic findings are like this. Many are genuinely theoretical. But the ratio of correct findings to false alarms is higher than it feels in the moment, because in the moment you're optimistic about the thing you're building and the critic is asking adversarial questions about it.

The practical advice: keep a record of critic findings you dismiss and why. Every quarter, review the dismissed findings for features you've shipped. The ones that turned out to be correct teach you about your blind spots. The ones that remained theoretical reinforce which categories of findings to weight lower.

## Constitution Staleness Is Invisible Until It's Visible

A constitution that isn't updated becomes an archaeological artifact rather than a governance document.

The DevSpark constitution went through three months without a meaningful update. During that time, the project evolved: new patterns emerged, new tools were adopted, new architectural decisions were made. The constitution still covered the old patterns. It said nothing about the new ones.

The site audit for those three months found zero violations of the constitution. That looked like a clean bill of health. It was actually a sign that the constitution had drifted from reality.

When I ran `/devspark.evolve-constitution` — the command that proposes constitution amendments based on recent PR history — it produced eight proposed amendments. Four of them addressed patterns that had emerged in practice but weren't in the constitution. The other four clarified principles that had been enforced inconsistently.

The four "missing" amendments were the meaningful ones: the audit had been giving passing scores for code that violated emerging team conventions that weren't yet in the constitution. The constitution was correct as written; it just didn't cover everything that should have been covered.

The practical advice: run `/devspark.evolve-constitution` quarterly. If it produces no proposed amendments, your constitution may be incomplete rather than comprehensive.

## The Single-Model Trap

DevSpark is AI-agnostic by design. The slash commands are markdown files — any AI coding assistant that supports local instruction files can use them. The workflow doesn't depend on any specific model's reasoning capabilities.

But in practice, I do most of my DevSpark work with Claude Code. And I've noticed that some of my prompts and command customizations have drifted toward assuming Claude's specific behavior — the way it formats tables, the way it resolves ambiguous instructions, the way it handles multi-step tasks.

This is the single-model trap: using a framework designed for any agent while optimizing it for one specific agent.

The DevSpark constitution for the DevSpark repository explicitly requires validating prompt changes against two different AI agents. That requirement exists because of the single-model trap. Without explicit multi-agent validation, prompts drift toward the model you use most.

If you're using DevSpark with a single AI agent and plan to continue doing so, the single-model trap isn't a problem. But if you anticipate switching agents (because your organization changes tooling, because a better model becomes available, because you want to use different agents for different tasks), the constitution-level multi-agent requirement is worth adding.

## What Genuinely Gets Better With Time

Despite the caveats above, there are things about DevSpark that genuinely improve with sustained use.

**Specification quality compounds.** The fourth specification I wrote on WebSpark.HttpClientUtility was materially better than the first, not because the framework changed but because I'd learned what makes specifications useful. The right level of specificity, the right questions to ask in clarification, the right scope to commit to — these improve with practice. The first few specs teach you what the subsequent ones need.

**The constitution becomes more accurate.** The first version of any constitution is too vague. After several amendment cycles — driven by `/devspark.evolve-constitution` and by the experience of enforcing it through PR reviews — the constitution converges on principles that are specific enough to generate actionable findings and broad enough to be sustainable.

**PR review becomes a conversation rather than a surprise.** When the PR review is run regularly and findings are addressed promptly, developers build an accurate mental model of what the constitution requires. They stop being surprised by review findings because they've internalized the principles. The review catches the things that fall through anyway — but the number of things that fall through decreases.

**Commit history becomes a resource.** After six months, `/devspark.commit-audit` and `/devspark.repo-story` produce genuinely useful output. The commit history has enough structure — conventional commits, PR linkage, spec references — to tell the story of how the codebase evolved. That story is valuable for onboarding, retrospectives, and for understanding why a particular piece of code is the way it is.

## The Honest Summary

Six months of DevSpark on real projects taught me:

1. The overhead is front-loaded and real. Budget for it. Don't use it as a reason to skip the workflow selectively — selective application is where the confidence trap lives.

2. The critic's value is a lagging indicator. Keep a record of dismissed findings. Review it quarterly.

3. Constitution staleness is invisible. Run `/devspark.evolve-constitution` regularly. A passing site audit score is not the same as a comprehensive constitution.

4. The single-model trap is real if you're using one agent. Add multi-agent validation to the constitution if you care about agent portability.

5. The compounding benefits require sustained use. A framework you use for two sprints and abandon produces none of the compounding benefits. The investment in specification quality, constitution accuracy, and PR review consistency pays off over quarters, not weeks.

The WebSpark.HttpClientUtility specifications are the best evidence I have for the compounding benefits. Four consecutive specifications on one project produced a cumulative improvement that no single specification could have achieved. The clarity from Spec 001 enabled the precision of Spec 002. The cleanliness from Spec 002 enabled the safety of Spec 003. The structure from Spec 003 shaped the design of Spec 004.

That's the claim I can make with confidence: DevSpark's value compounds with sustained use on a real project. The first specification is the most expensive and the least valuable. The fourth is cheaper than the first and worth more.
