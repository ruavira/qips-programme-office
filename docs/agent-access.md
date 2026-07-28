# Connecting Claude, Codex and ChatGPT to the same programme office

## One-time human setup

1. Add each agreed human collaborator to the private GitHub repository using their GitHub username.
2. Require two-factor authentication on collaborator accounts.
3. Protect `main`: require a pull request, at least one human review and passing repository checks.
4. Give the GitHub app used by Claude, Codex or ChatGPT access to this repository from the account doing the work.
5. Share the QIPS Drive folder separately, using viewer, commenter or editor access according to role.

## Claude

Connect the same GitHub repository in Claude. Ask Claude to read `CLAUDE.md`, `AGENTS.md`, current canon, open questions and the target workstream before starting. Claude should create a branch or return changes ready for a pull request; it should not use chat memory as the authoritative project state.

## Codex

Open or clone the repository, then ask Codex to follow `AGENTS.md`. Codex can work locally, run checks, push a branch and open a draft pull request. The GitHub connector should be authorized only to repositories the user has deliberately selected.

## ChatGPT workspaces

Connect the GitHub repository and Google Drive folder in the workspace. Start each task by naming the target workstream and requiring the assistant to read the repository instructions and canon. Any final decision must be written back through the repository process.

## Moving between accounts

No export of chat history is required. The handoff is the repository branch, pull request, workstream state and linked Drive document. A new account can resume by reading those records.

## What not to do

- Do not share one personal access token among people or AI tools.
- Do not give an AI unrestricted access to the whole GitHub account when repository-only access is available.
- Do not let a document in Drive and a file in GitHub both claim to be the editable master.
- Do not approve canon changes from a chat transcript alone.
