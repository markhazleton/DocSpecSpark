---
title: "Introduction"
---

# Introduction

DevSpark is a set of twenty-eight slash commands. That's the whole thing. No server, no database, no proprietary platform. When you install it, you get a directory of markdown files that your AI coding assistant reads as instructions. When you type `/devspark.specify`, your agent reads the instructions in that file and runs a structured intake workflow. When you type `/devspark.pr-review`, it reads your project constitution and your recent changes and produces a review organized by severity.

The insight behind DevSpark is that AI coding assistants are already capable of doing structured, methodical engineering work. They don't need new capabilities. They need prompts that channel those capabilities into a repeatable workflow — and a project constitution that tells them what "good" looks like for your specific project.

This book explains how that works, why it works, and how to get the most out of it in practice.

## What This Book Covers

The book is organized into five parts.

**Part I — Why DevSpark Exists** covers the problem that DevSpark solves and the history that informed how it was designed. Chapter 1 traces forty years of code generation tools — from Oracle CASE to PowerBuilder to modern AI assistants — and identifies the recurring pattern that made most of them fail. Chapter 2 tells the specific story that crystallized the problem: a hotfix I shipped on a legacy system that bypassed every quality gate I'd built, violated the project constitution, and worked anyway. That story revealed a gap in my own framework that I had to close. Chapter 2B steps back from software development entirely and tells the story of MuseumSpark — a museum data enrichment pipeline — which turned out to be the clearest demonstration I've found of when LLMs help and when they fail: they are excellent judges given structured evidence, poor researchers given vague instructions. The pipeline lesson from that project is the conceptual foundation for everything DevSpark does.

**Part II — How DevSpark Works** is the conceptual foundation. It covers the three pillars (project constitution, slash commands, tiered prompt resolution), the installation process, and how to write a constitution that actually gets enforced rather than ignored. If you read nothing else before running the quickstart, read Chapters 3 through 6.

**Part III — DevSpark in Action** is the heart of the book. Four consecutive production specifications on a single real project — WebSpark.HttpClientUtility, a .NET NuGet package with over ten thousand downloads — demonstrate the complete DevSpark workflow end to end. Each specification is documented with real decisions, real tradeoffs, and honest accounting of where the framework helped and where it added friction. You'll see what a 37KB specification looks like, what happens when eight clarification questions reveal a fundamental scope disagreement, and what an atomic package split accomplished that a single-PR refactor would have broken.

**Part IV — Advanced Architecture** covers the deeper capabilities: quality gates, the tiered prompt model, autonomy levels and guardrails, the optional harness runtime for declarative workflow execution, multi-agent team patterns, and monorepo support. Most developers won't need all of this immediately, but it's here when you're ready for it.

**Part V — Living with DevSpark** covers what happens after the first week. Chapter 19 describes building DevSpark on itself — the bootstrapping problem and what six months of commit history reveals about the framework's health. Chapter 20 documents the harder lessons: where the overhead is real, what the critic is actually for, and why a constitution that never gets updated is a constitution that stops working.

The appendices provide a complete command reference, four ready-to-use constitution templates for common project types, and a troubleshooting guide for the most common installation and runtime problems.

## Who This Book Is For

**Solo developers** who want AI-assisted development to produce consistent results rather than brilliant improvisation. If you've experienced the frustration of describing a feature to an AI assistant, getting something impressive, and then realizing three days later that it doesn't match what you actually needed — this book addresses that gap directly.

**Technical leads and staff engineers** who are responsible for maintaining quality standards across a team that uses AI tools. DevSpark's constitution model gives you a place to codify what "good" means for your project, and the PR review command enforces it consistently.

**Developers adopting AI tooling for the first time** who want to start with good habits rather than retrofitting structure later. The quickstart takes less than ten minutes. The habits it installs take months to fully appreciate.

You should be comfortable with command-line tools and have a working installation of at least one AI coding assistant: Claude Code, GitHub Copilot, or Cursor. No particular programming language or framework is required — DevSpark is language-agnostic.

## How to Read This Book

If you're new to DevSpark and want to get started quickly, read the Foreword and Chapters 3 and 4, then run the installation. Come back to Chapter 5 (the constitution) once you've seen the default behavior and want to customize it. Return to Part III when you want to see a complete real-world workflow.

If you're evaluating DevSpark for a team, read Part I (the motivation and history) and Part III (the real-world case studies) first. The case studies will give you the most honest picture of what the framework actually delivers in practice.

If you're an experienced DevSpark user who wants to go deeper on architecture or advanced patterns, Parts IV and V are written for you. They assume you already know the basic workflow and want to understand the reasoning behind the design decisions.

## A Note on the Examples

The WebSpark.HttpClientUtility specifications in Part III are drawn from real work on a real package. I've condensed and edited some of the documentation for readability, but the decisions, the tradeoffs, and the outcomes are accurate. The critic findings are real findings. The clarification questions are real questions that had to be answered before implementation could begin.

I've chosen to present this honestly rather than with cleaned-up examples that make the framework look smoother than it is. The friction is part of the story.

## Running the Examples

The DevSpark quickstart requires internet access to download the installation prompt from GitHub. Full installation instructions are in Chapter 4. The WebSpark.HttpClientUtility case studies in Part III are presented as worked examples — you don't need to reproduce them exactly, but running similar specifications on your own project will give you a much better intuition for how the framework behaves than reading about them will.

Let's begin.
