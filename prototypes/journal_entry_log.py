"""Game-independent entry history for one Sim in one save."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from uuid import uuid4


@dataclass(frozen=True)
class JournalEntry:
    id: str
    source: str
    category: str
    text: str
    sim_minute: int
    chapter_id: Optional[str] = None


class JournalEntryLog:
    """Keep one Sim's entries across chapter and Blueprint changes."""

    def __init__(self, save_id: str, sim_id: str) -> None:
        self.save_id = save_id
        self.sim_id = sim_id
        self._entries: Dict[str, JournalEntry] = {}

    def add_player_entry(self, text: str, sim_minute: int) -> JournalEntry:
        return self._add_entry(
            "player:" + uuid4().hex, "player", "personal", text, sim_minute,
        )

    def record_story_event(
        self,
        event_id: str,
        category: str,
        text: str,
        sim_minute: int,
        *,
        chapter_id: Optional[str] = None,
    ) -> JournalEntry:
        """Record a system event once using its stable occurrence ID."""
        if not event_id.strip() or not category.strip():
            raise ValueError("Story records require an event ID and category")
        entry_id = "system:" + event_id
        existing = self._entries.get(entry_id)
        if existing is not None:
            return existing
        return self._add_entry(entry_id, "system", category, text, sim_minute, chapter_id)

    def entries(self) -> Tuple[JournalEntry, ...]:
        """Return a chronological snapshot, keeping insertion order for ties."""
        return tuple(sorted(self._entries.values(), key=lambda entry: entry.sim_minute))

    def _add_entry(
        self,
        entry_id: str,
        source: str,
        category: str,
        text: str,
        sim_minute: int,
        chapter_id: Optional[str] = None,
    ) -> JournalEntry:
        if not text.strip():
            raise ValueError("Journal entry text cannot be blank")
        entry = JournalEntry(entry_id, source, category, text, sim_minute, chapter_id)
        return self._entries.setdefault(entry_id, entry)
