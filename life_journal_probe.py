"""In-game development entry point for the Journal beta diagnostics."""
import sys

import sims4.commands

from prototypes.zone_session import ZoneSession


session = ZoneSession()
hook_error = None

try:
    from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
    from sims4communitylib.events.zone_spin.events.zone_late_load import S4CLZoneLateLoadEvent
    from sims4communitylib.events.zone_spin.events.zone_teardown import S4CLZoneTeardownEvent

    class LifeJournalZoneEvents:
        @staticmethod
        @CommonEventRegistry.handle_events("LifeJournalBeta")
        def on_zone_loaded(event_data: S4CLZoneLateLoadEvent):
            session.start(event_data.zone)
            return True

        @staticmethod
        @CommonEventRegistry.handle_events("LifeJournalBeta")
        def on_zone_teardown(event_data: S4CLZoneTeardownEvent):
            session.stop(event_data.zone)
            return True

except Exception as error:
    hook_error = "{}: {}".format(type(error).__name__, error)


def check_storage():
    # Exercise actual Journal persistence with a disposable database.
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from prototypes.journal_entry_log import JournalEntry
    from prototypes.json_journal_store import JsonJournalStore

    with TemporaryDirectory(prefix="life-journal-probe-") as directory:
        path = Path(directory) / "probe.json"
        entry = JournalEntry("probe", "player", "personal", "Probe", 0)
        JsonJournalStore(path).record_entry("probe-save", "probe-sim", entry)
        if JsonJournalStore(path).entries("probe-save", "probe-sim") != (entry,):
            raise RuntimeError("Journal entry did not round-trip")


@sims4.commands.Command("lifejournal.diagnostics", command_type=sims4.commands.CommandType.Live)
def diagnostics(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("Life Journal Python: " + sys.version.split()[0])
    if hook_error:
        output("S4CL hooks FAILED: " + hook_error)
    else:
        output("S4CL hooks registered; zone " + ("active" if session.zone is not None else "inactive"))
    try:
        from sims4communitylib.dialogs.common_input_text_dialog import CommonInputTextDialog
        from sims4communitylib.dialogs.option_dialogs.common_choose_button_option_dialog import CommonChooseButtonOptionDialog
        output("S4CL dialog imports OK")
    except Exception as error:
        output("S4CL dialog imports FAILED: {}: {}".format(type(error).__name__, error))
    try:
        check_storage()
        output("Journal JSON write/read OK")
    except Exception as error:
        output("Journal JSON FAILED: {}: {}".format(type(error).__name__, error))
