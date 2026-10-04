# The Sims 4 Technical Research

## Purpose

This document records technical research for implementing Life Journal as a gameplay mod for The Sims 4.

Design documents describe what Life Journal should do.

This document investigates how those systems can actually be implemented within The Sims 4.

Technical claims should be researched before they are treated as implementation decisions.

---

# Research Area 1 — Mod Foundation

## Confirmed: Sims 4 Supports Script Mods

The Sims 4 supports gameplay mods that include script code.

Script mods use `.ts4script` files.

Life Journal is expected to require scripting because its planned systems include persistent story state, objectives, gameplay monitoring, story progression, and other dynamic behavior.

Life Journal may eventually use both script and package-based resources depending on implementation requirements.

---

## Confirmed: Script Mods Must Be Enabled

Players must allow script mods in The Sims 4.

The relevant game settings are located under:

Game Options
→ Other

The player must enable:

- Enable Custom Content and Mods
- Script Mods Allowed

The game must be restarted after changing these settings.

---

## Confirmed: Mod Installation Location

The Sims 4 loads user-installed mods from its Mods directory.

Typical Windows location:

Documents
→ Electronic Arts
→ The Sims 4
→ Mods

A future Life Journal development build may eventually be placed in a folder such as:

Mods
→ LifeJournal

---

## Confirmed: Script Mod Folder Depth Is Restricted

`.ts4script` files must not be placed too deeply inside the Mods directory.

Current EA community guidance states that script mods should be placed no more than one subfolder deep.

Example:

Mods
→ LifeJournal
→ LifeJournal.ts4script

This is acceptable.

A structure that places the `.ts4script` several folders deeper may prevent the game from loading it.

---

# What This Means for Life Journal

Life Journal should be treated as a gameplay/script mod project rather than only custom content.

The eventual development process will likely require:

Source Code
→ Build/Package Process
→ Life Journal Mod Files
→ The Sims 4 Mods Folder
→ In-Game Testing

The GitHub repository should contain development source files and documentation.

The player's Sims 4 Mods directory should contain the built/testable version of Life Journal.

These should not be treated as the same workspace.

---

# Still Requires Research

The following questions are NOT yet considered solved:

- Which Python version is required by the current version of The Sims 4?
- How should Life Journal source code be compiled or packaged into `.ts4script`?
- Which development tools should be installed?
- How can Life Journal safely store persistent data?
- How can the mod identify Sims and households?
- How can the mod detect friendship/relationship changes?
- How can the mod display notifications?
- How should tuning and `.package` resources be handled?
- How should debugging and logging work?
- How should the development build be deployed into the Mods folder?

These topics will be researched separately before implementation begins.

---

# Current Technical Status

Mod Type: Gameplay / Script Mod

Target Game: The Sims 4

Platform for Development: PC

Technical Research: In Progress

Prototype: Not Started

Implementation: Not Started
