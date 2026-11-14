"""Connect the order confirmation to game funds on the loaded home lot."""
from prototypes.game_context import home_context, sim_minutes
from prototypes.household_payment import HouseholdPayment
from prototypes.journal_access import JournalAccess
from life_journal_bootstrap import order_dialog_resolver
from life_journal_saved_store import SavedJournalStore


def bind_orders():
    import services
    from date_and_time import sim_ticks_per_day
    from sims4communitylib.enums.common_currency_modify_reasons import CommonCurrencyModifyReason
    from sims4communitylib.utils.sims.common_sim_currency_utils import CommonSimCurrencyUtils
    from sims4communitylib.utils.sims.common_household_utils import CommonHouseholdUtils
    from sims4communitylib.utils.sims.common_sim_name_utils import CommonSimNameUtils
    from prototypes.sims4_journal_dialogs import S4CLJournalDialogs
    from life_journal_order_interaction import OrderLifeJournalInteraction, bind_order_dialogs
    from life_journal_probe import session

    identity = home_context(services)
    if identity is None:
        return False
    live = session.guard()
    current = lambda: live() and home_context(services) == identity
    mod = OrderLifeJournalInteraction.get_mod_identity()
    store = SavedJournalStore(mod, 'journal_orders', current)
    access = JournalAccess(None, store=store)
    receipts = SavedJournalStore(mod, 'journal_payments', current)
    clock = lambda: sim_minutes(services, sim_ticks_per_day())

    def resolve(actor):
        sim = getattr(actor, 'sim_info', None)
        if sim is None:
            return None
        def context():
            if not current() or str(CommonHouseholdUtils.get_household_id(sim)) != identity[1]:
                return None
            return identity
        payment = HouseholdPayment(receipts, context,
            lambda: CommonSimCurrencyUtils.get_household_funds(sim),
            lambda amount: CommonSimCurrencyUtils.remove_simoleons_from_household(
                sim, amount, CommonCurrencyModifyReason.OBJECT_BUY, require_full_amount=True))
        resolver = order_dialog_resolver(access, identity[0], identity[1], clock, current,
            CommonHouseholdUtils.get_household_id, CommonSimNameUtils.get_full_name,
            lambda journal, owner, sim_clock: S4CLJournalDialogs(journal, mod, owner, sim_clock),
            payment)
        return resolver(actor)
    bind_order_dialogs(resolve)
    return True
