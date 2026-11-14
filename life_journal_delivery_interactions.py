"""S4CL entry points for loaded-zone delivery and the two object interactions."""
import sims4.commands

from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.zone_update.events.zone_update_event import S4CLZoneUpdateEvent

from life_journal_order_interaction import OrderLifeJournalInteraction
from life_journal_probe import session
from prototypes.delivery_runtime import DeliveryRuntime
from prototypes.game_context import home_context, sim_minutes


_binding = None


def bind_delivery(delivery, save_id, household_id, clock, resolve_parcel,
                  owns_planner, journal_for, *, context_is_current=None):
    """Bind verified adapters for the loaded home lot.

    resolve_parcel returns the stable parcel ID or None for unrelated objects.
    owns_planner verifies the actual object and owning Sim. journal_for returns
    owner-bound Journal dialogs using the current session guard.
    """
    lot_is_current = session.guard()

    def current():
        return lot_is_current() and (context_is_current is None or context_is_current())

    if not current():
        raise ValueError("Delivery requires an active zone")
    global _binding
    _binding = (DeliveryRuntime(delivery, save_id, household_id, clock, current),
                resolve_parcel, owns_planner, journal_for)


def bind_home_delivery(delivery, resolve_parcel, owns_planner, journal_for):
    """Called by the game bootstrap when object adapters are available."""
    import services
    from date_and_time import sim_ticks_per_day

    identity = home_context(services)
    if identity is None:
        return False
    save_id, household_id = identity
    bind_delivery(delivery, save_id, household_id,
                  lambda: sim_minutes(services, sim_ticks_per_day()),
                  resolve_parcel, owns_planner, journal_for,
                  context_is_current=lambda: home_context(services) == identity)
    return True


class LifeJournalDeliveryEvents:
    @staticmethod
    @CommonEventRegistry.handle_events("LifeJournalBeta")
    def on_zone_update(event_data: S4CLZoneUpdateEvent):
        binding = _binding
        if binding is not None and event_data.zone is session.zone and not event_data.is_paused:
            binding[0].tick()
        return True


class OpenLifeJournalPackageInteraction(OrderLifeJournalInteraction):
    def on_run(self, interaction_sim, interaction_target, timeline):
        binding = _binding
        if binding is None or not binding[0].current():
            return False
        runtime, resolve_parcel, _, _ = binding
        parcel_id = resolve_parcel(interaction_target)
        return runtime.collect(str(interaction_sim.sim_info.sim_id), parcel_id) is not None


class OpenLifeJournalPlannerInteraction(OrderLifeJournalInteraction):
    def on_run(self, interaction_sim, interaction_target, timeline):
        binding = _binding
        if binding is None or not binding[0].current():
            return False
        runtime, _, owns_planner, journal_for = binding
        return runtime.open_planner(
            str(interaction_sim.sim_info.sim_id),
            owns_planner(interaction_sim, interaction_target),
            lambda: journal_for(interaction_sim).open(),
        )


@sims4.commands.Command("lifejournal.express_delivery", command_type=sims4.commands.CommandType.Live)
def express_delivery(_connection=None):
    """Retry the active Sim's failed front-door delivery on their home lot."""
    from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils

    output = sims4.commands.CheatOutput(_connection)
    binding = _binding
    if binding is None or not binding[0].current():
        output("Life Journal: load the ordering household's home lot to retry delivery.")
        return
    sim = CommonSimUtils.get_active_sim_info()
    if sim is None:
        output("Life Journal: select the Sim who ordered the Journal.")
        return
    parcel = binding[0].retry_delivery(str(sim.sim_id))
    if parcel is None:
        output("Life Journal: no failed delivery could be completed. Check the active Sim and front door.")
    else:
        output("Life Journal: the package is at the front door.")
