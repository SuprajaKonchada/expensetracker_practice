description: Run documentation and React standards checks using the docstring-writer and react-standards-reviewer subagents.

Invoke these two subagents in parallel, in the same turn.

1. `docstring-writer` — add missing documentation comments to JavaScript/TypeScript classes, functions, methods, or public APIs that are missing them in the recently changed files.

2. `react-standards-reviewer` — review the recently changed frontend code and apply the installed React coding standards plugin without changing existing functionality.

After both subagents finish, provide a combined summary of:
- What documentation `docstring-writer` added (if anything).
- React standards issues found and fixed by `react-standards-reviewer`.
- Files changed by each agent.
- Any tests run and their results.