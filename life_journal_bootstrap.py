"""Bind the beta's order, delivery and planner interactions to one home lot."""
from prototypes.game_context import home_context, sim_minutes
from prototypes.journal_access import JournalAccess
from prototypes.journal_access_dialogs import JournalAccessDialogs
from prototypes.journal_interface import JournalInterface
from prototypes.sims4_journal_dialogs import S4CLJournalDialogs


def order_dialog_resolver(access, save_id, household_id, clock, current, household_for,
                          name_for, native_dialogs, debit_once, planner_is_missing=None):
    """Return an actor-bound dialog resolver that rechecks identity on each action."""
    store = access.store

    def resolve(actor):
        sim = getattr(actor, "sim_info", None)
        if sim is None or not sim.sim_id:
            return None
        sim_id = str(sim.sim_id)

        def actor_is_current():
            return (current() and str(sim.sim_id) == sim_id
                    and str(household_for(sim)) == household_id)

        if not actor_is_current():
            return None
        journal = JournalInterface(store, save_id, sim_id, name_for(sim),
                                   session_is_current=actor_is_current)
        return JournalAccessDialogs(access, native_dialogs(journal, sim, clock),
                                    household_id, 0, debit_once=debit_once,
                                    planner_is_missing=planner_is_missing)

    return resolve


def bind_home_journal(database_path, objects, debit_once, resolve_parcel, *,
                      planner_is_missing=None):
    """Called on the loaded home lot with configured object and wallet adapters.

    debit_once must use a save-backed receipt. Objects must use persistent
    markers. A caller still needs to configure both adapters and invoke this
    function from the game startup path.
    """
    import services
    from date_and_time import sim_ticks_per_day
    from sims4communitylib.utils.sims.common_household_utils import CommonHouseholdUtils
    from sims4communitylib.utils.sims.common_sim_name_utils import CommonSimNameUtils

    from life_journal_delivery_interactions import bind_delivery
    from life_journal_order_interaction import OrderLifeJournalInteraction, bind_order_dialogs
    from life_journal_probe import session

    identity = home_context(services)
    lot_is_current = session.guard()
    if identity is None or not lot_is_current():
        return False
    if not callable(debit_once) or not callable(resolve_parcel):
        raise ValueError("A paid wallet adapter and parcel resolver are required")
    save_id, household_id = identity
    access = JournalAccess(database_path)

    def current():
        return lot_is_current() and home_context(services) == identity

    def clock():
        return sim_minutes(services, sim_ticks_per_day())

    def native_dialogs(journal, sim, sim_clock):
        return S4CLJournalDialogs(journal, OrderLifeJournalInteraction.get_mod_identity(),
                                  sim, sim_clock)

    resolve = order_dialog_resolver(
        access, save_id, household_id, clock, current, CommonHouseholdUtils.get_household_id,
        CommonSimNameUtils.get_full_name, native_dialogs, debit_once, planner_is_missing,
    )

    def owns_planner(actor, planner):
        if planner is None or not current():
            return False
        sim = getattr(actor, "sim_info", None)
        if sim is None or str(CommonHouseholdUtils.get_household_id(sim)) != household_id:
            return False
        sim_id = str(sim.sim_id)
        order = access.state(save_id, sim_id)
        return (order is not None and order.received_at is not None
                and objects.matches(planner, (save_id, order.order_id, "planner", sim_id)))

    bind_delivery(objects.create_delivery(access), save_id, household_id, clock,
                  resolve_parcel, owns_planner, resolve, context_is_current=current)
    bind_order_dialogs(resolve)
    return True
