import json, random
random.seed(20261101)  # fixed seed, recorded in the amendments log
trials = [(t, c, r) for t in ("T1", "T2", "T3") for c in ("A", "B", "C") for r in (1, 2)]
random.shuffle(trials)
# Opaque trial ids so the grader can't infer condition from the id.
ids = random.sample(range(100, 1000), len(trials))
sched = [{"trial": f"P{i}", "task": t, "cond": c, "rep": r} for i, (t, c, r) in zip(ids, trials)]
print(json.dumps(sched, indent=1))
