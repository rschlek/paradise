#!/usr/bin/env python3
"""Validate the marketplace catalogs, every in-repo plugin, its skills and agents,
the cross-references between them, and the public-hygiene list. Exit 1 on any
error. Standard library only; runs on Python 3.8 or later (`python3` or `py -3`).

Checks:
  - catalogs and manifests parse; catalogs carry no `version` keys
  - every plugins/<x> is in the Claude catalog; every plugin shipping a
    .codex-plugin manifest is in the Codex catalog; an external plugin missing
    from the Codex catalog is only a warning (it may be Claude Code only):
    the validator can't inspect a remote repo for a Codex manifest
  - every plugin has a README.md
  - every SKILL.md has name + description, and name == directory name
  - every agents/*.md has name, description, a pinned model (not inherit),
    and a narrowed tools list (not "*")
  - every `<plugin>:<name>` mention of an in-repo plugin resolves to a real
    skill or agent
  - public hygiene (this repo is public): no file in the tree matches a generic
    pattern in PUBLIC_HYGIENE_PATTERNS (private network suffixes, personal email
    domains, private IPv4 ranges), or a word from the optional, gitignored
    `.hygiene-local` file at the repo root or the PARADISE_HYGIENE_WORDS
    environment variable (comma separated). Personal words live only there, so
    the script itself publishes none. In `.hygiene-local`, one word per line,
    `#` starts a comment, and a line `allow: <phrase>` exempts that phrase even
    when it contains a banned word.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE_JSON = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"

# Generic patterns that must never appear in this public repo, matched
# case-insensitively in every text file except this one: a private tailnet
# suffix, personal email addresses, GitHub's private commit-email domain, and
# IPv4 addresses in the private (10/8, 192.168/16) and carrier-grade NAT
# (100.64/10) ranges. Personal words (names, employers, private domains) are
# never written here: they are loaded at run time from HYGIENE_LOCAL_FILE and
# HYGIENE_ENV_VAR. Extend these; never weaken them to make a file pass.
PUBLIC_HYGIENE_PATTERNS = (
    ("private tailnet suffix", re.compile(r"\.ts\.net", re.IGNORECASE)),
    ("@gmail.com", re.compile(r"@gmail\.com", re.IGNORECASE)),
    ("users.noreply.github.com", re.compile(r"users\.noreply\.github\.com", re.IGNORECASE)),
    (
        "private IPv4 address",
        re.compile(
            r"(?<![\d.])(?:10(?:\.\d{1,3}){3}"
            r"|192\.168(?:\.\d{1,3}){2}"
            r"|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2})(?![\d.]*\d)"
        ),
    ),
)
HYGIENE_LOCAL_FILE = REPO_ROOT / ".hygiene-local"  # gitignored; never committed
HYGIENE_ENV_VAR = "PARADISE_HYGIENE_WORDS"
HYGIENE_SKIP_DIRS = {".git", "__pycache__", "worktrees"}
HYGIENE_SKIP_FILES = {"scripts/validate.py", ".hygiene-local"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".woff", ".woff2"}

# Plugins allowed to carry no skills or agents.
EMPTY_OK: set[str] = set()

errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def load_json(path: Path):
    if not path.is_file():
        errors.append(f"Missing manifest: {rel(path)}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  OK  {rel(path)}")
        return data
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in {rel(path)}: {e}")
        return None


def frontmatter(path: Path) -> dict | None:
    """Minimal YAML-ish frontmatter reader: top-level `key: value` lines only,
    folded `>-` blocks joined. Returns None when the delimiters are missing."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm: dict[str, str] = {}
    key = None
    for line in parts[1].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            fm[key] = "" if val in (">-", ">", "|", "|-") else val
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


# ---------------------------------------------------------------- skills / agents

def validate_skill(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{rel(skill_dir)}: missing SKILL.md")
        return None
    fm = frontmatter(skill_md)
    if fm is None:
        errors.append(f"{rel(skill_md)}: missing or malformed YAML frontmatter")
        return None
    ok = True
    for k in ("name", "description"):
        if not fm.get(k):
            errors.append(f"{rel(skill_md)}: frontmatter missing '{k}:'")
            ok = False
    if fm.get("name") and fm["name"] != skill_dir.name:
        errors.append(f"{rel(skill_md)}: name '{fm['name']}' != directory '{skill_dir.name}'")
        ok = False
    if ok:
        print(f"  OK  {rel(skill_md)}")
    return fm.get("name")


def validate_agent(agent_md: Path) -> str | None:
    fm = frontmatter(agent_md)
    if fm is None:
        errors.append(f"{rel(agent_md)}: missing or malformed YAML frontmatter")
        return None
    ok = True
    for k in ("name", "description", "model", "tools"):
        if not fm.get(k):
            errors.append(f"{rel(agent_md)}: agent frontmatter missing '{k}:' (AGENTS.md)")
            ok = False
    if fm.get("name") and fm["name"] != agent_md.stem:
        errors.append(f"{rel(agent_md)}: name '{fm['name']}' != file '{agent_md.stem}'")
        ok = False
    model = (fm.get("model") or "").lower()
    if model in ("inherit", ""):
        errors.append(f"{rel(agent_md)}: model must be pinned, not '{model}' (AGENTS.md)")
        ok = False
    tools = (fm.get("tools") or "").strip().strip('"').strip("'")
    if tools == "*":
        errors.append(f"{rel(agent_md)}: tools must be narrowed to the lane, not '*' (AGENTS.md)")
        ok = False
    if ok:
        print(f"  OK  {rel(agent_md)}")
    return fm.get("name")


# ---------------------------------------------------------------- plugins

def discover_plugins() -> list[Path]:
    if not PLUGINS_DIR.is_dir():
        return []
    return sorted(d for d in PLUGINS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))


def validate_plugin(plugin_dir: Path) -> set[str]:
    """Validate one plugin; return the set of names `<plugin>:<name>` may resolve
    to: its skills plus its agents (both are addressed that way, e.g.
    `paradise:setup`)."""
    print(f"Validating plugin: {plugin_dir.name}")
    load_json(plugin_dir / ".claude-plugin" / "plugin.json")
    codex_manifest = plugin_dir / ".codex-plugin" / "plugin.json"
    if codex_manifest.is_file():
        load_json(codex_manifest)
    if not (plugin_dir / "README.md").is_file():
        errors.append(f"{rel(plugin_dir)}: missing README.md")

    skills: set[str] = set()
    skills_dir = plugin_dir / "skills"
    skill_dirs = sorted(d for d in skills_dir.iterdir() if d.is_dir()) if skills_dir.is_dir() else []
    for d in skill_dirs:
        name = validate_skill(d)
        if name:
            skills.add(name)

    agents_dir = plugin_dir / "agents"
    agent_files = sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []
    for a in agent_files:
        agent_name = validate_agent(a)
        if agent_name:
            skills.add(agent_name)

    if not skill_dirs and not agent_files and plugin_dir.name not in EMPTY_OK:
        errors.append(f"{rel(plugin_dir)}: no skills/ or agents/ (empty plugin)")
    return skills


# ---------------------------------------------------------------- catalogs

def catalog_entries(catalog: Path) -> dict[str, str | dict]:
    """Return each catalog entry's source and flag stray versions."""
    out: dict[str, str | dict] = {}
    if not catalog.is_file():
        return out
    try:
        data = json.loads(catalog.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    label = rel(catalog)
    for entry in data.get("plugins", []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", "<unnamed>")
        if "version" in entry:
            errors.append(f"{label}: entry '{name}' has a 'version' key; it belongs in the plugin's own manifest")
        source = entry.get("source")
        if source:
            out[name] = source
    return out


def local_source_path(source: str | dict) -> str | None:
    if isinstance(source, str):
        return source
    if source.get("source") == "local":
        return source.get("path")
    return None


def check_catalog_coverage(plugins: list[Path]) -> None:
    claude = catalog_entries(MARKETPLACE_JSON)
    codex = catalog_entries(CODEX_MARKETPLACE_JSON)
    names = {p.name for p in plugins}
    for name, source in claude.items():
        src = local_source_path(source)
        if src and not (REPO_ROOT / src / ".claude-plugin" / "plugin.json").is_file():
            errors.append(f"Claude catalog: '{name}' source '{src}' has no .claude-plugin/plugin.json")
    for name, source in codex.items():
        src = local_source_path(source)
        if src and not (REPO_ROOT / src / ".codex-plugin" / "plugin.json").is_file():
            errors.append(f"Codex catalog: '{name}' source '{src}' has no .codex-plugin/plugin.json")
    for p in plugins:
        if p.name not in claude:
            errors.append(f"Claude catalog: plugins/{p.name} exists but is not listed in {rel(MARKETPLACE_JSON)}")
        if (p / ".codex-plugin" / "plugin.json").is_file() and p.name not in codex:
            errors.append(f"Codex catalog: plugins/{p.name} ships .codex-plugin but is not listed in {rel(CODEX_MARKETPLACE_JSON)}")
    for name in set(claude) - names:
        if local_source_path(claude[name]):
            errors.append(f"Claude catalog: '{name}' has no plugins/{name} directory")
        if name not in codex:
            # The validator can't inspect a remote repo for a Codex manifest, so
            # absence from the Codex catalog is the correct way to say "Claude
            # Code only": warn, don't fail.
            warnings.append(f"External plugin '{name}' is missing from the Codex catalog (Claude Code only?)")
        elif claude[name] != codex[name]:
            errors.append(f"External plugin '{name}' does not use the same source in both catalogs")


# ---------------------------------------------------------------- cross-refs

def check_markdown(plugins: list[Path], skills_by_plugin: dict[str, set[str]]) -> None:
    if not skills_by_plugin:
        return
    known = "|".join(re.escape(n) for n in sorted(skills_by_plugin, key=len, reverse=True))
    # `plugin:skill` where plugin is one of ours; skill = kebab token
    ref_re = re.compile(rf"(?<![\w/.-])({known}):([a-z][a-z0-9-]*)")
    md_files = list(REPO_ROOT.glob("*.md")) + list(PLUGINS_DIR.rglob("*.md"))
    for md in sorted(md_files):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        r = rel(md)
        for m in ref_re.finditer(text):
            plugin, skill = m.group(1), m.group(2)
            if text[max(0, m.start() - 5):m.start()] == "<!-- ":
                continue  # an HTML marker comment such as <!-- plugin:block start -->
            if skill not in skills_by_plugin[plugin]:
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{r}:{line}: dangling reference {plugin}:{skill} (no such skill or agent)")


# ---------------------------------------------------------------- public hygiene

def load_hygiene_words() -> tuple[list[str], list[str]]:
    """Return (banned words, allowed phrases), lower-cased, from the optional
    local file and the environment variable."""
    words: list[str] = []
    allowed: list[str] = []
    if HYGIENE_LOCAL_FILE.is_file():
        for raw in HYGIENE_LOCAL_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            if line.lower().startswith("allow:"):
                phrase = line[len("allow:"):].strip()
                if phrase:
                    allowed.append(phrase.lower())
            else:
                words.append(line.lower())
    for w in os.environ.get(HYGIENE_ENV_VAR, "").split(","):
        if w.strip():
            words.append(w.strip().lower())
    return words, allowed


def allowed_spans(low: str, allowed: list[str]) -> list[tuple[int, int]]:
    spans = []
    for phrase in allowed:
        start = low.find(phrase)
        while start >= 0:
            spans.append((start, start + len(phrase)))
            start = low.find(phrase, start + 1)
    return spans


def check_public_hygiene() -> None:
    words, allowed = load_hygiene_words()
    if not words:
        print(f"  note: no local hygiene words ({rel(HYGIENE_LOCAL_FILE)} or {HYGIENE_ENV_VAR}); generic patterns only")
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() in BINARY_SUFFIXES:
            continue
        if set(path.relative_to(REPO_ROOT).parts) & HYGIENE_SKIP_DIRS:
            continue
        r = rel(path)
        if r in HYGIENE_SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        low = text.lower()
        spans = allowed_spans(low, allowed)

        def exempt(s: int, e: int) -> bool:
            return any(a <= s and e <= b for a, b in spans)

        for label, pat in PUBLIC_HYGIENE_PATTERNS:
            for m in pat.finditer(text):
                if exempt(m.start(), m.end()):
                    continue
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{r}:{line}: public-hygiene pattern '{label}' (this repo is public)")
        for w in words:
            start = low.find(w)
            while start >= 0:
                if not exempt(start, start + len(w)):
                    line = text.count("\n", 0, start) + 1
                    # The word itself is not echoed: it is private by definition.
                    errors.append(f"{r}:{line}: public-hygiene word from the local list (this repo is public)")
                start = low.find(w, start + len(w))


# ---------------------------------------------------------------- main

def main() -> None:
    print("Validating marketplace catalogs...")
    load_json(MARKETPLACE_JSON)
    if CODEX_MARKETPLACE_JSON.is_file():
        load_json(CODEX_MARKETPLACE_JSON)
    print()

    plugins = discover_plugins()
    if not plugins:
        print("No plugins found under plugins/.")
    skills_by_plugin: dict[str, set[str]] = {}
    for plugin_dir in plugins:
        skills_by_plugin[plugin_dir.name] = validate_plugin(plugin_dir)

    print("\nChecking catalog coverage, cross-references, public hygiene...")
    check_catalog_coverage(plugins)
    check_markdown(plugins, skills_by_plugin)
    check_public_hygiene()

    print()
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
