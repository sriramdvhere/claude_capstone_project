---
description: "# Design Review Document Structure Instructions"
paths:
  - "docs/design-review.md"
---

# Design Review Document Structure Instructions

All design review documents saved to `docs/design-review.md` **must** follow the structure defined below.
Tie every finding back to `docs/architecture.md`, include explicit risk ratings, and update the review status on every substantive change.

---

## Required Document Structure

```markdown
# Design Review: [Project or Architecture Name]

## 1. Review Metadata
- **Source Document**: `docs/architecture.md`
- **Review Status**: [In Progress / Completed]
- **Overall Verdict**: [Ready / Ready with Conditions / Not Ready]
- **Reviewer**: [Agent/User/Team]
- **Last Updated**: [DD MMM YYYY — updated every time the document changes]

## 2. Review Context

### Scope
[What was reviewed — components, flows, or sections of `docs/architecture.md`]

### Constraints and Standards
[Budget, compliance requirements, reliability targets, platform mandates, security baselines]

## 3. Findings Register
| ID | Severity | Area | Finding | Impact | Recommendation | Owner | Status |
|----|----------|------|---------|--------|----------------|-------|--------|
| DR-001 | High | Reliability | [Observation tied to architecture text] | [Consequence if unresolved] | [Specific fix or mitigation] | [Owner name/team] | Open |

<!-- Severity levels: Critical | High | Medium | Low -->
<!-- Area options: Security | Data | Reliability | Performance | Operability | Maintainability | Delivery -->
<!-- Status options: Open | Accepted | Resolved | Deferred -->

## 4. Agreed Design Decisions
| Decision ID | Decision | Rationale | Trade-offs | Follow-up |
|-------------|----------|-----------|------------|-----------|
| DD-001 | [Decision statement] | [Why this was chosen] | [What was accepted or given up] | [Actions or conditions] |

## 5. Applied Updates to `docs/architecture.md`
- **Section changed**: [Section name or number]
- **What changed**: [Description of the update]
- **Reason for change**: [Finding or gap that triggered it]
- **Linked finding ID**: [DR-XXX]

## 6. Open Risks and Watch Items
- **Risk**: [Residual risk description]
  - **Mitigation / Monitoring**: [Plan to track or reduce this risk]

## 7. Exit Criteria
- [ ] No unresolved Critical findings
- [ ] High findings have approved mitigation or fix
- [ ] Key assumptions explicitly documented
- [ ] Architecture baseline updated and internally consistent
```

---

## Section Authoring Guidelines

| Section | Guidance |
|---|---|
| **1. Review Metadata** | Fill all fields before starting the review. Set Overall Verdict only at Phase 5 (Review Closure). Last Updated must be set to the current date on every change. |
| **2. Review Context** | Scope must name the specific sections or components reviewed, not just "the architecture". Constraints and Standards must list any non-negotiable limits that shaped review decisions. |
| **3. Findings Register** | Every finding must reference specific architecture text or a clearly missing control. Severity must use the defined scale. Status must be kept current — never leave stale `Open` items without a follow-up date. |
| **4. Agreed Design Decisions** | Capture decisions made during the review, not just findings. Rationale must explain *why*, not just *what*. Trade-offs must be explicit so future reviewers understand what was knowingly accepted. |
| **5. Applied Updates** | Record every direct change made to `docs/architecture.md` during this review. Each entry must link back to the finding that triggered it. Do not leave this section blank if architecture edits were made. |
| **6. Open Risks and Watch Items** | Residual risks that are Accepted or Deferred must appear here with an explicit monitoring or mitigation plan. Do not leave risks unowned. |
| **7. Exit Criteria** | All checkboxes must be ticked before Overall Verdict is set to `Ready`. If any remain unchecked, Verdict must be `Ready with Conditions` or `Not Ready`. |

---

## Risk Severity Definitions

| Severity | Definition |
|----------|------------|
| `Critical` | Blocks safe implementation; immediate design correction required before any work proceeds |
| `High` | Serious weakness with significant delivery or reliability impact; must be resolved before broad rollout |
| `Medium` | Important gap; should be resolved before production release |
| `Low` | Improvement opportunity; can be scheduled with a clear owner and timeline |

---

## Naming & Versioning

- **File path**: `docs/design-review.md` *(single, stable filename — review status and date are tracked inside the document)*
- **Status lifecycle**: `In Progress` → `Completed`
- **Verdict lifecycle**: `Not Ready` → `Ready with Conditions` → `Ready`
- **Last Updated field**: Set to the current date (DD MMM YYYY) every time the document is created or modified
- **Source document**: Always `docs/architecture.md`; update this field if a different baseline is reviewed
- **Commit convention**: `docs: Update design review for [project/feature name] - [short description]`
