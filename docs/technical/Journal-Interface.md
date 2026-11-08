# Journal interface: native dialog prototype

## Delivered

`JournalInterface` supplies owner-scoped pages and writing actions. `S4CLJournalDialogs` presents them using optional S4CL native game dialogs. Its imports are lazy and it registers no commands or interactions on import.

Sections: My Story, Objectives, Personal Entries, Story Updates, plus Write an Entry. Pages have previous/next controls and a return-to-menu action. Entries appear newest first, one per reading page. Free Journal writing works without an active Blueprint. Story pages show the current Blueprint/chapter identifiers until display-name metadata is supplied. Reading does not tick the clock or mutate the story.

Writing supports cancel, blank/length validation (2000 characters), duplicate-submit protection, and preserving the draft on a storage failure. Entries attach to the Journal owner, even if the player's selected Sim changes. The bootstrap must invalidate the session on unload; delayed callbacks are then rejected.

## Design target and limitation

The saved reference is “Aaliyah’s Life Journal: Self-Made Success.png”: a book-style Journal with story details, progress, entries, and story updates. That remains the visual target. These native dialogs are a functional development interface, not a reproduction of its open-book skin. No HTML renderer, custom game UI resource, book object, portrait artwork, or installable package is included.

My Circle, achievements, and interactive Crossroads are not populated with invented data or exposed as working controls. Story Updates displays recorded events only. Current objectives are shown; there is no future-objective preview until the story system provides an explicit visibility model. Within-chapter reveal sequencing remains unimplemented in StoryFlow.

## Bootstrap contract

Construct JournalInterface with JournalStore, verified save/Sim identity, name, and a `session_is_current` callable that checks the exact loaded-save session. Supply flow/story_id only for a story belonging to this owner. The default session guard rejects all operations.

Construct S4CLJournalDialogs with that interface, the mod's CommonModIdentity, the same owner's verified SimInfo, and a callable returning absolute Sim minutes. Call `.open()` on the game thread after the game UI is ready. Close the JournalInterface when the loaded-save session ends. The caller must not pass a different SimInfo or silently fall back to the active Sim.

Startup/save hooks, a Journal-object/phone interaction or debug command, runtime/version verification, and persistence synchronization remain required before in-game use. Test doubles validate dialog callbacks, not visual appearance or installed-game compatibility. Do not distribute this as a finished mod.

## Sources

S4CL primary source inspected 2026-11-08:

- https://github.com/DeviantGameMods/Sims4CommunityLibrary/blob/main/Scripts/sims4communitylib/dialogs/option_dialogs/common_choose_button_option_dialog.py
- https://github.com/DeviantGameMods/Sims4CommunityLibrary/blob/main/Scripts/sims4communitylib/dialogs/common_input_text_dialog.py
- https://github.com/DeviantGameMods/Sims4CommunityLibrary/blob/main/Scripts/sims4communitylib/dialogs/option_dialogs/options/response/common_dialog_response_option_context.py

## Validation

Eight interface tests cover Free Journal/reload/duplicate submission, invalid/cancelled/stale drafts, owner isolation and pagination, read-only story pages, navigation callbacks, native cancel/accept, storage failure/retry, and closed-session callbacks. Full local unittest suite: 40 passing tests. Game dialogs have not been visually tested in The Sims 4.
