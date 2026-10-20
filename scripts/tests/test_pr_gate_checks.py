"""Regression tests for scripts/pr_gate_checks.py (Wiki1 production rules):
  1. rename content/x -> protected path must FAIL (--no-renames)
  2. attacker-controlled file names must NOT execute (list-arg git, no shell)
  3. mass deletion heuristic (floor 500) FAILs
  4. plain appends must PASS (no false positives)
  5. XSS patterns in .md under content/reports/ FAIL
  6. llm-task edits of vault-rebuilt pages = PASS with warning (owner policy
     2026-10-19: full auto-merge with post-merge audit as safety wall)
Note: gate prints verdict on a line starting with "PASS"/"FAIL <reasons>".
"""
import pathlib
import subprocess
import sys

GATE = str(pathlib.Path(__file__).resolve().parents[1] / "pr_gate_checks.py")


def git(repo, *args):
    r = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.stderr[:200]}"
    return r.stdout.strip()


def make_repo(tmp):
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    content = repo / "content"
    content.mkdir()
    (content / "a.md").write_text(
        "\n".join(f"line {i} https://example.com/keep{i}" for i in range(600))
        + "\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    return repo


def commit_change(repo):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "change")
    return git(repo, "rev-parse", "HEAD")


def run_gate(repo, base, head, mode=None):
    args = [sys.executable, GATE, base, head] + ([mode] if mode else [])
    r = subprocess.run(
        args,
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = r.stdout
    verdict = None
    reasons = ""
    for l in out.splitlines():
        if l.startswith("PASS"):
            verdict = "PASS"
        elif l.startswith("FAIL"):
            verdict = "FAIL"
            reasons = l
    return verdict, reasons, out + r.stderr


def test_rename_to_protected_fails(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    (repo / "quartz").mkdir()
    (repo / "quartz" / "evil.md").write_text("evil\n", encoding="utf-8")
    (repo / "content" / "a.md").unlink()
    head = commit_change(repo)
    verdict, reasons, _ = run_gate(repo, base, head)
    assert verdict == "FAIL"
    assert "quartz" in reasons


def test_pwned_filename_does_not_execute(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    evil = repo / "content" / "$(touch PWNED_BY_PATH).md"
    evil.write_text("hello\n", encoding="utf-8")
    (repo / "content" / "a.md").write_text(
        (repo / "content" / "a.md").read_text(encoding="utf-8") + "append\n",
        encoding="utf-8",
    )
    head = commit_change(repo)
    verdict, reasons, out = run_gate(repo, base, head)
    assert verdict == "PASS", reasons
    side_effects = list(repo.rglob("PWNED_BY_PATH"))
    assert side_effects == [], f"shell injection side effects: {side_effects}"


def test_mass_deletion_fails(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    (repo / "content" / "a.md").write_text("core\n", encoding="utf-8")
    head = commit_change(repo)
    verdict, reasons, _ = run_gate(repo, base, head)
    assert verdict == "FAIL" and "mass deletion" in reasons


def test_plain_append_passes(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    p = repo / "content" / "a.md"
    text = p.read_text(encoding="utf-8")
    p.write_text(text + "append: see https://example.com/keep0 (unchanged)\n", encoding="utf-8")
    head = commit_change(repo)
    verdict, reasons, _ = run_gate(repo, base, head)
    assert verdict == "PASS", reasons


def test_xss_in_reports_fails(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    rdir = repo / "content" / "reports"
    rdir.mkdir(parents=True)
    (rdir / "evil.md").write_text("ok\n<script>alert(1)</script>\n", encoding="utf-8")
    head = commit_change(repo)
    verdict, reasons, _ = run_gate(repo, base, head)
    assert verdict == "FAIL" and "XSS" in reasons


def test_llm_task_vault_page_edit_passes_with_warning(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    adir = repo / "content" / "allusions"
    adir.mkdir(parents=True)
    (adir / "note.md").write_text("Gogmagog 仮説\n", encoding="utf-8")
    head = commit_change(repo)
    verdict, reasons, out = run_gate(repo, base, head, mode="llm-task")
    assert verdict == "PASS", reasons
    assert "::warning::" in out and "allusions" in out


def test_llm_task_reports_edit_passes(tmp_path):
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    rdir = repo / "content" / "reports"
    rdir.mkdir(parents=True)
    (rdir / "new-note.md").write_text("report note\n", encoding="utf-8")
    head = commit_change(repo)
    verdict, reasons, out = run_gate(repo, base, head, mode="llm-task")
    assert verdict == "PASS", reasons
