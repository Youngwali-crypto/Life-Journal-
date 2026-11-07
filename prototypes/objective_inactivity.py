"""Evaluate objective deadlines and inactivity on the elapsed Sim clock."""

from dataclasses import replace
from typing import AbstractSet, Optional, Tuple

from .chapter_progression import ChapterObjective, SIM_MINUTES_PER_DAY
from .event_mapper import SimEvent


def evaluate_objective_inactivity(
    objective: ChapterObjective,
    *,
    chapter_id: str,
    started_at: int,
    deadline: Optional[int],
    last_progress_at: Optional[int],
    now: int,
    recorded_event_ids: AbstractSet[str] = frozenset(),
) -> Tuple[ChapterObjective, Optional[SimEvent]]:
    """Evaluate an active objective and return any new Hiccup to record.

    Callers supply the timestamp of the latest meaningful progress, if any.
    Record the returned event by ID and pass recorded IDs on subsequent checks.
    """
    if objective.completed_at is not None and objective.completed_at <= now:
        return objective, None
    if deadline is None or now < deadline:
        return objective, None

    overdue = replace(objective, overdue=True)
    last_activity = started_at if last_progress_at is None else last_progress_at
    event_id = "inactivity:{}:{}".format(chapter_id, objective.id)
    if (
        not objective.required
        or now - last_activity <= SIM_MINUTES_PER_DAY
        or event_id in recorded_event_ids
    ):
        return overdue, None

    return overdue, SimEvent(
        id=event_id,
        chapter_id=chapter_id,
        title="Falling Behind",
        description="A required objective missed its deadline after a stretch without progress.",
        impact="low",
    )
