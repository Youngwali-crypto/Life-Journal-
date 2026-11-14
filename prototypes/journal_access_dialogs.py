"""Order/open actions using the existing native Journal dialog adapter.

A trusted game bootstrap supplies owner-verified dialogs and current-session
checks. There is deliberately no player-facing 'mark delivered' button.
"""

from .household_payment import PaymentUncertain


class JournalAccessDialogs:
    def __init__(self, access, dialogs, household_id, delivery_minutes, *, debit_once=None, planner_is_missing=None,
                 beta_home_delivery=False):
        self.access, self.dialogs = access, dialogs
        self.household_id, self.delivery_minutes = household_id, delivery_minutes
        self.debit_once = debit_once
        self.planner_is_missing = planner_is_missing
        self.beta_home_delivery = beta_home_delivery
        access._identity(household_id)
        access._time(delivery_minutes)

    def open(self):
        journal = self.dialogs.journal
        journal._check()
        status = self.access.opening(journal.save_id, journal.sim_id)
        if status == 'not_ordered':
            return self.dialogs._menu('Receive a Life Journal',
                'Order a Journal for ' + journal.sim_name +
                (' for §200.' if self.debit_once is not None else '.'), [('Order Journal', self.order)])
        if status == 'awaiting_delivery':
            return self.dialogs._menu('Journal on its way',
                'Your order is awaiting delivery. Open the Journal after it arrives.',
                [('Check Again', self.open)])
        if status == 'setup':
            return self.dialogs._menu('Your story starts here',
                'Start a Free Journal to write your own story. Blueprint selection and story generation are not available in this development build.',
                [('Start a Free Journal', self.start_free), ('Decide Later', lambda: None)])
        return self.dialogs.open()

    def order(self):
        journal = self.dialogs.journal
        journal._check()
        if self.debit_once is None:
            self.access.order(journal.save_id, journal.sim_id, self.household_id,
                              self.dialogs.clock(), self.delivery_minutes)
            return self.open()
        existing = self.access.state(journal.save_id, journal.sim_id)
        replacement_id = None
        if existing is not None:
            if (self.beta_home_delivery and existing.received_at is None
                    and existing.household_id == self.household_id
                    and self.dialogs.clock() >= existing.due_at):
                return self.dialogs._menu(
                    'Life Journal delivery is ready',
                    'Your order is due. Collect the beta Journal here while the physical book is being built.',
                    [('Collect Journal', self._collect_beta_delivery),
                     ('Later', lambda: None)],
                )
            if not self._can_replace(existing):
                return self.open()
            replacement_id = existing.order_id
        price = self.access.PRICE
        return self.dialogs._menu(
            ("Order replacement Life Journal for §{}?" if replacement_id else
             "Order Life Journal for §{}?").format(price),
            "Your package will arrive at your front door tomorrow at 9:00 AM.",
            [("Place Order", lambda: self._place_paid_order(replacement_id)),
             ("Cancel", lambda: None)],
        )

    def _can_replace(self, order):
        # Unknown or unloaded object state must never be treated as lost.
        return (order.received_at is not None and self.planner_is_missing is not None
                and self.planner_is_missing(order) is True)

    def _place_paid_order(self, replacement_id=None):
        journal = self.dialogs.journal
        journal._check()
        if replacement_id is not None:
            existing = self.access.state(journal.save_id, journal.sim_id)
            if existing is None or existing.order_id != replacement_id or not self._can_replace(existing):
                return self.open()
        try:
            order = self.access.order_paid(journal.save_id, journal.sim_id,
                                           self.household_id, self.dialogs.clock(), self.debit_once,
                                           replace_order_id=replacement_id)
        except (PaymentUncertain, OSError) as error:
            return self.dialogs._menu('Order could not be completed', str(error),
                                      [('Close', lambda: None)])
        if order is None:
            return self.dialogs._menu("Insufficient funds",
                "The household needs §{} to order Life Journal.".format(self.access.PRICE),
                [("Back", self.open)])
        return self.open()

    def _collect_beta_delivery(self):
        journal = self.dialogs.journal
        journal._check()
        if not self.beta_home_delivery:
            return self.open()
        order = self.access.state(journal.save_id, journal.sim_id)
        if (order is None or order.household_id != self.household_id
                or self.dialogs.clock() < order.due_at):
            return self.open()
        if order.received_at is None:
            self.access.receive(journal.save_id, journal.sim_id, self.household_id,
                                order.order_id, order.order_id, self.dialogs.clock())
        return self.open()

    def start_free(self):
        journal = self.dialogs.journal
        journal._check()
        self.access.start_free_journal(journal.save_id, journal.sim_id, self.dialogs.clock())
        return self.open()
