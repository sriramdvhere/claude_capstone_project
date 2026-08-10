---
description: Implementation Plan Document Structure Instructions
paths:
  - "docs/impl-plan.md"
---

# Implementation Plan Document Structure Instructions

All implementation plan documents saved to `docs/impl-plan.md` **must** follow the structure defined below.
Every task must reference its dependencies explicitly, blocked work must be registered, and the plan status must be kept current on every substantive change.

---

## Required Document Structure

```markdown
# Implementation Plan: [Project Name]

## 1. Plan Metadata
- **Source**: `docs/architecture.md`
- **Status**: [Draft/Reviewed/Approved]
- **Last Updated**: [Date]
- **Prepared By**: [Team/Agent]
- **Planning Horizon**: [e.g., MVP Sprint 1-3]

## 2. Planning Assumptions and Constraints
- [Assumption or constraint]

## 3. Dependency-Ordered Task List
| Order | Task ID | Task Name | Priority | Depends On | Outcome / Definition of Done | Status |
|------:|---------|-----------|----------|------------|-------------------------------|--------|
| 1 | IMP-001 | [Task] | P0 | None | [DoD] | Ready |

## 4. Blocked Task Register
| Task ID | Blocked By | Why Blocked | Unblock Condition | Owner | Notes |
|---------|------------|-------------|-------------------|-------|-------|
| IMP-010 | IMP-003, IMP-004 | [Reason] | [What must finish] | [Role] | [Optional] |

## 5. Milestones and Checkpoints
- **Milestone A**: [Scope and exit criteria]
- **Milestone B**: [Scope and exit criteria]

## 6. Risks to Delivery Sequence
- [Risk] -> [Mitigation]

## 7. Open Questions
- [Question requiring decision]

## 8. Approval
- **Decision**: [Approved / Rework Needed]
- **Approved By**: [Name/Role]
- **Approval Date**: [Date]
```

---

## Section Authoring Guidelines

| Section | Guidance |
|---|---|
| **1. Plan Metadata** | Fill all fields at plan creation. Set Status to `Draft` initially; update to `Approved` only after stakeholder sign-off. Last Updated must reflect the current date on every change. |
| **2. Planning Assumptions and Constraints** | List every assumption that could affect task order or scope. Include team size, timeline, tooling mandates, and release targets. |
| **3. Dependency-Ordered Task List** | Every task must list its dependencies explicitly (`None` if none exist). Task order must be consistent with dependency links. Priority must not override dependencies in sequencing. |
| **4. Blocked Task Register** | All tasks with unmet prerequisites must appear here. Include the specific unblock condition and a responsible owner. Never leave blocked tasks undocumented. |
| **5. Milestones and Checkpoints** | Each milestone must state its scope and a measurable exit criterion. Milestones must be derivable from the task list. |
| **6. Risks to Delivery Sequence** | Capture risks that can reorder or delay the execution sequence. Each risk must have a paired mitigation or monitoring action. |
| **7. Open Questions** | Record every unresolved decision that affects planning. Each question must be owned and have an expected resolution date where possible. |
| **8. Approval** | Leave blank until formal review is complete. Decision must be one of: `Approved`, `Rework Needed`. |

---

## Priority Level Definitions

| Priority | Definition |
|----------|------------|
| `P0` | Required to unlock the core path or prevent delivery failure |
| `P1` | Core functionality required for MVP completion |
| `P2` | Important but not on the critical path |
| `P3` | Deferred enhancements or operational hardening |

---

## Task Status Definitions

| Status | Definition |
|--------|------------|
| `Ready` | No unmet dependencies; can be started immediately |
| `Blocked` | One or more prerequisites are incomplete; must appear in Section 4 |
| `In Progress` | Work has started |
| `Done` | Outcome meets the Definition of Done |

---

## Quality Checklist

Before marking the plan `Approved`, verify all of the following:

- [ ] Every task references dependencies explicitly (`None` if no dependency)
- [ ] Task order is consistent with dependency links
- [ ] Blocked tasks appear in both the task list and the blocked register
- [ ] Core architecture flows are covered by at least one implementation task each
- [ ] Non-functional requirements have explicit implementation tasks
- [ ] Critical path is identifiable from ordering and dependency links
- [ ] No tasks are too vague to estimate or execute

---

## Naming & Versioning

- **File path**: `docs/impl-plan.md` *(single, stable filename — status and date are tracked inside the document)*
- **Status lifecycle**: `Draft` → `Reviewed` → `Approved`
- **Last Updated field**: Set to the current date (DD MMM YYYY) every time the document is created or modified
- **Source document**: Always `docs/architecture.md`
- **Commit convention**: `docs: Update implementation plan for [project/feature name] - [short description]`
