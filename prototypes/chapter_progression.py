"""Game-independent chapter handoff using elapsed Sim minutes."""

from dataclasses import dataclass, replace
from typing import AbstractSet, Optional, Tuple


SIM_MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class ChapterObjective:
    id: str
    required: bool
    completed_at: Optional[int] = None
    progress: int = 0
    overdue: bool = False
    carryovers: int = 0


@dataclass(frozen=True)
class Chapter:
    id: str
    max_days: int


@dataclass(frozen=True)
class EntryHurdle:
    objective_ids: Tuple[str, ...]
    escalated: bool


@dataclass(frozen=True)
class ChapterHandoff:
    reason: str
    ended_at: int
    next_chapter_id: Optional[str]
    next_chapter_deadline: Optional[int]
    carried_objectives: Tuple[ChapterObjective, ...]
    entry_hurdle: Optional[EntryHurdle]


def evaluate_chapter_handoff(
    chapter: Chapter,
    started_at: int,
    objectives: Tuple[ChapterObjective, ...],
    now: int,
    next_chapter: Optional[Chapter],
    relevant_optional_ids: AbstractSet[str] = frozenset(),
) -> Optional[ChapterHandoff]:
    """Calculate the first eligible handoff without changing the outgoing state.

    All timestamps use the same Sim clock. Supply objective progress as of the
    handoff when replaying a late evaluation. The caller supplies optional
    relevance for the incoming chapter's story and circumstances.
    """
    deadline = started_at + chapter.max_days * SIM_MINUTES_PER_DAY
    required = tuple(objective for objective in objectives if objective.required)
    completion_times = [
        objective.completed_at
        for objective in required
        if objective.completed_at is not None
    ]

    all_required_completed = bool(required) and len(completion_times) == len(required)
    last_completion = max(completion_times, default=deadline)
    if all_required_completed and last_completion < deadline and last_completion <= now:
        reason = "completed"
        ended_at = last_completion
    elif now >= deadline:
        reason = "expired"
        ended_at = deadline
    else:
        return None

    if next_chapter is None:
        return ChapterHandoff(reason, ended_at, None, None, (), None)

    carried = []
    unfinished_required = []
    for objective in objectives:
        if objective.completed_at is not None and objective.completed_at <= ended_at:
            continue
        if objective.required:
            unfinished_required.append(objective)
            carried.append(replace(
                objective, completed_at=None, overdue=True,
                carryovers=objective.carryovers + 1,
            ))
        elif objective.id in relevant_optional_ids:
            carried.append(replace(objective, completed_at=None))

    entry_hurdle = None
    if unfinished_required:
        entry_hurdle = EntryHurdle(
            objective_ids=tuple(objective.id for objective in unfinished_required),
            escalated=any(objective.carryovers > 0 for objective in unfinished_required),
        )

    return ChapterHandoff(
        reason=reason,
        ended_at=ended_at,
        next_chapter_id=next_chapter.id,
        next_chapter_deadline=ended_at + next_chapter.max_days * SIM_MINUTES_PER_DAY,
        carried_objectives=tuple(carried),
        entry_hurdle=entry_hurdle,
    )
