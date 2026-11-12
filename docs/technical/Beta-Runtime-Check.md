# Beta runtime check

The diagnostic entry point is `life_journal_probe.py`. The beta script package needs that module at its root and the `prototypes` modules under the same directory. Build the script with the game-compatible Python runtime and install it in a disposable test environment with script mods enabled. Record the game version and the installed Sims 4 Community Library (S4CL) release.

1. Load a disposable save. Open the cheat console and run `lifejournal.diagnostics`. Record Python, hook status, dialog import status, and the SQLite result.
2. Expect an active zone. Travel to another lot and repeat. Return to the main menu, load a different disposable save, and repeat. Verify the probe reports an active zone each time.
3. Keep the runtime and S4CL versions with the results. A failed SQLite result includes the exception. The probe uses a temporary database and verifies the real Journal store can write and reopen an entry. A pass establishes runtime storage support in the temporary directory. The final mod data directory and synchronization with game saves need separate tests.

The S4CL zone events can fire during travel and teardown also fires when exiting without saving. The guard is scoped to a loaded lot and invalidates prior callbacks even if the next lot belongs to the same save. It does not treat teardown as a successful game save. Pass `session.guard()` to the Journal interface when the game launcher constructs it, together with the verified save/Sim identity. Persistent services, save identity resolution and launcher integration still need wiring.

[S4CL zone lifecycle API](https://sims4communitylibrarywiki.readthedocs.io/en/latest/sims4communitylib.events.zone_spin.events.html)

## Build the diagnostic archive

From the repository root, use the interpreter that matches the target game. To try the development baseline with the installed Python 3.7 on Windows, run `py -3.7 tools/build_diagnostic.py --python 3.7`. This creates `dist/LifeJournalDiagnostic.ts4script`. The 3.7 setting is a candidate to check on the installed patch. The builder checks the selected interpreter version before compiling.

Install the diagnostic by itself with the test dependency in the Mods folder. Remove the diagnostic archive before installing a later Life Journal build to avoid loading the same modules twice.
