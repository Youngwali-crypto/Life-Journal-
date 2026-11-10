from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from prototypes.journal_access import JournalAccess


class PaidOrderTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "journal.db"
        self.access = JournalAccess(self.path)
        self.balance = 500
        self.charges = set()

    def debit(self, save, household, key, amount):
        if key in self.charges:
            return True
        if self.balance < amount:
            return False
        self.charges.add(key)
        self.balance -= amount
        return True

    def order(self, now):
        return self.access.order_paid("save", "sim", "house", now, self.debit)

    def test_repeat_from_other_menu_after_reload(self):
        phone = self.order(1439)
        self.access = JournalAccess(self.path)
        computer = self.order(1441)
        self.assertEqual(phone, computer)
        self.assertEqual(phone.due_at, 1980)
        self.assertEqual(self.balance, 300)

    def test_insufficient_funds_do_not_leave_order(self):
        self.balance = 199
        self.assertIsNone(self.order(10))
        self.assertIsNone(self.access.state("save", "sim"))
        self.balance = 200
        self.assertEqual(self.order(1441).due_at, 3420)

    def test_retry_after_charge_and_journal_failure(self):
        with patch.object(self.access, "_record", side_effect=RuntimeError("disk")):
            with self.assertRaises(RuntimeError):
                self.order(20)
        self.assertIsNone(self.access.state("save", "sim"))
        self.access = JournalAccess(self.path)
        self.assertEqual(self.order(30).ordered_at, 20)
        self.assertEqual(self.balance, 300)
        self.assertEqual(len(self.charges), 1)
