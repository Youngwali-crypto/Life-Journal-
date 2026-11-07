"""Connect prototype objectives, chapter rules, tracking, and Journal transactions.

Call start for a selected Main Character, update_progress for ordered gameplay
signals, and tick for elapsed Sim time. A progress occurrence ID must be stable
across retries. Chapter plans and progress persist with Journal records.

Explicitly paused stories reject updates. This prototype does not freeze the Sim
clock when paused; elapsed time is processed when an active story next ticks.
"""
import json
from dataclasses import asdict, dataclass, replace
from typing import Optional, Tuple

from .chapter_progression import (
    Chapter, ChapterObjective, SIM_MINUTES_PER_DAY, evaluate_chapter_handoff,
)
from .database_session import database_session
from .journal_entry_log import JournalEntry
from .journal_store import JournalStore
from .objective_inactivity import evaluate_objective_inactivity
from .story_tracking import StoryTracker


@dataclass(frozen=True)
class ObjectivePlan:
    id: str
    title: str
    required: bool
    target: int = 1
    deadline_days: Optional[int] = None
    relevant_chapters: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ChapterPlan:
    id: str
    title: str
    max_days: int
    objectives: Tuple[ObjectivePlan, ...]


@dataclass(frozen=True)
class FlowObjective:
    id: str
    title: str
    required: bool
    target: int
    started_at: int
    deadline: Optional[int]
    relevant_chapters: Tuple[str, ...] = ()
    last_progress_at: Optional[int] = None
    completed_at: Optional[int] = None
    progress: int = 0
    overdue: bool = False
    carryovers: int = 0

    def chapter_objective(self):
        return ChapterObjective(
            self.id, self.required, self.completed_at, self.progress,
            self.overdue, self.carryovers,
        )


class StoryFlow:
    def __init__(self, path):
        self.path = str(path)
        StoryTracker(path)
        JournalStore(path)
        with database_session(self.path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS story_flow "
                "(story_id TEXT PRIMARY KEY, data TEXT NOT NULL)"
            )

    def start(self, selected, blueprint_id, chapters, now):
        """Start a selected Main Character's Blueprint using an ordered chapter plan."""
        plans = [asdict(chapter) for chapter in chapters]
        self._validate_plans(plans)
        self._validate_time(now)
        with database_session(self.path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            tracker = StoryTracker(self.path, connection=connection)
            journal = JournalStore(self.path, connection=connection)
            existing = connection.execute(
                "SELECT data FROM story_flow WHERE story_id = ?", (selected.id,),
            ).fetchone()
            if existing is not None:
                data = json.loads(existing[0])
                if data["plan"] != json.loads(json.dumps(plans)) or data["blueprint_id"] != blueprint_id:
                    raise ValueError("This story already has a different plan")
                return tracker.get(selected.id)
            state = tracker.start_blueprint(
                selected, blueprint_id, plans[0]["id"],
                tuple(objective["id"] for objective in plans[0]["objectives"]),
            )
            data = {
                "plan": plans, "blueprint_id": blueprint_id, "index": 0,
                "started_at": now, "last_time": now,
                "objectives": self._new_objectives(plans[0], now), "receipts": {},
            }
            connection.execute(
                "INSERT INTO story_flow VALUES (?, ?)", (state.id, json.dumps(data)),
            )
            self._record(journal, state, "blueprint_started", "Blueprint started: " + blueprint_id, now)
            self._record(journal, state, "chapter_started", "Chapter started: " + plans[0]["title"], now)
            return state

    def snapshot(self, story_id):
        """Read tracking and objective state from a single database snapshot."""
        with database_session(self.path) as connection:
            connection.execute("BEGIN")
            tracker = StoryTracker(self.path, connection=connection)
            state = tracker.get(story_id)
            data = self._load(connection, story_id)
            return state, tuple(self._objective(item) for item in data["objectives"])

    def tick(self, story_id, now):
        return self._step(story_id, now)

    def update_progress(self, story_id, objective_id, progress, now, event_id):
        """Supply an absolute progress count and a stable gameplay occurrence ID."""
        if not event_id or type(progress) is not int or progress < 0:
            raise ValueError("Progress requires an event ID and a nonnegative integer")
        return self._step(story_id, now, (event_id, objective_id, progress))

    def _step(self, story_id, now, update=None):
        self._validate_time(now)
        with database_session(self.path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            tracker = StoryTracker(self.path, connection=connection)
            journal = JournalStore(self.path, connection=connection)
            state = tracker.get(story_id)
            data = self._load(connection, story_id)
            if update is not None:
                event_id, objective_id, progress = update
                payload = [objective_id, progress, now]
                if event_id in data["receipts"]:
                    if data["receipts"][event_id] != payload:
                        raise ValueError("Gameplay event ID was reused with different data")
                    return state
            if state.status != "active":
                raise ValueError("Story updates require an active Main Character")
            if now < data["last_time"]:
                raise ValueError("Gameplay timestamps must be processed in order")
            current = data["plan"][data["index"]]
            if state.chapter_id != current["id"]:
                raise ValueError("Tracking changed outside this flow; reconcile the chapter first")

            # Catch up before accepting new progress, while giving an exact-deadline
            # completion credit in the outgoing chapter.
            state = self._advance(tracker, journal, state, data, now - 1)
            if update is not None:
                if state.status != "active":
                    raise ValueError("The Blueprint ended before this progress event")
                objectives = [self._objective(item) for item in data["objectives"]]
                matches = [index for index, item in enumerate(objectives) if item.id == objective_id]
                if not matches:
                    raise ValueError("Objective is not in the active chapter")
                index = matches[0]
                objective = objectives[index]
                if progress < objective.progress:
                    raise ValueError("Progress cannot go backwards")
                if objective.completed_at is None and progress > objective.progress:
                    objective = replace(
                        objective, progress=min(progress, objective.target), last_progress_at=now,
                    )
                    if objective.progress == objective.target:
                        objective = replace(objective, completed_at=now)
                        self._record(
                            journal, state, "objective_completed",
                            "Objective completed: " + objective.title, now, objective.id,
                        )
                    data["objectives"][index] = asdict(objective)
                data["receipts"][event_id] = payload

            state = self._advance(tracker, journal, state, data, now)
            if state.status == "active":
                self._check_inactivity(journal, state, data, now)
            data["last_time"] = now
            connection.execute(
                "UPDATE story_flow SET data = ? WHERE story_id = ?",
                (json.dumps(data), story_id),
            )
            return state

    def _advance(self, tracker, journal, state, data, now):
        while state.status == "active":
            index = data["index"]
            current = data["plan"][index]
            following = data["plan"][index + 1] if index + 1 < len(data["plan"]) else None
            objectives = [self._objective(item) for item in data["objectives"]]
            relevant = {
                item.id for item in objectives
                if following is not None and following["id"] in item.relevant_chapters
            }
            handoff = evaluate_chapter_handoff(
                Chapter(current["id"], current["max_days"]), data["started_at"],
                tuple(item.chapter_objective() for item in objectives), now,
                Chapter(following["id"], following["max_days"]) if following else None, relevant,
            )
            if handoff is None:
                break
            self._record(
                journal, state, "chapter_ended",
                "Chapter ended: " + current["title"] + " (" + handoff.reason + ").",
                handoff.ended_at,
            )
            if following is None:
                self._record(journal, state, "blueprint_ended", "Blueprint ended.", handoff.ended_at)
                state = tracker.set_status(state, "completed")
                break

            original = {item.id: item for item in objectives}
            carried = []
            for item in handoff.carried_objectives:
                previous = original[item.id]
                carried.append(asdict(replace(
                    previous, completed_at=item.completed_at, overdue=item.overdue,
                    carryovers=item.carryovers,
                    deadline=handoff.next_chapter_deadline if item.required else previous.deadline,
                )))
            data["index"] += 1
            data["started_at"] = handoff.ended_at
            data["objectives"] = carried + self._new_objectives(following, handoff.ended_at)
            state = tracker.update_chapter(
                state, following["id"], tuple(item["id"] for item in data["objectives"]),
            )
            self._record(
                journal, state, "chapter_started",
                "Chapter started: " + following["title"], handoff.ended_at,
            )
            if handoff.entry_hurdle is not None:
                titles = [original[key].title for key in handoff.entry_hurdle.objective_ids]
                label = "Growing consequences" if handoff.entry_hurdle.escalated else "Unfinished business"
                self._record(
                    journal, state, "hurdle", label + ": " + ", ".join(titles), handoff.ended_at,
                )
        return state

    def _check_inactivity(self, journal, state, data, now):
        for index, item in enumerate(data["objectives"]):
            objective = self._objective(item)
            checked, event = evaluate_objective_inactivity(
                objective.chapter_objective(), chapter_id=state.chapter_id,
                started_at=objective.started_at, deadline=objective.deadline,
                last_progress_at=objective.last_progress_at, now=now,
            )
            data["objectives"][index] = asdict(replace(objective, overdue=checked.overdue))
            if event is not None:
                event = replace(event, id=state.id + ":" + event.id)
                journal.record_event(state.save_id, state.sim_id, event, now)

    @staticmethod
    def _record(journal, state, category, text, now, occurrence=""):
        entry = JournalEntry(
            "system:flow:" + ":".join((state.id, state.chapter_id, category, occurrence)),
            "system", category, text, now, state.chapter_id,
        )
        journal.record_entry(state.save_id, state.sim_id, entry)

    @staticmethod
    def _load(connection, story_id):
        row = connection.execute(
            "SELECT data FROM story_flow WHERE story_id = ?", (story_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Story has no connected flow; initialize its chapter plan first")
        return json.loads(row[0])

    @staticmethod
    def _objective(item):
        return FlowObjective(**dict(item, relevant_chapters=tuple(item["relevant_chapters"])))

    @staticmethod
    def _new_objectives(chapter, now):
        return [
            asdict(FlowObjective(
                item["id"], item["title"], item["required"], item["target"], now,
                now + item["deadline_days"] * SIM_MINUTES_PER_DAY
                if item["deadline_days"] is not None else None,
                tuple(item["relevant_chapters"]),
            ))
            for item in chapter["objectives"]
        ]

    @staticmethod
    def _validate_time(now):
        if type(now) is not int or now < 0:
            raise ValueError("Sim time must be a nonnegative integer number of minutes")

    @staticmethod
    def _validate_plans(plans):
        if not plans or len({plan["id"] for plan in plans}) != len(plans):
            raise ValueError("Provide chapters with unique IDs")
        objective_ids = set()
        for plan in plans:
            if not plan["id"] or not plan["title"] or type(plan["max_days"]) is not int or plan["max_days"] <= 0:
                raise ValueError("Each chapter needs a title, ID, and positive day limit")
            for item in plan["objectives"]:
                if not item["id"] or item["id"] in objective_ids or not item["title"]:
                    raise ValueError("Objectives need titles and globally unique IDs")
                if type(item["required"]) is not bool or type(item["target"]) is not int or item["target"] <= 0:
                    raise ValueError("Objectives require a boolean required flag and positive target")
                days = item["deadline_days"]
                if days is not None and (type(days) is not int or days <= 0):
                    raise ValueError("Objective deadlines must be positive Sim days")
                objective_ids.add(item["id"])
