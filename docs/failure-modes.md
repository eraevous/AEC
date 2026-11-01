# Failure modes AEC is evaluated against

**Status: evaluation design, written before WP1–WP5 (Kate, AEC coordination round 1: "design its evaluation criteria during WP0").** This catalogue is the backbone of the WP5 evaluation. A mechanism counts as useful only if it detects or prevents a row's failure better than ordinary tests plus Spec Kit, at an acceptable cost. Sources: Kate's failure-mode table in the coordination thread (which drew on Wasowski, "Brownfield Spec and Preservation Contract", Medium, Oct 2026, as an inventory of problems rather than a prescription), Zach's additions (race conditions, protocol handoffs, desync), and AEC's own history.

For each row, the evaluation records the following (columns 1–6 are filled per fixture when it is built):
1. The failure mechanism and the condition under which it occurs.
2. What ordinary tests, CI and Spec Kit `analyze`/`converge` detect.
3. What AEC can observe, and through which representation (a–e in `architecture.md`).
4. Whether detection comes **before** the harmful change, or only after it.
5. Which conclusion still needs human judgment.
6. False positives, false negatives and operational cost (authoring and maintenance minutes, tokens).

## In the software being developed

| # | Failure | Established practice | Possible AEC contribution | Fixture |
|---|---|---|---|---|
| S1 | **Unintended side effect**: a shared function is "cleaned up" for one caller and breaks another (the discount/export example) | regression tests, dependency analysis, interface contracts | find affected consumers through (a) and surface their guarantees before implementation | planned |
| S2 | **Undocumented dependency**: a consumer the author never knew of | program analysis, characterisation tests, observability | keep (a) and (b) current and report visibility limits ("no caller found" is not evidence of no caller) | planned |
| S3 | **Accident becomes contract**: observed behaviour someone relies on, never committed | compatibility tests, semver, change management | keep observed / proposed-protection / committed-protection distinct (evidence → provisional → committed requirement) | planned |
| S4 | **Implementation drifts from declared purpose**: the code does something other than its contract says (Cognitive-Scaffolding async contract vs sync stub, Sept 2025) | traceability, design review | reconciliation packet (a)+(d) judged by an independent reviewer | **mandatory** (WP3) |
| S5 | **Passes its contract, fails its purpose**: every operation correct, the system less able to achieve what it is for | outcome measurement, acceptance testing | `outcome-sufficiency` check (built, narrow); context that states what success means | partial |
| S6 | **Architectural degradation**: coupling grows, new cycles, boundaries crossed | modularity metrics, fitness functions | per-projection topology over commit history (WP1B) | planned |
| S7 | **Race condition / shared-state hazard** | synchronisation, transactions, isolation | locate shared state and async boundaries in (a); recommend the right validation. The AST cannot prove race-freedom | planned |
| S8 | **Lost rationale**: why something exists is forgotten, so it is removed (Chesterton's fence) | ADRs, provenance, event logs | decisions *and rejected alternatives* in (c), delivered through `aec context` | planned |
| S9 | **Incomplete verification**: evidence of the wrong kind for the claim | property tests, integration tests, formal methods where justified | match claims to evidence kinds; evidence applicability by revision | partial |
| S10 | **Stale historical evidence reused**: an observation of revision A used as if it described HEAD | versioned test reports | `observed_on` → needs_review (built); general applicability (planned) | partial |

## In the multi-agent development process

| # | Failure | Established practice | Possible AEC contribution | Fixture |
|---|---|---|---|---|
| P1 | **Stale context**: an agent acts on a superseded repository or record state (e.g. a review of a commit that has since been replaced) | version identifiers, optimistic concurrency | handoffs carry revision and record versions; scoped premise check (WP4) | planned |
| P2 | **Overlapping edits**: two agents change the same high-impact region on "separate" tasks | locking, conflict detection, code ownership | graph-informed task decomposition: predicted reach and collision points (WP5 experiment) | planned |
| P3 | **Lost handoff information**: conclusions arrive without their premises, objections or limits | message schemas, acknowledgements | handoff ledger format; claims, open questions and authority recorded with the handoff | planned |
| P4 | **Conflicting assumptions**: agents hold incompatible interpretations of one requirement | design review, specification clarification | detect divergent claims about the same record; flag as `contested` | partial |
| P5 | **Misread authority**: a model's report of a decision treated as the decision | approval workflows, signed commits | authority by subject; a typed `authorized_by` is a claim, not verified consent; quotes required in handoffs | partial |
| P6 | **Self-review**: the implementer documents and grades its own change | separation of duties | reviewer agents with separated context; verdicts recorded as candidate evidence with method | planned |
| P7 | **Governance outgrows the work**: process artefacts multiply without changing decisions | proportionality, lean review | count decisions changed and failures caught, not records written; imported records exposed only when relevant | ongoing |
| P8 | **Unsupported artefact attestation**: a model reports an artefact as existing and identified (a SHA-256, a path, "frozen") without keeping verifiable access to it. The precision of the digest lends the claim credibility it hasn't earned. Observed twice in representation-001 (2026-10-29/30): the question and key digests had no recoverable artefacts. | content addressing, reproducible builds, signed artefacts | verify existence, integrity and locator *separately* from support and authority. Results are `verified` / `missing` / `mismatch` / `locator_invalid` / `unavailable`. Failure to recover an artefact doesn't prove it never existed; it proves the provenance chain can't be verified | built (WP-S, `specs/004-source-anchors/`): five-state fixtures and offline retrieval; source meaning/authority remain outside the check |

## Lens: structural special cases (candidate, 2026-11-01)

From the 2026-10-31 drift round (`relay-kit-private/aec-drift/round-2/addendum-special-cases.md`; Kate and claude:aec; candidate C-05; not binding).

A special case is often not rare: it is ordinary conditions lining up badly. Rarity and exceptionalism are independent. A daylight-saving bug happens every year. When a fixture is built for any row above, classify it on two separate dimensions. They are not severity levels, and one incident can sit at several points.

| Dimension | Values |
|---|---|
| **Structural mechanism** | boundary (behaviour flips across a threshold); composition (each part is valid, the combination isn't); intersection (several rules apply at once); degeneracy (an assumption fails, as with collinear points); conflict (valid rules require incompatible outcomes); missing category |
| **Relation to the model** | anticipated and represented; representable but unanticipated; not representable (model-breaking: the concept is missing) |

**Examples from AEC's own history:**
- **The handoff ID collision (Oct 29).** Composition: two lanes each created a valid ID, and together they collided. It was also model-breaking, because the IDs had no concept of a namespace.
- **Data Guide's aggregate rows.** A missing category: "one row per country" didn't hold. It counts as model-breaking only where the data model had no notion of row type.
- **The WP0 deletion over-propagation.** Conflict: the vocabulary invariant and the code disagreed. Fixed in PR #21.

**Related heuristics (candidates):**
- Check that components' assumptions stay compatible when the components are composed. Treat a case that can't be represented as a possible defect in the model, not just a missing test.
- Choose the least costly mechanism whose applicability and reliability are justified for what is at stake. Escalate on evidence, not on self-reported confidence. Capability is not authority.

**Why this matters for P8 and WP-S:** "no conflict found" is not "compatible", and "no caller found" is not "no caller". Any index, register or summary is a lossy representation, and model-breaking cases are exactly what it never recorded.

## Not counted as success

More records, longer reports, more findings, or a passing structural check. A row is "caught" only when the finding is specific, comes before the harm (or explains it after), and a reviewer would act on it.
