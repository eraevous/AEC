# Releasing

Only Zach pushes release tags. Checklist for v0.5.0 (adapt the numbers for later releases):

1. Merge the release-readiness PR. Check that `pyproject.toml`, `aec.__version__` and the newest
   CHANGELOG heading name the same version (`tests/test_install.py` checks this).
2. Tag **v0.5.0 at the merge commit** and push the tag.
3. Flip the install lines from `@main   # 0.5.0 on main; tag v0.5.0 pending` to `@v0.5.0` in
   `README.md`, `docs/guide/getting-started.md` and `docs/demo.md`, and drop the "pending" notes.
4. Check the CI pin. `aec init` pins the generated CI job to the installed commit SHA for git installs
   (#51), and to `HEAD` when it runs from a source checkout (`PYTHONPATH=src` or an editable install). For an
   install with no known commit (a local directory or a wheel) it pins `@v0.5.0`, because it cannot tell
   offline whether that tag exists. That pin only works once step 2 is done.
5. Move other pins (this repo's docs, relay-kit, adopters' CI) from a commit or `@main` to the tag where
   wanted.
