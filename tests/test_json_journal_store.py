from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from prototypes.journal_entry_log import JournalEntry
from prototypes.json_journal_store import JsonJournalStore


class JsonJournalStoreTests(TestCase):
    def test_reopen_deduplicate_and_isolate(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "journal.json"
            first = JournalEntry("same", "player", "personal", "Café", 20)
            earlier = JournalEntry("earlier", "player", "personal", "Earlier", 10)
            JsonJournalStore(path).record_entry("save", "sim", first)
            reopened = JsonJournalStore(path)
            reopened.record_entry("save", "sim", earlier)
            self.assertEqual(reopened.record_entry("save", "sim", first), first)
            self.assertEqual(reopened.entries("save", "sim"), (earlier, first))
            self.assertEqual(reopened.entries("save", "other"), ())
            self.assertEqual(reopened.entries("other", "sim"), ())

    def test_interrupted_replace_preserves_existing_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "journal.json"
            store = JsonJournalStore(path)
            entry = JournalEntry("one", "player", "personal", "First", 10)
            store.record_entry("save", "sim", entry)
            with patch("prototypes.json_journal_store.os.replace", side_effect=OSError("disk")):
                with self.assertRaises(OSError):
                    store.record_entry("save", "sim", JournalEntry("two", "player", "personal", "Second", 20))
            self.assertEqual(store.entries("save", "sim"), (entry,))
            self.assertEqual(list(path.parent.iterdir()), [path])
