# review-001 prompt (as run, 2026-11-01)

Verbatim. The current protocol (`../review-protocol.md`) differs in two places; see review-001.md.

````markdown
# Independent Architecture, Implementation, and Code Quality Audit

## Objective

You are an independent engineering reviewer encountering this repository for the first time.

AEC (AI-Enhanced Coding) is an experimental system intended to help AI software-development agents preserve and reassess architectural purpose, requirements, evidence, and decision authority as code evolves.

Your assignment is to investigate the repository, evaluate its current implementation, and identify substantive strengths, weaknesses, defects, architectural tensions, and opportunities.

**This is an independent assessment, not an implementation assignment.**

Do not assume the existing architecture is correct. Equally, do not assume that finding something to change is necessary.

## Phase 1: Reconstruct the system

Examine the repository independently.

Read its relevant governing instructions, architectural documentation, specifications, tests, and implementation.

Establish:

1. What problem AEC is intended to solve.
2. What its governing architectural principles are.
3. Which capabilities are implemented, partially implemented, or merely proposed.
4. How the components interact.
5. How purpose, evidence, provenance, and authority are represented.
6. What limitations or unresolved questions are acknowledged.

Identify any ambiguities or contradictions in the documentation.

Do not invent missing information or treat inaccessible sources as verified.

## Phase 2: Technical investigation

Inspect the actual implementation.

Evaluate:

- Correctness and reliability.
- Architectural coherence.
- Module boundaries and coupling.
- Error handling and unexpected inputs.
- Determinism and reproducibility.
- Data integrity and record consistency.
- Test coverage and quality.
- False-positive and false-negative behavior.
- Maintainability and unnecessary complexity.
- Potential security or operational risks.

Run the existing tests where feasible.

For suspected defects, attempt to establish reproducible evidence through isolated, non-destructive experiments.

Distinguish confirmed defects from plausible concerns.

## Phase 3: Purpose and implementation alignment

Compare what AEC claims or intends to accomplish with what its implementation actually demonstrates.

Pay particular attention to:

- Whether the implementation enforces the guarantees its documentation describes.
- Whether structural findings are ever presented with more certainty than the evidence supports.
- Whether evidence and provenance remain traceable and appropriately scoped.
- Whether authority boundaries are preserved.
- Whether implementation decisions introduce unnecessary complexity.
- Whether a feature provides additional value beyond conventional engineering methods.

Identify cases where the code works as implemented but may not fulfill its stated purpose.

Also identify cases where an apparently unusual implementation choice is justified by the project's requirements.

## Phase 4: Independent architectural criticism

Challenge the architecture constructively.

Consider:

1. Which existing design choices are particularly strong?
2. Which assumptions deserve further investigation?
3. Which components might be unnecessarily complicated?
4. Are there important failure modes the current architecture misses?
5. What would you simplify, replace, or remove?
6. What capabilities appear missing or disproportionately underdeveloped?
7. Where might AEC itself experience the kinds of development drift it is intended to detect?

Do not recommend new infrastructure merely because it is conventional.

Explicitly distinguish improvements supported by evidence from speculative redesigns.

**The conclusion that a component should remain unchanged is entirely acceptable.**

## Phase 5: Report

Provide the following deliverables.

### A. System reconstruction
A concise architectural explanation demonstrating your understanding of the actual repository.

### B. Implementation assessment
What works, what is incomplete, and what is inconsistent with the documented design.

### C. Findings
Rank substantive findings by severity, confidence, and likely practical impact.

For each finding provide:
- Description.
- Relevant file paths and line references.
- Evidence or reproducible demonstration.
- Expected versus actual behavior.
- Consequences.
- Proposed remediation, if warranted.
- Remaining uncertainties.

### D. Architectural dissent
Your strongest well-supported criticisms of the current design, including arguments against your own recommendations where appropriate.

### E. Recommended next experiments
Suggest three bounded experiments or engineering tasks that would provide meaningful information about AEC's correctness, usefulness, or architecture.

Prioritize experiments that could invalidate assumptions, not merely demonstrate expected behavior.

### F. Self-assessment
Identify:
- What you could establish directly.
- What you inferred.
- What you could not verify.
- Which repository instructions materially affected your investigation.
- Which questions required information unavailable within the repository.

## Constraints

- Do not modify tracked repository files.
- Do not create commits or pull requests.
- Do not implement speculative features.
- Do not revise the project's goals or decisions.
- Keep any experimental files outside the tracked repository.
- Do not claim that passing tests establishes semantic correctness.
- Do not treat an absence of detected problems as proof that none exist.
- Prioritize substantive findings over stylistic preferences.

This review will be independently evaluated. Accuracy, evidence, discrimination, and intellectual independence are more valuable than the number of findings.

Proceed with the investigation.````
