# Agent guidance

<!-- playbook:base start (1.0.1) -->
## Working in this repo

This repo follows the playbook standard, version 1.0.1
(https://github.com/rschlek/playbook). This block is replaced when the
standard updates; put project-specific guidance in the section below it.

- Read `README.md` and `project.yaml` first: what this is, who it is for,
  and where related things live.
- Before changing `project.yaml`, `README.md`, `AGENTS.md`, `CLAUDE.md`, or
  the repo's layout, read `docs/project-conventions.md` and keep to it.
- Make one change for one purpose, and run the checks this repo documents
  before proposing it.
- Commit only the files you changed, by path. Never commit credentials,
  tokens, or data extracts.
- If `project.yaml` says `visibility: public`, anyone can read this repo:
  write no person, employer, team, host, or machine names into it.
- If it says `visibility: internal`, everyone in the organization that
  hosts this repo can read it: the organization's own names are fine,
  other people's personal details are not.
- The repo holds the project's own context; the tracker holds its work.
  A plan lives in its parent ticket, never in a file. Each decision is
  one file in `docs/decisions/`; research is a dated file under `docs/`.
  Write records for a reader who opens the project cold, and in a shared
  project (`shared: true`, or `visibility` set) show the user the exact
  text before writing one.
- Read and write tickets the way the tracker doc says: `docs/tracker.md`
  when present, else the user's own doc for the tracker `project.yaml` or
  the profile names. A ticket's status lives only in its tracker; never
  copy tickets between trackers, and never track progress in a document.
  Read `docs/project-conventions.md` before writing or moving anything
  under `docs/`, and leave existing documents as they are.
- The flow, each step a playbook skill: sharpen the idea (`grill-me`); if
  it is foggy, map its open questions (`wayfinder`, answering them with
  `research`, `prototype`, `grill-me`); plan and file the work
  (`to-tickets`); do each ticket (`tackle`); close the parent. Skip steps
  already clear. Any time: `capture` a stray item, `untangle` when lost,
  `next` when unsure what comes next.
- In a repo other people use, changes go in through its review process,
  not straight to the main branch.
- Keep work in progress in a worktree under `.claude/worktrees/`, one
  session per worktree, and push its branch before leaving it.
- Do not move or rename the repo, and keep `project.yaml` true when the
  project changes.
<!-- playbook:base end -->

## This project

How Claude Code, Codex, and any other harness work in this repo. `CLAUDE.md` is
a one-line import of this file; edit here, never there.

**Paradise** is a public Claude Code and Codex plugin marketplace, registered as
marketplace `paradise`. It carries one plugin of its own (`plugins/paradise`,
the setup door) and catalog entries for external plugins that live in their own
repos. It is also a template for anyone who wants a marketplace of their own.

### How publishing works

- The marketplace is consumed from GitHub, not from a local folder. A push to
  the default branch is a release; editing a file here changes no installed
  copy until it is committed and pushed.
- Claude plugin manifests omit `version`, so the harness uses the git commit
  SHA and every push is a new version. Never add `version` to a catalog entry.
- `.codex-plugin/plugin.json` carries a semver `version`: bump it whenever that
  plugin changes, or Codex will not pick the change up.
- External entries follow each repo's `stable` branch, which moves only by
  deliberate promotion from `main`.

### Layout

- `.claude-plugin/marketplace.json`: the Claude Code catalog.
- `.agents/plugins/marketplace.json`: the Codex catalog, listing only plugins
  that ship a `.codex-plugin/plugin.json`.
- `plugins/<plugin>/`: self-contained: `.claude-plugin/plugin.json`, a
  `README.md`, `skills/<skill>/SKILL.md` (discovered one level deep), and
  optional `.codex-plugin/`, `agents/`, `references/`, `hooks/`.
- `skill-template/`: the starting point for a new skill.
- `scripts/validate.py`: the pre-commit check.
- `docs/project-conventions.md`: the project-guide rules, copied; do not edit.

A skill's invocation name is `<plugin>:<skill-dir>`, such as `paradise:setup`;
an agent's is `<plugin>:<agent>`.

### Add a skill

1. `git pull`.
2. Pick the plugin that is its obvious home.
3. Copy `skill-template/` to `plugins/<plugin>/skills/<name>/` and write it to
   these conventions: generic voice ("the user", never a person's name),
   portable (bundled files by relative path or `${CLAUDE_PLUGIN_ROOT}`, no
   absolute paths), under about 100 lines, and a description that says what it
   does, "Use when" with literal trigger phrases, and "Do NOT use for" naming
   the nearest neighbors. `name` equals the directory name.
4. Add it to the plugin's `README.md` and manifest description.
5. Run the validator, then commit just that skill's paths and push.

An agent goes in `plugins/<plugin>/agents/<name>.md` with `name`,
`description`, a pinned `model`, and a narrowed `tools` list.

### Checks

`python3 scripts/validate.py` (on Windows, `py -3 scripts/validate.py`). It
must pass before every commit.

Its public-hygiene check carries only generic patterns in the script
(`PUBLIC_HYGIENE_PATTERNS`: a private tailnet suffix, personal email domains,
private IPv4 ranges). Personal words are kept out of the repo: they load from
an optional, gitignored `.hygiene-local` file at the repo root (one word per
line, `#` comments, a line `allow: <phrase>` exempts that phrase) and from the
`PARADISE_HYGIENE_WORDS` environment variable (comma separated). Never commit
`.hygiene-local`.

### Hard rules

- Commit by path, never `git add -A`.
- Run the validator before every commit.
- No secrets, tokens, or data extracts, ever.
- This repo is public: no person, employer, team, host, machine, or private
  network names in any file. The validator's public-hygiene check enforces
  this; extend its patterns or your local word list rather than weaken them.
- Changes from other people go in by pull request.

### Consume changes

After a push, `claude plugin marketplace update paradise` then
`claude plugin update <plugin>@paradise` (or rely on auto-update). A new or
changed skill or agent is visible only to sessions started after the update.
