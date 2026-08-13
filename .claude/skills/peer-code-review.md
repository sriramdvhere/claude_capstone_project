---
name: peer-code-review
description: Review local pre-push code changes for correctness, safety, test coverage, and maintainability before a pull request is opened. Invoke with /peer-code-review. Input: specify files or branches to review, or leave blank to review all uncommitted changes.
disable-model-invocation: true
triggers:
  - /peer-code-review
  - peer review
  - pre-PR review
  - code review before PR
  - review my changes
---

# Peer Code Review Skill

## Skill Mission
Act as a peer code reviewer who inspects implementation changes before a pull request is raised. Catch correctness, safety, test, and maintainability issues early while keeping review scope tightly limited to local work that is not pushed yet.

## Scope Boundaries
Review only the current local pre-push work:

**Included**:
- Staged changes
- Unstaged changes
- Newly added untracked source, test, or config files relevant to the implementation
- Local commits that have not been pushed to the tracked upstream yet

**Excluded** (strict, no exceptions):
- Committed history that is already pushed/shared upstream
- Unrelated repository areas with no connection to the changed files
- Any directory or file path listed in `.gitignore`
- Any change under the `.github` folder

If the working tree is clean and there are no local unpushed commits, stop and report that there is nothing to review.

---

## Review Workflow

### Phase 0: Review Readiness Check
1. Confirm the review is for local changes not yet pushed (uncommitted edits and local unpushed commits)
2. Inspect the working tree for staged, unstaged, or untracked changes
3. Inspect branch status for local commits ahead of upstream
4. Confirm `docs/requirements.md` is available as the requirements baseline
5. If there are no uncommitted changes and no local unpushed commits, stop with a graceful summary

### Phase 1: Change Scope Discovery
1. Inspect modified, added, renamed, and untracked files in the working tree
2. Capture both staged and unstaged diffs when both exist
3. Inspect local commits ahead of upstream and capture their file-level and commit-level deltas
4. Group the change set by concern: feature logic, API contract, persistence, validation/error handling, tests, dependency/config
5. Read the changed files and enough nearby context to understand intent and local impact

### Phase 2: Requirement and Behavior Verification
Use `docs/requirements.md` as the primary behavior reference.

- Does each changed component behave as required?
- Are inputs, outputs, and state changes consistent with the requirement?
- Are edge conditions handled where the requirement implies them?
- Did the change unintentionally break neighboring behavior?

When a requirement is ambiguous, state the ambiguity explicitly and mark the finding as a `Question`.

### Phase 3: Quality Review by Criteria
Review each area explicitly:

1. **Correctness** — behavior matches `docs/requirements.md`; inputs, outputs, and state changes are as intended
2. **Security** — secrets excluded from logs/output/fixtures; user input validated at the correct boundary; no injection risks or trust-boundary leaks
3. **Error Handling** — API failures, missing resources, and edge input handled predictably with clear messages
4. **Test Coverage** — happy path, Not Found, invalid-input, and regression scenarios are exercised
5. **Code Clarity** — names, control flow, and responsibility boundaries are easy to follow
6. **DRY** — duplicated logic identified and extractable without hurting readability
7. **Dependency Safety** — added or changed packages checked for known vulnerable versions

### Phase 4: Evidence-Based Validation
1. Run targeted tests for changed behavior: `python -m pytest tests/ -v --tb=short` (or equivalent)
2. Run broader test suites when the change touches shared logic
3. Inspect dependency manifests for changed package versions and flag known vulnerabilities
4. State clearly when execution is blocked by missing tooling or failing setup

### Phase 5: Findings and Recommendation
For each finding capture: ID (PCR-NNN), Severity, Area, File/Symbol, Observation, Recommendation.

Severity levels:
- `Critical` — unsafe to merge; severe correctness, security, or data-loss risk
- `High` — strong blocker for PR readiness; fix required before merging
- `Medium` — should be fixed before merge unless explicitly accepted
- `Low` — improvement that does not block the PR by itself
- `Question` — needs clarification before a firm judgment

Conclude with one of: `Ready for PR` | `Ready for PR with Minor Fixes` | `Not Ready for PR`

### Phase 6: Review Closure
Produce a concise, actionable summary covering: scope reviewed, files inspected, tests/checks executed, findings by severity, dependency safety result, overall recommendation, and next actions for the author.

---

## Output Document

Write the review summary to `peer-review-summary.md` at the project root, following the structure from `.claude/rules/peer-code-review.md` exactly. Commit the document with:

```
docs: Add peer code review summary for [branch/feature name]
```

The document must include all five sections: Review Metadata, Change Scope, Findings Register, Coverage and Risk Notes, and Final Recommendation. Set **Last Updated** to today's date (DD MMM YYYY). Do not leave any section blank — use "no issues found" for areas with nothing to report.
