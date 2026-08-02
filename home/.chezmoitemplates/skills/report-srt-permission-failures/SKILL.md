---
name: report-srt-permission-failures
description: Report the minimal Anthropic Sandbox Runtime (srt) permissions potentially needed after a command is denied and srt may be the cause. Include suspected srt denials without investigating causality, but exclude operations already covered by the applicable srt settings, whether allowed or explicitly denied, and denials clearly caused by something other than srt. Do not use for ordinary command failures or proactively.
---

# Report srt Permission Failures

When a command is denied and srt may be the cause:

1. Use only the original failure evidence and the applicable `srt-settings.json`. Do not rerun commands, inspect logs, run diagnostics, or otherwise investigate whether srt caused the denial.
2. Do not report an operation that the applicable `srt-settings.json` already allows or explicitly denies. Treat an explicit denial as intentional policy, not a missing permission.
3. Do not report a denial when the available evidence clearly shows that srt was not the cause. Do not treat an application error, invalid input, or unrelated command failure as an srt denial.
4. Otherwise, report the denial when srt is a plausible cause, even when the cause is not confirmed.
5. Identify each denied operation and the narrowest permission or configuration addition that might allow it, using only the evidence already available.
6. Report the failure to the user before attempting further work that depends on the denied operation.
7. List the potential permission additions as bullet points. For each item, name the permission or setting, its minimal scope, and the blocked operation or supporting evidence.
8. Clearly mark suspected denials and any uncertainty about the required permission. Do not present a guess as a confirmed requirement.
9. Defer investigation, confirmation, and refinement of suspected denials to a separate later session. Do not perform that work in the current session.

Use this response shape in the user's language:

```text
srt may have denied the operation. Its cause was not investigated in this session.

Potential permission additions:

- <permission or setting>: <minimal scope> - <blocked operation or supporting evidence>
```

Do not bypass srt, rerun the command inside or outside the sandbox, or request broad permissions, wildcard network access, or unrelated capabilities. Preserve the failed operation and existing defaults until the user changes the sandbox configuration or directs another approach.
