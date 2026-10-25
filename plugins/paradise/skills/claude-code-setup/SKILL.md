---
name: claude-code-setup
description: >-
  Set up the user's GLOBAL Claude Code config on the current device with a
  portable baseline: shared preferences and the statusline script into
  ~/.claude/settings.json, plus the whole-machine behavioral baseline block in
  ~/.claude/CLAUDE.md AND, when Codex is present, the identical block in
  ~/.codex/AGENTS.md. Backs up each file first and never touches the user's own
  text outside its markers. Use when the user is setting up a new or
  reinstalled machine, or says "set up my claude settings", "configure claude",
  "claude-code-setup", "apply the Paradise baseline", or "bootstrap claude
  settings". Do NOT use to register marketplaces or install plugins (that is
  paradise:setup), to configure a specific plugin's settings, to edit a
  project-level .claude/settings.json or CLAUDE.md, or to set env vars.
---

# Claude Code Setup

Reach this **end state**: the user's global `~/.claude/settings.json` carries a
small **portable baseline** of shared preferences (and is still **valid JSON** -
a malformed `settings.json` breaks Claude Code on next launch, so this is
load-bearing), and their global `~/.claude/CLAUDE.md` carries a small **managed
guidance block** of whole-machine behavioral defaults. Like `codex-setup`, this
skill ships **no script** and is fully model-driven: you treat the bundled
assets as *desired state*, reconcile each on-disk file toward its asset, then
**verify the artifact**.

**The guidance block is opt-in.** When invoked from `paradise:setup` with the
block skipped, or when the user asks for "settings and statusline only", do
everything except the `CLAUDE.md` / `AGENTS.md` block, and say in the final
report that the block was skipped and can be added later by running
`/paradise:claude-code-setup` and choosing to install the block. When invoked
directly with no instruction, ask before writing the block: install it / show
me first / skip. On "show me first", print the section headings of
`assets/claudemd.baseline.md` and the 7-bullet summary under "What the baseline
asks of Claude" in the repository README, give the asset's path, then ask:
install or skip. Settings keys and the statusline are the same either way.

**The user's own content is never changed.** Every byte of `CLAUDE.md` outside
the baseline markers, and every `settings.json` key this skill does not manage,
survives exactly as it was. Say so to the user before writing.

## The desired-state assets

```
claude-code-setup/assets/
  settings.baseline.json     # the settings.json keys this skill manages, at their values
  claudemd.baseline.md        # the CLAUDE.md guidance block this skill manages (marker-wrapped)
  statusline-command.sh       # the statusline script settings.baseline.json points at
```

Reference them under
`${CLAUDE_PLUGIN_ROOT}/skills/claude-code-setup/assets/`. Each is the **source of
truth** for what we manage - read it and reconcile the on-disk file toward it.

### settings.baseline.json

The settings baseline is deliberately tiny and **universal** (true for any user
on any machine):

| Key | Value | Why |
| --- | ----- | --- |
| `attribution` | `{ "commit": "", "pr": "" }` | No Claude attribution text in commits/PRs. (Modern replacement for `includeCoAuthoredBy`, which is ignored when `attribution` is set - so we do not write the old key.) |
| `agentPushNotifEnabled` | `true` | Phone push when a long task finishes or input is needed (no-op unless Remote Control is connected - pure upside). |
| `idleCompaction` | `false` | No compaction behind the user's back. By default Claude Code (2.1.290+) summarizes a long conversation after about an hour idle and sends the summary with the next message, so a session comes back lossy without anyone choosing it. Compaction stays a deliberate act: the statusline's red band is the cue, `/compact` or a fresh session is the response. Threshold auto-compact (`autoCompactEnabled`) is left alone. Older versions ignore the key. |
| `statusLine` | `{ "type": "command", "command": "bash ~/.claude/statusline-command.sh" }` | Always-visible context meter: the bundled script shows model, dir, git branch, and a color-coded context-usage percentage. Model quality degrades well before the window is full, so the red band (>= 70%) is the user's signal to `/compact` or start a fresh session - a deliberate manual ritual, not an automated one. |

Everything else is **out of scope on purpose** - we do NOT write `env`,
`enabledPlugins`, `extraKnownMarketplaces`, `autoUpdatesChannel`,
`includeCoAuthoredBy`, `skipDangerousModePermissionPrompt`, permissions, or
anything that references a marketplace. Plugins and marketplaces are installed
through the `claude plugin` commands (`paradise:setup`), never by editing
settings here.

### statusline-command.sh

The script `statusLine` points at. Plain bash with **no external dependencies**
beyond `bash` itself, which must be on PATH (on Windows, Git Bash) - and no
`jq` (Git Bash on a fresh Windows machine does not have it); it parses the
statusline JSON payload from stdin with bash/sed and prints model, directory
basename, git branch, and the context-usage percentage color-coded green
(< 50%), yellow (50-69%), bold red (>= 70%, the compact-now / fresh-session
signal). Install it by copying the asset to
`~/.claude/statusline-command.sh`. Same conservative merge as settings: absent
-> write it; byte-identical -> no-op; **present but different -> ASK** before
overwriting (the user may have customized their statusline).

### claudemd.baseline.md

Whole-machine **behavioral guidance** that can't be expressed as a setting -
portable defaults for how the agent should work (including no Co-Authored-By
trailer). **One asset, two targets:** Claude Code reads `~/.claude/CLAUDE.md`,
Codex reads `~/.codex/AGENTS.md`; the same block goes into both (the second only
when `~/.codex/` exists), so the two harnesses can never drift apart. The prose is
harness-neutral - where a rule names a tool it names the Claude Code one and says
so. It is a single block bounded by `<!-- paradise:baseline start -->` /
`<!-- paradise:baseline end -->` markers so it can be refreshed in place without
disturbing the user's own guidance. Same universality bar as the settings
baseline: nothing private, work-specific, or capability-specific goes in it.

## Backups

Before the first write to any file, copy it to
`<file>.paradise-backup-<YYYYMMDD-HHMMSS>` in the same folder (timestamp from
`date`), e.g. `~/.claude/CLAUDE.md.paradise-backup-20260101-120000`. Backups are
**kept** after a clean verify so the user can undo by hand; report each path.
Skip the backup only when the file did not exist or nothing is being written.

## Merge semantics

Both files are **personal and pre-existing**, so you reconcile conservatively
and never clobber the user's own content.

**settings.json (per managed key, ASK on conflict):**

- **Absent on disk** -> set it to our value.
- **Present and already equal** -> no-op.
- **Present but DIFFERENT** -> **STOP and ask the user** before overwriting. Show
  the current value vs. our proposed value and let them choose. The user may have
  set it deliberately; do not silently clobber it.
- **Every key we do NOT manage** -> **preserve byte-for-byte.** Never drop or
  reorder a user's existing settings.

**CLAUDE.md (marker-scoped, no ASK needed):** we own exactly what is between the
baseline markers and nothing else.

- **Markers present** -> replace everything from the start marker through the end
  marker with the baseline block.
- **Markers absent, file non-empty** -> append the block after a blank line.
- **File absent or empty** -> create it containing just the block.
- **Everything outside the markers** -> **preserve byte-for-byte.** The user's own
  guidance above or below the block is never touched.

## Procedure

1. **Locate** `~/.claude/settings.json`. If it does not exist (truly fresh
   machine), treat the starting point as an empty object `{}` and you will write a
   new file.
2. **Read and parse** the existing file. If it is present but does **not** parse
   as valid JSON, **stop and ask** - do not overwrite a file you could not read
   (you would lose their settings).
3. **Compute the merged result in memory** by the per-key merge rules above
   (asking on any conflict before resolving it). First check that `bash` is on
   PATH (see the statusline section below); if it is not, leave `statusLine`
   out of the merge.
4. **No-op short-circuit.** If the computed result is **identical** to what is
   already on disk, say settings already match the baseline and **skip the
   backup and the write entirely**. Never back up + rewrite a file you are not
   changing - that only risks reformatting it.
5. **Back up** `settings.json` as in Backups above.
6. **Write** the merged result with the **Write tool** (it emits UTF-8 **without
   BOM**; some readers choke on a BOM). Pretty-print with **2-space** indentation
   to match the user's existing style, and keep existing keys in place.
7. **Verification gate** (re-read the file from disk and assert on the artifact):
   1. **Valid JSON.** The written file parses cleanly. This is the load-bearing
      check - a broken `settings.json` breaks Claude Code.
   2. **Our keys landed** at our values (or the user's chosen value on a conflict).
   3. **Nothing clobbered.** Every key/section that was present before writing
      (and that we do not manage) is still present and unchanged.
   - On **any** failure: **restore the backup** over `settings.json` and
     escalate (next section). Do not leave a half-written file.

### Then: the statusline script

**Check for bash first** (`command -v bash`, or `Get-Command bash` in
PowerShell); step 3 above uses the same answer. If `bash` is not on PATH,
skip the script install and its smoke test (the `statusLine` key was left out
of the settings merge), and tell the user plainly: the statusline needs `bash`
on PATH (on Windows, install Git for Windows), and re-running this skill
afterwards adds it.

Install `assets/statusline-command.sh` to `~/.claude/statusline-command.sh` (the
path the managed `statusLine` key points at) by the conservative rules above:
read both files, **no-op if byte-identical**, write it if absent, and **ASK
before overwriting** an on-disk script that differs (show a short diff summary,
and back it up first). Then **verify the artifact**: pipe a sample payload
through it and assert it prints a statusline, e.g.

```
echo '{"model":{"display_name":"Test"},"workspace":{"current_dir":"~"},"context_window":{"used_percentage":72}}' \
  | bash ~/.claude/statusline-command.sh
```

must print the model name and a red `Ctx 72%`. If the script was installed but
the check fails, say so plainly - a silent statusline is the failure mode this
guard exists for.

### Then: the guidance block - CLAUDE.md, and AGENTS.md for Codex

Only when the user chose to install it (see the opt-in rule at the top);
otherwise skip this section entirely.

Apply `assets/claudemd.baseline.md` to `~/.claude/CLAUDE.md` by the marker-scoped
rules above, then repeat the identical procedure on `~/.codex/AGENTS.md` if
`~/.codex/` exists (create the file if absent; leave any other tool's own marked
block there untouched). This is the same treat-asset-as-desired-state,
verify-the-artifact loop, just on prose instead of JSON:

   1. **Read** `~/.claude/CLAUDE.md` (treat a missing/empty file as `""`) and read
      the bundled `assets/claudemd.baseline.md`.
   2. **Compute the result in memory:** replace the existing baseline
      block if the markers are present, else append it (file non-empty) or create
      the file with just the block (absent/empty). Leave every other line exactly
      as-is.
   3. **No-op short-circuit.** If the computed result is identical to what is on
      disk, say the guidance block already matches and **write nothing**.
   4. **Back up** the file as in Backups above. **Write** the result with the
      **Write tool** (UTF-8 without BOM).
   5. **Verify the artifact** (re-read from disk): exactly one baseline block, its
      start and end markers both present and in order, and every byte outside the
      block identical to before. On any failure, **restore the backup** and
      escalate (see below).

8. **Report** what landed: the baseline keys written (or confirmed already
   present), each conflict and how it was resolved, that `settings.json`
   re-read as valid JSON and pre-existing settings were preserved, whether the
   statusline script was installed / already current and passed its live smoke
   test, whether the guidance block in `CLAUDE.md` (and `~/.codex/AGENTS.md`
   when present) was created / appended / refreshed / already current / skipped
   (if skipped, how to add it later) and that the user's own guidance was
   preserved, and the path of every backup kept.

## Undo

- **From the backups:** copy a kept `.paradise-backup-*` file back over its
  original (`settings.json`, `CLAUDE.md`, `AGENTS.md`, or the statusline
  script).
- **By hand:** delete the block from `<!-- paradise:baseline start -->` through
  `<!-- paradise:baseline end -->` in `~/.claude/CLAUDE.md` (and
  `~/.codex/AGENTS.md`); remove the `attribution`, `agentPushNotifEnabled`,
  `idleCompaction`, and `statusLine` keys from `~/.claude/settings.json` (keep it valid JSON); and
  delete `~/.claude/statusline-command.sh`.

## Contextual human escalation

If a verification check fails after either write, or the situation is
**ambiguous-and-destructive** (an existing `settings.json` that does not parse, a
managed-key conflict you cannot safely resolve, or a `CLAUDE.md` whose markers are
malformed/unbalanced so you cannot tell which region is ours), **STOP and ask** -
never fail with a bare error or a half-written file. Compose a precise ask:

- what you read and **where** (resolved path),
- the failing check and the **actual** value/bytes,
- your best-guess cause,
- the **specific** confirmation or value you need to proceed.

When you have already written and a check failed, say plainly that you restored
the backup (name its path), so the user knows their original is intact.

## Notes

- **Idempotent.** Re-running changes nothing when both baselines are already
  present and equal (the settings keys match and the `CLAUDE.md` block is
  byte-identical); safe on every new device or re-run.
- **Two files, one seam.** `settings.json` holds what can be a *setting*;
  `CLAUDE.md` holds whole-machine *behavioral guidance* that cannot. Both are
  user-level and global; the skill never touches `settings.local.json`, project
  `CLAUDE.md` files, or `.claude.json` (harness state).
- **Privacy / portability.** All shipped assets are universal and carry no
  personal, machine-specific, or work-specific values. Nothing leaves your
  machine except the plugin downloads from GitHub; every change here is a
  local file write.
- **Why so small.** This is the Claude Code counterpart to `codex-setup`. Thin
  and focused is the point - it manages exactly the handful of universal
  preferences and the one small guidance block, and asks before touching
  anything the user already set.
