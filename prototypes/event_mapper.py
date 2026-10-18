"""Game-independent mapping; callers enforce blueprint and escalation timing rules."""
from dataclasses import dataclass, replace
from typing import Optional, List, Dict


@dataclass(frozen=True)
class SimEvent:
    id: str
    chapter_id: str
    title: str
    description: str
    impact: str
    requires_decision: bool = False
    has_multiple_options: bool = False
    options: Optional[List[Dict[str, str]]] = None


@dataclass(frozen=True)
class Objective:
    id: str
    event_id: str
    chapter_id: str
    title: str
    description: str
    type: str
    required: bool
    carryover_policy: str
    choices: Optional[List[Dict[str, str]]] = None
    escalation_reason: Optional[str] = None


def classify_event(event: SimEvent) -> str:
    if event.impact not in ('low', 'medium', 'high'):
        raise ValueError('invalid impact')
    if event.has_multiple_options:
        options = event.options or []
        ids = [option.get('id') for option in options]
        if not 2 <= len(options) <= 4 or len(set(ids)) != len(ids) or any(
            not option.get('id') or not option.get('label') for option in options
        ):
            raise ValueError('branching requires 2–4 uniquely identified, labeled options')
    if event.impact == 'high' or event.requires_decision:
        return 'hurdle'
    return 'crossroads' if event.has_multiple_options else 'hiccup'


def generate_objective_for_event(event: SimEvent) -> Objective:
    kind = classify_event(event)
    policies = {'hiccup': 'carry_when_relevant', 'crossroads': 'carry_with_deadline',
                'hurdle': 'required_persists'}
    return Objective(
        id='objective:' + event.id, event_id=event.id, chapter_id=event.chapter_id,
        title=event.title, description=event.description, type=kind,
        required=kind == 'hurdle', carryover_policy=policies[kind],
        choices=[dict(option) for option in event.options] if event.has_multiple_options else None,
    )


def escalate_hiccup_to_hurdle(objective: Objective, reason: str) -> Objective:
    """Apply escalation only after the caller verifies blueprint permission and expiry."""
    if objective.type != 'hiccup':
        raise ValueError('only hiccups can escalate')
    if not reason.strip():
        raise ValueError('escalation requires a reason')
    return replace(objective, type='hurdle', required=True,
                   carryover_policy='required_persists', escalation_reason=reason)
