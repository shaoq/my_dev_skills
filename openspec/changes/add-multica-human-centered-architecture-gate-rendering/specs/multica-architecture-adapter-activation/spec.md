## ADDED Requirements

### Requirement: Activation and conflict choices use operational action requests
Workspace Skill import, additive Agent binding, same-name conflict strategy and sandbox execution SHALL each require a current operational Human Action Request when a new human choice or authorization is needed. The request MUST name exact existing identities, proposed commands/writes, alternatives, overwrite or availability risks, excluded resource creation, verification and rollback/stop behavior, and an exact authorize/deny response.

#### Scenario: Human authorizes initial activation
- **WHEN** a human names an existing workspace and Architecture Agent but has not yet authorized the exact import/binding scope
- **THEN** the runbook presents the operational request and performs no import or binding until its explicit response covers both skill identities and planned additive writes

#### Scenario: Import conflict requires a new choice
- **WHEN** import discovers an existing same-name Skill
- **THEN** the prior activation authority is insufficient, a new conflict-strategy request explains fail/overwrite consequences, and no overwrite occurs without that exact authorization

### Requirement: Sandbox acceptance presents a human checklist
The sandbox run SHALL present the target member with a concise checklist for opening exact Design, Review and Packet materials on desktop and mobile, submitting a separate legal token, observing supersession and confirming failure retention. Each human-observed result MUST be recorded per check; a generic `OK` MUST NOT mark sandbox acceptance passed.

#### Scenario: Human completes only desktop checks
- **WHEN** desktop materials open but mobile or supersession checks are not individually confirmed
- **THEN** sandbox acceptance remains `not_run|failed` and production readiness is not claimed
