# Accountability and Authority: Walking the Tightrope

![Accountability and Authority: Walking the Tightrope — authority is the permission to act, accountability is the obligation to answer for it](/img/MarkHazleton-Authority-Accountability.png)

## Where We Left Off

If you read [When the Pressure Is On: Late Sprint Hotfix Governance](/blog/when-the-pressure-is-on-late-sprint-hotfix-governance/), you know how Dave's Friday ended.

Dave found a payment confirmation bug at 3:47 PM — customers were seeing stale order totals after applying a discount code. He was confident he could fix it in 20 minutes. The product owner wanted it in Tuesday's release. Customer success had four tickets on it. The VP of Sales had forwarded a screenshot from a key account: *"They're asking if we're aware."*

By 4:45 PM, Dave's fix had passed the readiness gate. Root cause confirmed. Code reviewed. Tests green. Rollback plan clear. The team made a deliberate choice: fast-follow. Tuesday's sprint release would ship clean, carrying two weeks of tested work. Dave's fix would deploy separately on Wednesday after dedicated regression coverage.

Dave went home at 5:30.

But the story wasn't over.

## The Monday Morning Meeting

When Dave arrived Monday morning, a calendar invite was waiting: "Urgent — Payment Display Bug / Tuesday Release." The VP of Sales had sent it over the weekend. 10 AM. No agenda.

Dave already knew what it was about.

At 10 AM, the VP opened with a statement, not a question: "I need this fix in Tuesday's release. I spoke with the account over the weekend. They're watching closely. I told them we'd have this resolved by Tuesday morning."

Everyone on the call looked at the engineering lead.

That moment — the pause before an answer, everyone waiting — is where accountability and authority either align or they don't. And what happens next matters more than the fix itself.

## The Authority-Accountability Matrix

The four quadrants tell the story clearly:

| | **High Accountability** | **Low Accountability** |
|---|---|---|
| **High Authority** | Leadership | Recklessness |
| **Low Authority** | Frustration | Irrelevance |

**Leadership** — high authority, high accountability — is the only sustainable quadrant. The PM who owns their decisions and owns the outcomes. The engineering lead who walks into a Monday morning meeting and makes a call they're prepared to defend at 2 AM. This is where effective project governance lives.

**Recklessness** — high authority, low accountability — is the VP of Sales in the Monday morning meeting. They have enough organizational power to influence the release decision. When it goes wrong at 2 AM, they won't be on the call. Authority without accountability corrodes trust faster than any technical failure.

**Frustration** — low authority, high accountability — is every team lead I've watched be held responsible for delivery dates they couldn't control. The coordinator accountable for quality that depends on decisions made above them. This quadrant is where burnout lives, where good people eventually stop trying to change things they can't affect.

**Irrelevance** — low authority, low accountability — is what happens to a project manager who has been stripped of decision rights and learned to stay out of the way. They're still on the org chart. They're not managing anything.

> Authority is the permission to act. Accountability is the obligation to answer for it. You cannot have one without the other without creating a dysfunction that eventually destroys both.

The goal of good governance is to keep the people with accountability in the high-authority quadrant. That sounds obvious. It's remarkably rare in practice.

## What the VP Was Actually Asking For

The VP of Sales was acting on a real business concern. Customer relationships matter. A key account's confidence matters. The frustration behind the request was completely legitimate.

But let's be precise about what the VP was actually doing.

**Authority** is the ability — formally granted or informally earned — to act and direct others. The engineering lead has it over the release schedule. The VP does not — not because their urgency isn't real, but because they won't be the one fielding calls at 2 AM if the release ships broken.

**Accountability** is the obligation to answer for what those actions produce. The engineering lead is accountable for Tuesday's release stability. The VP of Sales is accountable for the customer relationship — but not for what ships on Tuesday, and not for what breaks if something goes sideways in the middle of the night.

When the VP demanded the Tuesday release, they were exercising influence as a proxy for authority. They had made a commitment to a key account over the weekend without the authority to make that promise, and were showing up Monday to collect on it — while the engineering lead would own whatever happened next. It tends to be invisible to the person doing it, because from inside the urgency, making commitments feels like leadership.

This misalignment has two common forms. The most visible is **accountability without authority**: a team lead held responsible for delivery dates they don't control, a coordinator accountable for quality that depends on decisions made above them. That's where Dave had been on the edge of on Friday — implicitly accountable for customer impact from a bug, without authority over when to deploy the fix. The governance framework gave him a structured path through it.

The less visible but more dangerous form is **authority without accountability**: the ability to shape decisions without facing the consequences if they turn out wrong. That's closer to what the VP was doing on Monday — applying enough pressure to change the deployment decision, while the engineering lead would own the outcome either way.

## What the Engineering Lead Said

The engineering lead's response on that call is worth walking through carefully, because it's the model.

They didn't argue about the fix. They didn't relitigate the Friday decision. They didn't say "we told you so."

They said: "We can add Dave's fix to Tuesday's release. But here's exactly what that means: we compress QA's window from two days to one, across all fourteen features in the release. We're asking QA to sign off on a last-minute injection they've had less than a day to review. If they find a problem — or if there's an interaction we didn't catch — we're looking at a delayed Tuesday release or a partial rollback at 2 AM. Are you comfortable signing off on that risk for a display issue that doesn't affect customer charges?"

Silence.

Then: "What's the alternative?"

"Wednesday. Dave's fix deploys cleanly in its own release window with full regression coverage. The key account sees it resolved within 24 hours of Tuesday's release. We protect the quarter's deliverables from a rushed patch."

The VP said they'd call the account back.

The call ended in seven minutes.

## Why That Response Worked

The engineering lead did several things in that moment worth naming explicitly.

**They made the tradeoffs visible, not the decision itself.** They didn't say "no, we're not doing it." They said "here's exactly what yes means — now who's signing off?" That reframe puts the accountability where it actually belongs. It's no longer the engineering lead protecting a process; it's the VP deciding whether to accept a specific, named risk.

**They protected the team from unearned accountability.** QA was not going to be set up to absorb a last-minute change and then blamed if something broke. The engineering lead owned the decision and made it clear they owned it. That clarity is a form of protection.

**They used authority in service of the team, not in service of themselves.** This is the principle the French call *noblesse oblige* — "nobility obligates." The idea is simple: those who hold power or advantage have a corresponding duty to use it responsibly, in service of others. The engineering lead had the authority to say no. They used that authority to absorb the external pressure rather than let it flow downward onto people who couldn't redirect it.

A manager who simply passes VP pressure down unchanged — "the VP says we need it Tuesday, so figure it out" — hasn't exercised authority. They've changed the shape of the accountability-without-authority trap and handed it to the team.

## Noblesse Oblige in Practice

*Noblesse oblige* tends to get dismissed as a relic of aristocratic self-justification. But the underlying principle outlasted the aristocracy because it describes something real: authority without obligation corrodes. People who wield power without caring about what it does to others eventually find the authority withdrawn, one way or another.

In a leadership context, it shows up in smaller, everyday choices. It's the manager who absorbs criticism from above rather than passing it down unchanged. It's the project lead who advocates loudly for resources the team needs even when it's uncomfortable. It's the engineering lead who walks into a Monday call and takes the shot so QA doesn't have to.

Think about the CTO who sits through six months of board-level panic about a missed revenue target — fielding uncomfortable investor questions, absorbing the anxiety in quarterly reviews — specifically so the development team can focus on a complex, high-risk database migration without that dread flowing downstream. Or the middle manager who takes the full brunt of an enterprise client's anger over a missed SLA, declining to name the junior developer whose code caused the breach, because that developer already knows what went wrong and needs to fix it — not spend the next week in damage-control conversations they're not equipped to navigate.

Most people who have spent a few years in tech have been on one side of those scenarios or the other. The pattern is consistent: leaders who use their authority to absorb pressure tend to build teams that perform under it. Those who pass the heat downward tend to find that their teams get very good at protecting themselves first.

## The Buck Actually Stops Here

Harry Truman's desk sign — "The buck stops here" — has become a cliché. The principle hasn't.

The engineering lead on that Monday call owned Tuesday's release. That meant they could decide what went into it. It also meant that if the release shipped broken, the questions would run through them. Both things were true simultaneously. That's what accountability paired with authority looks like in practice: not a performance of responsibility, not "we decided as a team." The decision was theirs, the call was theirs, and the outcome — good or bad — was theirs.

What it didn't mean was making decisions arbitrarily or without transparency. The reasoning was visible. The tradeoffs were named out loud. That transparency is what makes authority defensible — to the VP, to the team, and to yourself at 2 AM if something goes wrong.

**Be explicit about what authority you're granting.** When you delegate, name the decision rights that come with the assignment. "You own this — bring me the outcome, not every intermediate decision" is very different from "check with me before committing to anything." Ambiguity here creates exactly the accountability-without-authority trap.

**Remember that authority can be delegated but accountability cannot.** You can hand off the ability to act. You cannot hand off the obligation to answer for results. The chain still runs through you.

**Never blame a subordinate for something you are accountable for.** When something goes wrong, the person with the most authority in the relevant decision chain owns the outcome. Redirecting that downward undermines trust in a way that's genuinely hard to rebuild.

**Watch for the frustration signal.** When someone on your team is consistently frustrated by their inability to move something they're being measured against, the most likely explanation is that they're accountable for something they can't control. That's a solvable problem — if you recognize what you're looking at.

## What Happened

Tuesday's sprint release shipped clean. Fourteen features. No drama. No last-minute injections. No 2 AM Slack messages.

Wednesday morning, Dave's fix deployed in its own release window. Full regression coverage. The display issue resolved. The key account's customer success team received a note that the fix was live.

The VP of Sales followed up with the engineering lead after Wednesday's deploy: "That was actually smoother than I expected. Good call."

That's the quiet reward of holding the line — not applause in the moment, but trust built over time. Stakeholders who initially push back on "not yet" tend to become the most vocal defenders of the process once they've seen it work twice.

## What This Means If You're in the Room

If you're the engineering lead in this story, your job in that Monday call is to be the authority that doesn't blink — not from stubbornness, but because you've thought through what you're actually protecting and you can explain it in business terms.

If you're the VP of Sales, start here: your accountability to revenue means your urgency is completely justified. A key account threatening to churn is a real emergency, and the impulse to solve it immediately is exactly what your role demands. The problem isn't the urgency — it's the form it takes.

Walking into a Monday meeting and saying "I need this in Tuesday's release" is dictating a technical solution you don't have the authority to own the consequences of. The engineering lead now has to either comply with a decision that's yours but a risk that's theirs, or spend political capital pushing back. Neither outcome serves the customer.

There's a better script. Instead of "I need this in Tuesday's release," try: *"The client is threatening to churn over this bug. What's the fastest safe way we can get a fix live?"* That one shift — from solution to problem — changes the entire dynamic in the room. It communicates the full weight of the business urgency while explicitly deferring to engineering's authority on what constitutes safe. You become a partner bringing a problem to people with the expertise to solve it, rather than an executive overriding a process you don't own.

That's not backing down from the customer. That's recognizing that your authority over the customer relationship and engineering's authority over the release train are different things — and that the best outcome for the customer happens when both are respected.

If you're Dave, your job is to understand that your accountability for the fix quality doesn't extend to the deployment decision, and that the framework protecting Tuesday's release is also protecting you from being blamed for a rushed deployment you didn't control.

The tightrope isn't a metaphor for a rare, difficult moment. It's the daily condition of leadership. Walking it well — holding accountability and authority in deliberate, honest alignment — is one of the more consequential skills you can develop. And when you hold the line the right way, for the right reasons, you don't just protect Tuesday's release.

You build the kind of trust that means the VP of Sales calls you first next time — before making promises.

## Further Reading

- [When the Pressure Is On: Late Sprint Hotfix Governance](/blog/when-the-pressure-is-on-late-sprint-hotfix-governance/) — the full story of Dave's Friday and the decision framework that made the fast-follow defensible
- [The Managed Transition Model: Leadership Promotion as Power Exchange](/blog/the-managed-transition-model-leadership-promotion-power-exchange/) — how authority and accountability shift when leadership roles change hands
- [From Features to Outcomes: Keeping Your Eye on the Prize](/blog/from-features-to-outcomes-keeping-your-eye-on-the-prize/) — accountability without measurable outcomes is accountability without a compass
- [Project Leadership in the Project Mechanics framework](/project-mechanics/leadership) — delegation, empowerment, and building team environments where authority and accountability are clear
