"""Durable prototype Journal records scoped to a save and Sim.

The caller supplies a local database path and verified save/Sim identifiers.
Sims 4 save callbacks and gameplay subscriptions remain adapter responsibilities.
"""
from dataclasses import astuple

from .database_session import database_session
from .event_mapper import classify_event
from .journal_entry_log import JournalEntry


class JournalStore:
    def __init__(self, path, *, connection=None):
        self.path = str(path)
        self.connection = connection
        with database_session(self.path, self.connection) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    save_id TEXT NOT NULL,
                    sim_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    text TEXT NOT NULL,
                    sim_minute INTEGER NOT NULL,
                    chapter_id TEXT,
                    PRIMARY KEY (save_id, sim_id, id)
                )
            """)

    def record_entry(self, save_id, sim_id, entry):
        """Commit one entry atomically. Repeated occurrence IDs keep the first record."""
        if not save_id or not sim_id or not entry.id or not entry.text.strip():
            raise ValueError("An entry requires save, Sim, entry ID, and text")
        with database_session(self.path, self.connection) as connection:
            connection.execute(
                "INSERT OR IGNORE INTO entries VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (save_id, sim_id) + astuple(entry),
            )
            row = connection.execute(
                "SELECT id, source, category, text, sim_minute, chapter_id "
                "FROM entries WHERE save_id = ? AND sim_id = ? AND id = ?",
                (save_id, sim_id, entry.id),
            ).fetchone()
        return JournalEntry(*row)

    def entries(self, save_id, sim_id):
        with database_session(self.path, self.connection) as connection:
            rows = connection.execute(
                "SELECT id, source, category, text, sim_minute, chapter_id "
                "FROM entries WHERE save_id = ? AND sim_id = ? ORDER BY sim_minute, rowid",
                (save_id, sim_id),
            ).fetchall()
        return tuple(JournalEntry(*row) for row in rows)

    def record_event(self, save_id, sim_id, event, sim_minute):
        """Accept an existing SimEvent from the story system."""
        entry = JournalEntry(
            "system:event:" + event.id, "system", classify_event(event),
            event.title + "\n" + event.description, sim_minute, event.chapter_id,
        )
        return self.record_entry(save_id, sim_id, entry)

    def record_objective_completion(
        self, save_id, sim_id, occurrence_id, objective, sim_minute,
    ):
        """Caller confirms completion and provides an ID unique to this occurrence."""
        if not occurrence_id:
            raise ValueError("Completion requires an occurrence ID")
        entry = JournalEntry(
            "system:completion:" + occurrence_id, "system", "objective_completed",
            "Objective completed: " + objective.title, sim_minute, objective.chapter_id,
        )
        return self.record_entry(save_id, sim_id, entry)
