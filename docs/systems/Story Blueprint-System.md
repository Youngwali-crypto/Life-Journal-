# Story Blueprint System

## Purpose

The Story Blueprint System provides structured storytelling experiences for Life Journal.

A Story Blueprint defines the framework of a story without completely scripting how the Main Character's life must unfold.

The Blueprint provides direction.

The player creates the actual story through gameplay.

The core principle is:

> The Blueprint creates possibilities. The player's choices determine the story.

Two Sims playing the same Story Blueprint should be capable of experiencing significantly different versions of that story.

---

# What Is a Story Blueprint?

A Story Blueprint is a reusable storytelling framework.

A Blueprint may define:

- Story premise
- Themes
- Eligibility requirements
- Chapters
- Objective pools
- Hiccup pools
- Hurdle pools
- Crossroad pools
- Milestones
- Side Story opportunities
- Household POV opportunities
- Story variables
- Ending conditions
- Multiple possible endings

The Blueprint should describe the type of journey the Main Character is entering without predetermining every event.

---

# Blueprint Structure

Conceptually, a Story Blueprint may contain:

Story Blueprint
→ Blueprint Information
→ Eligibility
→ Chapters
→ Objective Pools
→ Hiccup Pools
→ Hurdle Pools
→ Crossroad Pools
→ Story Variables
→ Side Story Rules
→ Ending Conditions
→ Possible Endings

The exact technical structure will be determined during implementation.

---

# Blueprint Information

Each Blueprint should contain basic information describing the experience.

Possible information includes:

- Blueprint ID
- Blueprint Name
- Description
- Story Premise
- Themes
- Eligible Life Stages
- Required Game Conditions
- Optional Pack Requirements
- Estimated Story Length
- Supported Story Filters
- Story Boundary Categories

Example:

Blueprint Name:
Finding My Lane

Premise:
A Sim explores who they are, what they enjoy, who belongs in their life, and what direction they want their future to take.

Themes:
Personal Growth
Friendship
Romance
Career
Education
Identity
Outside Influence

---

# Blueprint Eligibility

Not every Blueprint must be appropriate for every Sim.

Before starting a Blueprint, Life Journal may check whether the Main Character meets the necessary requirements.

Possible eligibility conditions may include:

- Life stage
- University enrollment
- Relationship status
- Career status
- Household situation
- Required Sims 4 packs
- Previous Blueprint history
- Previous Experiences
- Story Boundaries

Blueprint eligibility should prevent obviously incompatible stories while avoiding unnecessary restrictions.

---

# Chapters

Story Blueprints may be divided into Chapters.

Each Chapter represents a different stage of the story.

A Chapter may define:

- Chapter theme
- Available Objectives
- Available Hiccups
- Available Hurdles
- Available Crossroads
- Milestones
- Story variables
- Entry conditions
- Exit conditions

Example:

Finding My Lane

Chapter I:
Branching Out

Purpose:
Explore different parts of life and begin discovering what the Main Character wants.

Chapter II:
Choosing My Lane

Purpose:
Develop choices and emerging direction through objectives generated from the Main Character's interactions, relationships, repeated behaviors, and emerging routes. Chapter I discoveries inform this chapter without permanently locking the Sim into a path.

Chapter III:
Outside Noise

Purpose:
Challenge the choices and routes developed during Chapters I and II through relationships, pressure, opinions, and outside influence. Use those established routes to generate relevant Hiccups, Hurdles, Crossroads, and stronger story consequences.

Later Chapters:
Not yet finalized.

The [Life Journal Overview](../Life-Journal-Overview.md) contains the current Finding My Lane chapter design. This example summarizes that design; other Blueprints may use different chapter structures.

---

# Finding My Lane — Approved Chapter Gates

For Finding My Lane, complete all required Objectives for the current chapter path to make the next chapter ready. Required Objectives outnumber optional Objectives, and optional Objectives do not block progression. Time alone does not advance the chapter.

Each Objective has a realistic individual Sim-day deadline. An unmet deadline can introduce a related Hiccup, but an overdue required Objective remains available and is still needed for progression. Progress within the allotted time does not itself trigger an objective-related Hiccup, and inactivity alone does not trigger one before the deadline.

After Chapter I, give a brief chapter overview and reveal only 1–2 upcoming Objectives at a time. Objective completion or a relevant story event can reveal the next Objective. The full chapter list stays hidden.

See the [Finding My Lane plan](../Finding-My-Lane-Blueprint.md#approved-chapter-progression-rules). Exact counts, durations, and transition presentation remain undecided. Other Blueprints may define different gates.

---

# Dynamic Story Progression

Blueprints should not always progress through one fixed sequence.

Instead, progression may respond to:

- Objectives completed
- Objectives ignored
- Player choices
- Crossroad decisions
- Relationships
- Hiccups
- Hurdles
- Important Experiences
- Story variables
- Gameplay behavior
- Chapter timing
- Player-selected boundaries

This allows the same Blueprint to create different experiences for different Sims.

---

# Objective Pools

Blueprints may contain pools of eligible Objectives rather than one mandatory sequence.

The Objective System determines which Objectives are currently appropriate.

Example:

Finding My Lane may contain Objective categories related to:

- Friendship
- Hobbies
- Career
- University
- Romance
- Personal style
- My Circle
- Journal reflection

A Main Character's actions may influence which objective becomes relevant next.

Objectives may also form chains.

Example:

Meet New Sims
→ Build Friendship
→ Invite Sim Out
→ Consider Sim for My Circle

The Story Blueprint defines the available story content.

The Objective System handles objective tracking and completion.

---

# Hiccups

A Hiccup is a slight problem that can grow into a bigger issue or become a meaningful experience—even a good memory. How the Sim gets through it can strengthen their story.

A Hiccup may lead to a larger problem, growth, a stronger relationship, or a positive experience the Sim can look back on. Resolving it should preserve what the experience contributed to the story rather than simply erase the problem.

Example: A plan falls apart, but spending the evening with a new acquaintance becomes the beginning of an important friendship.

Not every Hiccup becomes a Hurdle. Timing and escalation mechanics remain proposals.

---

# Hurdles

A Hurdle is a severe problem that puts the player at an ultimatum. The choice they make heavily affects the story they are creating and can reshape its direction.

A Hurdle threatens something important and asks the player what the Main Character is willing to protect, sacrifice, or change. Its defining feature is the severity of the problem and the weight of the decision, rather than how long it takes to resolve.

Example: A partner demands that the Sim stop seeing someone in My Circle. Protecting the friendship, prioritizing the relationship, or rejecting the ultimatum can each significantly change the story.

A Hurdle may have multiple responses without becoming a lower-stakes Crossroad. Outcomes should meaningfully reflect the player's choice.

---

# Crossroads

A Crossroad is a less severe, multiple-choice decision that contributes to a shift in the story. It can open different opportunities and matter over time without carrying the immediate stakes of a Hurdle.

Crossroads present multiple reasonable options. Their role is to contribute to direction and opportunity, while Hurdles place the player at a severe story-changing ultimatum. Multiple-choice presentation alone does not make a Hurdle a Crossroad.

Example: Choose whether to spend the evening with a new friend, explore a hobby, or attend a career event. Each option can develop a different part of the Sim's story.

See the [Hiccups, Hurdles, and Crossroads System](Hiccups-Hurdles-Crossroads-System.md) for the approved definitions and draft mechanics.

---

# Story Variables

Blueprints may need to remember information that helps determine future events.

Conceptual examples include:

CareerFocus
RelationshipFocus
UniversityPath
SocialFocus
Independence
OutsideInfluence
CircleConflict
UnresolvedHiccups

These names are examples only.

Story variables may be influenced by player behavior and Blueprint events.

They may later affect:

- Objective selection
- Crossroad availability
- Hiccup eligibility
- Hurdle eligibility
- Chapter progression
- Side Stories
- Ending selection

The exact variable system requires technical design.

---

# Story Filters

Story Filters describe themes the player wants emphasized.

Possible examples:

- Romance
- Friendship
- Career
- University
- Family
- Personal Growth
- Drama

Filters may influence which optional Blueprint content becomes more likely or relevant.

Filters should not completely rewrite the Blueprint's central premise.

---

# Story Boundaries

Story Boundaries describe content the player does not want included.

Example:

The player enables Romance but disables cheating-related scenarios.

The Blueprint System should respect applicable Story Boundaries when determining eligible events.

Story Boundaries should prevent restricted content from becoming required for story progression.

---

# Side Stories

Blueprints may contain Side Story opportunities involving important supporting Sims.

Side Stories should be connected to the Main Character's story.

Possible participants may include:

- My Circle members
- Romantic partners
- Friends
- Family
- Rivals
- Other story-important Sims

The Side Story System will define the detailed behavior of these stories.

---

# Household POV

Blueprints may create opportunities for household members to react to the Main Character's story.

Example:

The Main Character becomes increasingly focused on career advancement.

A child or partner in the household experiences the consequences of the Main Character's reduced availability.

The Blueprint may make an appropriate Household POV event eligible.

The Household POV System will define the detailed behavior.

---

# Blueprint Endings

Story Blueprints are designed to support **multiple possible endings**.

A Blueprint should not normally have one universal success ending.

The ending should reflect the story the player created.

Ending selection may eventually consider:

- Major Crossroad decisions
- Objective outcomes
- Relationships
- Story variables
- Hiccups
- Hurdles
- Milestones
- Experiences
- Chapter outcomes
- Repeated player behavior

Different endings may represent different conclusions rather than simple success or failure.

---

# Ending Philosophy

Life Journal should avoid treating Blueprint endings as:

Good Ending
versus
Bad Ending

unless a specific story intentionally requires that structure.

Instead, endings should answer:

> Where did this Sim end up after this chapter of their life?

One Main Character may finish a story having clearly found direction.

Another may finish still exploring.

Another may discover that relationships matter most.

Another may prioritize ambition.

Another may remain uncertain.

Each result can create future storytelling opportunities.

---

# Hidden Ending Conditions

Players should generally **not see the exact requirements for every possible Blueprint ending**.

The player may know:

- The Blueprint premise
- Major themes
- Current Objectives
- Current problems
- Their own decisions

However, Life Journal should avoid displaying instructions such as:

"Complete these exact actions to unlock Ending A."

The goal is to encourage roleplay and natural decision-making rather than optimization toward a specific ending.

Ending conditions may therefore be tracked internally.

---

# Ending Reveal

When a Blueprint concludes, Life Journal may reveal the ending reached.

Conceptual example:

Finding My Lane

Ending:
Trusting Myself

The Main Character has learned to hear the opinions around them without allowing those voices to completely determine their direction.

The final presentation system has not yet been determined.

---

# Blueprint Ending and Journal History

When a Blueprint ends:

- The ending is recorded in the Main Character's Journal.
- Major story decisions may remain part of Journal history.
- Relevant Experiences remain available.
- Important relationships remain meaningful.
- The Main Character may return to Free Journal.
- Another household member may become Main Character.
- The Sim may eventually begin another Blueprint.

Blueprint completion must not erase the story that occurred.

---

# Future Story Connections

A Blueprint ending may eventually influence eligibility or context for future stories.

Example:

Finding My Lane
→ Ending: Still Exploring

Later:

A future Blueprint related to career, relationships, independence, or personal direction may recognize that previous outcome.

This allows Life Journal stories to connect without requiring every Blueprint to form one predetermined campaign.

---

# Blueprint Independence

The Story Blueprint System should be designed so new Blueprints can eventually be added without rewriting the entire Life Journal engine.

Conceptually:

Life Journal Core Systems
→ Run Story Blueprint

Finding My Lane
→ Blueprint Content

Future Relationship Story
→ Blueprint Content

Future Career Story
→ Blueprint Content

Future Family Story
→ Blueprint Content

The engine handles common storytelling behavior.

Blueprints provide the story-specific content.

This separation is important for future expansion.

---

# First Blueprint

The first planned Story Blueprint is:

## Finding My Lane

Finding My Lane will be used as the initial Blueprint for designing and testing the Story Blueprint System.

However, core systems should not become so specific to Finding My Lane that future Blueprints cannot use them.

Finding My Lane should help test the engine.

It should not become the engine.

---

# Initial Prototype Requirements

The first Story Blueprint prototype should remain intentionally small.

The prototype should support:

- One Main Character
- One active Blueprint
- Blueprint identification
- One Chapter
- A small Objective pool
- Objective progression
- Basic story state
- Basic Journal recording
- A simple Blueprint conclusion

The initial prototype does not need:

- Full Hiccup functionality
- Full Hurdle functionality
- Full Crossroad functionality
- Side Stories
- Household POV
- Story Generator
- Advanced Experience Memory
- Therapy integration
- The complete multiple-ending system

These systems can be introduced after the basic Blueprint loop works.

---

# Technical Questions

The following require Sims 4 technical research:

- How should Blueprint definitions be stored?
- Can Blueprint content be data-driven?
- How should Blueprint state persist?
- How should Chapters be represented?
- How should Story Variables be stored?
- How should the engine evaluate event eligibility?
- How should optional Sims 4 pack requirements be handled?
- How should Blueprint content reference Sims and relationships?
- How should ending conditions be evaluated?
- How easily can additional Blueprints be added later?
- Can Blueprint content eventually be distributed separately from core systems?

These questions should be answered before final implementation.

---

# Design Rules

1. A Story Blueprint provides structure without completely scripting the Main Character's life.

2. Two Sims using the same Blueprint should be capable of experiencing different stories.

3. Blueprints may contain multiple Chapters.

4. Objectives may be dynamic rather than one fixed sequence.

5. Blueprint events should respond to relevant story conditions whenever possible.

6. Crossroads should generally avoid one universally correct answer.

7. Hiccups and Hurdles should create storytelling opportunities rather than exist only as punishment.

8. Story Boundaries must be respected.

9. Story Blueprints should support multiple possible endings.

10. Exact ending requirements should generally remain hidden from the player.

11. Different endings should not automatically be classified as success or failure.

12. Blueprint endings must be recorded in Journal history.

13. Ending one Blueprint does not end the Sim's Life Journal.

14. Future Blueprints should be addable without redesigning the entire Life Journal engine.

15. Finding My Lane is the first Blueprint, not the definition of how every future Blueprint must work.

---

# Development Status

Status: Design

Technical Research: Not Started

Prototype: Not Started

Implementation: Not Started

This document defines the intended responsibilities of the Story Blueprint System. Technical implementation may change after Sims 4 modding research.
