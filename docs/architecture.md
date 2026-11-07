# AEC architecture: where it is going

**Status: approved by Zach (2026-10-29: "I approve the architecture doc").** A later backlog addition (WP6, 2026-10-30) is marked separately and does not amend the WP1–WP5 approval. Status labels in the tables still say what is built vs planned. This was agreed between Kate (ChatGPT) and Claude in the AEC coordination thread "Synthesize Compare AEC Documentation" (round 1, 2026-10-28), after Kate's reconstruction of Zach's 2025–2026 thinking on AI-native documentation. Nothing here is built unless the status table says so.

## Direction update, 2026-10-31 (adopted by Zach: DEC-016 to DEC-022)

Source: drift round 2 with Kate (`aec-drift/round-2/synthesis.md` in Zach's records, relay-kit-private). Canonical decisions: `governance/decisions.jsonl` in the owner's relay-kit records (made with `relay-kit init`); Zach's instance is his relay-kit-private repository. Zach, 18:12 CT: "Yes, pretty good counts as approval."

- **Foundation and augmentation (DEC-016).** AEC's core is four guarantees: **recover** sources, **establish authority**, **check applicability**, **verify claims**. Better agent judgment (inquiry, unknowns, ontological awareness, mathetics) is an *experimental* augmentation layer and is developed by evidence. Every new component must say which guarantee it serves, or what it adds to agent judgment.
- **Safeguards to build now (DEC-017).** One small work package after WP1A:
  - recoverable provenance for consequential authorizations;
  - artifact integrity checked by tools;
  - premise checks before consequential execution.
- **Ownership (DEC-018).**
  - **relay-kit:** coordination mechanics (handoffs, delivery, versions, IDs, the thread index).
  - **AEC:** development semantics (purpose, obligations, evidence, premises).
  - **Decisions:** one canonical decision record, kept in the owner's relay-kit records (made with `relay-kit init`; Zach's instance is relay-kit-private). AEC references it rather than duplicating it. Where Telosmith finds those records is a setting: see `docs/integrations/relay-kit.md`.
  - **WP4 narrows** to semantic premise checks, reusing relay-kit's mechanics.
- **Drift and run (DEC-019).** Information crosses freely between them; authority never crosses implicitly. Drift includes pilots and feasibility tests, and drift threads are scoped to their round.
- **Planning (DEC-020).** A decision queue kept by agents, separating candidates from commitments, with checkpoints triggered by events. No sprints. This is a one-month trial.
- **Experiments (DEC-021).** The ontology audit first, then a minimal-vs-full AEC scenario, both in short-lived contexts.
- **Open question (DEC-022).** Whether AEC/EACH is one product or a family.

## What AEC is for

> AEC should help an AI development system understand what it is building, observe what it is becoming, detect when those diverge, and preserve the reasoning needed to make deliberate changes.

This is the approved north star (Kate's formulation), an intended outcome rather than an established capability. It extends Zach's earlier work:
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

WP1–WP5 are approved as direction and work-package order. Each still requires its own spec and PR; approval does not mean its planned capabilities are implemented. **WP6 was added to the backlog on 2026-10-30 for later scoping; adding it to the roadmap does not authorize implementation.**

| WP | Content | Status |
|---|---|---|
| **WP0** | AEC reconciled with itself: importer repairs (singular field, structured fields, no silent truncation, heading variants); `AGENTS.md`, `CHARTER.md` and the constitution reconciled, and the `VISION.md` reference resolved; Oct 26–28 history imported as *candidate*, source-linked records, with a list of what Zach must confirm; evaluation criteria designed now (`docs/failure-modes.md`); a cold-agent usability check | **merged (PR #14), released in v0.4.0**: `specs/003-self-reconciliation/`. Reconstructed history remains proposed until Zach confirms it (`docs/decisions-to-confirm.md`) |
| WP1A | commit-addressed snapshots and structural diffs (merge-base vs head), basic reachability, fan-in and fan-out, a CI report as an artifact (no PR comments yet) | **approved by Zach 2026-10-30; merged (PR #31), not yet released**; spec `specs/005-commit-snapshots/` |
| **WP2-probe** | Before any context delivery: show that giving agents graph information changes what they do, compared with the counterfactual of what they would produce without it, and find when it helps and when it misleads. Hand-built briefings at different levels of complexity, tasks where a hidden dependency matters, a control arm with ordinary repo access, and decoy (wrong or irrelevant) briefings | **run as probe-001 (2026-11-01): no signal** on easy tasks; it exposed the resolver gap fixed in C-11 (PR #32). A harder probe is C-12 |
| WP2A | minimal `aec context <symbol>` and `--change` | **moved back** behind WP2-probe (Zach, 2026-10-30): its design depends on what the probe shows actually changes agent decisions |
| **WP-S** | Source anchors/rationale; raw-byte integrity and locator observations; bounded record-directed retrieval and direct configured-root fallback | **merged (PR #17), released in v0.4.0**: `specs/004-source-anchors/`; meaning, authority, private providers and representation-002 remain outside this implementation |
| WP1B | historical analytics: SCC per projection, temporal deltas, churn, co-change, boundary changes | alongside WP2 expansion |
| WP3 | reconciliation packet, reviewer-agent protocol, `aec drift` | once WP1A and WP2A are usable |
| WP4 | handoff premise check through relay-kit | — |
| WP5 | evaluation: Data-Guide replays (realistic and information-matched), documentation-effectiveness conditions A/B/C, Kate's five blind cases, and graph-informed multi-agent task decomposition (fewer integration conflicts?) | criteria designed in WP0 |
| **WP6** | **adaptive project reporting**: baseline facts, purpose-/phase-specific versioned reporting profiles, provenance-linked reviewer interpretation, and proposals to update (or preserve) the profile when circumstances change; lightweight CLI/Markdown/JSON first, optional dashboards later | **backlog — tracked in [#15](https://github.com/eraevous/Telosmith/issues/15); not specified or implemented** |

### Value map and build gates (DEC-032, 2026-11-01)

Most of AEC's stated promise sits in parts that aren't built. That's especially true of getting the right
context to agents at the right time, and of coordination across agents. The costs are present today:
writing records, keeping them current, reviewing false alarms. Most of the planned cost relief is future
work. To stop "the next feature will unlock the value" becoming a standing excuse, every planned item is
tagged by what kind of value it offers and gated by a result it must show before it is built.

**Kinds**
- **Core:** the built mechanism whose value is being tested.
- **Cost reducer:** makes records cheaper to write or keep accurate.
- **Adoption unlock:** makes AEC usable or visible to someone outside the project without more research.
- **Research bet:** a hypothesis about agents or projects that needs evidence before engineering.

**Rules**
1. No planned item gets a spec until its gate is written and Zach has accepted it. The gates below are
   proposals; each is settled when its item comes up.
2. A gate names three things: the cheapest alternative the item must beat, the result that would justify
   building it, and the result that would mean dropping or simplifying it.
3. Gates for research bets are pre-registered, like probe-001 and the DEC-021 replay. A research bet runs as an
   `experiment` record (DEC-033): trying a few variants commits to no feature and no long-term support.
   Only a result that passes its gate is promoted into a spec.
4. A null result lowers an item's priority. "A later feature will make it pay off" isn't a reason to proceed.

| Item | Kind | Cheapest alternative to beat | Gate: result required before building | Evidence so far |
|---|---|---|---|---|
| Records, `check`, `impact`, `code-impact` | core | notes or ADRs, tests and PR review with the same facts | **DEC-021 replay** (pre-registered, not run; `evaluations/dec-021-protocol.md`, which superseded the value-001 draft): catches a consequential issue the well-configured baseline misses, at acceptable cost | probe-001: no outcome effect from graph briefings; self-hosting catches lapses, which a cheaper rule might also catch |
| Record authoring aid (agents draft records from specs, purpose files and PRs; people confirm) | cost reducer, adoption unlock | hand-written records; `import-purpose` | drafted records reach the same accuracy at much lower authoring time per record kept, measured on a real repository | `import-purpose` seeds provisional claims; authoring cost only partly logged (`docs/speckit-log.md`) |
| `code-impact` as a pull-request comment (WP1A posts no comments yet) | adoption unlock | running the command by hand; the CI artifact | over a run of real PRs, reviewers act on a meaningful share of comments, and the false-alarm rate on harmless changes is acceptable | AEC's own CI step is report-only; one known false alarm (AEC-R8, #20) |
| WP2A `aec context` (context delivery) | research bet | an agent searching the repository itself | a pre-registered harder probe (C-12) where search falls short shows briefings change outcomes, without the token cost eating the gain | probe-001: no signal, higher cost on 2 of 3 tasks |
| WP3 `aec drift`, reconciliation packet, automatic triggers | cost reducer, research bet | periodic manual audit (dogfood-001 is the baseline) | on a real history, finds stale records people missed, with high precision, in less review time than a manual audit | dogfood-001 found records lagging code by hand |
| Semantic reconciliation (purpose-file contracts against code) | research bet | `import-purpose`'s caller comparison; reading the purpose file in review | finds real contract–code breaks (such as Data-Guide `097c307`) beyond what the caller comparison already reports, at acceptable false alarms | value-001's scenario search: 3 qualifying breaks in about 320 commits |
| WP1B co-change and history analytics | research bet | static graph and `git log` | recovers dependants that later broke and that the static graph missed, on real history | none |
| WP4 handoff premise check (with relay-kit) | research bet | the handoff's "Context" section and a recipient re-reading main | a replay of real handoffs finds a recipient acting on a stale premise that the check would have flagged | relay-kit challenges list coordination failures, none yet traced to a stale premise |
| WP6 adaptive reporting | research bet | a plain status report from existing facts | its own validation (two project types, a lifecycle change, an immaterial-change decoy) shows decisions changed compared with the plain report | none; backlog (#15) |
| C-17 decision-context distillation | research bet | the decision ledger plus `git log` and the threads | a retrieval test recovers why a decision was made better or faster than those sources | none |
| Tiered agents with asymmetric information (C-20; AMB-tiered-agents; DEC-034: the stated purpose of edge snapshots) | research bet | every agent sees everything | an experiment where an architect agent works only from the edge snapshot, and implementers hold module and function detail, beats or matches the all-see arm on a task where architecture-level decisions matter, at lower cost or with fewer integration conflicts | none; probe-001 tested briefings, not this division of labour |
| WP5 evaluation | — | — | not a feature: the gates above are its instalments | the DEC-021 replay is the first |

**Ambitions.** Directions AEC might take are recorded as `ambition` records (DEC-033), not as roadmap
commitments. Before an item here is committed, the question is which recorded ambitions it would
foreclose. AEC's own: others find it useful, and tiered agentic development.

**Not gated here (decisions for Zach, not evidence questions):** the anchors question (C-09), how current
edge-snapshot use compares with its stated purpose (C-16, owner-held; purpose stated in DEC-034), and the package name and PyPI release.

### WP6 — adaptive reporting (backlog addition, 2026-10-30)

**Question:** Are we making meaningful progress toward *this project's* purposes, and what evidence supports that assessment? Different software projects and phases may warrant different reporting questions. WP6 is a **reporting projection over AEC's existing evidence**, not a competing project-management system or new source of purpose authority.

- **Baseline layer:** source-linked, deterministic reporting of available status, changes, tests, challenges, outstanding findings, and visibility/coverage limitations. Missing information remains missing.
- **Adaptive layer:** per-project, versioned reporting profiles driven by the committed purpose, project type/stage, risks, and unresolved questions. Indicator definitions, sources, applicability, reasons for inclusion, and any proposed-vs-accepted status remain inspectable.
- **Interpretive layer:** reviewer agents may identify consequential changes, evidence gaps, assumptions, and possible shifts of focus; interpretations are explicitly candidate claims rather than structural facts or owner decisions.
- **Report-profile reconciliation:** meaningful changes may prompt a *proposed* profile revision with an explained delta. **No change warranted** must remain a valid outcome when new information is immaterial. There is no silent replacement of committed reporting criteria.
- **Delivery:** an inspectable report model exposed first as CLI/Markdown/JSON for agents and people. Interactive dashboards may eventually consume it; no web app, central service, universal cross-project score, or Jira/Grafana replacement is in scope by default.

**Dependencies:** reuse WP1A/WP1B's source-addressed facts, WP2A's context delivery, and WP3's reconciliation packets; evaluate incrementality with WP5's information-matched baseline and cost accounting. Scoping and implementation need a later spec/PR and authorization. A proposed validation is two different project types, one meaningful lifecycle transition, one immaterial-change decoy, provenance/applicability checks, and measurement of decision usefulness and false alarms rather than report volume. See [issue #15](https://github.com/eraevous/Telosmith/issues/15).

Implementation is one implementer at a time **per overlapping architectural area**. Independent tasks may run in parallel.

The evaluation counts useful outcomes, never the number of records or reports produced. For example:
- an endangered guarantee caught before the harmful change;
- two agents found working from incompatible states;
- a dependency cycle caught while it is still cheap to fix.
