from prototypes.chapter_progression import (
    SIM_MINUTES_PER_DAY as DAY,
    Chapter,
    ChapterObjective,
    EntryHurdle,
    evaluate_chapter_handoff,
)


CHAPTER_ONE = Chapter("chapter-1", 10)
CHAPTER_TWO = Chapter("chapter-2", 12)
CHAPTER_THREE = Chapter("chapter-3", 12)


def test_required_completion_starts_chapter_two_with_optional_work_open():
    objectives = (
        ChapterObjective("friends", required=True, completed_at=2 * DAY),
        ChapterObjective("hobby", required=True, completed_at=4 * DAY),
        ChapterObjective("optional", required=False),
    )

    assert evaluate_chapter_handoff(CHAPTER_ONE, 0, objectives, 3 * DAY, CHAPTER_TWO) is None
    result = evaluate_chapter_handoff(CHAPTER_ONE, 0, objectives, 4 * DAY, CHAPTER_TWO)

    assert result.reason == "completed"
    assert result.ended_at == 4 * DAY
    assert result.next_chapter_id == CHAPTER_TWO.id
    assert result.next_chapter_deadline == 16 * DAY
    assert result.carried_objectives == ()
    assert result.entry_hurdle is None


def test_expiry_carries_required_work_and_only_relevant_optional_work():
    objectives = (
        ChapterObjective("friends", required=True, progress=1),
        ChapterObjective("hobby", required=True),
        ChapterObjective("keep", required=False),
        ChapterObjective("drop", required=False),
    )

    result = evaluate_chapter_handoff(
        CHAPTER_ONE, 0, objectives, 10 * DAY, CHAPTER_TWO, {"keep"},
    )

    assert result.reason == "expired"
    assert result.next_chapter_id == CHAPTER_TWO.id
    assert result.next_chapter_deadline == 22 * DAY
    assert result.carried_objectives == (
        ChapterObjective("friends", required=True, progress=1, overdue=True, carryovers=1),
        ChapterObjective("hobby", required=True, overdue=True, carryovers=1),
        ChapterObjective("keep", required=False),
    )
    assert result.entry_hurdle == EntryHurdle(("friends", "hobby"), escalated=False)


def test_required_work_still_open_at_second_handoff_escalates_one_hurdle():
    first = evaluate_chapter_handoff(
        CHAPTER_ONE, 0, (ChapterObjective("friends", required=True),),
        10 * DAY, CHAPTER_TWO,
    )
    second = evaluate_chapter_handoff(
        CHAPTER_TWO, first.ended_at, first.carried_objectives, 22 * DAY, CHAPTER_THREE,
    )

    assert second.entry_hurdle == EntryHurdle(("friends",), escalated=True)
    assert second.carried_objectives[0].carryovers == 2


def test_late_evaluation_preserves_the_earliest_handoff():
    completed_early = (ChapterObjective("friends", required=True, completed_at=9 * DAY),)
    completed_late = (ChapterObjective("friends", required=True, completed_at=11 * DAY),)

    early = evaluate_chapter_handoff(CHAPTER_ONE, 0, completed_early, 12 * DAY, CHAPTER_TWO)
    late = evaluate_chapter_handoff(CHAPTER_ONE, 0, completed_late, 12 * DAY, CHAPTER_TWO)

    assert early.reason == "completed"
    assert early.next_chapter_deadline == 21 * DAY
    assert late.reason == "expired"
    assert late.next_chapter_deadline == 22 * DAY
    assert late.carried_objectives[0].completed_at is None


def test_completion_at_exact_deadline_counts_as_expiry_with_no_unfinished_work():
    objectives = (ChapterObjective("friends", required=True, completed_at=10 * DAY),)

    result = evaluate_chapter_handoff(CHAPTER_ONE, 0, objectives, 10 * DAY, CHAPTER_TWO)

    assert result.reason == "expired"
    assert result.carried_objectives == ()
    assert result.entry_hurdle is None


def test_final_chapter_expiry_creates_no_handoff_hurdle():
    result = evaluate_chapter_handoff(
        Chapter("chapter-5", 14), 0, (ChapterObjective("friends", required=True),),
        14 * DAY, None,
    )

    assert result.reason == "expired"
    assert result.next_chapter_id is None
    assert result.next_chapter_deadline is None
    assert result.carried_objectives == ()
    assert result.entry_hurdle is None
