from prototypes.event_mapper import SimEvent, classify_event, generate_objective_for_event, escalate_hiccup_to_hurdle


def test_hiccup_event_creates_optional_objective():
    event = SimEvent(
        id="evt-1",
        chapter_id="chapter-1",
        title="Missed Coffee with Alex",
        description="A small social miss caused some tension.",
        impact="low",
    )

    objective = generate_objective_for_event(event)

    assert classify_event(event) == "hiccup"
    assert objective.type == "hiccup"
    assert objective.required is False
    assert objective.carryover_policy == "carry_when_relevant"


def test_crossroads_event_creates_choice_objective():
    event = SimEvent(
        id="evt-2",
        chapter_id="chapter-1",
        title="Join the Community Theater or Start a Band?",
        description="Two creative paths become available.",
        impact="medium",
        has_multiple_options=True,
        options=[
            {"id": "theater", "label": "Join theater"},
            {"id": "band", "label": "Start a band"},
            {"id": "focus", "label": "Stay independent"},
        ],
    )

    objective = generate_objective_for_event(event)

    assert classify_event(event) == "crossroads"
    assert objective.type == "crossroads"
    assert objective.required is False
    assert objective.choices is not None
    assert len(objective.choices) == 3
    assert objective.carryover_policy == "carry_with_deadline"


def test_hurdle_event_creates_required_objective():
    event = SimEvent(
        id="evt-3",
        chapter_id="chapter-2",
        title="Job Offer: Move or Stay",
        description="A job offer requires relocation.",
        impact="high",
        requires_decision=True,
    )

    objective = generate_objective_for_event(event)

    assert classify_event(event) == "hurdle"
    assert objective.type == "hurdle"
    assert objective.required is True
    assert objective.carryover_policy == "required_persists"


def test_hiccup_can_escalate_to_hurdle():
    event = SimEvent(
        id="evt-4",
        chapter_id="chapter-1",
        title="Repeated social friction",
        description="A small issue keeps recurring.",
        impact="low",
    )

    hiccup_obj = generate_objective_for_event(event)
    escalated = escalate_hiccup_to_hurdle(hiccup_obj, reason="ignored for 5 days")

    assert hiccup_obj.type == "hiccup"
    assert escalated.type == "hurdle"
    assert escalated.required is True
    assert escalated.carryover_policy == "required_persists"
