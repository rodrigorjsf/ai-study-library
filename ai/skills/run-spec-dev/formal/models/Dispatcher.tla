---- MODULE Dispatcher ----
EXTENDS Integers, Sequences, FiniteSets

CONSTANTS InitialTickets, BlockedTickets, AttachableTickets,
          ResumeCap, AttemptCap, RoundCap, TriageCap, WaveSize, MaxCrashes

VARIABLES phase, stage, crashes,
          inScope, branch, committed, status, followUps, merged, attempts, resumes, integrations, origin,
          log, read, reported, proven, unproven, base, fixFile,
          owedWave, owedFix, triageIns, triageOpen,
          wave, collected, failing, toMerge, mergedInWave, waveStep, waveFor,
          sorted, toCleanUp, toIntegrate, toResume

ControlVars == <<phase, stage, crashes>>
TicketVars == <<inScope, branch, committed, status, followUps, merged, attempts, resumes, integrations, origin>>
ReviewVars == <<log, read, reported, proven, unproven, base, fixFile>>
TriageVars == <<owedWave, owedFix, triageIns, triageOpen>>
WaveVars == <<wave, collected, failing, toMerge, mergedInWave, waveStep, waveFor>>
RecoveryVars == <<sorted, toCleanUp, toIntegrate, toResume>>
vars == <<ControlVars, TicketVars, ReviewVars, TriageVars, WaveVars, RecoveryVars>>

Tickets == InitialTickets \union BlockedTickets \union AttachableTickets
Rounds == 1 .. (RoundCap + 2)
NoBase == -1
WaveSource == 0
NoTriage == -1

Remaining == {t \in inScope : ~merged[t] /\ attempts[t] < AttemptCap}
Ready == Remaining \ BlockedTickets

MergedOrphan(t) == branch[t] /\ merged[t]
FailedOrphan(t) == branch[t] /\ ~merged[t] /\ status[t] = "FAILED"
FinishedOrphan(t) == branch[t] /\ ~merged[t] /\ status[t] = "DONE"
UnfinishedOrphan(t) == branch[t] /\ ~merged[t] /\ status[t] = "none"

ReportedCount == Cardinality({r \in Rounds : reported[r]})
NextRound == ReportedCount + 1
Blocking(r) == proven[r]
Advisory(r) == unproven[r]
Route(r) == IF Blocking(r) > 0 THEN "blocking" ELSE IF Advisory(r) > 0 THEN "advisory-only" ELSE "clean"
FixerCommitted(r) == \E i \in DOMAIN log : log[i].kind = "fix" /\ log[i].round = r
FixerOwed(r) == reported[r] /\ Route(r) # "clean" /\ ~fixFile[r]
AnyFixerOwed == \E r \in Rounds : FixerOwed(r)
TriageOwed == triageIns < TriageCap /\ (owedWave > 0 \/ owedFix # {})
AttachedTicketMerged(r) == \E i \in DOMAIN log : log[i].kind = "ticket" /\ log[i].after = r
NoTicketSince(from) == \A i \in DOMAIN log : i > from => log[i].kind # "ticket"
ReadsFrom(r) == IF r = 1 THEN 0 ELSE base[r - 1]

ShipNow ==
  \/ NextRound > RoundCap
  \/ /\ NextRound >= 2
     /\ Len(log) = base[NextRound - 1]
  \/ /\ NextRound >= 2
     /\ Blocking(NextRound - 1) = 0
     /\ \/ Route(NextRound - 1) = "clean"
        \/ /\ fixFile[NextRound - 1]
           /\ NoTicketSince(base[NextRound - 1])

TriageContext ==
  \/ phase = "wave" /\ waveStep = "triaging"
  \/ phase = "recover" /\ stage = "triage"
  \/ phase = "review" /\ ~AnyFixerOwed

Init ==
  /\ phase = "recover"
  /\ stage = "sort"
  /\ crashes = 0
  /\ inScope = InitialTickets \union BlockedTickets
  /\ branch = [t \in Tickets |-> FALSE]
  /\ committed = [t \in Tickets |-> FALSE]
  /\ status = [t \in Tickets |-> "none"]
  /\ followUps = [t \in Tickets |-> FALSE]
  /\ merged = [t \in Tickets |-> FALSE]
  /\ attempts = [t \in Tickets |-> 0]
  /\ resumes = [t \in Tickets |-> 0]
  /\ integrations = [t \in Tickets |-> 0]
  /\ origin = [t \in Tickets |-> 0]
  /\ log = <<>>
  /\ read = {}
  /\ reported = [r \in Rounds |-> FALSE]
  /\ proven = [r \in Rounds |-> 0]
  /\ unproven = [r \in Rounds |-> 0]
  /\ base = [r \in Rounds |-> NoBase]
  /\ fixFile = [r \in Rounds |-> FALSE]
  /\ owedWave = 0
  /\ owedFix = {}
  /\ triageIns = 0
  /\ triageOpen = NoTriage
  /\ wave = {}
  /\ collected = {}
  /\ failing = {}
  /\ toMerge = {}
  /\ mergedInWave = {}
  /\ waveStep = "none"
  /\ waveFor = "none"
  /\ sorted = {}
  /\ toCleanUp = {}
  /\ toIntegrate = {}
  /\ toResume = {}

SessionDrops ==
  /\ phase \in {"frontier", "wave", "recover", "review"}
  /\ crashes < MaxCrashes
  /\ crashes' = crashes + 1
  /\ phase' = "recover"
  /\ stage' = "sort"
  /\ wave' = {}
  /\ collected' = {}
  /\ failing' = {}
  /\ toMerge' = {}
  /\ mergedInWave' = {}
  /\ waveStep' = "none"
  /\ waveFor' = "none"
  /\ sorted' = {}
  /\ toCleanUp' = {}
  /\ toIntegrate' = {}
  /\ toResume' = {}
  /\ UNCHANGED <<TicketVars, ReviewVars, TriageVars>>

RemoveMergedOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \notin sorted
  /\ MergedOrphan(t)
  /\ sorted' = sorted \union {t}
  /\ toCleanUp' = toCleanUp \union {t}
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, TriageVars, WaveVars, toIntegrate, toResume>>

RemoveFailedOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \notin sorted
  /\ FailedOrphan(t)
  /\ sorted' = sorted \union {t}
  /\ toCleanUp' = toCleanUp \union {t}
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, TriageVars, WaveVars, toIntegrate, toResume>>

QueueFinishedOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \notin sorted
  /\ FinishedOrphan(t)
  /\ sorted' = sorted \union {t}
  /\ toIntegrate' = toIntegrate \union {t}
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, TriageVars, WaveVars, toCleanUp, toResume>>

DiscardUnfinishedOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \notin sorted
  /\ UnfinishedOrphan(t)
  /\ t \notin Remaining
  /\ sorted' = sorted \union {t}
  /\ toCleanUp' = toCleanUp \union {t}
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, TriageVars, WaveVars, toIntegrate, toResume>>

ResumeUnfinishedOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \notin sorted
  /\ UnfinishedOrphan(t)
  /\ t \in Remaining
  /\ resumes[t] + 1 <= ResumeCap
  /\ resumes' = [resumes EXCEPT ![t] = resumes[t] + 1]
  /\ sorted' = sorted \union {t}
  /\ toResume' = toResume \union {t}
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, status, followUps, merged, attempts, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, toCleanUp, toIntegrate>>

FailInterruptedOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \notin sorted
  /\ UnfinishedOrphan(t)
  /\ t \in Remaining
  /\ resumes[t] + 1 > ResumeCap
  /\ attempts' = [attempts EXCEPT ![t] = attempts[t] + 1]
  /\ sorted' = sorted \union {t}
  /\ toCleanUp' = toCleanUp \union {t}
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, status, followUps, merged, resumes, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, toIntegrate, toResume>>

CleanUpOrphan(t) ==
  /\ phase = "recover" /\ stage = "sort"
  /\ t \in toCleanUp
  /\ branch[t]
  /\ branch' = [branch EXCEPT ![t] = FALSE]
  /\ UNCHANGED <<ControlVars, inScope, committed, status, followUps, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, RecoveryVars>>

FinishSortingOrphans ==
  /\ phase = "recover" /\ stage = "sort"
  /\ \A t \in Tickets : branch[t] => t \in sorted
  /\ \A t \in toCleanUp : ~branch[t]
  /\ stage' = "integrate"
  /\ UNCHANGED <<phase, crashes, TicketVars, ReviewVars, TriageVars, WaveVars, RecoveryVars>>

IntegrateFinishedOrphans ==
  /\ phase = "recover" /\ stage = "integrate"
  /\ toIntegrate # {}
  /\ phase' = "wave"
  /\ waveFor' = "integrate"
  /\ wave' = toIntegrate
  /\ collected' = toIntegrate
  /\ toMerge' = toIntegrate
  /\ mergedInWave' = {}
  /\ waveStep' = "integrating"
  /\ UNCHANGED <<stage, crashes, TicketVars, ReviewVars, TriageVars, failing, RecoveryVars>>

NoFinishedOrphans ==
  /\ phase = "recover" /\ stage = "integrate"
  /\ toIntegrate = {}
  /\ stage' = "record"
  /\ UNCHANGED <<phase, crashes, TicketVars, ReviewVars, TriageVars, WaveVars, RecoveryVars>>

RecordUnrecordedMerges ==
  LET unrecorded == {t \in Tickets : merged[t] /\ status[t] = "DONE" /\ integrations[t] = 0}
  IN /\ phase = "recover" /\ stage = "record"
     /\ integrations' = [t \in Tickets |-> IF t \in unrecorded THEN integrations[t] + 1 ELSE integrations[t]]
     /\ owedWave' = owedWave + IF \E t \in unrecorded : followUps[t] THEN 1 ELSE 0
     /\ stage' = "triage"
     /\ UNCHANGED <<phase, crashes, inScope, branch, committed, status, followUps, merged, attempts, resumes, origin,
                    ReviewVars, owedFix, triageIns, triageOpen, WaveVars, RecoveryVars>>

FinishOwedTriage ==
  /\ phase = "recover" /\ stage = "triage"
  /\ triageOpen = NoTriage
  /\ ~TriageOwed
  /\ stage' = "resume"
  /\ UNCHANGED <<phase, crashes, TicketVars, ReviewVars, TriageVars, WaveVars, RecoveryVars>>

ResumeOrphans ==
  /\ phase = "recover" /\ stage = "resume"
  /\ toResume # {}
  /\ phase' = "wave"
  /\ stage' = "none"
  /\ waveFor' = "resume"
  /\ waveStep' = "running"
  /\ wave' = toResume
  /\ collected' = {}
  /\ sorted' = {}
  /\ toCleanUp' = {}
  /\ toIntegrate' = {}
  /\ toResume' = {}
  /\ UNCHANGED <<crashes, TicketVars, ReviewVars, TriageVars, failing, toMerge, mergedInWave>>

NoOrphansToResume ==
  /\ phase = "recover" /\ stage = "resume"
  /\ toResume = {}
  /\ phase' = "frontier"
  /\ stage' = "none"
  /\ sorted' = {}
  /\ toCleanUp' = {}
  /\ toIntegrate' = {}
  /\ UNCHANGED <<crashes, TicketVars, ReviewVars, TriageVars, WaveVars, toResume>>

DispatchWave ==
  /\ phase = "frontier"
  /\ Ready # {}
  /\ \E picked \in SUBSET Ready :
       /\ picked # {}
       /\ Cardinality(picked) <= WaveSize
       /\ wave' = picked
       /\ branch' = [t \in Tickets |-> t \in picked \/ branch[t]]
       /\ committed' = [t \in Tickets |-> t \notin picked /\ committed[t]]
       /\ status' = [t \in Tickets |-> IF t \in picked THEN "none" ELSE status[t]]
       /\ followUps' = [t \in Tickets |-> t \notin picked /\ followUps[t]]
  /\ phase' = "wave"
  /\ waveFor' = "frontier"
  /\ waveStep' = "running"
  /\ collected' = {}
  /\ UNCHANGED <<stage, crashes, inScope, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, failing, toMerge, mergedInWave, RecoveryVars>>

Running(t) ==
  /\ phase = "wave" /\ waveStep = "running"
  /\ t \in wave \ collected
  /\ status[t] = "none"
  /\ t \notin failing

ImplementerCommits(t) ==
  /\ Running(t)
  /\ ~committed[t]
  /\ committed' = [committed EXCEPT ![t] = TRUE]
  /\ UNCHANGED <<ControlVars, inScope, branch, status, followUps, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, RecoveryVars>>

ImplementerFinishes(t) ==
  /\ Running(t)
  /\ committed[t]
  /\ status' = [status EXCEPT ![t] = "DONE"]
  /\ \/ followUps' = [followUps EXCEPT ![t] = TRUE]
     \/ followUps' = [followUps EXCEPT ![t] = FALSE]
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, RecoveryVars>>

ImplementerWritesFailure(t) ==
  /\ Running(t)
  /\ attempts' = [attempts EXCEPT ![t] = attempts[t] + 1]
  /\ failing' = failing \union {t}
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, status, followUps, merged, resumes, integrations, origin,
                 ReviewVars, TriageVars, wave, collected, toMerge, mergedInWave, waveStep, waveFor, RecoveryVars>>

ImplementerReportsFailure(t) ==
  /\ phase = "wave" /\ waveStep = "running"
  /\ t \in failing
  /\ status' = [status EXCEPT ![t] = "FAILED"]
  /\ failing' = failing \ {t}
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, followUps, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, wave, collected, toMerge, mergedInWave, waveStep, waveFor, RecoveryVars>>

CollectResult(t) ==
  /\ phase = "wave" /\ waveStep = "running"
  /\ t \in wave \ collected
  /\ status[t] # "none"
  /\ collected' = collected \union {t}
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, TriageVars, wave, failing, toMerge, mergedInWave, waveStep, waveFor,
                 RecoveryVars>>

CleanUpFailedTicket(t) ==
  /\ phase = "wave" /\ waveStep = "running"
  /\ t \in collected
  /\ status[t] = "FAILED"
  /\ branch[t]
  /\ branch' = [branch EXCEPT ![t] = FALSE]
  /\ UNCHANGED <<ControlVars, inScope, committed, status, followUps, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, RecoveryVars>>

StartIntegration ==
  /\ phase = "wave" /\ waveStep = "running"
  /\ collected = wave
  /\ \A t \in wave : status[t] = "FAILED" => ~branch[t]
  /\ toMerge' = {t \in wave : status[t] = "DONE"}
  /\ mergedInWave' = {}
  /\ waveStep' = "integrating"
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, TriageVars, wave, collected, failing, waveFor, RecoveryVars>>

MergeTicket(t) ==
  /\ phase = "wave" /\ waveStep = "integrating"
  /\ t \in toMerge \ mergedInWave
  /\ merged' = [merged EXCEPT ![t] = TRUE]
  /\ log' = IF merged[t] THEN log ELSE Append(log, [kind |-> "ticket", after |-> origin[t]])
  /\ mergedInWave' = mergedInWave \union {t}
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, status, followUps, attempts, resumes, integrations, origin,
                 read, reported, proven, unproven, base, fixFile, TriageVars,
                 wave, collected, failing, toMerge, waveStep, waveFor, RecoveryVars>>

RemoveMergedBranch(t) ==
  /\ phase = "wave" /\ waveStep = "integrating"
  /\ t \in mergedInWave
  /\ branch[t]
  /\ branch' = [branch EXCEPT ![t] = FALSE]
  /\ UNCHANGED <<ControlVars, inScope, committed, status, followUps, merged, attempts, resumes, integrations, origin,
                 ReviewVars, TriageVars, WaveVars, RecoveryVars>>

RecordWave ==
  /\ phase = "wave" /\ waveStep = "integrating"
  /\ mergedInWave = toMerge
  /\ \A t \in mergedInWave : ~branch[t]
  /\ integrations' = [t \in Tickets |-> IF t \in mergedInWave THEN integrations[t] + 1 ELSE integrations[t]]
  /\ owedWave' = owedWave + IF \E t \in mergedInWave : followUps[t] THEN 1 ELSE 0
  /\ waveStep' = "triaging"
  /\ UNCHANGED <<ControlVars, inScope, branch, committed, status, followUps, merged, attempts, resumes, origin,
                 ReviewVars, owedFix, triageIns, triageOpen, wave, collected, failing, toMerge, mergedInWave, waveFor,
                 RecoveryVars>>

TriageStart(source) ==
  /\ TriageContext
  /\ triageOpen = NoTriage
  /\ triageIns < TriageCap
  /\ \/ /\ source = WaveSource
        /\ owedWave > 0
        /\ owedWave' = owedWave - 1
        /\ UNCHANGED owedFix
     \/ /\ source \in owedFix
        /\ owedFix' = owedFix \ {source}
        /\ UNCHANGED owedWave
  /\ triageIns' = triageIns + 1
  /\ triageOpen' = source
  /\ UNCHANGED <<ControlVars, TicketVars, ReviewVars, WaveVars, RecoveryVars>>

TriageFinish ==
  /\ TriageContext
  /\ triageOpen # NoTriage
  /\ triageOpen' = NoTriage
  /\ \/ UNCHANGED <<phase, inScope, origin>>
     \/ /\ \E ticket \in AttachableTickets \ inScope :
             /\ inScope' = inScope \union {ticket}
             /\ origin' = [origin EXCEPT ![ticket] = ReportedCount]
        /\ phase' = IF phase = "review" THEN "frontier" ELSE phase
  /\ UNCHANGED <<stage, crashes, branch, committed, status, followUps, merged, attempts, resumes, integrations,
                 ReviewVars, owedWave, owedFix, triageIns, WaveVars, RecoveryVars>>

FinishWave ==
  /\ phase = "wave" /\ waveStep = "triaging"
  /\ triageOpen = NoTriage
  /\ ~TriageOwed
  /\ IF waveFor = "integrate"
       THEN /\ phase' = "recover"
            /\ stage' = "record"
            /\ toIntegrate' = {}
       ELSE /\ phase' = "frontier"
            /\ UNCHANGED <<stage, toIntegrate>>
  /\ wave' = {}
  /\ collected' = {}
  /\ failing' = {}
  /\ toMerge' = {}
  /\ mergedInWave' = {}
  /\ waveStep' = "none"
  /\ waveFor' = "none"
  /\ UNCHANGED <<crashes, TicketVars, ReviewVars, TriageVars, sorted, toCleanUp, toResume>>

ReadFrontier ==
  /\ phase = "frontier"
  /\ Ready = {}
  /\ phase' = "review"
  /\ UNCHANGED <<stage, crashes, TicketVars, ReviewVars, TriageVars, WaveVars, RecoveryVars>>

FixerRecordsBase(r) ==
  /\ phase = "review"
  /\ FixerOwed(r)
  /\ base[r] = NoBase
  /\ base' = [base EXCEPT ![r] = Len(log)]
  /\ UNCHANGED <<ControlVars, TicketVars, log, read, reported, proven, unproven, fixFile, TriageVars, WaveVars, RecoveryVars>>

FixerCommits(r) ==
  /\ phase = "review"
  /\ FixerOwed(r)
  /\ base[r] # NoBase
  /\ ~FixerCommitted(r)
  /\ log' = Append(log, [kind |-> "fix", round |-> r])
  /\ UNCHANGED <<ControlVars, TicketVars, read, reported, proven, unproven, base, fixFile, TriageVars, WaveVars, RecoveryVars>>

FixerReturns(r) ==
  /\ phase = "review"
  /\ FixerOwed(r)
  /\ base[r] # NoBase
  /\ fixFile' = [fixFile EXCEPT ![r] = TRUE]
  /\ \/ owedFix' = owedFix \union {r}
     \/ UNCHANGED owedFix
  /\ UNCHANGED <<ControlVars, TicketVars, log, read, reported, proven, unproven, base,
                 owedWave, triageIns, triageOpen, WaveVars, RecoveryVars>>

ReviewRound ==
  /\ phase = "review"
  /\ ~AnyFixerOwed
  /\ triageOpen = NoTriage
  /\ ~TriageOwed
  /\ ~ShipNow
  /\ reported' = [reported EXCEPT ![NextRound] = TRUE]
  /\ \E blockingFindings \in 0 .. 1, advisoryFindings \in 0 .. 1 :
       /\ proven' = [proven EXCEPT ![NextRound] = blockingFindings]
       /\ unproven' = [unproven EXCEPT ![NextRound] = advisoryFindings]
  /\ read' = read \union {i \in DOMAIN log : i > ReadsFrom(NextRound)}
  /\ UNCHANGED <<ControlVars, TicketVars, log, base, fixFile, TriageVars, WaveVars, RecoveryVars>>

ShipReport ==
  /\ phase = "review"
  /\ ~AnyFixerOwed
  /\ triageOpen = NoTriage
  /\ ~TriageOwed
  /\ ShipNow
  /\ phase' = "reported"
  /\ UNCHANGED <<stage, crashes, TicketVars, ReviewVars, TriageVars, WaveVars, RecoveryVars>>

ReportIsPrinted ==
  /\ phase = "reported"
  /\ UNCHANGED vars

Next ==
  \/ SessionDrops
  \/ \E t \in Tickets :
       RemoveMergedOrphan(t) \/ RemoveFailedOrphan(t) \/ QueueFinishedOrphan(t)
       \/ DiscardUnfinishedOrphan(t) \/ ResumeUnfinishedOrphan(t) \/ FailInterruptedOrphan(t)
       \/ CleanUpOrphan(t)
  \/ FinishSortingOrphans
  \/ IntegrateFinishedOrphans \/ NoFinishedOrphans
  \/ RecordUnrecordedMerges
  \/ FinishOwedTriage
  \/ ResumeOrphans \/ NoOrphansToResume
  \/ DispatchWave
  \/ \E t \in Tickets :
       ImplementerCommits(t) \/ ImplementerFinishes(t) \/ ImplementerWritesFailure(t)
       \/ ImplementerReportsFailure(t) \/ CollectResult(t) \/ CleanUpFailedTicket(t)
       \/ MergeTicket(t) \/ RemoveMergedBranch(t)
  \/ StartIntegration \/ RecordWave
  \/ \E source \in {WaveSource} \union Rounds : TriageStart(source)
  \/ TriageFinish
  \/ FinishWave
  \/ ReadFrontier
  \/ \E r \in Rounds : FixerRecordsBase(r) \/ FixerCommits(r) \/ FixerReturns(r)
  \/ ReviewRound
  \/ ShipReport
  \/ ReportIsPrinted

Spec == Init /\ [][Next]_vars

TypeOK ==
  /\ phase \in {"recover", "frontier", "wave", "review", "reported"}
  /\ stage \in {"sort", "integrate", "record", "triage", "resume", "none"}
  /\ crashes \in 0 .. MaxCrashes
  /\ status \in [Tickets -> {"none", "DONE", "FAILED"}]
  /\ branch \in [Tickets -> BOOLEAN]
  /\ merged \in [Tickets -> BOOLEAN]
  /\ reported \in [Rounds -> BOOLEAN]
  /\ waveStep \in {"none", "running", "integrating", "triaging"}
  /\ \A i \in DOMAIN log : log[i].kind \in {"ticket", "fix"}

NeverIntegratedTwice == \A t \in Tickets : integrations[t] <= 1

ResumeCapHolds == \A t \in Tickets : resumes[t] <= ResumeCap

AttemptCapHolds == \A t \in Tickets : attempts[t] <= AttemptCap

FailedNeverMerged == \A t \in Tickets : status[t] = "FAILED" => ~merged[t]

NoOrphanSurvivesRecovery == phase = "frontier" => \A t \in Tickets : ~branch[t]

EveryTicketResolved ==
  phase = "reported" => \A t \in inScope : merged[t] \/ attempts[t] >= AttemptCap \/ t \in BlockedTickets

RoundsCapped == ReportedCount <= RoundCap

TriageCapped == triageIns <= TriageCap

AdvisoryNeverStartsRound ==
  \A r \in 2 .. (RoundCap + 2) : reported[r] => proven[r - 1] > 0 \/ AttachedTicketMerged(r - 1)

ShipsUnread(unit) ==
  \/ unit.kind = "ticket" /\ unit.after >= RoundCap
  \/ /\ unit.kind = "fix"
     /\ \/ unit.round >= RoundCap
        \/ Route(unit.round) = "advisory-only" /\ ~AttachedTicketMerged(unit.round)

UnreadIsListed ==
  phase = "reported" =>
    {i \in DOMAIN log : i \notin read} = {i \in DOMAIN log : ShipsUnread(log[i])}
====
