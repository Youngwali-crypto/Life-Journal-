from unittest import TestCase

from prototypes.zone_session import ZoneSession


class ZoneSessionTests(TestCase):
    def test_duplicate_load_and_travel_keep_only_current_callbacks(self):
        session = ZoneSession()
        first, second = object(), object()
        self.assertFalse(session.guard()())
        first_token = session.start(first)
        first_guard = session.guard()
        self.assertIs(session.start(first), first_token)
        self.assertTrue(first_guard())

        session.start(second)
        second_guard = session.guard()
        session.stop(first)
        self.assertFalse(first_guard())
        self.assertTrue(second_guard())
        session.stop(second)
        self.assertFalse(second_guard())
        session.start(second)
        self.assertFalse(second_guard())
