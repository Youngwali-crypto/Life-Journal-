import tempfile
from pathlib import Path
from unittest import TestCase

from prototypes.event_mapper import SimEvent, generate_objective_for_event
from prototypes.journal_entry_log import JournalEntryLog
from prototypes.journal_store import JournalStore


class JournalStoreTests(TestCase):
    def test_notes_events_and_completion_survive_reopening(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "journal.db"
            store = JournalStore(path)
            log = JournalEntryLog("save", "sim")
            note = log.add_player_entry("Today felt different.", 10)
            store.record_entry(log.save_id, log.sim_id, note)
            event = SimEvent("meetup", "chapter-1", "Missed meetup", "Reach out.", "low")
            hiccup = store.record_event("save", "sim", event, 20)
            objective = generate_objective_for_event(event)
            completion = store.record_objective_completion("save", "sim", "done-1", objective, 30)

            reopened = JournalStore(path)
            self.assertEqual(reopened.entries("save", "sim"), (note, hiccup, completion))
            self.assertEqual(reopened.record_event("save", "sim", event, 40), hiccup)
            self.assertEqual(
                reopened.record_objective_completion("save", "sim", "done-1", objective, 40),
                completion,
            )
            self.assertEqual(len(reopened.entries("save", "sim")), 3)
            self.assertEqual(reopened.entries("other-save", "sim"), ())
            self.assertEqual(reopened.entries("save", "other-sim"), ())

    def test_two_store_instances_preserve_both_writers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "journal.db"
            first, second = JournalStore(path), JournalStore(path)
            log = JournalEntryLog("save", "sim")
            one = log.add_player_entry("First", 20)
            two = log.add_player_entry("Second", 10)
            first.record_entry("save", "sim", one)
            second.record_entry("save", "sim", two)
            self.assertEqual(first.entries("save", "sim"), (two, one))
