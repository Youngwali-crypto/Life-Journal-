# Story Systems

## Overview

Life Journal uses three core story-event categories to shape a Sim's life: Hiccups, Hurdles, and Crossroads.

These categories are not interchangeable. They serve different roles in the story engine and carry different consequences, requirements, and player impact.

## 1) Hiccup

### Definition
A Hiccup is a minor, usually non-blocking story problem or setback that may become meaningful later. It creates a small narrative event, an optional objective, or a short-lived complication without stopping chapter progression by itself.

### Purpose
Hiccups help the story feel reactive and human. They represent awkward, annoying, or slightly disruptive moments that do not need to become a major turning point unless the player ignores them or the story escalates.

### Detection rules
A Hiccup should be triggered by:
- minor relationship friction
- a small failure or embarrassing moment
- a missed optional activity
- a low-stakes social issue
- a temporary setback that does not force a large decision

### Typical behavior
- Creates a journal entry
- Creates an optional objective or a low-priority task
- May add a small relationship, mood, or context penalty
- May schedule an escalation timer if the issue is ignored
- Does not block chapter completion by itself

### Resolution
A Hiccup resolves when the Sim addresses the issue or the story context changes. If left unresolved for too long, it may escalate into a more serious event.

### Escalation
A Hiccup may escalate into a Hurdle only if the blueprint explicitly allows escalation and the issue remains unresolved after an escalation window.

### Example
A Sim misses a coffee date with a friend. The friend is disappointed, but the situation is not a major life decision. This is a Hiccup. The player may choose to apologize, reschedule, or leave it alone.

### Acceptance tests
- A small social issue creates a Hiccup record and an optional objective.
- The chapter still continues normally even if the Hiccup remains unresolved.
- An ignored Hiccup can escalate only after the escalation window expires.

## 2) Hurdle

### Definition
A Hurdle is a serious, high-impact story event or decision with lasting consequences. It creates a major turning point and usually requires a required objective or explicit decision to resolve.

### Purpose
Hurdles represent the moments when the Sim's path is meaningfully disrupted or forced to change. They can affect relationships, careers, physical environment, identity, or life direction.

### Detection rules
A Hurdle should be triggered by:
- a severe conflict or emotional rupture
- a major opportunity with real stakes
- a forced decision with long-term consequences
- repeated ignored Hiccups that pile up into a serious issue
- failure of a major required objective that changes the story path

### Typical behavior
- Creates a required objective
- Creates a journal entry with strong story implications
- May create branching outcomes
- May change long-term state, relationship values, or available future options
- Can meaningfully affect chapter progression and story direction

### Resolution
A Hurdle must be addressed through an explicit objective or choice. The player must resolve the issue, or the system handles the outcome according to the chapter's carryover and expiry rules.

### Default chapter rule
Per the project design, an overdue required objective remains available within the current chapter and is required for completion-based progression, but does not block chapter-time expiry.

### Example
A Sim receives a career-changing opportunity that requires a move or a major lifestyle shift. This is a Hurdle because choosing or rejecting it will significantly alter the story.

### Acceptance tests
- A Hurdle generates a required objective.
- The objective is required for completion-based progression.
- The chapter can still expire when its timer reaches the limit even if the Hurdle is still unresolved, subject to the documented rules.
- Choosing different resolutions changes the direction of the story and updates chapter state.

## 3) Crossroads

### Definition
A Crossroads is a meaningful decision point with multiple viable paths. It is more serious than a Hiccup but less severe than a Hurdle. It shapes the Sim's next direction without always creating an immediate crisis.

### Purpose
Crossroads are the major branching system for personal growth. They help define the player choice between different life paths, identities, relationships, or future opportunities.

### Detection rules
A Crossroads should be triggered by:
- invitations or opportunities with multiple paths
- identity-defining decisions
- new social or creative possibilities
- moments where different futures become viable

### Typical behavior
- Creates a choice-based objective or branch prompt
- Provides 2–4 plausible options
- Modifies upcoming objectives, future availability, or journal context
- May or may not be required depending on blueprint requirements

### Resolution
A Crossroads is resolved when the player selects an option or when the system applies a default resolution after a deadline expires. A choice should meaningfully shape the Sim's future story path.

### Example
A Sim has the chance to join a community group, pursue a creative path, or stay isolated. Each option creates different future chances and objectives. This is a Crossroads.

### Acceptance tests
- A Crossroads presents multiple valid options.
- Each option results in different future opportunities or narrative outcomes.
- If not resolved by the deadline, a default outcome is applied and recorded.

## Core behavior across all three systems

### Severity Ladder
Hiccup < Crossroads < Hurdle

### Story effect order
- Hiccup: small disruption, optional consequence
- Crossroads: meaningful choice, branching path
- Hurdle: massive consequence, often required resolution

### Required vs optional
- Hiccups are usually optional and low-priority
- Crossroads may be optional or required depending on chapter needs
- Hurdles are usually required, with strong consequences and planning weight

### Persistence
Each story event should be recorded with:
- unique event ID
- event type
- trigger source
- status (active, resolved, escalated, failed, auto-resolved)
- related objective ID
- chapter ID
- deadline / escalation deadline
- metadata for consequences applied

## Recommended system defaults

### Default event policy
- Hiccups are low-risk and do not block progression by default
- Crossroads drive branching without forcing a crisis
- Hurdles create required, consequence-heavy resolution paths

### Default carryover policy
- Required objectives should remain available within the current chapter and continue to count toward completion-based progression rules.
- Optional objectives do not block chapter completion.
- Carryover into future chapters depends on relevance and blueprint design.

## Pseudocode for event handling

```pseudo
function handle_story_event(event):
  if event.type == "hiccup":
    create_optional_objective(event)
    if event.should_escalate:
      schedule_escalation(event)

  if event.type == "crossroads":
    create_choice_objective(event)

  if event.type == "hurdle":
    create_required_objective(event)
    apply_immediate_story_impact(event)
```

## JSON schema summary

```json
{
  "id": "string",
  "type": "hiccup|crossroads|hurdle",
  "title": "string",
  "description": "string",
  "severity": "low|medium|high",
  "status": "active|resolved|escalated|failed|auto_resolved",
  "required": true,
  "deadline": "ISO timestamp or null",
  "escalation_deadline": "ISO timestamp or null",
  "chapter_id": "string",
  "objective_id": "string or null",
  "metadata": {}
}
```

## Open design decisions to finalize in Phase A

1. Whether Hiccups can escalate to Hurdles in all blueprints or only selected ones.
2. Whether Crossroads are always optional, or sometimes required for chapter completion.
3. Whether default resolution for an expired Crossroads should be a neutral outcome or a predetermined path.
4. Whether chapter timers pause while the Sim is not currently playing the active household.
5. Whether an overdue required objective remains visible in the chapter through completion-based progression but does not block chapter expiry.

## Phase A completion criteria

This document is complete when:
- each story system has a clear definition and purpose
- examples exist for each system
- the severity order is agreed upon
- objective behavior is consistent across chapters
- unresolved edge cases are documented for final design approval

## Implementation note

This system design is meant to drive the first prototype and should not be treated as a literal final implementation spec. It establishes the story rules that the technical and gameplay layers must obey.

---

This document is part of the design work for the Finding My Lane chapter structure and is intended to support the current Phase A milestone.
