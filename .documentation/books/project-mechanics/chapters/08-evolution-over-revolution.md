# Evolution over Revolution: A Pragmatic Approach

![Evolution over Revolution - A Pragmatic Approach to Software Development](/img/MarkHazleton-Evolution-over-Revolution.png)

## The Retrospective That Changed Everything

Thursday afternoon: sprint retrospective.

The team worked through the usual rhythm — what went well, what didn't, what to try differently next sprint. Then Dave spoke up.

"Before we close out, I want to flag something. This is the third time in six months we've patched a caching bug in the cart service. The most recent one was a missing cache invalidation call — actively losing the business money by serving stale discount totals. Before that it was a stale session cache. Before that, cache TTL drift on high-volume SKUs. We keep treating symptoms. The underlying problem is that the cart caching layer was written in a hurry during the 2023 platform migration and nobody has touched the design since. I want to propose a full rewrite."

The room went quiet in a particular way — the quiet of people who have heard this kind of proposal before and aren't sure whether they agree or just feel the pull of it.

Jordan, one of the senior developers, asked the question nobody else had raised yet: "What does rewrite actually mean, exactly?"

Dave had his notes ready. He'd been building the case since the last outage.

## What "Rewrite" Actually Costs

Jordan's question wasn't skeptical. It was sincere. But it forced Dave to be precise.

"A proper service extraction," Dave said. "Clean repository. Modern caching patterns. No more bolted-on invalidation logic spread across three files. I'm thinking five to six weeks, assuming we don't get pulled into other priorities."

Jordan walked to the whiteboard and drew two columns: **Revolution** and **Evolution**.

Under Revolution: five to six weeks minimum. Cart feature development frozen during the build. Every edge case in the existing system rediscovered from scratch. All session handling re-tested from zero. And one constraint neither of them had fully reckoned with: the cart service was processing live transactions right now. There was no pause window, no maintenance window long enough, no moment when the system could simply stop while a replacement was built.

Under Evolution: one sprint on test coverage and documentation of the existing caching logic. One sprint on targeted refactoring of the invalidation layer — the three files with bolted-on logic consolidated into one well-named function. One sprint on an incremental cache-key redesign, deployed behind a feature flag. At the end of three sprints, the caching behavior would be solid, well-tested, and understood. Cart feature development would continue throughout.

Dave looked at the two columns. He had come into the retro certain about the answer. He was considerably less certain now.

"The rewrite gets us a cleaner design," Jordan said. "No question. But where are we after sprint three? We're mid-rewrite. Cart features are frozen. The existing system is still handling all live traffic because we haven't shipped anything yet. We've spent six weeks getting to the point where the evolutionary path would have already delivered a substantially better codebase — and kept shipping features the whole time."

Dave started to push back, but Jordan was already drawing a timeline across the bottom of the whiteboard.

"You know about Duke Nukem Forever?"

Dave did. Every developer did.

"Fourteen years," Jordan said. "Scott Miller's team at 3D Realms kept rebooting every time a better engine came along. Each restart made perfect sense on its own — why ship on last year's tech when this year's is right there? But cumulatively, the pattern destroyed the project. When it finally shipped in 2011, it couldn't match expectations that had been compounding for over a decade." He tapped the Revolution column. "If we freeze cart development to rewrite from scratch, and three weeks in product discovers a new edge case in multi-currency pricing — which they will — it resets our timeline. We end up chasing a moving target, shipping nothing, while the old code handles every live transaction."

Dave had heard enough rewrite horror stories. But he had a counterargument ready. "And what if we spend three sprints polishing a system that's fundamentally broken? What if the problem isn't the invalidation logic — what if it's the infrastructure underneath it?"

Jordan nodded slowly. That was the right question.

"Last year," Jordan said, "the platform team spent three full sprints refactoring the session-invalidation layer in the notification service. Clean test coverage, careful incremental deploys, everything by the book. Two days after they shipped the final improvement, infrastructure announced the underlying message broker was being deprecated. The entire data model was incompatible with the replacement. Three sprints of disciplined evolutionary work — completely useless. They had to rewrite the service from scratch anyway."

The room was quiet again.

"That's why I don't argue evolution is always the answer," Jordan said. "But here's the difference: I know our cache infrastructure isn't going anywhere. The Redis cluster was upgraded last quarter. The cart schema is stable. The problem is genuinely in the invalidation logic, not in the foundation underneath it."

He wrote one more line on the whiteboard — a boundary condition: *If the cache-key redesign requires altering the core order-processing schema, we stop.*

"We take the evolutionary path for two sprints," Jordan said. "But if we discover the foundation is the problem — not just the logic on top of it — we re-evaluate. At that point it's not evolution anymore. It's a hack, and we design a targeted rewrite with a real exit condition and a staffing plan."

## The Illusion of the Clean Slate

The appeal of the rewrite is partly aesthetic. A clean repository, modern patterns, no accumulated cruft. But that framing misses something important: the problems embedded in an existing system are usually not architectural accidents. They're scar tissue from decisions that made sense at the time — integration constraints, edge cases that only appeared in production, workarounds for dependencies that no longer exist but whose absence was never documented.

A rewrite doesn't transfer that knowledge. It discards it. Teams spend months not just rebuilding the system but rediscovering why it works the way it does — often arriving at something that looks cleaner but behaves in subtly worse ways until it has accumulated the same lived-in complexity it was meant to replace.

Dave was right that the cart caching layer was messy. It was. But that messiness contained twelve production edge cases, four of which had never been formally documented anywhere. Writing the test coverage in sprint one of the evolutionary path would surface all twelve. A rewrite would have to rediscover them under production pressure — the hard way.

## Building the Plane While Flying It

Electronic Data Systems had a phrase that Dave's retro argument had to eventually reckon with: *building the plane while flying it.* The cart service wasn't a system that could be taken offline, redesigned, and relaunched. It was processing live transactions. The 2023 migration that left the caching layer in rough shape had been done under exactly those conditions — and the team had made the best calls they could while keeping the system running.

A full rewrite required landing the plane. There was no runway.

The evolutionary alternative was designed for this condition. Rather than a complete service replacement as a big-bang event, you build the improved implementation incrementally, test it against real production behavior behind a feature flag, and route traffic to the new path as confidence grows. Azure Front Door and similar traffic managers make this tractable at the infrastructure level; feature flags handle it at the application layer. The new component gets tested against real production traffic. Issues surface in a controlled way. The existing system remains operational throughout.

None of this means the changes are small. Evolutionary development can involve large code changes and significant structural refactoring — replacing an entire caching strategy, rewriting an invalidation pipeline, swapping out a data access layer. The difference isn't the size of the change. It's that the system keeps working the whole time. The business stays in the air. Customers keep checking out. Revenue keeps flowing. The alternative — grounding the plane in a hangar for months while a team rebuilds it from the landing gear up — means nothing is flying. No features ship. No bugs get fixed. The business absorbs all of the risk of the rebuild with none of the incremental benefit.

It's a delicate balance between risk and reward. Every structural change made to a live system carries the possibility of breaking something that's currently working. But that risk is managed — feature flags, incremental rollouts, documented rollback paths, production-validated test coverage. The risk of the hangar approach isn't managed at all. It's deferred. Everything rides on the moment the rebuilt plane attempts its first takeoff, and by then months of accumulated assumptions are being tested simultaneously.

These aren't workarounds. They're the mature engineering practice for systems that can't be paused. And they're the practice that lets teams execute genuinely ambitious architectural change — not just trim-tab adjustments — without forcing the business to hold its breath for six weeks.

## When Revolution Is Actually the Answer

None of this is an argument that systems should never be replaced. Sometimes the accumulated technical debt really is too severe. Sometimes the underlying platform has shifted so fundamentally that incremental migration isn't honest — Jordan's notification service story was proof of that. Sometimes a project has genuinely run its course.

The key is entering that decision with clear eyes: a realistic picture of what the existing system contains, a genuine plan for what the new one will look like and how it will get there, adequate resources to execute, and — critically — a credible exit condition. How will you know when the rewrite is done? What does "done" look like, specifically?

Duke Nukem Forever wasn't a failure because its developers chose to rebuild. It was a failure because they rebuilt repeatedly without a roadmap, without adequate staffing, and without an answer to that last question. Each individual reboot decision made sense. The pattern destroyed the project.

Dave's proposal was missing the exit condition. "A proper rewrite" is an intention, not a plan. The evolutionary alternative had a concrete plan: sprint one delivers documented test coverage, sprint two delivers targeted invalidation refactoring, sprint three delivers improved cache-key design behind a feature flag. Each sprint ships something independently useful. The team can stop at any checkpoint with a net improvement over where they started. And Jordan's boundary condition gave them a clear, measurable signal for when to abandon the incremental approach and escalate.

The rewrite had no equivalent checkpoint.

Robert J. Kriegel and Louis Palter's [*If It Ain't Broke... Break It!*](https://a.co/d/bg9eJrg) makes the counterargument compellingly: complacency — the comfort of the status quo — is its own form of failure. Sometimes genuine progress requires the willingness to break what seems to be working. That's worth taking seriously. The danger of the evolutionary framing is that it can rationalize avoidance, patching something that genuinely needs to be rethought because change feels risky.

The distinction is between *calculated disruption* — knowing what you're breaking, why, and what success looks like on the other side — and *reckless revolution* — starting over because the existing thing is frustrating. Dave's frustration was legitimate. The design wasn't. Not because a cart service rewrite could never be the right call, but because this proposal lacked the specificity that makes revolution something other than Duke Nukem Forever.

## Three Sprints Later

Dave took the evolutionary path. He didn't love it at first. Writing tests for code he wanted to discard felt like polishing something he'd rather burn.

Somewhere during sprint two, staring at the invalidation logic he was refactoring instead of replacing, he thought about Betamax. Technically superior to VHS in every way that should have mattered — better video quality, cleaner engineering. But VHS won anyway, because JVC focused on practical advantages: longer recording times, lower manufacturing costs, licensing terms that encouraged wider distribution. None of those were glamorous improvements. They were evolutionary adjustments aimed at what consumers actually needed — recording a full football game, finding tapes at the local video store, affording the hardware on a normal budget. The cart service didn't need to be beautiful. It needed to stop producing stale discount totals and ship on Friday.

But the tests found the edge cases. All twelve of them. Including one that had never surfaced in three years of production use: a silent data-loss scenario in a specific multi-currency cart configuration that would have appeared in the rewrite's first month in production and been blamed on the new code.

Sprint two's targeted refactoring cleaned up the invalidation logic. The three files with scattered, bolted-on invalidation calls became one well-named function with documented behavior and test coverage. It still wasn't beautiful. But for the first time, it was comprehensible — a new engineer could read it and understand what it was doing and why. By the end of sprint two, it was clear they wouldn't hit Jordan's boundary condition. The cache-key redesign could be implemented entirely within the caching layer — no changes to the core order-processing schema required. The foundation was sound. The logic on top of it had just needed a disciplined hand.

Sprint three's cache-key redesign was the satisfying part. The clean architecture Dave had been imagining, implemented in the specific layer where it was needed, validated against twelve documented edge cases, deployed incrementally behind a feature flag with a clean rollback path. The feature flag came down on a Thursday morning. Zero incidents.

Three sprints in, the cart caching module was solid, tested, and documented. Not a clean slate. Something better: a system whose behavior was understood, whose edge cases were covered, and whose improvements had been delivered while cart feature development continued uninterrupted at full pace.

The rewrite, had they chosen it, would have still been in progress.

## A Useful Frame for Every Project Decision

The question that cut through the retro argument was the one Jordan had been circling from the start: *what's the minimal change that moves us meaningfully forward?*

"Minimal" doesn't mean trivial. Sprint two's refactoring was real work. The cache-key redesign in sprint three was a genuine architectural improvement. "Minimal" means targeted — not taking on more disruption than the change actually requires.

That question keeps teams honest. "Rewrite the cart service" answers with an ambition. "Refactor the invalidation layer, add test coverage, and redesign the cache-key structure over three sprints" answers with a plan. Plans are buildable. Ambitions are where Duke Nukem Forever lives.

Agile practices exist for exactly this reason. Sprints create forcing functions for prioritization. Retrospectives surface small problems before they compound into large ones. The continuous feedback loop keeps teams aligned with what users actually need rather than what developers imagine they should need.

The impulse that drives "we need to rewrite this" comes from the same place as the impulse that made Dave stay at his desk until 4:45 on a Friday to make sure his fix passed every gate before it went anywhere near production. It comes from caring about the work. The discipline of evolution isn't about dulling that impulse. It's about channeling it into changes that actually ship, compound, and hold.

## Further Reading

- [When the Pressure Is On: Late Sprint Hotfix Governance](/blog/when-the-pressure-is-on-late-sprint-hotfix-governance/) — where Dave's story began: the Friday bug, the readiness gate, and the fast-follow decision
- [Accountability and Authority: Walking the Tightrope](/blog/accountability-and-authority-walking-the-tightrope/) — the Monday morning that followed, and what it revealed about who actually owns what
- [From Features to Outcomes: Keeping Your Eye on the Prize](/blog/from-features-to-outcomes-keeping-your-eye-on-the-prize/) — evolutionary progress only means something if it's moving toward the right outcome
- [Building Resilient .NET Applications with Polly](/blog/building-resilient-net-applications-with-polly/) — practical patterns for incrementally improving application resilience
- [*If It Ain't Broke... Break It!*](https://a.co/d/bg9eJrg) — Kriegel & Palter's case for strategic disruption, worth reading alongside the evolutionary argument
