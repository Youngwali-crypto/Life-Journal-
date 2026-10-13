type StoryType = "hiccup" | "crossroads" | "hurdle";
type ObjectiveStatus = "active" | "completed" | "failed" | "overdue" | "auto_resolved";
type ChapterStatus = "active" | "completed" | "expired";

type CarryoverPolicy =
  | "required_persists"
  | "carry_when_relevant"
  | "carry_with_deadline"
  | "drop";

interface StoryEvent {
  id: string;
  type: StoryType;
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
  chapterId: string;
  required: boolean;
  status: "active" | "resolved" | "failed" | "escalated" | "auto_resolved";
  createdAt: string;
  deadline?: string | null;
  escalationDeadline?: string | null;
  objectiveId?: string | null;
}

interface Objective {
  id: string;
  chapterId: string;
  title: string;
  description: string;
  required: boolean;
  status: ObjectiveStatus;
  createdAt: string;
  deadline?: string | null;
  carryoverPolicy: CarryoverPolicy;
  resolvedAt?: string | null;
}

interface Chapter {
  id: string;
  name: string;
  index: number;
  maxDays: number;
  timerEndsAt: string;
  status: ChapterStatus;
  requiredObjectiveIds: string[];
  optionalObjectiveIds: string[];
}

interface JournalState {
  chapterIndex: number;
  chapters: Record<string, Chapter>;
  objectives: Record<string, Objective>;
  events: Record<string, StoryEvent>;
  journalEntries: string[];
}

function addDays(date: Date, days: number): Date {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy;
}

function iso(date: Date): string {
  return date.toISOString();
}

function createChapter(
  id: string,
  index: number,
  name: string,
  startDate: Date,
  maxDays: number
): Chapter {
  return {
    id,
    name,
    index,
    maxDays,
    timerEndsAt: iso(addDays(startDate, maxDays)),
    status: "active",
    requiredObjectiveIds: [],
    optionalObjectiveIds: [],
  };
}

function createObjective(
  id: string,
  chapterId: string,
  title: string,
  description: string,
  required: boolean,
  startDate: Date,
  daysUntilDeadline: number,
  carryoverPolicy: CarryoverPolicy
): Objective {
  return {
    id,
    chapterId,
    title,
    description,
    required,
    status: "active",
    createdAt: iso(startDate),
    deadline: iso(addDays(startDate, daysUntilDeadline)),
    carryoverPolicy,
  };
}

function createStoryEvent(
  id: string,
  type: StoryType,
  chapterId: string,
  title: string,
  description: string,
  required: boolean
): StoryEvent {
  return {
    id,
    type,
    title,
    description,
    severity:
      type === "hurdle" ? "high" : type === "crossroads" ? "medium" : "low",
    chapterId,
    required,
    status: "active",
    createdAt: iso(new Date()),
    deadline: null,
    escalationDeadline:
      type === "hiccup" ? iso(addDays(new Date(), 5)) : null,
    objectiveId: null,
  };
}

function evaluateObjective(objective: Objective, now: Date): Objective {
  if (objective.status === "completed" || objective.status === "failed") {
    return objective;
  }

  if (objective.deadline && now > new Date(objective.deadline)) {
    objective.status = "overdue";
  }

  return objective;
}

function chapterComplete(chapter: Chapter, objectives: Record<string, Objective>): boolean {
  const required = chapter.requiredObjectiveIds
    .map(id => objectives[id])
    .filter(Boolean);

  return required.length > 0 && required.every(obj => obj.status === "completed");
}

function chapterExpired(chapter: Chapter, now: Date): boolean {
  return now >= new Date(chapter.timerEndsAt);
}

function transitionChapterIfNeeded(
  chapter: Chapter,
  objectives: Record<string, Objective>,
  now: Date
): Chapter {
  if (chapterComplete(chapter, objectives)) {
    chapter.status = "completed";
    return chapter;
  }

  if (chapterExpired(chapter, now)) {
    chapter.status = "expired";
    return chapter;
  }

  return chapter;
}

function assignObjectiveToChapter(chapter: Chapter, objective: Objective) {
  if (objective.required) {
    chapter.requiredObjectiveIds.push(objective.id);
  } else {
    chapter.optionalObjectiveIds.push(objective.id);
  }
}

function resolveObjective(
  state: JournalState,
  objectiveId: string,
  newStatus: ObjectiveStatus
) {
  const objective = state.objectives[objectiveId];
  if (!objective) {
    throw new Error(`Objective ${objectiveId} not found`);
  }

  objective.status = newStatus;
  objective.resolvedAt = iso(new Date());
}

function applyCarryoverDefaults(
  state: JournalState,
  objectiveId: string,
  nextChapterId?: string
) {
  const objective = state.objectives[objectiveId];
  if (!objective) return;

  if (objective.required) {
    objective.carryoverPolicy = "required_persists";
    return;
  }

  if (nextChapterId) {
    objective.carryoverPolicy = "carry_when_relevant";
  } else {
    objective.carryoverPolicy = "drop";
  }
}

function nextChapterId(currentChapterId: string): string {
  const chapterMap: Record<string, string> = {
    "chapter-1": "chapter-2",
    "chapter-2": "chapter-3",
    "chapter-3": "chapter-4",
    "chapter-4": "chapter-5",
  };

  return chapterMap[currentChapterId] ?? "complete";
}

// Example usage
const start = new Date("2026-10-01T00:00:00Z");

const chapter1 = createChapter("chapter-1", 1, "Branching Out", start, 10);
const chapter2 = createChapter("chapter-2", 2, "Choosing My Lane", addDays(start, 10), 12);

const state: JournalState = {
  chapterIndex: 1,
  chapters: {
    "chapter-1": chapter1,
    "chapter-2": chapter2,
  },
  objectives: {},
  events: {},
  journalEntries: [],
};

const req1 = createObjective(
  "obj-1",
  "chapter-1",
  "Meet new people",
  "Build your social circle and discover possible interests.",
  true,
  start,
  3,
  "required_persists"
);

const optional1 = createObjective(
  "obj-2",
  "chapter-1",
  "Try a new hobby",
  "Experiment with one activity that could reveal a hidden talent.",
  false,
  start,
  4,
  "carry_when_relevant"
);

assignObjectiveToChapter(chapter1, req1);
assignObjectiveToChapter(chapter1, optional1);

state.objectives[req1.id] = req1;
state.objectives[optional1.id] = optional1;

resolveObjective(state, req1.id, "completed");
const now = new Date("2026-10-05T00:00:00Z");

transitionChapterIfNeeded(chapter1, state.objectives, now);

console.log("chapter1 status:", chapter1.status);
console.log("required objective status:", state.objectives[req1.id].status);
console.log("optional objective status:", state.objectives[optional1.id].status);

// Simulate chapter expiry with unresolved required objective
const unresolved = createObjective(
  "obj-3",
  "chapter-2",
  "Choose a direction",
  "Pick the lane that best matches your values and interests.",
  true,
  start,
  7,
  "required_persists"
);

const chapter2Obj = chapter2;
assignObjectiveToChapter(chapter2Obj, unresolved);

state.objectives[unresolved.id] = unresolved;

const expiredNow = new Date("2026-10-22T00:00:00Z");
transitionChapterIfNeeded(chapter2Obj, state.objectives, expiredNow);

console.log("chapter2 status after expiry:", chapter2Obj.status);
console.log("unresolved required objective still active:", state.objectives[unresolved.id].status);
