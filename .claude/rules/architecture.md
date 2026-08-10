---
description: Architecture Document Structure Instructions
paths:
  - "docs/architecture.md"
---

# Architecture Document Structure Instructions

All architecture documents saved to `docs/architecture.md` **must** follow the structure defined below.
Use clear, implementation-agnostic language. Tie every decision back to `docs/requirements.md`, document trade-offs explicitly, and update the version on every substantive change.

---

## Required Document Structure

```markdown
# Architecture Document: [Project Name / Requirement Set]

## 1. Overview
- **Source**: `docs/requirements.md`
- **Status**: [Draft/Reviewed/Approved]
- **Last Updated**: [DD MMM YYYY — updated every time the document changes]
- **Owners**: [Team/Stakeholders]
- **Architecture Style**: [e.g., Layered Modular Monolith / Event-Driven Microservices]

## 2. Context and Drivers

### Business and Product Drivers
[Key outcomes and product goals derived from requirements]

### Architectural Drivers
[Performance, security, reliability, scalability, compliance, cost constraints]

## 3. High-Level Architecture Recommendation

### Recommended Approach
[Describe the selected architecture and the reasoning behind the choice]

### Alternatives Considered
- Option A: [Name] — [Pros / Cons]
- Option B: [Name] — [Pros / Cons]

## 4. Component Diagram
[Provide a high-level component view; Mermaid diagrams are acceptable]

## 5. Key Components and Responsibilities

### Component 1: [Name]
- **Responsibility**: [What this component owns]
- **Interfaces**: [APIs / events / contracts it exposes or consumes]
- **Data Owned**: [Primary entities or data stores it manages]
- **Scaling Considerations**: [How this component scales under load]

<!-- Repeat the Component N block above for each major component -->

## 6. Data Flow

### Core Flow 1: [Use Case Name]
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Data Stores and Movement
- **Source Data**: [Where data originates]
- **Processing**: [How data is transformed or enriched]
- **Persistence**: [Where data is stored and in what form]
- **Consumption**: [Who or what consumes the data downstream]

## 7. Technology Choices
- **Frontend**: [Technology and rationale]
- **Backend**: [Technology and rationale]
- **Data Layer**: [Database / cache / queue and rationale]
- **Infrastructure**: [Cloud / runtime / networking approach]
- **Observability**: [Monitoring / logging / tracing strategy]
- **Security Controls**: [AuthN / AuthZ, secrets management, encryption]

## 8. Cross-Cutting Concerns
- **Security**: [Approach and controls]
- **Reliability & Resilience**: [Failure handling, retries, circuit breakers]
- **Performance**: [Targets and strategies]
- **Scalability**: [Horizontal / vertical scaling strategy]
- **Maintainability**: [Code structure, modularity, documentation standards]
- **Operational Readiness**: [Deployment, runbooks, alerting]

## 9. Risks, Assumptions, and Open Questions

### Risks
- [Risk description and proposed mitigation]

### Assumptions
- [Thing believed to be true but not yet verified]

### Open Questions
- [Question requiring stakeholder input before proceeding]

## 10. Approval
- **Decision**: [Approved / Rework Needed]
- **Approved By**: [Name / Role]
- **Approval Date**: [DD MMM YYYY]
```

---

## Section Authoring Guidelines

| Section | Guidance |
|---|---|
| **1. Overview** | Fill all fields; never leave Status or Last Updated blank. Use `Draft` until reviewed. Link Source to `docs/requirements.md`. |
| **2. Context and Drivers** | Business Drivers answer *why this system exists*; Architectural Drivers capture the non-functional constraints that shape every design decision. |
| **3. High-Level Recommendation** | State one primary approach clearly. Alternatives Considered must list at least one option with explicit pros and cons to show the decision was not made in isolation. |
| **4. Component Diagram** | Diagrams must match the components listed in Section 5. Prefer Mermaid for version-control-friendly diagrams. Label all external integrations. |
| **5. Key Components** | Every component that owns data or exposes an interface must have its own block. Scaling Considerations must not be left blank for any stateful component. |
| **6. Data Flow** | Document at least one end-to-end flow per major use case. Data Stores and Movement must describe origin, transformation, persistence, and consumer for every significant data type. |
| **7. Technology Choices** | Every entry must include a rationale, not just a name. Tie choices back to the drivers in Section 2. |
| **8. Cross-Cutting Concerns** | All six concerns must be addressed. Use `N/A — [reason]` only when genuinely not applicable; do not leave items blank. |
| **9. Risks, Assumptions, Open Questions** | Each Risk must have a mitigation. Open Questions must be resolved before Status moves to `Approved`. |
| **10. Approval** | Leave blank until explicit sign-off is received. Do not self-approve. |

---

## Naming & Versioning

- **File path**: `docs/architecture.md` *(single, stable filename — version and date are tracked inside the document)*
- **Status lifecycle**: `Draft` → `Reviewed` → `Approved`
- **Last Updated field**: Set to the current date (DD MMM YYYY) every time the document is created or modified
- **Commit convention**: `docs: Update architecture for [project/feature name] - [short description]`
- **Re-architecture**: When the recommended approach changes significantly, reset Status to `Draft`, update Last Updated, and record the rationale for the change in Section 3 under Alternatives Considered
