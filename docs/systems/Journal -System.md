# Life Journal System

## Purpose

The Life Journal System is the persistent storytelling foundation of the Life Journal mod.

Its primary responsibility is to maintain the history of a participating Sim's life.

The Journal should remember important information even when the Sim is not currently participating in a Story Blueprint.

The core principle is:

> A Story Blueprint can end. The Sim's Journal continues.

---

# Core Responsibilities

The Journal System should eventually be capable of tracking:

- Journal participation
- Main Character status
- Active Story Blueprint
- Current Chapter
- Active Objectives
- Completed Objectives
- Player-written Journal Entries
- Story-generated Journal Records
- My Circle
- Important Experiences
- Major Decisions
- Career and Education Events
- Family Events
- Relationship Events
- Milestones
- Previous Story Blueprints

Not every category must be implemented in the first version.

---

# Journal Ownership

Journal history belongs to the Sim.

It should not permanently belong to a physical Journal object.

A physical Journal, phone interaction, computer interaction, or other interface may provide access to Life Journal, but losing that object should not erase the Sim's history.

Conceptually:

Sim
→ owns Life Journal data

Journal Object / Interface
→ provides access to that data

This allows the interface to change later without requiring the underlying story history to be redesigned.

---

# Starting a Journal

When a Sim begins using Life Journal for the first time, the system should create or activate their personal Journal.

The player may eventually be presented with three starting options:

## Generate My Story

Life Journal helps the player select an appropriate Story Blueprint.

## Choose a Story Blueprint

The player manually selects a Story Blueprint.

## Start a Free Journal

The Sim begins using Life Journal without activating structured Story Blueprint gameplay.

The exact Sims 4 interface used for this setup will be determined during technical development.

---

# Free Journal

Free Journal allows Life Journal to function without an active Story Blueprint.

The player controls the story.

Life Journal provides tools for recording and organizing that story.

The philosophy is:

> You create the story. Life Journal remembers it.

Free Journal may eventually support:

- Personal Journal Entries
- Player-created Goals
- Major Life Events
- Relationship Events
- Career and Education Events
- Family Events
- My Circle
- Life History
- Therapy and Reflection

---

# Journal Entries

Life Journal should distinguish between two types of records.

## Player Journal Entries

These are intentionally written or created by the player.

Example:

> Wale is starting to wonder whether college is actually what he wants. He has been much more interested in gaming lately.

These entries represent the player's interpretation of the Sim's story.

## System Journal Records

These are created automatically when Life Journal detects or generates an important story event.

Example:

Finding My Lane started.

Chapter I — Branching Out began.

Objective completed: Find Two Friends.

Crossroad encountered: Same Night, Different Plans.

Decision: Attend the networking event.

System records provide a structured history of what occurred during gameplay.

---

# Journal Information

Conceptually, a participating Sim may eventually have information similar to:

Sim:
Wale Killem

Journal Status:
Active

Current Role:
Main Character

Active Story:
Finding My Lane

Current Chapter:
Branching Out

Current Objective:
Find Two Friends

My Circle:
Not yet declared

Story History:
Finding My Lane — Active

Experiences:
None recorded

Journal Entries:
1

This example describes the information the system may need.

It does not determine how the information must be stored technically.

---

# Journal Categories

The Journal may eventually organize information into categories such as:

- Personal Entries
- Goals
- Story History
- Relationships
- My Circle
- Experiences
- Career and Education
- Family
- Major Decisions
- Milestones

The final interface and organization will be determined after technical research and UI planning.

---

# Relationship With Story Blueprints

The Journal System and Story Blueprint System have different responsibilities.

Story Blueprints determine what structured story is currently happening.

The Journal remembers what happened.

Example:

Story Blueprint creates an Objective
→ Player completes Objective
→ Objective System confirms completion
→ Journal records completion
→ Story Blueprint determines what happens next

The Journal should not be responsible for deciding the entire story.

It provides persistent memory that other systems may use.

---

# Persistent History

Journal information should remain available after a Story Blueprint ends.

Example:

Wale completes Finding My Lane.

His Blueprint becomes inactive.

His Journal still remembers:

- Finding My Lane
- Important objectives
- Major decisions
- Relationships
- Experiences
- Milestones

Wale may then continue using Free Journal or participate in another Story Blueprint later.

---

# Future Experience Integration

Important Journal events may eventually become Experiences.

Example:

Wale experiences Academic Trouble.

He resolves the situation by asking friends for help.

Life Journal records:

Experience:
Academic Trouble

Response:
Asked Friends for Help

Outcome:
Recovered Academically

Later, another Sim may experience Academic Trouble.

If Wale is important to that Sim, another system may recognize that Wale has relevant experience and allow the Sim to ask him for advice.

This creates the long-term pattern:

Experience
→ Memory
→ Advice
→ New Decision

The Journal System is responsible for preserving the history needed for systems like this to work.

---

# Initial Prototype Requirements

The first prototype should remain intentionally small.

The Journal System should initially be capable of supporting:

- A Sim participating in Life Journal
- Identifying the current Main Character
- Recording the active Story Blueprint
- Recording the active Chapter
- Recording the active Objective
- Recording Objective completion
- Preserving basic story state during normal gameplay

The prototype does not need the complete Journal experience.

Its purpose is to prove that the core storytelling loop can function.

---

# Future Features

Later versions may introduce:

- Player-written Journal Entries
- Automatic Life Event tracking
- My Circle history
- Relationship history
- Experience Memory
- Advice based on past Experiences
- Generational history
- Therapy records
- Rich Life History
- Multiple completed Blueprint histories
- More advanced Journal UI
- Searchable or categorized Journal records

These features should not block development of the initial prototype.

---

# Technical Questions

The following questions require Sims 4 technical research before implementation:

- How should Journal data be associated with a Sim?
- How should Journal data persist across saves and reloads?
- What data can safely be stored by a script mod?
- Which Sims 4 events can be observed reliably?
- How should Life Journal identify Sims across sessions?
- What UI options are available for viewing Journal information?
- Can a custom physical Journal object provide access to the system?
- Can phone or computer interactions provide additional access?
- How should mod updates handle previously stored Journal data?

These questions should be researched before choosing the final technical architecture.

---

# Design Rules

1. Journal history belongs to the Sim, not an object.

2. A Sim does not need an active Story Blueprint to have a Journal.

3. Ending a Story Blueprint must not erase Journal history.

4. Journal records should preserve meaningful story information rather than attempting to record every minor gameplay action.

5. The Journal should support storytelling without controlling every aspect of gameplay.

6. Systems should be designed so additional Journal categories can be introduced later.

7. Technical implementation may change, but the intended player experience should remain consistent whenever possible.

---

# Development Status

Status: Design

Technical Research: Not Started

Prototype: Not Started

Implementation: Not Started

This document defines the intended responsibilities of the Life Journal System and should not be interpreted as an instruction to implement every future feature immediately.
