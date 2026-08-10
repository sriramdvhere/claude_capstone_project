---
description: "# Requirements Document Structure Instructions"
paths:
  - "docs/requirements.md"
---

# Requirements Document Structure Instructions

All requirements documents saved to `docs/requirements.md` **must** follow the structure defined below.
Use clear, unambiguous language throughout. Include examples where applicable, link to related stories, and version the document on every update.

---

## Required Document Structure

```markdown
# Requirements Document: [User Story Title/ID]

## 1. Overview
- **Story ID**: [JIRA/Story ID]
- **Title**: [Story Title]
- **Version**: [e.g., v1.0]
- **Last Updated**: [DD MMM YYYY — updated every time the document changes]
- **Status**: [Draft/Reviewed/Approved]
- **Owners**: [Names/Teams]

## 2. User Story Context

### Original Story
[Include original user story text]

### Business Context
[Explain the business problem and objectives]

## 3. Functional Requirements

### FR-1: [Requirement Name]
- **Description**: [Detailed description]
- **Acceptance Criteria**:
  - Criteria 1
  - Criteria 2
  - Criteria 3
- **Use Cases**: [Related use cases]
- **Data Requirements**: [Input/Output data specifications]

<!-- Repeat the FR-N block above for each additional functional requirement -->

## 4. Non-Functional Requirements

### NFR-1: Performance
- **Requirement**: [Specify performance metrics]
- **Target**: [e.g., <100ms response time]

### NFR-2: Security
- **Requirement**: [Security specifications]
- **Implementation**: [How to implement]

<!-- Include other relevant NFRs as needed:
     Scalability | Availability | Maintainability | Usability |
     Compatibility | Localization | Logging & Monitoring | Data Retention -->

## 5. Dependencies & Integrations
- **External Systems**: [List systems]
- **Internal Dependencies**: [Related features/modules]
- **APIs Required**: [List APIs]

## 6. Constraints & Assumptions

### Constraints
- [Technical constraints]
- [Business constraints]
- [Timeline constraints]

### Assumptions
- [Business assumptions]
- [Technical assumptions]
- [Environmental assumptions]

## 7. Acceptance Criteria
- [Acceptance criteria from user story]
- [Additional criteria from clarifications]

## 8. Open Questions & Notes
- [Any unresolved issues]
- [Future considerations]
- [Follow-up items]
```

---

## Section Authoring Guidelines

| Section | Guidance |
|---|---|
| **1. Overview** | Fill all fields; never leave Status, Version, or Last Updated blank. Use `Draft` until reviewed. Start Version at `v1.0`. |
| **2. User Story Context** | Paste the verbatim original story. Business Context explains *why*, not *what*. |
| **3. Functional Requirements** | Number sequentially (FR-1, FR-2 …). Each FR must have at least one measurable acceptance criterion. |
| **4. Non-Functional Requirements** | Number sequentially (NFR-1, NFR-2 …). Always include Performance and Security at minimum. |
| **5. Dependencies & Integrations** | List every external system or internal module this feature touches. |
| **6. Constraints & Assumptions** | Constraints are fixed limits; Assumptions are things believed true but not yet verified. |
| **7. Acceptance Criteria** | Mirror the story's original ACs, then add any discovered during clarification. All items must be testable. |
| **8. Open Questions & Notes** | Record unresolved items here rather than leaving blank sections above. Resolve before status moves to `Approved`. |

---

## Naming & Versioning

- **File path**: `docs/requirements.md` *(single, stable filename — version and date are tracked inside the document)*
- **Version field**: Start at `v1.0`; increment the minor version (e.g., `v1.0` → `v1.1`) on every substantive change; increment the major version (e.g., `v1.x` → `v2.0`) for scope-changing rewrites
- **Last Updated field**: Set to the current date (DD MMM YYYY) every time the document is created or modified
- **Status lifecycle**: `Draft` → `Reviewed` → `Approved`
- **Commit convention**: `docs: Update requirements for [Story ID] - [short title]`
