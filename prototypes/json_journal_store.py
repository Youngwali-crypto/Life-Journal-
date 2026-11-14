"""File-backed Journal entries for game runtimes without SQLite."""
import json
import os
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock

from .journal_entry_log import JournalEntry


_lock = RLock()


class JsonJournalStore:
    """Store one versioned document. Writers share a lock within the game process."""

    def __init__(self, path):
        self.path = Path(path)

    def _read(self):
        try:
            with self.path.open(encoding="utf-8") as stream:
                data = json.load(stream)
        except FileNotFoundError:
            return {"version": 1, "entries": []}
        if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("entries"), list):
            raise ValueError("Unsupported Life Journal storage format")
        return data

    def record_entry(self, save_id, sim_id, entry):
        if not save_id or not sim_id or not entry.id or not entry.text.strip():
            raise ValueError("An entry requires save, Sim, entry ID, and text")
        with self.transaction() as data:
            return self.record(data, save_id, sim_id, entry)

    @staticmethod
    def record(data, save_id, sim_id, entry):
        for record in data["entries"]:
            if (record["save_id"], record["sim_id"], record["entry"]["id"]) == (save_id, sim_id, entry.id):
                return JournalEntry(**record["entry"])
        data["entries"].append(dict(save_id=save_id, sim_id=sim_id, entry=asdict(entry)))
        return entry

    @contextmanager
    def transaction(self, *, write=True):
        with _lock:
            data = self._read()
            before = json.dumps(data) if write else None
            yield data
            if write and json.dumps(data) != before:
                self._write(data)

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=str(self.path.parent),
                                    prefix=".life-journal-", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(data, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(str(temporary), str(self.path))
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    def entries(self, save_id, sim_id):
        with _lock:
            records = self._read()["entries"]
            return tuple(sorted(
                (JournalEntry(**record["entry"]) for record in records
                 if (record["save_id"], record["sim_id"]) == (save_id, sim_id)),
                key=lambda entry: entry.sim_minute,
            ))
