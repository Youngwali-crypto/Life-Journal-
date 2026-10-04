# Main Character System

## Purpose

The Main Character System determines which Sim in a household is currently receiving the primary Life Journal Story Blueprint experience.

The Main Character is the central Sim whose objectives, chapters, Hiccups, Hurdles, Crossroads, and other major story events are currently being driven by Life Journal.

The Main Character is a storytelling role.

It is not a permanent identity.

---

# Core Rule

A household may have only **one active Main Character at a time**.

Other household members may still participate in the story through systems such as:

- Household POV
- Side Stories
- My Circle
- Journal Entries
- Experiences
- Relationship events
- Story reactions
- Advice

However, they cannot simultaneously run their own full Story Blueprint while another household member is the active Main Character.

This restriction may be reconsidered in a future version, but it is a core rule for the initial design.

---

# Selecting a Main Character

When a household does not currently have an active Main Character, the player may select an eligible Sim to take that role.

Conceptually:

Household
→ Select Sim
→ Make Main Character
→ Choose Story Experience

The selected Sim may then:

- Generate a Story
- Choose a Story Blueprint
- Continue an existing eligible story
- Use Life Journal without immediately starting a Blueprint

The final Sims 4 interaction flow will be determined during technical development.

---

# Main Character State

Life Journal should be able to determine whether a participating Sim is:

- Current Main Character
- Former Main Character
- Supporting Household Sim
- Journal participant without an active Blueprint

The exact technical representation of these states has not yet been determined.

---

# Main Character and Story Blueprints

Only the active Main Character may run the household's primary Story Blueprint.

Example:

Household:

Wale
Marcus
Jordan

Current Main Character:
Wale

Active Blueprint:
Finding My Lane

Current Chapter:
Branching Out

Marcus and Jordan remain normal playable Sims.

They may still influence Wale's story and receive relevant supporting content.

They are not required to become passive Sims simply because Wale is the Main Character.

---

# Supporting Household Sims

Non-Main-Character household members should remain important to Life Journal.

Depending on the systems available, they may:

- Appear in Main Character objectives
- Participate in Crossroads
- React to Main Character decisions
- Receive Household POV events
- Participate in Side Stories
- Become members of My Circle
- Create Experiences
- Provide advice
- Maintain their own Journal history

The Main Character system should create focus without making the rest of the household irrelevant.

---

# Household POV

Household POV allows another household member to experience part of the Main Character's story from their own perspective.

Example:

Wale becomes increasingly focused on his career.

Marcus lives in the same household and begins feeling ignored.

A Household POV event may be generated for Marcus.

Marcus's reaction becomes part of his own history.

This allows one event to contribute to the stories of multiple Sims while keeping Wale as the active Main Character.

Household POV does not make Marcus a second Main Character.

---

# Side Stories

Supporting Sims may receive Side Stories connected to the Main Character's active Blueprint.

Example:

Wale is the Main Character.

Marcus is one of Wale's closest friends.

A relationship conflict causes Marcus to receive a Side Story.

The Side Story may contain its own smaller objectives or decisions while remaining connected to Wale's primary story.

A Side Story does not make the supporting Sim a Main Character.

---

# Changing Main Characters

The Main Character role should be transferable.

A new Main Character may be selected when the household no longer has another active Main Character.

Possible situations include:

- The current Blueprint ends
- The player intentionally ends the current story
- The current story is paused in a way that allows transfer
- The Main Character leaves the household
- The Main Character dies
- Another future condition makes the Main Character unavailable

The exact rules for each situation require additional design and technical research.

---

# Blueprint Completion

Completing a Story Blueprint does not remove the Sim from Life Journal.

Example:

Wale completes Finding My Lane.

Life Journal records Finding My Lane in Wale's Story History.

Wale is no longer required to remain the active Main Character.

The player may then select Marcus.

Marcus becomes the Main Character.

Marcus begins his own Blueprint.

Wale remains in the household and may now participate in Marcus's story as a supporting Sim.

---

# Former Main Characters

Former Main Characters retain their Journal history.

Their previous experiences may eventually influence later stories.

Example:

Wale previously experienced Academic Trouble during his time as Main Character.

Marcus later becomes Main Character and experiences a similar problem.

If the appropriate systems are available, Life Journal may recognize Wale's previous experience and allow Marcus to ask Wale for advice.

This allows former Main Characters to remain narratively important after their primary story ends.

---

# Rotating Household Stories

The Main Character System allows the household spotlight to move between Sims over time.

Example:

Wale
→ Main Character
→ Completes Finding My Lane

Marcus
→ Becomes Main Character
→ Begins a new Story Blueprint

Later:

Another household member
→ Becomes Main Character

Previous Main Characters remain part of the household's history.

This allows one household to gradually develop an interconnected collection of stories.

---

# Main Character Availability

A household should never accidentally have multiple active Main Characters.

Before assigning a new Main Character, Life Journal should conceptually check:

Does this household already have an active Main Character?

If YES:
Do not activate another Main Character.

If NO:
Allow eligible Sim to become Main Character.

The exact implementation of this check will be determined during technical development.

---

# Player Control

The player should remain in control of who receives the Main Character role.

Life Journal may suggest Sims or stories, but it should not permanently assign the household spotlight without player involvement.

The player should understand:

- Who the current Main Character is
- Which Blueprint they are playing
- Whether the role can currently be transferred
- What will happen to the existing story before changing Main Characters

Major story data should never be silently deleted when changing roles.

---

# Initial Prototype Requirements

The first prototype should support:

- Identifying one household
- Assigning one Sim as Main Character
- Preventing a second household Sim from simultaneously becoming Main Character
- Connecting the Main Character to an active Blueprint
- Connecting the Main Character to an active Chapter
- Connecting the Main Character to an active Objective
- Recognizing when the Main Character role becomes available again

The first prototype does not need the complete Household POV or Side Story systems.

---

# Future Features

Future versions may include:

- Main Character selection UI
- Household POV integration
- Side Story integration
- Main Character recommendations
- Former Main Character history
- Advice from former Main Characters
- Generational storytelling
- Main Character succession
- Special handling for death or household departure
- Story pause and resume functionality
- More advanced role-transfer rules

Multiple simultaneous Main Characters may be researched in the future but are not part of the current design.

---

# Technical Questions

The following require Sims 4 technical research:

- How should Life Journal identify households?
- How should Main Character status be stored?
- How should the system detect household changes?
- What happens when the Main Character moves households?
- What happens when households merge?
- What happens when households split?
- What happens when the Main Character dies?
- How should Blueprint state behave when a Main Character becomes unavailable?
- How should Main Character status persist across saves?
- Can the system reliably prevent conflicting Blueprint states?

These questions should be answered before final implementation.

---

# Design Rules

1. Only one active Main Character is allowed per household.

2. Main Character is a temporary storytelling role.

3. Supporting household Sims remain fully playable.

4. Supporting Sims may participate through POV events, Side Stories, relationships, Experiences, and other connected systems.

5. A supporting Sim cannot simultaneously run another full primary Blueprint while the household already has a Main Character.

6. Finishing a Blueprint does not erase the former Main Character's Journal.

7. Former Main Characters remain capable of influencing future stories.

8. Changing Main Characters must not silently destroy story history.

9. The player should retain control over who becomes Main Character.

10. Multiple simultaneous Main Characters are outside the current project scope.

---

# Development Status

Status: Design

Technical Research: Not Started

Prototype: Not Started

Implementation: Not Started

This document defines the intended responsibilities of the Main Character System. Technical implementation may change after Sims 4 modding research.
