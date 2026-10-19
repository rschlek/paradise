---
name: codex-setup
description: >-
  Set up Codex on the current device with the global features other workflows
  rely on: plugin hooks enabled, the user's choice on Codex's built-in memories,
  and one-time hook trust, all in ~/.codex/config.toml with unrelated
  configuration preserved. Use on a new or reinstalled machine, for "set up
  Codex", "configure Codex", "codex-setup", or missing plugin hooks in Codex.
  Do NOT use for Claude Code's global settings (paradise:claude-code-setup),
  for installing plugins (paradise:setup), or for terminal configuration.
---

# Codex setup

Reach this end state:

- `~/.codex/config.toml` remains valid and preserves unrelated configuration.
- `[features].hooks = true`.
- `[features].memories` matches the user's choice, or is left untouched.
- The user knows how to trust installed plugin hooks once per device.

## 1. Preflight and memories choice

Confirm Codex is installed or `~/.codex/` exists. Read and parse
`~/.codex/config.toml`; stop on malformed TOML instead of overwriting it.

Ask whether Codex's built-in memories should be on or off. It is the user's
call: on keeps Codex's own automatic memory; off suits a user who keeps one
long-term memory elsewhere (for example the `memory` plugin in the Paradise
marketplace, on a Hindsight server), since two automatic stores can diverge.
If the user has no preference, leave the key untouched. Changing it is
reversible and deletes no files.

## 2. Reconcile `[features]`

Manage only these keys:

| Key | Desired value | Rule |
| --- | --- | --- |
| `hooks` | `true` | Always; ask before overriding a deliberate `false`. |
| `memories` | the user's choice | Only after the user chooses. Otherwise leave untouched. |

Make the smallest possible edit. Preserve every other table, key, comment, ordering,
and formatting choice. No-op if already correct. Otherwise back up to
`config.toml.paradise-backup-<YYYYMMDD-HHMMSS>` (timestamp from `date`), write
UTF-8 without BOM, re-read and parse, and verify the managed values and all
unrelated state. Restore the backup and stop on any failed check. Keep the
backup and report its path.

## 3. Optional: a shared browser

If the user wants browser automation shared between Claude Code and Codex,
offer the `playwright-mcp-shared` plugin from the Paradise marketplace (it is in
the Codex catalog: `codex plugin add playwright-mcp-shared@paradise`) and its
`playwright-mcp-shared:setup` skill, which owns `[mcp_servers.playwright]`.
Skip this step otherwise; do not configure browser servers here.

## 4. Hook trust

With hooks enabled, tell the user that installed plugin hooks may require one-time
trust in Codex. Open the hooks UI or use `/hooks` when that command is available in the
installed Codex version, review each hook, and trust only the plugin hooks they intend
to run. Do not grant trust programmatically.

## 5. Report

Report the final feature values, that TOML parsed after the change, the backup
path if one was made, whether the optional browser step ran, and any remaining
hook-trust step. Remind the user to start a new Codex session so newly
installed plugin content loads.

## Safety

- Never write secrets to `config.toml`.
- Never rewrite the whole TOML file merely to change two feature keys.
