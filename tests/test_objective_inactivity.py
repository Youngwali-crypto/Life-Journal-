from prototypes.chapter_progression import ChapterObjective, SIM_MINUTES_PER_DAY as DAY
from prototypes.event_mapper import generate_objective_for_event
from prototypes.objective_inactivity import evaluate_objective_inactivity


REQUIRED = ChapterObjective("reach-hobby-level-four", required=True)


def evaluate(objective=REQUIRED, *, now, deadline=4 * DAY, last_progress_at=None,
             recorded_event_ids=frozenset()):
    return evaluate_objective_inactivity(
        objective,
        chapter_id="chapter-2",
        started_at=0,
        deadline=deadline,
        last_progress_at=last_progress_at,
        now=now,
        recorded_event_ids=recorded_event_ids,
    )


def test_idleness_before_deadline_does_not_trigger_hiccup():
    assert evaluate(now=3 * DAY) == (REQUIRED, None)


def test_progress_protects_an_overdue_objective_for_one_full_sim_day():
    overdue, event = evaluate(now=4 * DAY, last_progress_at=3 * DAY)
    assert overdue.overdue
    assert event is None

    _, event = evaluate(overdue, now=4 * DAY + 1, last_progress_at=3 * DAY)
    assert event is not None


def test_stalled_required_objective_generates_one_optional_hiccup():
    overdue, event = evaluate(now=4 * DAY)
    assert overdue.overdue
    assert event is not None
    assert event.chapter_id == "chapter-2"
    follow_up = generate_objective_for_event(event)
    assert follow_up.type == "hiccup"
    assert not follow_up.required

    assert evaluate(overdue, now=5 * DAY, recorded_event_ids={event.id}) == (overdue, None)


def test_completed_optional_and_untimed_objectives_do_not_trigger_hiccups():
    completed = ChapterObjective("completed", required=True, completed_at=4 * DAY)
    assert evaluate(completed, now=4 * DAY) == (completed, None)

    optional = ChapterObjective("optional", required=False)
    overdue, event = evaluate(optional, now=4 * DAY)
    assert overdue.overdue
    assert event is None

    assert evaluate(now=5 * DAY, deadline=None) == (REQUIRED, None)
