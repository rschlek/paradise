# paradise (plugin)

The setup door for the Paradise marketplace. Works in Claude Code; the skills
also ship to Codex through `.codex-plugin/plugin.json`.

| Skill | What it does |
| --- | --- |
| `paradise:setup` | Registers the marketplace, asks one batch of questions (plugins, terminal, Codex), installs the chosen plugins, runs the two skills below, and hands off to terminal setup. Ends with a report of what changed, where the backups are, and how to undo. |
| `paradise:claude-code-setup` | Merges three universal keys into `~/.claude/settings.json` (asking on any conflict), installs a dependency-free context-meter statusline, and, only if the user opts in (with a preview offered first), writes a guidance block between `<!-- paradise:baseline start -->` / `<!-- paradise:baseline end -->` markers in `~/.claude/CLAUDE.md`, and in `~/.codex/AGENTS.md` when Codex is present. |
| `paradise:codex-setup` | Enables plugin hooks in `~/.codex/config.toml`, leaves the built-in memories choice to the user, optionally offers the shared browser plugin, and walks through one-time hook trust. |

## Guarantees

- The guidance block is opt-in: the user is asked to install it, preview it
  first, or skip it. Skipping still applies the settings and statusline.
- Every file is backed up to `<file>.paradise-backup-<timestamp>` before its
  first write, and the backup is kept.
- Text outside the baseline markers, and settings keys the skill does not
  manage, are never changed.
- Nothing leaves your machine except the plugin downloads from GitHub.
- The statusline needs `bash` on PATH (Git Bash on Windows); without it the
  statusline is skipped with a note.

## Undo

- Copy a kept `*.paradise-backup-*` file back over its original, or undo by
  hand as below.
- Delete the block from `<!-- paradise:baseline start -->` to
  `<!-- paradise:baseline end -->` in `~/.claude/CLAUDE.md` and
  `~/.codex/AGENTS.md`.
- Remove the `attribution`, `agentPushNotifEnabled`, and `statusLine` keys from
  `~/.claude/settings.json`, and delete `~/.claude/statusline-command.sh`.
- `claude plugin uninstall <plugin>@paradise` for each installed plugin.

## Assets

`skills/claude-code-setup/assets/` holds the desired state:
`settings.baseline.json`, `claudemd.baseline.md`, and `statusline-command.sh`.
Edit those to change what the baseline installs.
