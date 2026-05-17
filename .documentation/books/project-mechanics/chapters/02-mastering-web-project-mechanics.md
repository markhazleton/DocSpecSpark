# Mastering Web Project Mechanics

## The Visibility Problem

> Web projects fail visibly. A back-office system can have problems that the organization manages internally. A website with problems exposes every visitor to them before anyone inside the company is aware. That asymmetry shapes everything.

Web projects fail differently than other kinds of projects. When a back-office system has problems, the organization manages them internally — there's time to assess, prioritize, and fix. When a website has problems, every visitor encounters them: customers, clients, competitors, prospective employees. The failure is visible, immediate, and public before anyone inside the organization is aware it's happening.

This asymmetry shapes everything about how web projects need to be managed. The tolerance for visible failure is lower. The feedback loop is faster. The number of people who have opinions about the outcome is larger. And the technology is changing fast enough that the approach considered standard practice eighteen months ago may already be outdated.

Project Mechanics doesn't change for web projects. The life cycle, the constituency model, the change control discipline — all of it applies. What changes is the context in which that framework operates, and the specific failure modes that web projects generate most reliably.

## The Constituencies Look Different on Web Projects

The three-constituency model — client, staff, and management — holds, but each constituency has web-specific characteristics worth understanding.

**The client** on a web project often has a split identity. There's the organizational client — the business unit, marketing team, or product owner who is sponsoring the work — and there's the end user, who will actually use what gets built. These two groups have different definitions of success, and in web projects the gap between them is often larger than in internal-facing systems.

The organizational client tends to focus on features and functionality: the navigation structure, the content sections, the forms and integrations. The end user cares about whether the site is fast, clear, and actually helps them accomplish what they came to do. Building only for the organizational client's requirements without involving end-user perspectives is how you produce a website that satisfies the brief and frustrates its users. The organizational client may approve the requirements; they're usually not the ones who use the search function, fill out the contact form, or try to find the pricing on a mobile device at 11 PM.

**The staff** on web projects deals with a distinctive technical environment: the intersection of front-end rendering performance, accessibility standards, SEO implications of markup decisions, cross-browser compatibility, and responsive layout concerns, all layered on top of conventional software engineering concerns of security, scalability, and maintainability. Technical choices made in planning have compounding downstream effects that are harder to unwind in a web context than in most other software domains.

This is where the "sidetracked by sizzle" dynamic is particularly acute. Web development is a field with high novelty velocity — new frameworks, new architectural patterns, and new tooling emerge constantly. The professional satisfaction of working with modern technology is real. The discipline of choosing the approach that best serves the project's outcomes — rather than the approach that's most technically interesting — is the project manager's responsibility to maintain.

**Management** on web projects often has difficulty with the long tail of maintenance reality. The tendency to treat a website as a capital project with a completion date — rather than as a living system that needs ongoing stewardship — sets up the gradual decay that makes websites feel stale and frustrating years after launch. Getting the ongoing maintenance structure defined before launch is part of what responsible web project management delivers.

## Planning for Web: What's Different

Web project planning requires attention to elements that don't appear in most generic planning templates.

**SEO implications of technical decisions.** Architectural choices — URL structure, server-side versus client-side rendering, page load performance, use of JavaScript for content search engines need to index — have measurable SEO consequences. Teams that treat SEO as a marketing afterthought rather than a technical constraint tend to discover the problem after launch, when fixing it requires revisiting architectural decisions that were locked in during development. The right moment to involve SEO considerations is during requirements and design, not after go-live.

**Accessibility as a first-class requirement.** Web accessibility — the ability of users with disabilities to effectively use the site — is both an ethical obligation and, in many jurisdictions, a legal requirement. Accessibility is dramatically cheaper to build in during development than to retrofit after launch; a site that fails WCAG AA standards requires rework that often touches fundamental markup and interaction patterns across every page. Treating accessibility as a checklist item at the end of testing rather than as a design constraint from the beginning is a decision that will cost more than it saves.

**Performance as a feature.** Web performance is not a technical optimization to be considered after the site is functional. It is a user experience dimension that affects conversion rates, session duration, and user satisfaction in measurable ways. A site that is fully functional but slow is a site with a significant UX deficiency. Planning should include performance targets established early — not performance tuning conducted after launch when the architectural decisions that most affect performance have already been made.

**Content strategy before content production.** Web projects consistently underestimate the content component. A site architecture exists to organize content; the content should inform the architecture, not the other way around. Projects that design the site and then commission the content tend to produce content that doesn't quite fit the containers designed for it. Content strategy — understanding what content needs to exist, for what audience, in service of what purpose — needs to happen in the planning phase alongside UX and technical architecture.

## Managing Ongoing Change

Web projects are more susceptible than most to scope drift, for two reasons. First, the deliverable is visible in a way that generates stakeholder feedback continuously — as soon as a design direction is shown or a staging environment is available, opinions proliferate. Second, web technology evolves fast enough that a long project can reasonably encounter a technology shift that makes some planned approach obsolete before it ships.

The scope management discipline that Chapter 1 describes applies to web projects with particular urgency. Every change request to a web project needs to be evaluated for its cascading impact on performance, accessibility, and SEO — not just its impact on schedule and budget. A "simple" addition of a third-party analytics tag has performance implications. A "minor" change to URL structure has SEO implications. Web project scope changes are rarely as contained as they appear in a requirements meeting.

The ongoing change reality that follows launch requires its own management structure. A web property managed as a finite project becomes stale; a web property treated as a living system — with a clear owner, a defined process for updates, and an ongoing budget for maintenance — continues to serve its purpose over time. Getting this structure in place before launch is part of what responsible web project management delivers, not an afterthought for the next budget cycle.

## What Successful Web Projects Do Differently

The pattern I've observed in web projects that succeed over time — not just at launch, but a year and two years later — is that they treat the web property as a product rather than a project. Products have owners, roadmaps, metrics, and ongoing investment.

> Treating a website as a capital project with a completion date is how you produce a property that feels stale six months after launch. The moment you declare "done" is the moment the property starts falling behind.

Projects have completion dates. Products don't.

The transition from project thinking to product thinking usually happens at launch, which is too late. The groundwork for product ownership — who is accountable for the site's performance, how changes are prioritized and funded, what metrics determine whether the site is working — needs to be laid during the project, as part of the governance conversation that happens alongside the technical work.

Project Mechanics provides the framework for the build. Product thinking provides the framework for what comes after. Getting both right, before go-live, is the discipline that separates web projects that age well from those that don't.

## Further Reading

- [The Art and Science of Project Management](01-art-and-science-of-project-management.md) — the foundational framework that applies across all project types, including web
- [Sidetracked by Sizzle: Staying Focused on True Value](05-sidetracked-by-sizzle.md) — web projects are particularly vulnerable to technology novelty pulling teams away from business outcomes
- [From Features to Outcomes: Keeping Your Eye on the Prize](04-from-features-to-outcomes.md) — for web projects, conversion rates, session duration, and user task completion are outcomes; features are the means
- [Evolution over Revolution: A Pragmatic Approach](08-evolution-over-revolution.md) — web platforms evolve best incrementally; large redesigns carry the same risks as all rewrites, plus the SEO disruption that comes with URL and structure changes
