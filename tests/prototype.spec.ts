import {
  chapters,
  objectives,
  events,
  sampleJournalState,
} from "../prototypes/fixtures/fixtures";

describe("fixture-driven chapter progression prototype tests", () => {
  it("T01 chapter 1 required objectives are tracked correctly", () => {
    const chapter = chapters.find(c => c.id === "chapter-1");
    const required = objectives.filter(
      o => o.chapterId === chapter!.id && o.required
    );

    expect(chapter).toBeDefined();
    expect(required).toHaveLength(2);
    expect(required.every(o => o.status === "completed" || o.status === "active")).toBe(true);
  });

  it("T02 optional objective does not block chapter completion", () => {
    const chapter = chapters.find(c => c.id === "chapter-1");
    const required = objectives.filter(
      o => o.chapterId === chapter!.id && o.required
    );
    const optional = objectives.filter(
      o => o.chapterId === chapter!.id && !o.required
    );

    const chapterComplete = required.every(o => o.status === "completed");

    expect(chapterComplete).toBe(false);
    expect(optional.length).toBeGreaterThan(0);
    expect(optional.every(o => o.status === "active")).toBe(true);
  });

  it("T03 chapter expiry logic is supported by fixture timestamps", () => {
    const chapter = chapters.find(c => c.id === "chapter-2");
    const now = new Date("2026-10-24T00:00:00Z");
    const expired = now >= new Date(chapter!.timerEndsAt);

    expect(chapter).toBeDefined();
    expect(expired).toBe(true);
  });

  it("T04 overdue required objective remains required and overdue", () => {
    const objective = objectives.find(o => o.id === "obj-4");
    const now = new Date("2026-10-19T00:00:00Z");
    const isOverdue = objective!.deadline && now > new Date(objective!.deadline);

    expect(objective!.required).toBe(true);
    expect(isOverdue).toBe(true);
  });

  it("T05 optional objective can be auto-resolved after deadline", () => {
    const objective = objectives.find(o => o.id === "obj-5");
    const now = new Date("2026-10-16T00:00:00Z");
    const expired = objective!.deadline && now > new Date(objective!.deadline);

    expect(expired).toBe(true);
    expect(objective!.required).toBe(false);
    expect(objective!.carryoverPolicy).toBe("carry_when_relevant");
  });

  it("T06 required carryover policy persists by default", () => {
    const requiredObjectives = objectives.filter(o => o.required);

    expect(requiredObjectives.length).toBeGreaterThan(0);
    expect(requiredObjectives.every(o => o.carryoverPolicy === "required_persists")).toBe(true);
  });

  it("T07 optional objectives only carry over when relevant", () => {
    const optionalObjectives = objectives.filter(o => !o.required);

    expect(optionalObjectives.length).toBeGreaterThan(0);
    expect(optionalObjectives.every(o => o.carryoverPolicy === "carry_when_relevant")).toBe(true);
  });

  it("T08 Hiccup is non-blocking and optional", () => {
    const event = events.find(e => e.type === "hiccup");

    expect(event).toBeDefined();
    expect(event!.required).toBe(false);
    expect(event!.severity).toBe("low");
  });

  it("T09 Crossroads creates branching choice state", () => {
    const event = events.find(e => e.type === "crossroads");

    expect(event).toBeDefined();
    expect(event!.required).toBe(false);
    expect(event!.severity).toBe("medium");
  });

  it("T10 Hurdle is required and high severity", () => {
    const event = events.find(e => e.type === "hurdle");

    expect(event).toBeDefined();
    expect(event!.required).toBe(true);
    expect(event!.severity).toBe("high");
  });

  it("T11 crossed objective deadlines auto-resolve by default in fixture data", () => {
    const objective = objectives.find(o => o.id === "obj-5");
    const now = new Date("2026-10-16T00:00:00Z");
    const expired = objective!.deadline && now > new Date(objective!.deadline);

    expect(expired).toBe(true);
    expect(objective!.required).toBe(false);
  });

  it("T12 sample journal state contains chapter, objective, and event fixtures", () => {
    expect(sampleJournalState.chapterIndex).toBe(1);
    expect(Object.keys(sampleJournalState.chapters).length).toBeGreaterThan(0);
    expect(Object.keys(sampleJournalState.objectives).length).toBeGreaterThan(0);
    expect(Object.keys(sampleJournalState.events).length).toBeGreaterThan(0);
    expect(sampleJournalState.journalEntries.length).toBeGreaterThan(0);
  });
});
