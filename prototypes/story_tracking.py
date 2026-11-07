"""Persistent Main Character selection and story tracking outside the game."""
import json
from dataclasses import dataclass
from typing import Optional, Tuple
from uuid import uuid4

from .database_session import database_session


@dataclass(frozen=True)
class StoryState:
    id: str
    save_id: str
    household_id: str
    sim_id: str
    status: str
    blueprint_id: Optional[str]
    chapter_id: Optional[str]
    objective_ids: Tuple[str, ...]
    revision: int


class StoryTracker:
    def __init__(self, path, *, connection=None):
        self.path = str(path)
        self.connection = connection
        with database_session(self.path, self.connection) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id TEXT PRIMARY KEY, save_id TEXT NOT NULL,
                    household_id TEXT NOT NULL, sim_id TEXT NOT NULL,
                    status TEXT NOT NULL, blueprint_id TEXT, chapter_id TEXT,
                    objective_ids TEXT NOT NULL, revision INTEGER NOT NULL
                )
            """)
            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS active_household_story
                ON stories(save_id, household_id) WHERE status = 'active'
            """)
            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS active_sim_story
                ON stories(save_id, sim_id) WHERE status = 'active'
            """)

    @staticmethod
    def _state(row):
        if row is None:
            return None
        return StoryState(*row[:7], tuple(json.loads(row[7])), row[8])

    def get(self, story_id):
        with database_session(self.path, self.connection) as connection:
            return self._state(connection.execute(
                "SELECT * FROM stories WHERE id = ?", (story_id,),
            ).fetchone())

    def active(self, save_id, household_id):
        with database_session(self.path, self.connection) as connection:
            return self._state(connection.execute(
                "SELECT * FROM stories WHERE save_id = ? AND household_id = ? AND status = 'active'",
                (save_id, household_id),
            ).fetchone())

    def select_main_character(self, save_id, household_id, sim_id):
        """Caller verifies household membership and player selection."""
        if not all((save_id, household_id, sim_id)):
            raise ValueError("Save, household, and Sim identifiers are required")
        story_id = uuid4().hex
        with database_session(self.path, self.connection) as connection:
            connection.execute(
                "INSERT INTO stories VALUES (?, ?, ?, ?, 'active', NULL, NULL, '[]', 0)",
                (story_id, save_id, household_id, sim_id),
            )
        return self.get(story_id)

    def start_blueprint(self, state, blueprint_id, chapter_id, objective_ids=()):
        if state.status != "active" or state.blueprint_id is not None:
            raise ValueError("Starting a Blueprint requires an active Main Character without a story")
        return self._update_story(state, blueprint_id, chapter_id, objective_ids)

    def update_chapter(self, state, chapter_id, objective_ids):
        if state.status != "active" or state.blueprint_id is None:
            raise ValueError("Chapter updates require an active Blueprint")
        return self._update_story(state, state.blueprint_id, chapter_id, objective_ids)

    def _update_story(self, state, blueprint_id, chapter_id, objective_ids):
        objectives = tuple(objective_ids)
        if not blueprint_id or not chapter_id or any(not value for value in objectives):
            raise ValueError("Blueprint, chapter, and objective identifiers must be nonempty")
        if len(set(objectives)) != len(objectives):
            raise ValueError("Objective identifiers must be unique")
        return self._write(
            state, "blueprint_id = ?, chapter_id = ?, objective_ids = ?",
            (blueprint_id, chapter_id, json.dumps(objectives)),
        )

    def set_status(self, state, status):
        """Explicit pause or completion releases the household role and preserves history."""
        allowed = {"active": ("paused", "completed"), "paused": ("active",)}
        if status not in allowed.get(state.status, ()):
            raise ValueError("Invalid story status transition")
        return self._write(state, "status = ?", (status,))

    def _write(self, state, assignments, values):
        with database_session(self.path, self.connection) as connection:
            cursor = connection.execute(
                "UPDATE stories SET " + assignments + ", revision = revision + 1 "
                "WHERE id = ? AND revision = ?",
                values + (state.id, state.revision),
            )
            if cursor.rowcount != 1:
                raise ValueError("Story changed. Reload its current state before updating")
        return self.get(state.id)
