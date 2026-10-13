# Objective System

## Purpose

The Objective System gives the Main Character short-term gameplay direction during a Story Blueprint.

Objectives translate the Blueprint's story into actions the player can actually perform in The Sims 4.

The core principle is:

> Objectives guide the story without completely controlling the player.

Objectives should respond to the Main Character's current story whenever possible.

---

# Core Responsibilities

The Objective System should eventually be capable of:

- Activating Objectives
- Tracking Objective progress
- Detecting Objective completion
- Recording completed Objectives
- Selecting eligible future Objectives
- Supporting Objective chains
- Supporting optional Objectives
- Supporting conditional Objectives
- Supporting time-sensitive Objectives
- Communicating Objective updates to the player
- Sending important Objective results to the Journal
- Providing Objective outcomes to the Story Blueprint System

---

# Objectives Belong to Story Blueprints

Primary story Objectives should originate from the active Story Blueprint.

This prevents Objectives from becoming unrelated generic tasks.

Example:

Finding My Lane may contain Objectives involving:

- Friendship
- Hobbies
- Career
- University
- Romance
- Personal style
- My Circle
- Reflection

A future family-focused Blueprint would contain a different Objective pool.

The Objective System manages Objectives.

The Story Blueprint determines which types of Objectives belong to its story.

---

# Objective Structure

Conceptually, an Objective may contain:

Objective ID

Objective Name

Description

Blueprint

Chapter

Objective Category

Eligibility Conditions

Activation Conditions

Completion Conditions

Optional Time Limit

Priority

Next Objective Possibilities

Story Variable Effects

Journal Record

The exact technical structure will be determined during implementation.

---

# Objective States

An Objective may move through several states.

Possible states include:

Locked

Eligible

Active

Completed

Failed

Expired

Cancelled

Skipped

Not every Objective needs to support every state.

Conceptually:

Locked
→ Eligibility conditions become true
→ Eligible
→ Objective selected
→ Active
→ Player performs required gameplay
→ Completed

Other outcomes may include:

Active
→ Time limit expires
→ Expired

or:

Active
→ Story direction changes
→ Cancelled

The meaning of these states should be defined consistently across Blueprints.

---

# Dynamic Objectives

Blueprint Objectives should not always appear as one predetermined checklist.

Instead, Life Journal may determine which Objectives become appropriate based on the Main Character's story.

Possible influences include:

- Current Chapter
- Previous Objectives
- Player behavior
- Relationships
- Career
- Education
- Skills
- Previous Crossroads
- Hiccups
- Hurdles
- My Circle
- Story Variables
- Story Filters
- Story Boundaries
- Previous Experiences

This allows the same Blueprint to produce different Objective sequences.

---

# Objective Pools

A Blueprint may contain a pool of possible Objectives.

Example:

Finding My Lane
Chapter I — Branching Out

Possible Objective Areas:

- Friendship
- Hobby
- Career
- University
- Social
- Personal Style
- My Circle
- Reflection

Life Journal does not necessarily need to activate every possible Objective for every Main Character.

The story determines which Objectives become relevant.

---

# Objective Chains

Objectives may connect together to create story progression.

Example:

Meet New Sims

→ Find Two Friends

→ Invite a Friend Out

→ Develop Important Relationship

→ Consider Sim for My Circle

Another possible chain:

Explore Interests

→ Discover Hobby

→ Practice Hobby

→ Reach Skill Level 4

→ Reflect on whether this interest matters to the Main Character

Objective chains should be capable of branching.

---

# Branching Objectives

An Objective outcome may make different future Objectives eligible.

Example:

Objective:
Explore Career Options

Outcome A:
Main Character accepts a job.

Possible next Objective:
Give the Career a Chance

Outcome B:
Main Character rejects available careers.

Possible next Objective:
Explore Another Direction

Outcome C:
Main Character focuses on University instead.

Possible next Objective:
Explore a Major

The Objective System should support story divergence rather than forcing every Main Character back into the same sequence.

---

# Objective Eligibility

Before an Objective can activate, the system may check whether it is appropriate.

Possible conditions include:

- Correct Blueprint
- Correct Chapter
- Correct life stage
- Required relationship exists
- Required career state exists
- Required university state exists
- Required skill exists
- Previous Objective completed
- Specific Crossroad choice occurred
- Story Boundary allows the content
- Story Variable meets a condition

Eligibility prevents irrelevant Objectives from appearing.

---

# Conditional Objectives

Some Objectives should exist only when the Main Character's circumstances support them.

Example:

Choose a Major

This Objective should only become available if the Main Character is attending University or otherwise meets the necessary education conditions.

A Sim who is not attending University should not receive an impossible Objective.

The Blueprint may provide an alternative Objective instead.

Example:

University path:
Choose a Major

Non-University path:
Explore a Career Direction

---

# Required and Optional Objectives

Blueprints may contain both required and optional Objectives.

## Required Objectives

These represent important story beats. Completing all required objectives allows early Chapter progression; the chapter timer can also end the chapter with required objectives unfinished.

## Optional Objectives

These provide additional opportunities to develop the story but are not mandatory.

Optional Objectives may still influence:

- Story Variables
- Relationships
- Future events
- Ending conditions
- Journal history

A player should not necessarily need to complete every Objective to experience a valid story.

---

# Required Objective Carryover and Entry Hurdles

When a chapter timer expires with required objectives unfinished, the story advances. If a next chapter exists, those unfinished required objectives carry into it and trigger a Hurdle upon entry.

The entry Hurdle must connect to the unfinished required work and its story context. Carryover preserves the unresolved responsibility while the Hurdle makes its consequences part of the new chapter.

This differs from optional carryover: unfinished optional objectives carry forward only when relevant and do not trigger a Hurdle merely because they were left incomplete.

Multiple unfinished required objectives produce **one combined chapter-entry Hurdle**, not a separate entry Hurdle for every objective. Its severity scales with how much required work remains unfinished. Meaningful progress must be recognized rather than treating a partially completed objective as entirely untouched.

Still to define:
- The exact severity thresholds and how meaningful progress is measured.
- Timers and completion handling for carried required objectives.
- Handling when an objective becomes impossible or its circumstances change.
- Resolution at the final chapter, where no next chapter exists.

---

# Optional Objectives and Chapter Progression

A chapter ends when all of its **required objectives** are completed or its chapter timer expires, whichever happens first. Optional objectives can be completed by choice but never hold up chapter advancement.

At a chapter transition, an unfinished optional objective carries into the next chapter **only if it remains relevant to that chapter's story and the Main Character's current circumstances**. Objectives must not carry forward merely because they are unfinished.

Optional objectives that no longer fit the next chapter are not carried forward. Not completing an optional objective is not, by itself, a failure or a reason for punishment.

The exact relevance checks, handling of timers on carried objectives, and Journal wording for objectives that are not carried forward still require design.

---

# Objective Timing

Some Objectives may have time limits.

Others may remain active until completed or until the story changes.

Possible timing types include:

No Time Limit

Complete Within One Sim Day

Complete Within Several Sim Days

Complete Before Chapter End

Complete Before Specific Story Event

Time limits should be used intentionally.

Not every Objective should create constant urgency.

---

# Objective Failure

Failure should not automatically mean the story stops.

An Objective may fail because:

- The time limit expired
- The player intentionally ignored it
- Required conditions became impossible
- The story changed direction

Failure may create:

- A Hiccup
- A Hurdle
- A different Objective
- A new Crossroad
- A Story Variable change
- A different Chapter outcome
- A different Blueprint ending

The core philosophy is:

> Failure can become story content.

---

# Objective Completion

When an Objective is completed, the Objective System may:

1. Mark the Objective as completed.

2. Notify the player.

3. Send the result to the Story Blueprint System.

4. Update relevant Story Variables.

5. Record the important result in the Journal.

6. Evaluate whether another Objective should become eligible.

7. Evaluate whether the Chapter can progress.

Not every Objective completion must perform every action.

---

# Objective Notifications

The player should understand:

- What the current Objective is
- What they need to do
- Whether progress has been made
- When the Objective is completed
- When the Objective changes

Notifications should remain concise.

The Journal may contain more detailed information.

---

# Example Objective — Find Two Friends

Finding My Lane uses "Find Two Friends" as one of its early Objective concepts.

Conceptually:

Objective ID:
FML_CH1_FIND_TWO_FRIENDS

Blueprint:
Finding My Lane

Chapter:
Branching Out

Category:
Friendship

Objective:
Find Two Friends

Description:
The Main Character is beginning to branch out. Build meaningful connections with at least two Sims.

Completion Condition:
The Main Character establishes qualifying friendship relationships with two Sims.

Progress:

0 / 2 Friends

1 / 2 Friends

2 / 2 Friends

Completed

Possible Result:

Friendship exploration becomes established.

Additional social Objectives may become eligible.

Potential My Circle candidates may begin developing.

The exact Sims 4 relationship threshold used to define a qualifying friend requires technical research.

---

# Example Objective Chain — Friendship

Find Two Friends

→ Invite a Sim Out

→ Continue Developing Relationship

→ Declare My Circle

The chain does not necessarily need to occur identically for every player.

For example, the Main Character may already have friends when the Blueprint begins.

In that case, Life Journal may need to recognize existing relationships rather than forcing the player to create artificial new friendships.

This behavior requires further design.

---

# Existing Gameplay State

Life Journal should eventually consider what is already true about the Main Character.

Example:

Finding My Lane begins.

The Main Character already has three close friends.

The Objective System should not blindly require:

"Find Two Friends"

if the story purpose of that Objective has already been satisfied.

Possible responses include:

- Automatically recognize the condition
- Replace the Objective
- Adapt the Objective
- Generate a deeper friendship Objective

The final behavior will be determined during Objective design.

---

# Objective Progress Detection

Whenever possible, Objective progress should be detected from actual gameplay.

Examples may include:

- Relationship changes
- Skill progression
- Career changes
- University status
- Social interactions
- Travel
- Purchases
- Household changes

However, technical feasibility must be confirmed before assuming every gameplay action can be detected reliably.

Some Objectives may require alternative completion methods if direct detection is not practical.

---

# Manual Completion

Certain storytelling Objectives may be difficult or inappropriate to detect automatically.

Life Journal may eventually allow some Objectives to be manually marked complete by the player.

This could be useful for highly interpretive goals.

Example:

"Decide whether this career feels right."

The game cannot necessarily determine the player's interpretation of the Sim's feelings.

Manual completion may therefore be appropriate.

Manual completion should not be used when reliable automatic detection is available unless there is a good gameplay reason.

---

# Objective and Journal Integration

Important Objective events should be recorded in the Journal.

Example:

Finding My Lane

Chapter I — Branching Out

Objective Completed:
Find Two Friends

The Journal does not necessarily need to record every minor progress update.

The goal is to preserve meaningful story history.

---

# Objective and Hiccup Integration

Some Objective outcomes may create Hiccups.

Example:

Objective:
Keep Up With Coursework

Player ignores Objective.

Time expires.

Possible result:

Hiccup:
Falling Behind

The Objective System reports the outcome.

The Hiccup System determines the complication.

---

# Objective and Hurdle Integration

Repeated Objective problems may eventually contribute to a Hurdle.

Example:

Repeated academic Objectives ignored

→ Multiple Hiccups

→ Academic Trouble Hurdle

The Objective System should provide information needed by other systems without becoming responsible for every consequence itself.

---

# Objective and Crossroad Integration

Objectives may create Crossroads.

Crossroads may also create new Objectives.

Example:

Objective:
Explore Career Opportunities

→ Crossroad:
Career Opportunity vs Night Out

Player chooses Career Opportunity

→ New Objective:
Attend Networking Event

This allows decisions and gameplay actions to interact.

---

# Objective and Ending Integration

Objective outcomes may contribute to Blueprint ending selection.

The player should generally not be told:

"Complete this Objective to unlock Ending A."

Instead, Objective history becomes one part of the Main Character's overall story.

Possible ending evaluation may consider:

- Objectives completed
- Objectives ignored
- Objective categories pursued
- Repeated behavior
- Major decisions
- Relationships
- Hiccups
- Hurdles
- Story Variables

Objectives contribute to endings.

They should not reduce endings to a visible score.

---

# Finding My Lane — Current Chapter I Objective Areas

The current design contains eight major Objective areas:

1. Find at least two friends

2. Discover a favorite hobby and reach Level 4

3. Find a career path

4. Choose a Major if attending University

5. Invite a Sim out

6. Shop for new clothes or explore a new look

7. Declare My Circle

8. Complete the First Journal Entry

These are currently design concepts.

They are not finalized as eight mandatory Objectives appearing in a fixed sequence.

The Objective System may adapt their order, replace incompatible Objectives, or use them as parts of larger Objective chains.

---

# First Journal Entry

The First Journal Entry may have a special role in Finding My Lane.

Instead of appearing only at the end of Chapter I, it may occur early.

The entry could ask what the Main Character currently wants to explore.

Possible answers may include:

- Friendships
- Love and relationships
- Career and future
- Education
- Hobbies and interests
- Personal growth
- I honestly do not know

The answer may influence early Objective selection.

However, the player's later gameplay behavior should still be capable of changing the story direction.

The First Journal Entry should influence the story.

It should not permanently lock the player into one path.

---

# Initial Prototype Requirements

The first Objective System prototype should support:

- One active Objective
- One Main Character
- One active Blueprint
- One active Chapter
- Objective identification
- Objective progress
- Objective completion
- Basic player notification
- Basic Journal recording
- Selection of a next Objective

The first prototype does not need:

- Large Objective pools
- Complex branching
- Full Hiccup integration
- Full Hurdle integration
- Full Crossroad integration
- My Circle integration
- Multiple simultaneous Objectives
- Advanced ending calculations

The first goal is to prove:

Objective activates
→ Player performs gameplay
→ Life Journal detects progress
→ Objective completes
→ Journal records it
→ Next Objective becomes available

---

# First Prototype Objective

The recommended first Objective for technical testing is:

## Find Two Friends

Why:

- It belongs to Finding My Lane.
- It uses normal Sims gameplay.
- Progress can be represented clearly as 0/2, 1/2, and 2/2.
- It provides a useful test of relationship detection.
- It provides a clear completion event.
- It can later connect naturally to My Circle.

This Objective should be technically researched before implementation.

---

# Technical Questions

The following require Sims 4 technical research:

- How can a script mod detect relationship changes?
- How does The Sims 4 determine friendship status?
- Can relationship thresholds be monitored reliably?
- Can Life Journal subscribe to gameplay events?
- How should Objective state persist across saves?
- How should progress counters be stored?
- How should existing gameplay state be evaluated when an Objective begins?
- How should Objectives reference specific Sims?
- How should timed Objectives use Sim time?
- How can Objectives trigger notifications?
- Can Objectives be defined through external data rather than hard-coded individually?
- How should manually completed Objectives work?
- How should Objectives react when their target Sim dies, moves, or becomes unavailable?

These questions should be answered during technical research.

---

# Design Rules

1. Objectives provide direction without completely controlling gameplay.

2. Primary Objectives should support the active Blueprint's story.

3. Objectives may be selected dynamically.

4. Objectives may form branching chains.

5. Existing gameplay state should eventually be considered.

6. Conditional Objectives must not appear when they are impossible.

7. Not every Objective needs to be mandatory.

8. Objective failure should be capable of creating new story content.

9. Objectives may use automatic or manual completion depending on what is being measured.

10. Important Objective results should be recorded in the Journal.

11. Objective outcomes may influence future Objectives and Blueprint endings.

12. Exact ending calculations should remain hidden from the player.

13. Objectives should not become a visible score for determining whether the player is playing correctly.

14. Technical feasibility must be confirmed before assuming an action can be automatically detected.

15. The Objective System should support future Blueprints without requiring a separate Objective engine for every story.

---

# Development Status

Status: Design

Technical Research: Not Started

Prototype: Not Started

Implementation: Not Started

This document defines the intended responsibilities of the Objective System. Technical implementation may change after Sims 4 modding research.
