---
description: Structural template and authoring instructions for the peer code review summary output. Agents and contributors must follow this structure when producing or updating a peer code review report.
globs: "peer-review-summary.md"
---

# Peer Code Review Summary Document Structure Instructions

All peer code review summaries **must** follow the structure defined below.
Every finding must be tied to evidence from the change set, severity must reflect actual merge risk, and the overall recommendation must be updated whenever findings change.

---

## Required Document Structure

```markdown
# Peer Code Review Summary

## 1. Review Metadata
- **Scope**: Uncommitted changes + local unpushed commits
- **Requirements Baseline**: `docs/requirements.md`
- **Review Status**: [Completed / Blocked]
- **Overall Recommendation**: [Ready for PR / Ready for PR with Minor Fixes / Not Ready for PR]
- **Last Updated**: [DD MMM YYYY — updated every time the document changes]

## 2. Change Scope
### Files Reviewed
- `path/to/changed-file.py`
- `path/to/test_file.py`

### Checks Run
- [test command and result]
- [dependency safety check and result, if applicable]

## 3. Findings Register
| ID | Severity | Area | File / Symbol | Observation | Recommendation |
|----|----------|------|---------------|-------------|----------------|
| PCR-001 | High | Correctness | `module.function` | [What was observed] | [What should be changed] |

<!-- Severity levels: Critical | High | Medium | Low | Question -->
<!-- Area options: Correctness | Security | Error Handling | Test Coverage | Code Clarity | DRY | Dependency Safety -->

## 4. Coverage and Risk Notes
- Happy path coverage: [adequate / partial / missing]
- Edge case coverage: [adequate / partial / missing]
- Error handling notes: [summary of gaps or strengths]
- Security notes: [summary of secrets, input validation, trust boundaries]
- Dependency safety notes: [summary of version checks or no changes]

## 5. Final Recommendation
- **Outcome**: [Ready for PR / Ready for PR with Minor Fixes / Not Ready for PR]
- **Required fixes before PR**:
  - [finding ID and short description]
- **Optional improvements**:
  - [finding ID and short description]
```

---

## Section Authoring Guidelines

| Section | Guidance |
|---|---|
| **1. Review Metadata** | Fill all fields before starting the review. Set Overall Recommendation only after all findings are assessed. Last Updated must reflect the current date on every change. |
| **2. Change Scope** | List only the files that were actually inspected. Record every test or validation command that was executed and its outcome. Do not list files that were not reviewed. |
| **3. Findings Register** | Each finding must cite a specific file, function, or symbol. Observation must state what was found, not just that a problem exists. Recommendation must be actionable and specific enough to implement without further clarification. |
| **4. Coverage and Risk Notes** | Assess each dimension explicitly — do not skip a category. Use `adequate`, `partial`, or `missing` for coverage fields. Security and dependency notes are required even when no issues are found; state "no issues found" rather than leaving blank. |
| **5. Final Recommendation** | Outcome must be one of the three defined values only. Required fixes must list every `Critical` and `High` finding. Optional improvements list `Medium` and `Low` findings that do not block the PR. |

---

## Severity Definitions

| Severity | Definition |
|----------|------------|
| `Critical` | Unsafe to merge; severe correctness, security, or data-loss risk — must be fixed before PR is opened |
| `High` | Strong blocker for PR readiness; fix required before merging |
| `Medium` | Should be fixed before merge unless explicitly accepted by the team |
| `Low` | Improvement that does not block the PR by itself |
| `Question` | Needs clarification before a firm judgment can be made; ties to `docs/requirements.md` where applicable |

---

## Review Area Definitions

| Area | What It Covers |
|------|----------------|
| `Correctness` | Behavior matches `docs/requirements.md`; inputs, outputs, and state changes are as intended |
| `Security` | Secrets, input validation, injection risks, and trust-boundary handling |
| `Error Handling` | API failures, missing resources, and edge input are handled predictably with clear messages |
| `Test Coverage` | Happy path, `Not Found`, invalid-input, and regression scenarios are exercised |
| `Code Clarity` | Names, control flow, and responsibility boundaries are easy to follow without comments |
| `DRY` | Duplicated logic is identified and can be extracted without hurting readability |
| `Dependency Safety` | Added or changed packages are checked for known vulnerable versions |

---

## Naming & Versioning

- **File path**: `peer-review-summary.md` at project root, or as agreed with the team *(single file per review cycle)*
- **Review Status lifecycle**: `Blocked` → `Completed`
- **Recommendation lifecycle**: `Not Ready for PR` → `Ready for PR with Minor Fixes` → `Ready for PR`
- **Last Updated field**: Set to the current date (DD MMM YYYY) every time the document is created or modified
- **Requirements baseline**: Always `docs/requirements.md` unless the user specifies otherwise
- **Commit convention**: `docs: Add peer code review summary for [branch/feature name]`
