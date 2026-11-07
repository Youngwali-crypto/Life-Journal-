# Finding My Lane — Chapter Progression Design Draft

Status: Phase A draft  
Project: Life Journal  
Blueprint: Finding My Lane  
Related issue: Youngwali-crypto/Life-Journal-#2

## Purpose
This document defines how chapters progress, how objectives behave, and how story events create or resolve chapter transitions for the Finding My Lane story blueprint.

This document is intended to be the design reference for the first playable prototype and should be used as the source of truth before code implementation begins.

---

## 1. Core design principles

1. A chapter ends when all required objectives are completed or the chapter timer expires, whichever happens first.
2. Optional objectives do not block progression.
3. Required objectives can be overdue but remain available within the current chapter.
4. Overdue required objectives remain relevant to completion-based progression, but do not prevent chapter-time expiry.
5. Objective deadlines are individual and should not be treated as a single global timer for the chapter.
6. Story events and objective failures can produce Hiccups, Crossroads, or Hurdles depending on severity and impact.
7. After Chapter I, only a brief overview and a small number of near-term objectives should be visible at once.
8. Each chapter path should have more required objectives than optional objectives.

---

## 2. Chapter structure

Finding My Lane uses five confirmed chapters:

- Chapter I — Branching Out
- Chapter II — Choosing My Lane
- Chapter III — Outside Noise
- Chapter IV — Standing on My Own
- Chapter V — The Lane I Choose

### Confirmed timing
| Chapter | Name | Max duration |
|---|---|---|
| I | Branching Out | 10 Sim days |
| II | Choosing My Lane | 12 Sim days |
| III | Outside Noise | 12 Sim days |
| IV | Standing on My Own | 14 Sim days |
| V | The Lane I Choose | 14 Sim days |

These are chapter time limits, not minimum waiting periods. A chapter may end earlier when required objectives are completed.

---

## 3. Chapter completion rules

### 3.1 Required completion rule
A chapter is considered complete when either:
- all required objectives for that chapter are completed, or
- the chapter's time limit expires

The first condition wins if it occurs before the timer ends.

### 3.2 Optional objective rule
Optional objectives should not block chapter completion. They may remain active, be delayed, or be resolved later if relevant, but they do not prevent chapter progression.

### 3.3 Timer expiry rule
When the chapter timer expires:
- the chapter ends automatically
- required objectives that remain incomplete are not immediately discarded
- unfinished required objectives are preserved in the outgoing chapter history and carry into the next chapter when one exists
- the next chapter starts automatically, and its timer starts at the handoff

This default behavior matches the current project direction:
- overdue required objectives remain part of the current chapter’s story state
- they are relevant to completion-based progression
- they do not block timer-based chapter expiry

---

## 4. Objective lifecycle

Each objective should be tracked as an independent object with the following states:

- active
- completed
- failed
- overdue
- auto_resolved

### 4.1 Objective fields
A goal/objective should include:
- objective ID
- chapter ID
- title
- description
- required or optional
- priority
- created timestamp
- deadline
- status
- carryover policy
- related story event
- related stat or relationship impact

### 4.2 Deadline behavior
Each objective should have its own realistic daily deadline, not a single chapter-wide deadline. A realistic “Sim-day” representation should be assigned to each objective based on the activity or story context.

Examples:
- social interaction objective: 2–3 Sim days
- skill-based objective: 4–6 Sim days
- major decision or life consequence: 1–2 Sim days or a chapter-aligned deadline

### 4.3 Overdue behavior
If an objective misses its deadline:
- the objective becomes overdue
- if it is required, it remains visible and may still be completed within the chapter
- if it is optional, it may fail or resolve automatically depending on blueprint rules
- an overdue required objective can trigger a related Hiccup or Hurdle if the unresolved issue becomes serious enough

### 4.4 Fail and auto-resolve behavior
An objective may move to:
- failed: player did not resolve it within the allowed timeline and the system marks it as lost
- auto_resolved: system resolves it with a default outcome when the player does nothing
- escalated: the system converts the issue into a stronger story event

---

## 5. Story event interactions

### 5.1 Hiccup
A Hiccup is a minor story complication. It should usually:
- be optional
- create a small story consequence
- generate a low-priority optional objective
- not block chapter progression

A missed or ignored Hiccup may later escalate into a more serious event if the project chooses to support that flow.

### 5.2 Crossroads
A Crossroads is a meaningful decision with multiple viable options. It should:
- create choice-based objective(s)
- generate branching future paths
- reveal new optional objectives after the player chooses
- not usually block the chapter by itself

### 5.3 Hurdle
A Hurdle is a high-severity story challenge or forced decision. It should:
- create a required objective
- create strong story consequences
- potentially affect future chapter availability or state
- be capable of carrying over if unresolved or if the chapter expires

---

## 6. Carryover and relevance rules

### 6.1 Optional objectives
Optional objectives should carry forward only when they remain relevant to the next chapter or story direction.

Recommended default:
- optional objective is dropped if no longer relevant
- optional objective may carry over if it connects directly to the next chapter’s story
- optional objective should never prevent chapter completion

### 6.2 Required objectives
Required objectives should remain active until either:
- they are completed, or
- the chapter ends by timer expiry

If the chapter expires while a required objective remains incomplete:
- the outgoing chapter records the objective as unmet
- if a next chapter exists, the objective carries into it and contributes to one combined entry Hurdle tied to the unfinished required work
- the entry Hurdle accounts for meaningful progress. If carried required work is still unfinished at the next chapter boundary, the following chapter opens with a bigger related Hurdle
- completing carried work does not automatically erase an existing Hurdle or its story consequences

### 6.3 Relevant story event carryover
If a story event is directly relevant to the next chapter, the system should carry forward:
- the objective in a reduced or transformed state
- a journal reminder
- the existing narrative context

If not relevant:
- the unresolved issue should be resolved as a default outcome or dropped from active chapter tracking

---

## 7. chapter transition behavior

### 7.1 Transition trigger
A chapter transition occurs when:
- all required objectives are complete, or
- the chapter timer expires

The handoff is automatic. It requires no Journal reflection or player confirmation. The incoming chapter's time limit starts at the handoff.

If a chapter ends due to objective completion:
- the next chapter begins immediately
- the next chapter reveals a brief overview and a limited number of upcoming objectives
- old chapter outcomes are recorded in story history, and eligible unfinished optional objectives may carry forward

If a chapter ends due to timer expiry:
- the chapter is marked as expired
- unfinished required objectives carry forward and produce one combined entry Hurdle if another chapter exists
- the next chapter begins with a brief summary of what happened

### 7.2 Chapter preview behavior
After Chapter I, the player should not see an overwhelming list of future objectives. Instead:

- show a brief chapter overview
- reveal only 1–2 upcoming objectives at a time
- reveal additional objectives only when:
  - a previous objective is completed, or
  - a relevant story event unlocks a new objective

This prevents the journal from feeling like a task list instead of a story overview.

---

## 8. Objective resolution and story pacing

### 8.1 Hiccup-driven pacing
Hiccups should be used to keep the story alive between major decisions, providing subtle tension or emotional events without forcing the player into heavy chapter-blocking gameplay.

### 8.2 Crossroad-driven pacing
Crossroads should be used to provide player agency and branching outcomes. They are central to the identity-building process in Finding My Lane.

### 8.3 Hurdle-driven pacing
Hurdles should be used sparingly and strategically. They should represent major life decisions or turning points with elevated consequence.

---

## 9. State-machine summary

```text
Objective states:
active -> completed
active -> failed
active -> overdue -> completed | failed | auto_resolved
active -> escalated -> hurdle / required follow-up objective

Chapter states:
active -> complete
active -> expired
complete -> next chapter begins
expired -> next chapter begins
```

---

## 10. Recommended rules to implement first

These are the rules to lock in before full gameplay implementation:

1. Required objectives are the gate for chapter completion.
2. Optional objectives do not block chapter transition.
3. Overdue required objectives remain active and relevant within the current chapter.
4. Chapter timers still end the chapter even if required objectives remain incomplete.
5. Optional objectives carry into the next chapter only if directly relevant.
6. After Chapter I, show a brief preview and only a small set of goals at a time.
7. Hiccups may escalate to Hurdles if repeatedly ignored and the blueprint allows it.
8. Crossroads create branching future objectives and reveal the next meaningful choices.

---

## 11. Open decisions still to finalize
These are the remaining design decisions to resolve before implementation:

- Should Hiccups escalate to Hurdles in all blueprints or only selected ones?
- Should Crossroads ever be required?
- Should expired Crossroads resolve with a neutral default or a predetermined choice?
- Should chapter timers continue while the player is not active in the household?
- How should carried objective timers work, and how should optional relevance be evaluated?
- How should meaningful progress affect entry Hurdle severity?
- How should impossible objectives and unfinished work at the final chapter be handled?
- How should the inactivity Hiccup threshold of more than one Sim day interact with an objective's own deadline? Meaningful progress should protect the Sim from an inactivity Hiccup.

These decisions should be made as part of Phase A sign-off before technical implementation begins.

---

## 12. Acceptance criteria for this document
This draft is considered valid when:

- chapter completion logic is clearly defined
- require/optional objective rules are explicit
- overdue required objective behavior is documented
- chapter timer and objective deadline interactions are clear
- carryover rules are defined
- transition logic is testable without gameplay implementation
- the next chapter can be revealed without overwhelming the player

---

## 13. Summary
Finding My Lane should feel like a living story, not a checklist. The chapter progression rules should keep the story moving while preserving emotional and narrative continuity. Required objectives drive completion, optional objectives support atmosphere and personality, and chapter time limits keep the Sim’s life moving forward without requiring every objective to be perfect.

This draft is designed to support a prototype and future implementation while preserving the design intent already captured in issue #2 and the project README.
