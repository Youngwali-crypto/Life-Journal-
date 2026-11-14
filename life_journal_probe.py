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


@sims4.commands.Command("lifejournal.ordercheck", command_type=sims4.commands.CommandType.Live)
def ordercheck(_connection=None):
    """Report whether ordering tuning loaded and reached live computers."""
    output = sims4.commands.CheatOutput(_connection)
    try:
        import services
        from sims4.resources import Types
        interaction_id = 15165149906037668690
        manager = services.get_instance_manager(Types.INTERACTION)
        tuning = manager.get(interaction_id)
        output("Order tuning registered: {}".format(tuning is not None))
        if tuning is None:
            output("The package tuning did not load; check the package XML and script class.")
            return
        objects = services.object_manager()
        computers = [obj for obj in objects.values()
                     if "computer" in type(obj).__name__.lower()
                     or "computer" in str(getattr(obj, "definition", "")).lower()]
        output("Live computer candidates: {}".format(len(computers)))
        for obj in computers[:5]:
            for attribute in ("_super_affordances", "super_affordances"):
                value = getattr(obj, attribute, None)
                if callable(value):
                    try:
                        value = value()
                    except Exception as error:
                        output("Computer {} {} callable: {}".format(
                            getattr(obj, "id", "?"), attribute, type(error).__name__))
                        continue
                try:
                    affordances = tuple(value or ())
                except TypeError:
                    output("Computer {} {} is {}".format(
                        getattr(obj, "id", "?"), attribute, type(value).__name__))
                    continue
                attached = any(getattr(a, "guid64", None) == interaction_id
                               or a == interaction_id for a in affordances)
                output("Computer {} {}: {} entries; order attached {}".format(
                    getattr(obj, "id", "?"), attribute, len(affordances), attached))
    except Exception as error:
        output("Order check FAILED: {}: {}".format(type(error).__name__, error))


@sims4.commands.Command("lifejournal.orderstatus", command_type=sims4.commands.CommandType.Live)
def orderstatus(_connection=None):
    """Show the active Sim's saved order and the clock used for its due time."""
    output = sims4.commands.CheatOutput(_connection)
    try:
        import services
        from date_and_time import sim_ticks_per_day
        from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils
        from life_journal_order_interaction import OrderLifeJournalInteraction
        from life_journal_saved_store import SavedJournalStore
        from prototypes.game_context import home_context, sim_minutes
        from prototypes.journal_access import JournalAccess

        identity = home_context(services)
        sim = CommonSimUtils.get_active_sim_info()
        if identity is None or sim is None:
            output("Life Journal: select the ordering Sim on their home lot.")
            return
        current = session.guard()
        access = JournalAccess(None, store=SavedJournalStore(
            OrderLifeJournalInteraction.get_mod_identity(), 'journal_orders', current))
        order = access.state(identity[0], str(sim.sim_id))
        now = sim_minutes(services, sim_ticks_per_day())
        if order is None:
            output("Life Journal: no saved order for the selected Sim in this save.")
            return
        output("Life Journal clock: {} Sim minutes; due: {}; remaining: {}".format(
            now, order.due_at, max(0, order.due_at - now)))
        output("Order household matches home: {}; received: {}".format(
            order.household_id == identity[1], order.received_at is not None))
    except Exception as error:
        output("Life Journal order status FAILED: {}: {}".format(
            type(error).__name__, error))
