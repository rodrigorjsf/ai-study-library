export const title = "What the owner sees while /run-spec runs";

const ownerState = (v) => {
  if (v.phase === "reported") return "done";
  if (v.phase === "review") return "reviewing";
  if (v.crashes === 0) return "running";
  return v.phase === "recover" || v.waveFor === "integrate" ? "interrupted" : "resumed";
};

export const state = ownerState;

export const group = (v) =>
  ({ running: "working", resumed: "working", interrupted: "stopped", reviewing: "checking", done: "finished" })[
    ownerState(v)
  ];

export const colors = { working: "blue", stopped: "orange", checking: "purple", finished: "teal" };

const labels = {
  SessionDrops: "the session drops",
  RemoveMergedOrphan: "the dispatcher removes the branch of a ticket that already merged",
  RemoveFailedOrphan: "the dispatcher removes the branch of a failed ticket",
  QueueFinishedOrphan: "the dispatcher queues a finished ticket that was never integrated",
  DiscardUnfinishedOrphan: "the dispatcher discards an unfinished ticket that is done or skipped",
  ResumeUnfinishedOrphan: "the dispatcher resumes an unfinished ticket",
  FailInterruptedOrphan: "the dispatcher fails a ticket that was cut off too often",
  CleanUpOrphan: "the dispatcher cleans up an orphan branch",
  FinishSortingOrphans: "the dispatcher finishes sorting the orphan branches",
  IntegrateFinishedOrphans: "the dispatcher integrates the finished tickets",
  NoFinishedOrphans: "no finished ticket waits for integration",
  RecordUnrecordedMerges: "the dispatcher records the merges nobody recorded",
  FinishOwedTriage: "the dispatcher runs the triage it owed",
  ResumeOrphans: "the dispatcher resumes the unfinished tickets",
  NoOrphansToResume: "no unfinished ticket needs resuming",
  DispatchWave: "the dispatcher starts a wave of tickets",
  ImplementerCommits: "a ticket's implementer commits",
  ImplementerFinishes: "a ticket's implementer finishes",
  ImplementerWritesFailure: "a ticket's implementer fails",
  ImplementerReportsFailure: "a ticket's implementer fails",
  CollectResult: "the dispatcher collects a ticket's result",
  CleanUpFailedTicket: "the dispatcher cleans up a failed ticket",
  StartIntegration: "the dispatcher starts integrating the wave",
  MergeTicket: "a ticket merges into the work branch",
  RemoveMergedBranch: "the dispatcher removes the branch of a merged ticket",
  RecordWave: "the dispatcher records the wave",
  TriageStart: "the dispatcher triages the follow-ups",
  FinishWave: "the wave ends",
  ReadFrontier: "no ticket is left to build",
  FixerRecordsBase: "the fixer notes where its fixes start",
  FixerCommits: "the fixer commits a fix",
  FixerReturns: "the fixer returns",
  ReviewRound: "a final review round reports",
  ShipReport: "the final report is printed",
  ReportIsPrinted: "the run is over",
};

export const step = (action, from, to) => {
  if (action === "TriageFinish")
    return to.inScope.length > from.inScope.length
      ? "the triage attaches a follow-up ticket"
      : "the triage ends";
  return labels[action];
};
