#!/usr/bin/env python3
"""
inject_dates.py — wiki/ の各 .md に created/modified を frontmatter として注入する。

- created  = 初出コミット日時（git log --follow でリネーム追跡）
- modified = 最終修正コミット日時
- 既存 frontmatter がある場合はそのブロック内に追加、なければファイル先頭に新規作成
- 既存の created/modified は上書きしない（--force で上書き）
- 日付は YYYY-MM-DD（JST）

使い方:
  python inject_dates.py            # dry-run（変更せず要約のみ）
  python inject_dates.py --apply    # 実際に書き込み
"""
import subprocess
import sys
import os
import re
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # vault root (script in _temp/)
WIKI = os.path.join(ROOT, "wiki")
JST = timezone(timedelta(hours=9))

def git_dates(path):
    """Return (created, modified) as 'YYYY-MM-DD' or (None, None)."""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%aI", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=60
        ).stdout.strip().splitlines()
        if not out:
            return None, None
        def to_jst(iso):
            dt = datetime.fromisoformat(iso)
            return dt.astimezone(JST).strftime("%Y-%m-%d")
        modified = to_jst(out[0])   # newest
        created = to_jst(out[-1])   # oldest
        return created, modified
    except Exception as e:
        print(f"  ERROR {path}: {e}", file=sys.stderr)
        return None, None

def inject(content, created, modified, force=False):
    """Return (new_content, action). action in {'create','update','skip'}."""
    lines = content.split("\n")

    has_fm = False
    fm_end = -1
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                has_fm = True
                fm_end = i
                break

    if has_fm:
        fm_block = lines[1:fm_end]
        has_created = any(re.match(r"^created\s*:", l) for l in fm_block)
        has_modified = any(re.match(r"^modified\s*:", l) for l in fm_block)
        if not force and has_created and has_modified:
            return content, "skip"
        new_block = []
        for l in fm_block:
            if re.match(r"^created\s*:", l) and created:
                new_block.append(f"created: {created}")
            elif re.match(r"^modified\s*:", l) and modified:
                new_block.append(f"modified: {modified}")
            else:
                new_block.append(l)
        if created and not any(re.match(r"^created\s*:", l) for l in new_block):
            new_block.append(f"created: {created}")
        if modified and not any(re.match(r"^modified\s*:", l) for l in new_block):
            new_block.append(f"modified: {modified}")
        lines = [lines[0]] + new_block + lines[fm_end:]
        return "\n".join(lines), "update"
    else:
        fm = ["---"]
        if created:
            fm.append(f"created: {created}")
        if modified:
            fm.append(f"modified: {modified}")
        fm.append("---")
        fm.append("")
        return "\n".join(fm + lines), "create"

def main():
    apply = "--apply" in sys.argv
    force = "--force" in sys.argv

    files = []
    for dirpath, dirnames, filenames in os.walk(WIKI):
        for fn in filenames:
            if fn.endswith(".md"):
                files.append(os.path.join(dirpath, fn))
    files.sort()

    stats = {"create": 0, "update": 0, "skip": 0, "error": 0}
    for i, path in enumerate(files):
        rel = os.path.relpath(path, ROOT)
        created, modified = git_dates(rel)
        if not created and not modified:
            stats["error"] += 1
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        new_content, action = inject(content, created, modified, force)
        stats[action] += 1
        if apply and action in ("create", "update"):
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
        if (i + 1) % 200 == 0:
            print(f"  processed {i+1}/{len(files)}...", file=sys.stderr)

    print(f"\nTotal: {len(files)} files")
    print(f"  create (new frontmatter): {stats['create']}")
    print(f"  update (existing fm):     {stats['update']}")
    print(f"  skip (already has both):  {stats['skip']}")
    print(f"  error:                    {stats['error']}")
    if not apply:
        print("\n[DRY-RUN] No files modified. Use --apply to write.")

if __name__ == "__main__":
    main()
