# Multica adapter activation runbook

## Authorization gate

This runbook is operational guidance, not an implicit authorization. Before any real Multica command, render [the operational authorization request](../templates/multica-operational-authorization.md) and obtain its exact current authorize response. The request names:

- the existing target workspace by stable identity;
- the existing Architecture Agent by stable identity; and
- the requested activation scope for the independently installed core and adapter skills.

It also lists the exact import/additive-binding commands, existing skill identities, planned writes, excluded resource creation/replace-all/configuration, overwrite and availability risks, verification readback and stop behavior. Architecture content approval, an adapter delivery request or a generic instruction to activate cannot substitute.

Repository implementation, local packaging, temporary-HOME link checks, an adapter delivery request, a recommendation, or a Review conclusion do not authorize workspace import or Agent binding. Never create a missing Skill, Agent, Team, Project, Issue, or fallback binding. If the named workspace or Agent cannot be resolved, stop, report the missing identity, and request new human direction.

## Authorized activation procedure

1. Confirm the local package identity and the selected existing workspace/Agent identities with the human. Package/import the adapter only from the reviewed artifact; keep the core skill independently installed rather than embedding or replacing it.
2. Import with conflict-safe behavior, for example:

   ```bash
   multica skill import --file <adapter.skill-or-zip> --on-conflict fail --output json
   ```

   If the import reports a same-name conflict, stop. Record the existing skill identity and the platform-supported choices. The observed target changed, so the prior activation authority is exhausted. Render a new `operation variant=conflict_strategy` request explaining `fail|platform-supported overwrite` consequences, exact target, retained object and risk. Do not overwrite, replace, rename around, or delete the existing skill unless the new exact authorization selects a supported strategy.
3. Resolve the human-named existing Architecture Agent again, then bind skills additively. Do not use a replace-all or `set` operation:

   ```bash
   multica agent skills add <existing-agent-id> <core-skill-id>
   multica agent skills add <existing-agent-id> <adapter-skill-id>
   ```

   Skip an already-present ID only after the read-back below confirms it. Do not create an Agent or choose a substitute if either ID cannot be resolved.
4. Perform the final read-only verification:

   ```bash
   multica agent skills list <existing-agent-id> --output json
   ```

   Confirm that both the core and adapter skill IDs are present and record the selected workspace/Agent identities, adapter repository commit, consumed core revision, and observed Multica/CLI version or commit.
5. Do not claim production readiness from import/binding alone. Run the dedicated sandbox acceptance checklist before enabling the adapter for a production Architecture Agent.

## Closing conditions

- Missing workspace or Agent: stop with `activation=not_run`; request an existing identity from the human.
- Import conflict: stop with `activation=not_run`; request a separately authorized platform-supported conflict strategy.
- Missing core/adapter ID in final list: stop with `activation=not_run`; do not compensate by creating or replacing resources.
- Any command requiring credentials, network access, workspace mutation, or configuration change: execute only after the authorization gate above; otherwise retain `activation=not_run`.
- Superseded or incomplete operational request: retain `activation=not_run`; identify the current request and exact authorize/deny response.
