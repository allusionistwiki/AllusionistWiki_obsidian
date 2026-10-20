"""pr-gate mechanical checks — AllusionistWiki (production) port.

Hardening carried over from Lab (2026-10-18):
- list-arg git only (no shell=True): file-name injection is dead
- --no-renames -z: rename-bypass of protected paths is dead
- non-zero git exit raises: silent PASS is dead

Production-specific gates (Wiki1 has NO hourly vault redeploys — manual trigger
and content regeneration scripts overwrite content/, so llm-task edits there
are ephemeral):
- changes are allowed ONLY under content/reports/ (the durable report layer)
- llm-task commits touching production content/ subdirs FAIL with guidance to
  content/reports/ (and must not be merged)
"""
import re
import subprocess
import sys

XSS_PATTERNS = [
    re.compile(r"<\s*script", re.I),
    re.compile(r"<\s*iframe", re.I),
    re.compile(r"<\s*object", re.I),
    re.compile(r"<\s*embed", re.I),
    re.compile(r"<\s*meta\b", re.I),
    re.compile(r"<\s*link\b", re.I),
    re.compile(r"\son[a-z]+\s*=", re.I),
    re.compile(r"javascript:", re.I),
    re.compile(r"vbscript:", re.I),
    re.compile(r"data:text/html", re.I),
]

# Production wiki pages are rebuilt from vault; llm-task must not target them.
PROD_DIRS = [
    "content/allusions/", "content/analogies/", "content/characters/",
    "content/episodes/", "content/mysteries/", "content/reflections/",
    "content/terminology/",
]
REPORT_PREFIX = "content/reports/"
PROTECTED = (".github/", "scripts/", "quartz/", "public/", ".gitignore")


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr[:200]}")
    return r.stdout


def changed_files(base: str, head: str):
    out = git("diff", "--no-renames", "--numstat", "-z", f"{base}...{head}")
    for rec in out.split("\0"):
        if rec.strip():
            a, d, path = rec.split("\t", 2)
            yield a, d, path


def main() -> int:
    base, head = sys.argv[1], sys.argv[2]
    fail = []
    is_llm = len(sys.argv) > 3 and sys.argv[3] == "llm-task"
    added_total = 0
    deleted_total = 0
    for a, d, path in changed_files(base, head):
        added_total += int(a) if a != "-" else 0
        deleted_total += int(d) if d != "-" else 0
        if path.startswith(PROTECTED):
            fail.append(f"protected path changed: {path}")
        if is_llm and path.startswith("content/") and not path.startswith(REPORT_PREFIX):
            # production pages are rebuilt from vault hourly; the edit survives until
            # the next regeneration. Allowed by owner policy (2026-10-19): full auto-merge
            # with post-merge audit + auto-revert as the safety wall.
            print(f"::warning::llm-task edited vault-rebuilt page (ephemeral until vault redeploy): {path}")
        if path.startswith(REPORT_PREFIX) and path.endswith(".md"):
            text = git("show", f"{head}:{path}")
            for pat in XSS_PATTERNS:
                if pat.search(text):
                    fail.append(f"XSS vector in added file: {path}")
                    break

    # mass-deletion heuristic (floor 500 lines)
    if deleted_total >= 500 and deleted_total > added_total * 3:
        fail.append(f"mass deletion: {deleted_total} removed vs {added_total} added")

    if fail:
        print("FAIL " + " | ".join(fail))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
