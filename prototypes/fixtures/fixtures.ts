// Chapter / Objective / Event fixtures for prototype testing
// Path: prototypes/fixtures/fixtures.ts

export const START_DATE = "2026-10-01T00:00:00Z";

export const chapters = [
  {
    id: "chapter-1",
    name: "Branching Out",
    index: 1,
    maxDays: 10,
    timerEndsAt: "2026-10-11T00:00:00Z",
    status: "active",
    requiredObjectiveIds: ["obj-1", "obj-2"],
    optionalObjectiveIds: ["obj-3"]
  },
  {
    id: "chapter-2",
    name: "Choosing My Lane",
    index: 2,
    maxDays: 12,
    timerEndsAt: "2026-10-23T00:00:00Z",
    status: "active",
    requiredObjectiveIds: ["obj-4"],
    optionalObjectiveIds: ["obj-5"]
  }
];

export const objectives = [
  {
    id: "obj-1",
    chapterId: "chapter-1",
    title: "Meet new people",
    description: "Attend 2 social gatherings and exchange contacts.",
    required: true,
    status: "completed",
    createdAt: "2026-10-01T00:00:00Z",
    deadline: "2026-10-04T00:00:00Z",
    carryoverPolicy: "required_persists"
  },
  {
    id: "obj-2",
    chapterId: "chapter-1",
    title: "Find a hobby",
    description: "Try at least one new hobby and journal about it.",
    required: true,
    status: "active",
    createdAt: "2026-10-01T00:00:00Z",
    deadline: "2026-10-05T00:00:00Z",
    carryoverPolicy: "required_persists"
  },
  {
    id: "obj-3",
    chapterId: "chapter-1",
    title: "Apologize to Alex",
    description: "You missed coffee; reach out and reschedule.",
    required: false,
    status: "active",
    createdAt: "2026-10-01T00:00:00Z",
    deadline: "2026-10-06T00:00:00Z",
    carryoverPolicy: "carry_when_relevant"
  },
  {
    id: "obj-4",
    chapterId: "chapter-2",
    title: "Choose study focus",
    description: "Decide between Creative Arts, Sciences, or Social Studies.",
    required: true,
    status: "active",
    createdAt: "2026-10-11T00:00:00Z",
    deadline: "2026-10-18T00:00:00Z",
    carryoverPolicy: "required_persists"
  },
  {
    id: "obj-5",
    chapterId: "chapter-2",
    title: "Attend club meeting",
    description: "Visit one club meeting to learn more.",
    required: false,
    status: "active",
    createdAt: "2026-10-11T00:00:00Z",
    deadline: "2026-10-15T00:00:00Z",
    carryoverPolicy: "carry_when_relevant"
  }
];

export const events = [
  {
    id: "evt-1",
    type: "hiccup",
    title: "Missed Coffee with Alex",
    description: "Missed a meetup; friend is slightly annoyed.",
    severity: "low",
    chapterId: "chapter-1",
    required: false,
    status: "active",
    createdAt: "2026-10-01T01:00:00Z",
    deadline: "2026-10-06T00:00:00Z",
    escalationDeadline: "2026-10-11T00:00:00Z",
    objectiveId: "obj-3"
  },
  {
    id: "evt-2",
    type: "crossroads",
    title: "Join Theater or Start a Band",
    description: "Two creative paths open; choose one.",
    severity: "medium",
    chapterId: "chapter-1",
    required: false,
    status: "active",
    createdAt: "2026-10-02T09:00:00Z",
    deadline: "2026-10-07T00:00:00Z",
    escalationDeadline: null,
    objectiveId: null
  },
  {
    id: "evt-3",
    type: "hurdle",
    title: "Job Offer: Move or Stay",
    description: "A high-impact offer requiring relocation.",
    severity: "high",
    chapterId: "chapter-2",
    required: true,
    status: "active",
    createdAt: "2026-10-12T12:00:00Z",
    deadline: "2026-10-20T00:00:00Z",
    escalationDeadline: null,
    objectiveId: "obj-4"
  }
];

export const sampleJournalState = {
  chapterIndex: 1,
  chapters: chapters.reduce((acc, c) => ({ ...acc, [c.id]: c }), {}),
  objectives: objectives.reduce((acc, o) => ({ ...acc, [o.id]: o }), {}),
  events: events.reduce((acc, e) => ({ ...acc, [e.id]: e }), {}),
  journalEntries: [
    "2026-10-01: Started Chapter I — Branching Out",
    "2026-10-01: Missed coffee with Alex",
  ]
};
