# Paradise

Paradise is a small plugin marketplace for Claude Code and Codex: a one-command
terminal setup plus a handful of portable plugins for working with coding
agents. It is also a template: fork it into a private marketplace of your
own.

## Set up in one line

Paste this into Claude Code:

```
Set me up with Paradise: https://github.com/rschlek/paradise
```

Claude reads this README, adds the marketplace, installs `paradise@paradise`,
and runs `/paradise:setup`.

## Or by hand

```
claude plugin marketplace add rschlek/paradise
claude plugin install paradise@paradise
```

Then start a new session and run `/paradise:setup`. Codex users can also run
`codex plugin marketplace add rschlek/paradise` and
`codex plugin add <plugin>@paradise` for any plugin in the table below; every
one of them is in the Codex catalog too.

## What `paradise:setup` does

1. Registers the `paradise` marketplace (and stops if a different marketplace
   already uses that name).
2. Asks one batch of questions: which plugins, which terminal (Warp, WezTerm,
   or neither), and whether Codex is on the machine.
3. Installs the chosen plugins with `claude plugin install`, and in Codex when
   present. Plugins installed in a session load at the next session start, so
   it may ask you to restart Claude Code and run `/paradise:setup` again; the
   second run sees what is already done and carries on.
4. Applies a portable Claude Code baseline: three settings keys (no AI
   attribution in commits, push notifications, a context-meter statusline) and
   an optional guidance block in your global `~/.claude/CLAUDE.md` about
   delegation, autonomy, secrets, shell habits, and communication. The block is
   opt-in: setup asks whether to install it, show it to you first, or skip it.
   The same block goes into `~/.codex/AGENTS.md` when Codex is present. The statusline is a bash script,
   so it needs `bash` on your PATH (on Windows, Git Bash); without it the
   statusline is skipped with a note.
5. Sets up Codex features (plugin hooks on, built-in memories your call).
6. Hands off to Warp or WezTerm setup if you picked one.
7. If a keep-awake utility that works by faking keypresses is running
   (Caffeine on Windows), offers to relaunch it in its no-input mode, so each
   tick stops scrolling your terminal to the bottom.
8. Reports what changed, where the backups are, and how to undo it.

Every step checks first and skips what is already in place, so running it
again is safe.

What it does **not** do:

- It never changes your `CLAUDE.md` outside its
  `<!-- paradise:baseline start -->` / `<!-- paradise:baseline end -->` markers,
  and never changes a settings key it does not manage. On a conflicting key it
  asks.
- It backs up every file before writing to it, as
  `<file>.paradise-backup-<timestamp>`, and keeps the backup.
- Nothing leaves your machine except the plugin downloads from GitHub.

To undo:

- Copy a kept `*.paradise-backup-*` file back over its original, or undo by
  hand as below.
- Delete the block from `<!-- paradise:baseline start -->` to
  `<!-- paradise:baseline end -->` in `~/.claude/CLAUDE.md` (and
  `~/.codex/AGENTS.md`).
- Remove the `attribution`, `agentPushNotifEnabled`, and `statusLine` keys from
  `~/.claude/settings.json`, and delete `~/.claude/statusline-command.sh`.
- `claude plugin uninstall <plugin>@paradise` for each plugin (in Codex, remove
  it from the plugins menu).

## What the baseline asks of Claude

The guidance block is opinionated and opt-in: setup asks before installing it,
and "show me first" previews its sections and this summary. Read it before
installing:
[`claudemd.baseline.md`](plugins/paradise/skills/claude-code-setup/assets/claudemd.baseline.md).
In short:

- Hub and spokes: the main session plans and decides; subagents do the reading
  and building, each pinned to a cheaper model.
- Reversible actions are done without asking; irreversible or destructive ones
  are confirmed first, on a concrete list.
- No secrets in the chat; interactive logins go through a shared terminal pane
  when one is available.
- Shell discipline: no sleep-and-poll loops, detached long jobs, bounded remote
  reads.
- Anything you must paste (a command, a path, a snippet) is put on your
  clipboard, not only shown.
- No AI attribution trailers on commits or pull requests.
- Keep the session under about half its context, and say when to compact.

## Plugins

| Plugin | What it is | Default |
| --- | --- | --- |
| `paradise` | The setup door: `setup`, `claude-code-setup`, `codex-setup`. Lives in this repo. | yes |
| [`productivity`](https://github.com/rschlek/productivity) | handoff, grill-me, watch, explain, untangle, write-a-skill, deepen. | yes |
| [`terminal`](https://github.com/rschlek/terminal) | A shared WezTerm window for interactive logins, seeded chats in Warp tabs, Warp and WezTerm setup. | yes |
| [`project-guide`](https://github.com/rschlek/project-guide) | A small standard for laying out and describing projects, with skills to apply it. | offered |
| [`playwright-mcp-shared`](https://github.com/rschlek/playwright-mcp-shared) | One Playwright MCP browser shared safely by concurrent agent sessions. | offered |
| [`todoist`](https://github.com/rschlek/todoist) | Todoist skills: capture, inbox triage with an overdue walk, idea pruning, board reconcile, structure review, tackle. Uses Doist's hosted Todoist MCP server. | offered |
| [`memory`](https://github.com/rschlek/memory) | Long-term memory skills. Needs a running [Hindsight](https://github.com/vectorize-io/hindsight) memory server (open source). | off |

External plugins follow each repo's `stable` branch.

## Make it yours

Use this repo as a template for your own marketplace, private or public:

1. Create a repo from this template (or fork it).
2. Rename the marketplace: change `name` in `.claude-plugin/marketplace.json`
   and `.agents/plugins/marketplace.json`, and `owner` to your account.
3. Add your own plugins under `plugins/<yours>/` (start a skill from
   `skill-template/`) and list each in the catalogs.
4. Keep the external entries if you want them; they install from their own
   repos.
5. Run `python3 scripts/validate.py` before every commit. `AGENTS.md` has the
   authoring rules.
6. The validator's public-hygiene check ships only generic patterns (private
   network suffixes, personal email domains, private IP ranges). Put your own
   names and private domains in a gitignored `.hygiene-local` file at the repo
   root (one word per line, `#` comments, `allow: <phrase>` to exempt a
   phrase) or in the `PARADISE_HYGIENE_WORDS` environment variable (comma
   separated), so the check catches them without publishing them.

`docs/project-conventions.md` is a copy of the rules of the
[project-guide](https://github.com/rschlek/project-guide) standard this repo
follows.

## Support

Issues and pull requests are welcome. Support is best effort.

## License

MIT; see [LICENSE](LICENSE). External plugins carry their own licenses.
