# Technical watch

A repeatable method to find what is worth changing in this repository, from current evidence and
primary sources, and to hand it over as one small, dated package. Run it with the skill
`tech-watch`, or on a schedule (`loops/orchestrator.sh watch`, monthly by default).

## 1. Start from current evidence

- Read `AGENTS.md`, `knowledge/index.md`, the concepts the topic touches, and `work/current.md`.
- Record the branch, whether the working tree is clean, the commit you inspected, and a cutoff date.
- Inspect the real code: callers, contracts, tests, configuration, the versions actually pinned
  (lockfiles, images, the CI matrix). State what you could not inspect.

## 2. Form findings before reading older reports

Look at `pending/*/index.md` only to avoid duplicating an open item: reuse the item that already
covers an issue. Never copy an older finding, test result or production state into a new package.

## 3. Search and judge

- **Sources, newest first:** official docs, release notes and security advisories **for the
  versions this project pins**; papers and preprints; credible practitioners. Open the original
  behind every post or summary.
- **Record** for each source: the query, the retrieval date, its publication or version date, its
  kind (documented capability, reported benchmark, locally observed result, unresolved hypothesis)
  and how deeply you read it.
- **Check the claim:** method, comparator, measurement, horizon, leakage, costs, limitations.
- **Search the repository first:** does it already do this, or something close?
- **Decide, for each idea:** *adopt*, *evaluate*, *retain* (keep what we have), *defer* or *reject*,
  with its local fit and the smallest useful experiment. No quota: "nothing worth changing" is a
  valid result. No new dependency, service or platform without a demonstrated need.
- Production checks, if any, are bounded and read-only. A watch never authorizes a deploy, a
  restart, a policy change, a paid experiment or a message on someone's behalf.

## 4. Deliver one package

- Create `pending/YYYY-MM-DD-<topic>/index.md` (add a suffix if the name exists; never overwrite).
- The index holds: the baseline commit and cutoff; the scope; a table **ID · Priority · State
  (OPEN, BLOCKED, NEEDS_OWNER) · Smallest next action and acceptance · Detail · Resolution
  evidence**; designs kept unchanged; rejected alternatives (listed, not turned into tasks).
- Tasks already in `work/current.md` are pointed to, never duplicated.
- Each recommendation separates observation, confirmed cause, hypothesis and proposed fix.
- Supporting files stay in the package; every link resolves; nothing outside the package names it.
- Open one pull request with the package.

## 5. Process and close a package

1. Re-check the item's evidence in the current checkout; make one coherent, minimal change; run
   the checks.
2. Record a terminal disposition with its evidence in the package index: **IMPLEMENTED**,
   **ALREADY_FIXED**, **NOT_APPLICABLE**, **DECLINED** (an owner decision) or **TRACKED_ELSEWHERE**
   (a real, existing task). OPEN, BLOCKED and NEEDS_OWNER are not finished.
3. Move durable facts into `knowledge/`; update an existing `work/current.md` entry rather than
   adding one.
4. When every item is terminal, delete the whole package folder in the closing commit. Git is the
   archive; there is no `done/` folder.
