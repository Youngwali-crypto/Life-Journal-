from tempfile import TemporaryDirectory
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from prototypes.household_payment import HouseholdPayment, PaymentUncertain
from prototypes.json_journal_store import JsonJournalStore
from prototypes.journal_access import JournalAccess
from unittest.mock import patch


class HouseholdPaymentTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.receipts = JsonJournalStore(self.root / 'receipts.json')
        self.funds = SimpleNamespace(money=500)
        self.calls = 0
        self.context = ('save', 'house')
        self.wallet = self.make_wallet()

    def remove(self, amount):
        self.calls += 1
        self.funds.money -= amount

    def make_wallet(self):
        return HouseholdPayment(self.receipts, lambda: self.context,
                                lambda: self.funds, self.remove)

    def test_paid_receipt_survives_adapter_recreation(self):
        self.assertTrue(self.wallet('save', 'house', 'order', 200))
        self.assertTrue(self.make_wallet()('save', 'house', 'order', 200))
        self.assertEqual((self.funds.money, self.calls), (300, 1))

    def test_insufficient_funds_then_retry(self):
        self.funds.money = 199
        self.assertFalse(self.wallet('save', 'house', 'order', 200))
        self.funds.money = 200
        self.assertTrue(self.wallet('save', 'house', 'order', 200))
        self.assertEqual(self.calls, 1)

    def test_wrong_household_blocks_charge(self):
        self.context = ('save', 'other')
        with self.assertRaises(ValueError):
            self.wallet('save', 'house', 'order', 200)
        self.assertEqual(self.calls, 0)

    def test_journal_write_failure_reuses_payment(self):
        access = JournalAccess(self.root / 'journal.json')
        with patch.object(access, '_record', side_effect=OSError('disk')):
            with self.assertRaises(OSError):
                access.order_paid('save', 'sim', 'house', 10, self.wallet)
        order = access.order_paid('save', 'sim', 'house', 20, self.make_wallet())
        self.assertEqual(order.due_at, 1980)
        self.assertEqual((self.funds.money, self.calls), (300, 1))

    def test_uncertain_payment_does_not_charge_again(self):
        self.wallet.remove = lambda amount: setattr(self.funds, 'money', 450)
        with self.assertRaises(PaymentUncertain):
            self.wallet('save', 'house', 'order', 200)
        with self.assertRaises(PaymentUncertain):
            self.make_wallet()('save', 'house', 'order', 200)
        self.assertEqual(self.calls, 0)
