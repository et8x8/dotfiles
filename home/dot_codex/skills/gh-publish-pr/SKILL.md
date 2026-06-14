---
name: gh-publish-pr
description: Publish approved repository changes by committing, pushing, and creating or updating a GitHub pull request. Use only when the user explicitly invokes $gh-publish-pr; never invoke implicitly.
---

# GitHub Publish PR

## Delegate First

Immediately create a subagent using `model: gpt-5.5` and `reasoning_effort: low`. Delegate the entire publishing workflow to that subagent. Keep the parent responsible for user communication and approvals.

If the subagent returns because a rebase has conflicts, do not resolve them. Ask the user how to proceed, then resume the same subagent with the user's answer.

## Inspect Before Publishing

Require the subagent to:

1. Read and obey repository instructions and publishing conventions.
2. Inspect Git status, current branch and HEAD, remotes, and any existing pull request for the current work.
3. Use the existing pull request base when one exists. Otherwise use the remote default branch as the intended base; stop and ask the user if it cannot be determined unambiguously.
4. Inspect the complete pending diff without reading secret values.
5. Stop and report if any repository-prohibited file is present in the diff. Do not inspect, stage, modify, or publish that file.
6. Never read `.env.keys` or inspect, print, confirm, or expose environment-variable values.

## Prepare the Branch and Commit

- If HEAD is detached or checked out on the base branch, derive a concise slug from the changes and create a non-conflicting `codex/<slug>` branch.
- Otherwise, preserve the current feature branch unless publishing it would be unsafe or ambiguous.
- Stage all and only the allowed uncommitted changes in scope.
- Preserve existing history and create exactly one new commit for staged changes. If there is no diff to commit, skip the commit.
- Run normal commit hooks. Never bypass hooks or use `--no-verify`.

## Push Safely

- Push the feature branch to its appropriate remote.
- Never use ordinary force push.
- If the push is rejected only because the base branch advanced, fetch and rebase onto the updated base.
- If that rebase conflicts, stop without resolving conflicts and return control to the parent.
- Use `--force-with-lease` only when the successful base update rebase rewrote commits already published on the feature branch.
- For feature-branch divergence, unexpected remote history, ambiguous upstreams, or any rejection not solely caused by an advanced base, stop and ask the user before continuing.

## Create or Update the Pull Request

- If no pull request exists, create a Draft pull request.
- If one exists, preserve its current draft or ready state and update its title and body.
- Write in English.
- Treat pull request titles and bodies as the bridge between AI agent sessions.
- Pull requests are merged into the target branch with Squash and merge, and the pull request body becomes part of the resulting commit message. Write the pull request body so that someone reading the squashed commit message can understand what changed, why it changed, and any important follow-up context.
- Write pull request titles so that git log --oneline -20 remains the most reliable compact record of what happened recently.
- Target the confirmed base branch.
- Never merge the pull request.
