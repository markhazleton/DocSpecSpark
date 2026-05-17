---
title: "Chapter 2B: The Pipeline Lesson — What MuseumSpark Taught Me About When to Use LLMs"
part: "Part I: Why DevSpark Exists"
---

# Chapter 2B: The Pipeline Lesson — What MuseumSpark Taught Me About When to Use LLMs

> **What you'll learn in this chapter:**
> - Why using LLMs as researchers produces worse results than using them as judges
> - How a 71% failure rate led to a complete architectural rethink
> - What "context first, judge second" means in practice
> - Why building the pipeline is often more valuable than the output the pipeline produces

I'm going to tell you about a museum database I almost built the wrong way.

It started with a text from my daughter: "Dad, I ran out of ChatGPT tokens. Can I use your Pro account to finish this prompt?"

She was building a trip-planning dataset for Walker reciprocal network museums — a sortable, scorable list with impressionist collection strength, admission costs, visit time estimates, and priority rankings. Her approach was to ask ChatGPT to generate it all: the museums, the data, the scores, the structure. State by state, city by city, alphabetically through all fifty states.

She hit her token limit somewhere around Arizona. She had incomplete museum lists, inconsistent formatting, unverifiable data, and forty-seven states to go.

I didn't give her my Pro account credentials. I built MuseumSpark instead.

## The First Version Got It Wrong

When I started, I made a predictable mistake: I handed the problem directly to the most powerful LLM I had and asked it to solve everything at once.

The prompt was roughly: "You are a museum expert. For each museum, research its collections, evaluate its impressionist and modern art holdings, assign scores from 1–5, and fill in any missing location and admission data."

This sounds reasonable. An expert researcher who also scores — why wouldn't that work?

The answer showed up in my output as `imp=?` — the shorthand I'd used to flag museums where `impressionist_strength` returned null. A few nulls were expected. But when I processed Colorado as a test run — 19 museums, $1.14 in API costs — five out of seven museums came back with null scores. Museums I knew had world-class impressionist collections were refusing to score.

The model wasn't broken. It was being honest about its uncertainty. The prompt said "return null if you lack sufficient evidence." So when I gave it a museum name, a city, and not much else, it returned null rather than guess. Which was the right behavior for a wrong architecture.

The real number was 71% failure. For a dataset of 1,269 museums, that meant over 900 museums with unusable scoring data.

## The Analysis

When I went looking for the cause, the failure wasn't in the model's capability — it was in how I'd structured the work.

Four problems were intertwined:

**Research and judgment were tangled together.** I was asking the model to discover facts (what does this museum's collection actually contain?) and simultaneously make judgments (given those facts, how strong is the impressionist collection?). These are different tasks with different requirements. Research requires finding and verifying specific information. Judgment requires applying expertise to evidence. I'd handed both to the same prompt at the same time.

**Context wasn't gathered before judgment was requested.** The Wikipedia article, the museum's own website, the IRS 990 filing — none of this was being assembled before I asked for a score. The model was being asked to judge in the absence of evidence.

**The prompts were punitive about uncertainty.** "Return null if insufficient evidence" is a reasonable instruction for preventing hallucination. It's also an instruction that causes a well-calibrated model to return null any time it has only partial evidence, even when that partial evidence — combined with the model's trained knowledge — would be enough for a reasonable assessment.

**There was no separation of phases.** Everything happened in one call: ingest a museum name, produce a fully scored and enriched record. The failure mode of "I don't have enough information" cascaded across all outputs simultaneously.

## The Rebuild: Context First, Judge Second

I rebuilt MuseumSpark around a single principle: **gather context first, then ask LLMs to judge.**

The pipeline became ten phases, each with a specific responsibility and clear input/output contract:

```
Phase 0:   Google Places (identity, coordinates)
Phase 0.5: Wikidata (website, postal code, address)
Phase 0.7: Website Content (hours, admission, collections)
Phase 1:   Backbone (city tier, visit time, clustering)
Phase 1.5: Wikipedia Enrichment (art museums only)
Phase 1.8: CSV Database (IRS 990 data, phone numbers)
─── Context Gathered. Now Judge. ───────────────────
Phase 2:   LLM Scoring (judgment only, NOT research)
Phase 2.5: Content Generation (web-ready descriptions)
Phase 3:   Priority Scoring (deterministic math, no API)
```

Every phase wrote its output back to the same state JSON file — `data/states/{STATE}.json`. Every subsequent phase checked whether its output was already present before doing any work. The caching was built into the architecture from day one, not retrofitted.

What changed at Phase 2 wasn't just the prompt. It was what the model received before the prompt. Instead of a museum name, it received an evidence packet:

```json
{
  "museum_name": "Art Institute of Chicago",
  "museum_type": "art",
  "wikipedia_extract": "...one of the oldest and largest art museums...",
  "wikipedia_categories": ["Impressionist museums", "Modern art museums"],
  "website_content": {
    "collections": ["French Impressionism", "Modern Art"],
    "hours": "10am-5pm daily",
    "admission": "$25 adults"
  },
  "context": "Located in Chicago, IL. 4 nearby art museums."
}
```

The prompt changed from "research and score this museum, return null if insufficient evidence" to "you are a museum expert, use your knowledge combined with the evidence provided to make informed assessments."

The Art Institute of Chicago went from `imp=? mod=?` to `imp=4 mod=4`. Success rate across the full dataset went from 29% to 95%.

Total cost for all 1,269 museums: $31.94.
Rerun cost after prompt changes or model upgrades: $0.

## What the Pipeline Actually Taught Me

The caching number is the one I keep coming back to. Not the $32 total cost — that's impressive, but it's downstream. The $0 rerun cost is the structural insight.

Because I'd invested in building the pipeline, every improvement to the judgment phase was free to apply. I changed the scoring prompt four times. I switched the content generation model partway through. I added a new Wikipedia category signal after the initial run. Each change required only re-running the affected phase on the records that hadn't yet been processed with the new logic. Everything upstream was cached.

This is the investment pattern I hadn't fully understood before MuseumSpark: **the pipeline is more durable than the output.**

The specific scores in the database will drift as museums change their collections. The LLM I used will be replaced by a better one. The prompt engineering best practices will evolve. But the phase structure, the caching strategy, the separation of context-gathering from judgment — those hold. They survive model upgrades. They survive prompt iterations. They survive the discovery that you needed one more data source that you didn't know about at the start.

My daughter had tried to build the output directly. She got fragile, unverifiable output that couldn't survive a context window reset. I built the pipeline that produces the output. The pipeline is still running. The output improves every time I learn something new.

## The Transfer to Software Development

Here is why this story belongs in the opening of a book about DevSpark.

DevSpark is the same pattern applied to software development.

When a developer opens a conversation with an AI coding assistant and types "add user authentication to this application," they're making the same mistake I made in my first MuseumSpark prompt. They're handing the AI a vague task and expecting it to simultaneously research the codebase, understand the constraints, identify the right approach, and generate correct code — all in one shot. Sometimes it works. When it doesn't, the failure mode is inconsistencies, missing edge cases, and outputs that don't align with what the project actually needs.

The DevSpark approach is to separate the phases. Before the AI writes code, it reads the specification. Before the specification exists, requirements are gathered and clarified. Before clarification, the problem is scoped. Before implementation is accepted, the output is reviewed against the project constitution.

The spec is the evidence packet. The constitution is the accumulated context about what "good" means for this project. The phases are the separation of concerns that keeps judgment tasks from being polluted by research tasks.

The AI doesn't research and judge at the same time in DevSpark. It specifies first, plans second, implements third, reviews fourth. Each phase has clear input, clear output, and a clear responsibility. The context is gathered before the judgment is requested.

There's another parallel. The $0 rerun cost in MuseumSpark corresponds to the value of the specification artifacts in DevSpark. When a developer returns to a feature six months later, the spec is still there. When a new team member joins, the spec documents the decisions and the trade-offs. When the AI model is upgraded, the spec is the stable input that produces consistent results from the new model. The artifacts are more durable than any single output.

## What LLMs Are Actually For

Before MuseumSpark, I would have described LLMs as tools that can "do a lot of different things." After MuseumSpark, I describe them more precisely: LLMs are excellent judges when given structured evidence. They are poor researchers when given vague instructions.

That's a constraint, not a criticism. A judge needs a case file — evidence, context, the governing rules. Give a judge a blank room and ask them to figure out what the verdict should be, and they'll either guess or refuse. Give them the case file and ask for a verdict, and they'll apply expertise you couldn't replicate manually.

Every time I've seen an AI coding assistant produce inconsistent or low-quality output, the root cause has been the same: the assistant was asked to be a researcher and a judge simultaneously, without the structured context that judgment requires.

DevSpark's job is to make sure that structured context exists before judgment is requested. Not because the AI isn't capable — but because the capability is only accessible when the context is right.

My daughter spent her ChatGPT quota trying to generate a museum dataset from nothing. I built a pipeline that enriched 1,269 verified museums for $32 total.

The difference wasn't the model. The difference was the pipeline.

---

> **Connection to DevSpark**
>
> The MuseumSpark pipeline phases — context gathering, then judgment, then deterministic derivation — map directly to DevSpark's workflow stages. `/devspark.specify` is context gathering: it forces scope, constraints, and open questions to be resolved before implementation begins. `/devspark.plan` converts that context into structured tasks. `/devspark.implement` gives the AI a structured input for what would otherwise be vague instructions. `/devspark.pr-review` applies the constitution as the governing rules for judgment. The AI operates as a judge with a case file at every stage, not a researcher improvising from a blank slate.
