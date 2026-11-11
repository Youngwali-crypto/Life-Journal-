"""Script class for the phone and computer Order Life Journal tuning."""
from sims4communitylib.classes.interactions.common_super_interaction import CommonSuperInteraction
from sims4communitylib.mod_support.mod_identity import CommonModIdentity

from life_journal_probe import session


_identity = CommonModIdentity("Life Journal Beta", "Youngwali-crypto",
                              __name__, __file__, "0.1")
_order_dialogs = None


def bind_order_dialogs(resolve):
    """Bind an actor-to-JournalAccessDialogs resolver for the current lot.

    The resolver must verify the actor's save and household, and supply the
    paid wallet adapter and a JournalInterface with the current session guard.
    """
    current = session.guard()
    if not current() or not callable(resolve):
        raise ValueError("Ordering needs a live zone and a dialog resolver")
    global _order_dialogs
    _order_dialogs = (current, resolve)


class OrderLifeJournalInteraction(CommonSuperInteraction):
    @classmethod
    def get_mod_identity(cls):
        return _identity

    def on_run(self, interaction_sim, interaction_target, timeline):
        binding = _order_dialogs
        if binding is None or not binding[0]():
            return False
        dialogs = binding[1](interaction_sim)
        if dialogs is None or not callable(dialogs.debit_once):
            return False
        dialogs.order()
        return True
