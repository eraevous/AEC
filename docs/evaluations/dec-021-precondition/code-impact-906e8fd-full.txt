# derived 20 change event(s) from the structural diff
# aec impact

- change: revise code:src.fathom.charts.svg_chart (by code, authorized_by None)
- change: revise code:src.fathom.config.validate_config (by code, authorized_by None)
- change: revise code:src.fathom.exports.pdf_bytes (by code, authorized_by None)
- change: revise code:src.fathom.exports.pptx_bytes (by code, authorized_by None)
- change: revise code:src.fathom.models.validate_document (by code, authorized_by None)
- change: revise code:src.fathom.profiler.profile (by code, authorized_by None)
- change: revise code:src.fathom.profiler.rank_pairs (by code, authorized_by None)
- change: revise code:src.fathom.profiler.select_pairs (by code, authorized_by None)
- change: revise code:src.fathom.renderers.render_html (by code, authorized_by None)
- change: revise code:src.fathom.renderers.render_markdown (by code, authorized_by None)
- change: revise code:src.fathom.target.association (by code, authorized_by None)
- change: revise code:src.fathom.target.build_target_analysis (by code, authorized_by None)
- change: revise code:src.fathom.target.relationship_chart (by code, authorized_by None)
- change: revise code:src.fathom.target.summarize_groups (by code, authorized_by None)
- change: revise code:src.fathom.target.target_candidates (by code, authorized_by None)
- change: revise code:src.fathom.target_marks.plot_marks (by code, authorized_by None)
- change: revise code:src.fathom.univariate.numeric_profile (by code, authorized_by None)
- change: revise code:tests.test_target.test_hand_computed_measures_and_clean_decoys (by code, authorized_by None)
- change: revise code:tests.test_target.test_scatter_sampling_log_coverage_and_native_log_ecdf (by code, authorized_by None)
- change: revise code:tests.test_target.test_small_group_counts_missing_and_contrasts (by code, authorized_by None)

[stale] FT-UNI-R1@2: Implement the report and univariate scope in spec 003 using the transparent date/numeric parsing, fixed sample settings and FT-R14 detail readings in its intent note; proposed for Zach to accept, without accepting FT-R14 detail or changing accepted scope.
    via code:src.fathom.charts.svg_chart -> FT-UNI-R1@2
[stale] FT-PL-R1@2: Implement spec005 plots and layout using its disclosed distribution, formatting, exact missingness-mask and static-layout readings, including a screenshot/practice review; proposed for Zach to accept without accepting FT-R15 detail.
    via code:src.fathom.charts.svg_chart -> FT-PL-R1@2
[stale] FT-PO-R1@2: Implement FT-R18 via spec006 disclosed static grid/disclosure, positive-only log coverage, tick/label/formatting and summary-deck readings, proposed for Zach to accept; preserve raw artifact authority and repeat the visual review.
    via code:src.fathom.charts.svg_chart -> FT-PO-R1@2
[stale] FT-TA-R1@2: Implement spec007 target analysis and FT-R19 with its disclosed association, shared budget/group reservation, bounded group/plot, leakage-exclusion and log-display readings; proposed for Zach to accept, preserving inferred semantics and artifact authority.
    via code:src.fathom.charts.svg_chart -> FT-TA-R1@2
[stale] FT-SX-R1@2: Implement spec004 special-type local checks and artifact-derived optional exports using its disclosed syntax, range, font and deterministic packaging readings; proposed for Zach to accept, without accepting new domain semantics.
    via code:src.fathom.exports.pdf_bytes -> FT-SX-R1@2
[stale] FT-DQ-R1@2: Implement FT-R2@2 through FT-R6@2 using the transparent diagnostic thresholds, shared ranking budget and artifact-derived report refinements in specs/002-data-quality and the data-quality intent note. These algorithmic readings are proposed for Zach to accept; they do not change the accepted requirements.
    via code:src.fathom.models.validate_document -> FT-DQ-R1@2
[stale] FT-R1@2: Deliver a CSV/wide data-to-decisions slice: evidenced review actions and unknowns, overridable inferred semantics, bounded target-selected relationships, versioned artifact with standalone reports and human working record, and context-first profile comparison. Scope is specs/001-data-review/spec.md; proposed for Zach to accept.
    via code:src.fathom.profiler.profile -> FT-R1@2
[needs_review] FT-UNI-E1@1: 118 passed with SciPy; core117 passed,1 optional-presence skipped. Exact date/numeric/text/sample metrics, legacy/saved artifacts, fresh-process bytes, labels/order/technical disclosure and browser raw-sample/full-view controls passed.
    via code:src.fathom.charts.svg_chart -> FT-UNI-E1@1
[needs_review] FT-PL-E1@1: Full suite147 passed with extras; core141 passed,6 optional skipped. Exact ECDF/log eligibility/category coverage/text length/calendar/mask bounds and decoys pass; existing fresh-process bytes/degradation/legacy tests pass. Affected plot/export tests rerun after visual fixes.
    via code:src.fathom.charts.svg_chart -> FT-PL-E1@1
[needs_review] FT-PO-E1@1: 154tests passed with extras; core147passed/7optional skipped. Tests cover positive log subset counts/decoys, compact headers/scaling, logical formatting/examples, identifier/nearunique suppression, months/ticks/box/captions and summary/full budget/bytes/CLI. Separate public fresh processes produce identical HTML/Markdown/PDF/PPTX/status in both modes.
    via code:src.fathom.charts.svg_chart -> FT-PO-E1@1
[needs_review] FT-TA-E3@1: Actual HTML/PDF/Impress-PPTX reviewed at1280/390 with representative full-size views/contact sheets; spec007 gallery documents all4FT-R19 fixes. Original-unit native log ECDF,110-unit SVG box/noY, sticky stats y12/height585, positive ECDF3147/47zeros. Fixed clipping/shadows/crowded ticks/narrow tables/PDF quantities/mislabelled scatter omission. Phone zoom/table scrolling, fixed slide canvas and comprehensive report length remain open.
    via code:src.fathom.charts.svg_chart -> FT-TA-E3@1
[needs_review] FT-PL-E3@1: Actual HTML, PDF and LibreOffice-rendered PPTX screenshots reviewed at1280/390; gallery/issue ledger in specs/005-plots-and-layout/review. Fixed narrow evidence, formatting, stacked values, bar gaps, box labels, PDF orphans and slide title/label crowding. Phone pan/zoom, rotated titles, sparse ticks, length and font coverage remain open; claude:aec independent pass pending.
    via code:src.fathom.exports.pdf_bytes -> FT-PL-E3@1
[needs_review] FT-PO-E3@1: Actual HTML/PDF/Impress-PPTX reviewed at1280/390 with full-size samples and contact sheets; spec006 gallery records fixes/open items. Films1280height60186before→16861default/45082all-columns-open; college75832→8669default. Both summary decks12slides; films full61. Fractional count ticks, redundant numeric rarity notes, legacy months and full-deck box ticks fixed on repeat capture. Fixed exports need phone zoom; comprehensive views remain long.
    via code:src.fathom.exports.pdf_bytes -> FT-PO-E3@1
[needs_review] FT-E1@1: Clean core install: 67 passed, 1 SciPy-present decoy skipped. With stats extra: 68 passed. Quickstart profile/render/compare/validate succeeds; fresh-process outputs match byte-for-byte. Dirty fixture has exactly two evidenced review actions; clean decoy has neither.
    via code:src.fathom.profiler.profile -> FT-E1@1
[needs_review] FT-DQ-E1@2: 101 tests pass with optional statistics available; core-only run has 100 passed and 1 optional-presence decoy skipped. Tests cover exact diagnostics/summary, violation/decoys, stronger-later/reordered/shared-budget ranking, screening limits, retained overrides, legacy artifacts, text escaping, CLI fresh-process bytes and saved-artifact views. Chromium confirms the summarized default, one-click disclosure of 44 grouped original workshop items, return to summary, unique IDs and resolving evidence links. A shared-absence adversarial decoy verifies that a near-copy diagnosis/exclusion also requires jointly-present agreement.
    via code:src.fathom.profiler.rank_pairs -> FT-DQ-E1@2
[needs_review] FT-TA-E1@1: 164tests pass with extras; core157pass/7optional skips. Exact Pearson signed values, eta0/1,V0/1, config/structural exclusions, group reservation/budget, group valid/missing/share/rest, small cautions, rates/empty bins, skipped/legacy, malformed artifact rejection, original-unit log ECDF and200-point scatter coverage/native log markup pass. Fresh processes match HTML/Markdown/PDF/PPTX/status in summary/full modes.
    via code:src.fathom.profiler.rank_pairs -> FT-TA-E1@1
[needs_review] FT-TA-E2@1: Planted40x7 ranks group eta.918643,signal r.689275; excludes configured exact target rank/raw copy/ID; reports shifted3-row group mean2903 vs regular524.5 with caution/actions. Clean40x7 no marked group contrast. Late24x5 shows categorical rates/empty bins but unmarked0/1target encoding and incomplete copy remain ranked, documented misses. Pair-local grouping does not cross every other column. Public movies/college found/missed ledger in spec007 validation.
    via code:src.fathom.target.build_target_analysis -> FT-TA-E2@1
[needs_review] FT-UNI-C1@1: Spec003 conforms on tested synthetic tables: revised report order/identity, bounded fixed-seed raw samples, labelled charts, proposed advanced univariate metrics and typed date/zero/identifier findings. FT-R14 detail and independent usefulness are not accepted by these tests.
    via code:src.fathom.charts.svg_chart -> FT-UNI-E1@1 -> FT-UNI-C1@1
[needs_review] FT-PL-C1@1: Spec005 conforms on tested synthetic tables: static full-width entries with formatted tables/inline plots, ECDF/log/category/text/calendar/missingness views and time-name fix; actual HTML/PDF/PPTX screenshot review completed with explicit open issues. FT-R15 detail and independent usefulness remain unaccepted.
    via code:src.fathom.charts.svg_chart -> FT-PL-E1@1 -> FT-PL-C1@1
[needs_review] FT-PO-C1@1: Spec006 implements all seven FT-R18 polish items on tested synthetic/public tables: compact scalable disclosures/grid, intermediate ticks, positive-only log coverage, separated box summaries, unclipped reviewed captions, logical rounded statistics/examples, capitalized months and suppressed identifier top-N, default12-slide summary and optional full deck. Repeat FT-R17 gallery and explicit open limits; independent acceptance remains unclaimed.
    via code:src.fathom.charts.svg_chart -> FT-PO-E1@1 -> FT-PO-C1@1
[needs_review] FT-TA-C1@1: Spec007 implements tested FT-R7 target ranking with Pearson/eta/Cramer V, configured and structural exclusions, shared bounded quality/value pairs, pair-local group summaries/contrasts/cautions and selected plots; FT-R19 original-unit log ticks, slim boxes, sticky statistics and positive-only log ECDFs reviewed across outputs. Builder misses and independent-acceptance limits explicit.
    via code:src.fathom.charts.svg_chart -> FT-TA-E3@1 -> FT-TA-C1@1
[needs_review] FT-C1@1: The implementation conforms to the proposed FT-R1 slice on the tested synthetic scenarios: evidenced review actions and unknowns, inference overrides, bounded target pairs, saved reports, and context-first comparisons. This is not owner acceptance or a claim that the purpose outcome is achieved.
    via code:src.fathom.profiler.profile -> FT-E1@1 -> FT-C1@1
[needs_review] FT-DQ-C1@1: Slice 002 conforms to the tested FT-R2..FT-R6 scope: evidenced quality diagnostics, shared-budget relevance ranking, linked dataset summary and readable grouped/full artifact-derived reports. Builder found/missed results and known false alarms are disclosed; independent usefulness and owner acceptance are not claimed.
    via code:src.fathom.profiler.rank_pairs -> FT-DQ-E1@2 -> FT-DQ-C1@1

23 affected, 45 conclusions unaffected
