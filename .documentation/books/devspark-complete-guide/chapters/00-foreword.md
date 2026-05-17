---
title: "Foreword: Building the Plane While Flying It"
---

# Foreword: Building the Plane While Flying It

There is an old EDS commercial from the early 2000s where a team of engineers assembles an airplane mid-flight — riveting panels to the fuselage while passengers sit inside, laying track ahead of the landing gear as it rolls. The tagline was something about EDS doing the hard work of technology. I saw it once and never forgot it, because it captured something honest about how software actually gets built.

We don't build software on the ground and then fly it. We take off with a half-finished plane and figure out the rest on the way up.

I've been doing this for over thirty years. I started in the era of CASE tools — Computer-Aided Software Engineering — when the industry was convinced that diagrams would replace code and that if you just captured requirements precisely enough, the software would generate itself. Oracle CASE. S-Designer. PowerBuilder. I used them all. They each worked, for a while, in a narrow band of conditions. Then the requirements would shift, or the business would grow in an unexpected direction, or someone would need to do something the tool's code generator didn't anticipate, and you'd find yourself writing around the tool instead of with it.

The pattern repeated so many times I stopped believing it could be broken.

Then large language models arrived and changed the terms of the problem in a way that none of the old tools did. An AI coding assistant doesn't generate code from a diagram. It reasons about code the way a senior developer reasons about code — understanding context, making tradeoffs, applying patterns from a vast knowledge base. The ceiling on what it can help you build is dramatically higher than any CASE tool ever achieved.

But a reasoning system without structure is not a system. It's a conversation. And conversations, left unmanaged, don't produce software — they produce drafts, detours, and creative ambiguity. I discovered this the hard way in the first months I used AI assistants seriously. The output was often impressive. It was not reliable. It did not remember what we'd agreed on yesterday. It did not know what "done" meant. It could not tell me whether the thing we were building was the thing we'd specified, because we hadn't specified anything — we'd just talked.

DevSpark is my answer to that problem. It's a framework of slash commands that gives an AI coding assistant a structured lifecycle: specification before planning, planning before implementation, quality gates before merge. It stores decisions in files the AI can read. It enforces the project's governing principles through every review. It makes the gap between "what we said we'd build" and "what we built" visible and closable.

I built it while using it. The first DevSpark specifications were written using DevSpark itself — a bootstrapping problem I'll discuss in Chapter 19. The framework has governed its own development since the `v0.1.0` tag. If DevSpark couldn't pass its own site audit, that would be a signal that something was deeply wrong.

This book is not a sales pitch. I've tried to be honest about where the overhead is real, where the framework helps most, and where it still has rough edges. The four WebSpark.HttpClientUtility specifications in Part III are real specifications run on a live NuGet package — not cleaned-up examples but the actual decisions and tradeoffs, including the one where eight clarification questions had to be answered before the plan could be written and the one where the critic flagged a risk I'd dismissed and turned out to be right.

If you're looking for a way to make AI-assisted development feel less like improvisation and more like engineering, this book is for you. If you're skeptical that a framework of markdown files can actually change how you work — good. Skepticism is the right starting position. Read the case studies, run the commands on a real project, and see what the data shows.

The plane is in the air. Let's build a better one.

— Mark Hazleton  
Wichita, Kansas  
Spring 2025
