---
name: research-orchestrator
description: "Master orchestrator for the Research Vault harness. Coordinates 4 specialist agents (research-analyst, vault-curator, schedule-manager, project-overseer) to handle complex multi-domain tasks. TRIGGER when: user requests involve multiple domains (e.g., 'review papers and organize them', 'create daily briefing with project status'), when a task requires coordination across research, vault, schedule, and project management, or when the user says 'harness', 'full workflow', 'coordinate', or gives a complex multi-step request."
---

# Research Orchestrator

Coordinate the 4 specialist agents to execute complex, multi-domain workflows in the Research Vault.

## Architecture

**Pattern**: Expert Pool + Fan-out/Fan-in hybrid
**Execution Mode**: Agent Team (default) or Sub-agent (for single-domain tasks)

### Agent Registry

| Agent | Type | Model | Domain | Primary MCPs |
|-------|------|-------|--------|-------------|
| research-analyst | general-purpose | opus | Papers, literature | arxiv, semantic-scholar, fetch, brave-search |
| vault-curator | general-purpose | opus | Vault organization | obsidian |
| schedule-manager | general-purpose | opus | Calendar, daily notes | google-calendar, gmail, obsidian |
| project-overseer | general-purpose | opus | Project tracking | obsidian, google-calendar |

### Routing Table

| User Request Pattern | Primary Agent | Supporting Agents |
|---------------------|---------------|-------------------|
| Paper search/review | research-analyst | vault-curator (filing) |
| Literature survey | research-analyst | vault-curator (filing), project-overseer (linking) |
| Organize/tag/clean | vault-curator | — |
| Daily briefing | schedule-manager | project-overseer (deadlines) |
| Calendar/schedule | schedule-manager | — |
| Project status | project-overseer | schedule-manager (calendar sync) |
| Inbox triage | vault-curator | research-analyst (paper classification) |
| Full workflow | ALL | Fan-out/Fan-in |

## Workflow Phases

### Phase 1: Request Analysis

1. Parse user request to identify involved domains
2. Select execution mode:
   - **Single domain** → Sub-agent mode (spawn one agent directly)
   - **Multi domain** → Agent Team mode (coordinate multiple agents)
3. Identify data dependencies between agents

### Phase 2: Team Composition (Agent Team mode only)

```
TeamCreate:
  team_name: "research-vault-team"
  members:
    - agent: research-analyst (if research tasks present)
    - agent: vault-curator (if organization tasks present)
    - agent: schedule-manager (if schedule tasks present)
    - agent: project-overseer (if project tasks present)

TaskCreate:
  - task for each agent based on request decomposition
  - dependencies specified (e.g., vault-curator depends on research-analyst output)
```

### Phase 3: Execution

**Fan-out**: Each agent works on their domain in parallel
- research-analyst searches/reviews papers
- vault-curator organizes existing notes
- schedule-manager syncs calendar
- project-overseer scans project status

**Communication**: Agents share findings via SendMessage
- research-analyst → vault-curator: "New review note created at [path], needs tagging"
- project-overseer → schedule-manager: "Deadline in 3 days for [project], add reminder"

**Artifacts**: Each agent saves intermediate results to `_workspace/`:
- `_workspace/{agent}_{artifact}.md`

### Phase 4: Integration

1. Collect outputs from all agents
2. Resolve any conflicts (e.g., duplicate tags, calendar mismatches)
3. Produce unified summary for user

### Phase 5: Cleanup

1. Summary report to user
2. _workspace/ artifacts preserved for audit
3. Team dissolved

## Common Workflows

### Morning Briefing (daily-briefing skill)
```
1. schedule-manager → fetch calendar + create daily note
2. project-overseer → scan deadlines (parallel)
3. vault-curator → count inbox items (parallel)
4. Integration → compile into daily note
```

### Paper Review + File
```
1. research-analyst → search + review paper
2. vault-curator → tag and file review note
3. schedule-manager → log in daily note
```

### Weekly Review
```
1. project-overseer → generate project dashboard
2. research-analyst → reading-tracker progress
3. vault-curator → inbox audit + tag audit
4. schedule-manager → next week preview
5. Integration → compile weekly review note
```

## Data Flow Protocol

| Strategy | When to Use |
|----------|------------|
| **File-based** | Large artifacts (review notes, survey docs, dashboards) |
| **Message-based** | Real-time coordination ("tagging done", "deadline found") |
| **Task-based** | Progress tracking, dependency management |

File naming: `_workspace/{phase}_{agent}_{artifact}.md`
Final outputs: saved to appropriate vault folders (01-inbox/, 02-daily-notes/, etc.)

## Error Handling

| Scenario | Action |
|----------|--------|
| Single agent fails | Retry once, then proceed without that domain (note omission in summary) |
| MCP connection lost | Agent falls back to direct file access or skips that data source |
| Conflicting data | Present both versions to user, do not auto-resolve |
| > 50% agents fail | Abort workflow, report to user with partial results |

## Test Scenarios

### Normal Flow: Morning Briefing
**Input**: "Give me today's briefing"
**Expected**:
1. schedule-manager fetches calendar → 3 events found
2. project-overseer scans deadlines → 1 deadline within 7 days
3. vault-curator counts inbox → 5 unprocessed items
4. Daily note created at `02-daily-notes/2026/04/2026-04-04.md`
5. Summary displayed to user

### Error Flow: Calendar Unavailable
**Input**: "Give me today's briefing" (Google Calendar MCP down)
**Expected**:
1. schedule-manager reports calendar failure
2. Daily note created with "[Calendar sync pending]" placeholder
3. Other agents proceed normally
4. Summary includes warning about missing calendar data
