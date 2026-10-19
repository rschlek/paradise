---
name: setup
description: >-
  Set up Claude Code (and Codex, when present) in the terminal from the
  Paradise marketplace: register the marketplace, ask one batch of questions,
  install the chosen plugins, apply the portable baseline, and hand off to
  terminal setup, with backups and an undo path. Use when the user says "set me
  up with Paradise", "install Paradise", "copy this terminal setup", "set up
  Claude Code in the terminal", "run paradise setup", or pastes the Paradise
  repository link and asks to be set up. Do NOT use to change only the
  settings and guidance baseline (paradise:claude-code-setup), only Codex
  features (paradise:codex-setup), or to author a plugin or skill.
---

# Paradise setup

Nothing leaves the machine except the plugin downloads from GitHub; every
file touched is backed up first. Every step checks the current state and skips
what is already done, so the skill can be run again at any point, and is meant
to be after the restart in step 4.

## Procedure

1. **Register the marketplace.** Run `claude plugin marketplace list`. If a
   marketplace named `paradise` exists and points somewhere other than
   `rschlek/paradise`, stop: say which source it uses and ask before going on.
   If it already points at `rschlek/paradise`, go on. If it is absent, run
   `claude plugin marketplace add rschlek/paradise` and confirm it lists as
   `paradise`.
2. **Ask once, in one batch** (a structured multi-question ask, such as
   AskUserQuestion in Claude Code). First run `claude plugin list` (and, with
   Codex, check its installed plugins) so already-installed plugins show as
   installed rather than as choices; on a re-run with everything chosen
   already in place, ask only what is still open.
   - Plugins. Checked by default: `productivity`, `terminal`. Offered:
     `project-guide`, `playwright-mcp-shared`. Listed but unchecked: `memory`,
     which needs a Hindsight memory server; off unless the user has one.
   - Terminal: Warp, WezTerm, or neither.
   - Codex: present on this machine? Check for `~/.codex/` or a `codex`
     command first and offer the answer as the default.
   - Guidance block for Claude: install it / show me first / skip. On "show
     me first", print the section headings of
     `claude-code-setup/assets/claudemd.baseline.md` and the 7-bullet summary
     under "What the baseline asks of Claude" in the repository README, give
     the asset's path, then ask: install or skip.
3. **Install.** For each chosen plugin not already installed,
   `claude plugin install <plugin>@paradise` (`paradise@paradise` is already
   installed if this skill is running; install it if not). When Codex is
   present, run `codex plugin marketplace add rschlek/paradise` if Codex does
   not list it yet, then `codex plugin add <plugin>@paradise` for
   `paradise` and each chosen plugin not already added; every plugin offered
   above is in the Codex catalog. Confirm each install from the command's
   output; report any failure and carry on with the rest.
4. **Restart if plugins were just installed.** Plugins installed this session
   load at the next session start. If step 3 installed anything and a later
   step hands off to one of those plugins' skills (such as
   `terminal:warp-setup`), finish steps 5 and 6 (they need nothing new), then
   tell the user to restart Claude Code and run `/paradise:setup` again; the
   skill detects what is already done and continues. Stop there with the
   report in step 8.
5. **Apply the baseline.** Run `paradise:claude-code-setup`, passing the
   guidance block answer (install or skip). It writes nothing that already
   matches, backs up each file first, writes only between its markers, asks
   on any settings conflict, and keeps the user's own CLAUDE.md text byte for
   byte.
6. **Codex.** If Codex is present, run `paradise:codex-setup` (a no-op when its
   features are already set).
7. **Terminal.** For Warp, hand off to `terminal:warp-setup`; for WezTerm, to
   `terminal:wezterm-setup`. If the skill is still not available, the plugin
   did not load: check `claude plugin list` and repeat the restart in step 4.
8. **Report**:
   - what was installed, in each harness, and what was already in place;
   - what changed on disk, file by file, and what was already current;
   - where each backup is (`*.paradise-backup-*` beside the original);
   - how to undo: copy a backup back over its original; or delete the block
     from `<!-- paradise:baseline start -->` to
     `<!-- paradise:baseline end -->` in `~/.claude/CLAUDE.md` (and
     `~/.codex/AGENTS.md`), remove the `attribution`,
     `agentPushNotifEnabled`, and `statusLine` keys from
     `~/.claude/settings.json`, and delete `~/.claude/statusline-command.sh`;
     and `claude plugin uninstall <plugin>@paradise` (in Codex, remove it
     from the plugins menu);
   - whether a restart and a second `/paradise:setup` run are still needed.

## Make it yours

Paradise is also a template for a marketplace of one's own: point the user at
https://github.com/rschlek/paradise#make-it-yours

## Notes

- Never edit `enabledPlugins` or `extraKnownMarketplaces` by hand; the
  `claude plugin` commands own them.
- If a plugin install needs a login or approval, stop at that step and let the
  user complete it; never handle their credentials.
- Re-running is safe: installed plugins and a current baseline are no-ops.
