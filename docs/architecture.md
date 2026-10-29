# AEC architecture: where it is going

**Status: proposed, pending Zach.** This was agreed between Kate (ChatGPT) and Claude in the AEC coordination thread "Synthesize Compare AEC Documentation" (round 1, 2026-10-28), after Kate's reconstruction of Zach's 2025–2026 thinking on AI-native documentation. Nothing here is built unless the status table says so.

## What AEC is for

> AEC should help an AI development system understand what it is building, observe what it is becoming, detect when those diverge, and preserve the reasoning needed to make deliberate changes.

This is a candidate north star (Kate's formulation), not an established capability. It extends Zach's earlier work:
- **Dual-Channel Coding** (June 2025): executable code and semantic architecture are kept as coupled representations and reconciled continuously.
- **Run/Drift** (July 2025): implementation alternates with reflection on whether the project is still becoming what it was meant to be.
- **The evidence-and-authority model** (October 2026): what justifies a conclusion, and who may revise it.

Zach's framing for the next stage: **preserve the engineering wisdom, not necessarily the engineering workflow.** Established techniques (contracts, regression tests, version control, concurrency control) stay where they work. The workflow around them is redesigned for a setting in which several AI agents implement, inspect and review. Spec Kit is one integration surface, not the boundary of AEC.

## The current imbalance

The justification machinery (records, change impact, authority, evidence tiers) is ahead of the machinery that **captures, maintains, reconciles and delivers** architectural knowledge to agents. At WP0 planning, AEC itself contained the drift it exists to catch (repaired in spec 003; pending review):
- an `AGENTS.md` and `CHARTER.md` inherited from Cognitive-Scaffolding (Typer, FAISS, S3, a missing `VISION.md`);
- an importer that drops the singular `@ai-source-file` used by AEC's own purpose files.

## Representations

Each representation is kept separately, with its own edge types and provenance. Cross-representation queries are allowed; collapsing different relationships into one meaning is not. A call edge, a declared responsibility, a `supports` relation and a handoff dependency establish different things.

| | Representation | Question it answers | Status |
|---|---|---|---|
| a | **Code topology**: AST edges (`defines`, `imports`, `inherits`, `calls`, `references`) | What is connected to what? | built (`aec edges`) |
| b | **Co-change**, from git history | What changes together? (not proof of coupling) | planned (WP1B) |
| c | **Reasoning records** | What justifies what, and who may revise it? | built (`.aec/records.jsonl`, `check`, `impact`) |
| d | **Semantic contracts**: purpose files parsed into declared IO, responsibilities, guarantees, risks | What is each part supposed to do? | partial (WP0 imports structured declarations and full text; semantic reconciliation remains planned) |
| e | **Coordination**: handoffs and the commit and record versions they relied on | What did each agent assume when it acted? | planned (WP4, via relay-kit's handoff ledger) |

**Graph metrics are computed per projection, never across all edge kinds.** The projections are:
- module dependency;
- resolved calls;
- inheritance;
- containment (`defines`);
- co-change.

Each metric states its direction, granularity, how it treats unresolved edges, and what it can legitimately mean. Known reachability is not runtime impact. A **visibility** figure (unresolved edges and skipped files in the region, reported separately, with an explicit denominator) goes with every structural answer.

## Kinds of finding

A detected difference is not automatically a defect:
- **Observation:** something changed.
- **Potential conflict:** the change may violate a declared relationship, requirement or assumption.
- **Confirmed divergence:** evidence supports an actual inconsistency.
- **Authorized evolution:** the project deliberately changed its design or purpose.

There are three kinds of drift, each defined as a disagreement between representations:

| Drift | Representations compared |
|---|---|
| implementation drift | (a) vs (d) |
| architectural drift | (a) over time, against declared boundaries |
| coordination drift | (e) vs the current (a) and (c) |

Drift review supports evolution: it does not enforce conformity with the previous design.

## Who does what

| Role | Does | Never |
|---|---|---|
| **Core (AEC, deterministic)** | establishes facts and their provenance; checks formal invariants (including architectural constraints that can be stated precisely, such as forbidden imports or declared public interfaces); finds inconsistencies and potential impacts; builds context and reconciliation packets | judges semantic adequacy; edits records it didn't create on request |
| **Reviewer agents** | interpret ambiguous findings; compare declared intent with observed implementation; challenge assumptions; propose revisions or experiments | silently change the commitments they evaluate. Their verdicts enter as candidate-tier evidence or claims, recording what was examined, the method used and the limits |
| **Execution agents** | implement authorized changes; collect the resulting observations | review their own work as if independent |
| **Zach (or an explicitly authorized decision-maker)** | sets or revises goals, commitments, permissions and acceptable trade-offs | — |

A typed `authorized_by` is a *claim* of authorization, not verified consent.

## Mechanisms

- **Commit-addressed snapshots.** A snapshot is keyed by the source revision *and* the extraction method: extractor version, configuration, exclusions, normalisation. Environment-dependent header fields are normalised before results are compared across machines. PR comparisons use the actual merge-base and head. Working-tree snapshots stay separate and never claim to be a commit. Extraction never executes the target's code.
- **Evidence applicability.** An observation records the revision and the symbols it concerned, the method, its conditions, and what it does not establish. A code change never erases or falsifies a historical observation. It triggers reassessment of whether the observation still applies to the *current* claim (`observed_on` today; to be generalised).
- **Context delivery.** `aec context <symbol>` gives architectural understanding; `aec context --change <scope>` gives what a proposed change needs. The briefing is deterministic, concise and source-linked, and it includes:
  - declared purpose and what success means (outcome, not just conformance);
  - committed requirements and provisional claims;
  - structural neighbours and known consumers;
  - decisions, *rejected alternatives* where they were recorded, and open challenges;
  - visibility limits.

  It never contains an unsourced narrative.
- **Semantic reconciliation.** AEC builds a packet that sets the declared contract alongside the observed facts:
  - signatures, sync vs async, imports and callers;
  - tests touching the code, history, decisions and evidence;
  - known analysis limits.

  An independent reviewer agent judges it. Mandatory fixture: Cognitive-Scaffolding's documented async orchestrator that is actually a synchronous stub (September 2025 audit). Negative controls: implementation changes that still satisfy the contract.
- **Run/Drift as events.** `aec drift` lists triggers:
  - topology: a new strongly connected component in the right projection, an edge crossing a declared boundary, a jump in fan-in;
  - records: stale or contested conclusions;
  - coordination: a handoff whose premises may no longer hold.

  A drift review is an agent role. Its loop is: understand → implement → observe → reconcile → revise → preserve → retrieve.
- **Preservation**, using existing records:
  - observed behaviour is evidence (`behavioral_observation`);
  - proposed protection is a provisional requirement;
  - committed protection is a committed requirement.

  An undiscovered dependency is not an absent dependency.
- **Handoff premise checks** adapt relay-kit's ledger rather than duplicating it. The result is scoped:

  | result | meaning |
  |---|---|
  | source changed | the source version moved |
  | relevant dependency changed | something the handoff relied on moved |
  | referenced record superseded | a record it cited has a newer version |
  | premise invalidated | a premise demonstrably no longer holds |
  | **unable to determine** | the checker can't tell whether the change matters |

  Staleness is a reason to investigate, not proof of error.

## Constraints that stay

- Standard library only, deterministic output, report-only.
- Records are append-only.
- Every check has a violating fixture and a decoy.
- Results are labelled "structural".
- No graph database or service unless plain records demonstrably fail.

## Work packages

| WP | Content | Status |
|---|---|---|
| **WP0** | AEC reconciled with itself: importer repairs (singular field, structured fields, no silent truncation, heading variants); `AGENTS.md`, `CHARTER.md` and the constitution reconciled, and the `VISION.md` reference resolved; Oct 26–28 history imported as *candidate*, source-linked records, with a list of what Zach must confirm; evaluation criteria designed now (`docs/failure-modes.md`); a cold-agent usability check | **implemented, pending review**: `specs/003-self-reconciliation/`. Claude reviews the technical side, Kate reviews purpose; candidate history still needs Zach’s confirmation |
| WP1A | commit-addressed snapshots and structural diffs (merge-base vs head), basic reachability, fan-in and fan-out, a CI report as an artifact (no PR comments yet) | after WP0 |
| WP2A | minimal `aec context <symbol>` and `--change` | right after WP1A |
| WP1B | historical analytics: SCC per projection, temporal deltas, churn, co-change, boundary changes | alongside WP2 expansion |
| WP3 | reconciliation packet, reviewer-agent protocol, `aec drift` | once WP1A and WP2A are usable |
| WP4 | handoff premise check through relay-kit | — |
| WP5 | evaluation: Data-Guide replays (realistic and information-matched), documentation-effectiveness conditions A/B/C, Kate's five blind cases, and graph-informed multi-agent task decomposition (fewer integration conflicts?) | criteria designed in WP0 |

Implementation is one implementer at a time **per overlapping architectural area**. Independent tasks may run in parallel.

The evaluation counts useful outcomes, never the number of records or reports produced. For example:
- an endangered guarantee caught before the harmful change;
- two agents found working from incompatible states;
- a dependency cycle caught while it is still cheap to fix.
