# AG Mode Manager Architecture & Design Specification

## Overview
**AG Mode Manager** is an external, non-invasive working-mode and domain-intelligence system for Google AntiGravity. It allows developers to operate AntiGravity under specialized personas, quality gates, architectural patterns, UI/UX engines, and security boundaries.

---

## High-Level Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │              User / Developer                │
                  └──────────────────────┬───────────────────────┘
                                         │
                   Interactive TUI / CLI │ (ag-mode)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               AG MODE MANAGER                │
                  │                                              │
                  │  ┌──────────────┐          ┌──────────────┐  │
                  │  │ ModeRegistry │◄─────────┤ ConfigEngine │  │
                  │  └──────┬───────┘          └──────────────┘  │
                  │         │                                    │
                  │  ┌──────▼───────┐          ┌──────────────┐  │
                  │  │  Resolver &  ├─────────►│BackupManager │  │
                  │  │   Composer   │          └──────────────┘  │
                  │  └──────┬───────┘                            │
                  │         │                                    │
                  │  ┌──────▼───────┐          ┌──────────────┐  │
                  │  │   Security   │          │  Diagnostics │  │
                  │  │  Sanitizer   │          │   & Logger   │  │
                  │  └──────────────┘          └──────────────┘  │
                  └──────────────────────┬───────────────────────┘
                                         │ Safe Integration Layer
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │             Target Workspace                 │
                  │                                              │
                  │  <workspace>/                                │
                  │  ├── .agents/                                │
                  │  │   ├── rules/                              │
                  │  │   │   ├── ag_active_mode.md               │
                  │  │   │   ├── ag_quality_gate.md              │
                  │  │   │   └── ag_tools.md                     │
                  │  │   ├── skills/ag-mode/SKILL.md             │
                  │  │   └── ag_mode_state.json                  │
                  │  └── GEMINI.md                               │
                  └──────────────────────┬───────────────────────┘
                                         │ Auto-discovered
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │          Google AntiGravity Agent            │
                  │      (IDE / 2.0 Desktop / CLI 'agy')         │
                  └──────────────────────────────────────────────┘
```

---

## Safe AntiGravity Integration Mechanism
AG Mode Manager adheres to strict safety invariants:
1. **Zero Modifications to Core Binaries**: AntiGravity executables, internal Electron files, databases, chat transcripts, and conversations are never modified or patched.
2. **First-Class Discovery Roots**:
   - `.agents/rules/*.md`: AntiGravity automatically discovers and injects directory and project rules into the agent's context.
   - `GEMINI.md`: Root-level instructions that AntiGravity respects unconditionally across all turns.
   - `.agents/skills/ag-mode/SKILL.md`: On-demand interactive skills.
3. **Atomic Reversibility**: Every activation creates an exact SHA-256 snapshot in `~/.ag-mode-manager/backups/`. Running `ag-mode rollback` or `ag-mode deactivate` restores the workspace bit-for-bit.

---

## Mode Composition & Dependency Resolution
Modes can depend on other modes (e.g. `fullstack` depends on `frontend` and `backend`).
The `DependencyResolver` uses a directed acyclic graph (DAG) topological sort with cycle detection to resolve parent instructions and quality gates without duplicate prompts.
The `ModeComposer` allows activating combinations (e.g. `web` + `cybersecurity`), automatically merging quality gates and security policies.
