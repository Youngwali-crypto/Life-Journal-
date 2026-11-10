"""Order/open actions using the existing native Journal dialog adapter.

A trusted game bootstrap supplies owner-verified dialogs and current-session
checks. There is deliberately no player-facing 'mark delivered' button.
"""


class JournalAccessDialogs:
    def __init__(self, access, dialogs, household_id, delivery_minutes, *, debit_once=None):
        self.access, self.dialogs = access, dialogs
        self.household_id, self.delivery_minutes = household_id, delivery_minutes
        self.debit_once = debit_once
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
        if self.access.state(journal.save_id, journal.sim_id) is not None:
            return self.open()
        price = self.access.PRICE
        return self.dialogs._menu(
            "Order Life Journal for §{}?".format(price),
            "Your package will arrive at your front door tomorrow at 9:00 AM.",
            [("Place Order", self._place_paid_order), ("Cancel", lambda: None)],
        )

    def _place_paid_order(self):
        journal = self.dialogs.journal
        journal._check()
        order = self.access.order_paid(journal.save_id, journal.sim_id,
                                       self.household_id, self.dialogs.clock(), self.debit_once)
        if order is None:
            return self.dialogs._menu("Insufficient funds",
                "The household needs §{} to order Life Journal.".format(self.access.PRICE),
                [("Back", self.open)])
        return self.open()

    def start_free(self):
        journal = self.dialogs.journal
        journal._check()
        self.access.start_free_journal(journal.save_id, journal.sim_id, self.dialogs.clock())
        return self.open()
