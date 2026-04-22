---
name: workspace-relative-paths
description: Always applies. Prefer relative workspace paths in shells, scripts, and tool arguments; avoid absolute paths unless necessary.
---

# Workspace-relative paths

## Rule

When specifying files or directories, use **relative paths** by default. Reserve absolute paths for cases with a clear, stated reason (for example, system locations outside the repo, or tooling that truly requires absolutes).

Applies to:

- Shell commands and scripts you run or generate
- Read, write, and delete operations
- Any arguments where a path is passed (including to agents/tools)

## Rationale

Absolute paths often trigger repeated execution approval in Cursor and slow the loop. Relative paths usually stay inside the workspace and reduce friction.

## Practical guidance

- Change the working directory when it helps. When paths live under a git-managed tree, prefer `cd` into that repository (or the appropriate subdirectory under it) before running commands so paths stay relative to that root.
- Prefer paths relative to the project root or the current working directory, consistent with the task and repo layout.
- In documentation or comments, relative paths are still preferred when they refer to repo files.
- If an absolute path is required, state the reason briefly so the choice is intentional.
