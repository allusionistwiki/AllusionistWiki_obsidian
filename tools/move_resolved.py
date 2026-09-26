#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
move_resolved.py — 回収された謎を Open_Questions.md から Resolved.md へ移動する再利用ヘルパー。

使い方（vaultルートから）：
    $env:PYTHONUTF8=1
    # dry-run（検証のみ・書き込みなし）
    python move_resolved.py --spec _temp/spec_ch008.json --dry-run
    # 適用
    python move_resolved.py --spec _temp/spec_ch008.json

spec JSON の形式（リスト）：
[
  {
    "match": "ゼノグラシアの正体",          // Open_Questions の「謎」セルに一意に含まれる文字列
    "recovery": "第021話／第035話／第043話", // 回収話（解答が示された話数）
    "evidence": "[[episodes/ch021]]（pp.991–996）・…",  // 典拠（wikilink・raw相対リンク可）
    "summary": "解答の概要。→ [[関連ページ]]"           // 概要（事実と解釈は分離）
  },
  ...
]

挙動：
- Open_Questions.md の表行を走査し、match が「謎」セルに**ちょうど1回**含まれる行を探す。
  0件 or 2件以上なら全エントリ検証後にエラー終了（書き込みなし）。
- 該当行を Open_Questions.md から削除し、Resolved.md の表末尾へ
  | 謎 | 初出話 | 回収話 | 典拠 | 概要 | 形式で追記。
- Resolved.md にプレースホルダ行（「Open_Questions.md から回収された謎をここに移動」）があれば削除。
- 最後に Open_Questions の残件数と初出話別の集計（status.md コア層更新用）を表示。
"""
import json
import os
import re
import sys

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # vault root (script in tools/)
OQ_PATH = os.path.join(VAULT, "wiki", "mysteries", "Open_Questions.md")
RS_PATH = os.path.join(VAULT, "wiki", "mysteries", "Resolved.md")
PLACEHOLDER_MARK = "Open_Questions.md から回収された謎をここに移動"


def split_row(line):
    # 表行 "| a | b | c |" -> ["a","b","c"]（両端の空セルを除く）
    body = line.strip()
    if not (body.startswith("|") and body.endswith("|")):
        return None
    cells = [c.strip() for c in body[1:-1].split("|")]
    return cells


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    spec_path = None
    if "--spec" in args:
        i = args.index("--spec")
        spec_path = args[i + 1]
    if not spec_path:
        print("usage: python move_resolved.py --spec <file.json> [--dry-run]")
        sys.exit(2)

    with open(spec_path, "r", encoding="utf-8") as f:
        specs = json.load(f)

    with open(OQ_PATH, "r", encoding="utf-8") as f:
        oq_lines = f.read().splitlines()
    with open(RS_PATH, "r", encoding="utf-8") as f:
        rs_lines = f.read().splitlines()

    # 1) 全エントリのマッチ検証（先に全部確認→失敗時は書き込みなし）
    plan = []  # (spec_idx, line_idx, mystery, first_ep)
    errors = []
    used = set()
    for si, sp in enumerate(specs):
        matches = []
        for li, line in enumerate(oq_lines):
            if li in used:
                continue
            cells = split_row(line)
            if not cells or len(cells) < 5:
                continue
            if cells[0].startswith("謎") or set(cells[0]) <= {"-", " ", ":"}:
                continue  # ヘッダ・区切り行
            if sp["match"] in cells[0]:
                matches.append(li)
        if len(matches) != 1:
            errors.append(f"spec[{si}] match={sp['match']!r} -> {len(matches)} hits")
            continue
        li = matches[0]
        used.add(li)
        cells = split_row(oq_lines[li])
        plan.append((si, li, cells[0], cells[1]))

    if errors:
        print("ERROR (no files written):")
        for e in errors:
            print("  " + e)
        sys.exit(1)

    # 2) Open_Questions から削除
    remove_idx = {li for _, li, _, _ in plan}
    new_oq = [ln for i, ln in enumerate(oq_lines) if i not in remove_idx]

    # 3) Resolved.md に追記（表の最後の行の後）
    last_table_row = max(i for i, ln in enumerate(rs_lines) if ln.strip().startswith("|"))
    new_rows = []
    for si, li, mystery, first_ep in plan:
        sp = specs[si]
        row = f"| {mystery} | {first_ep} | {sp['recovery']} | {sp['evidence']} | {sp['summary']} |"
        new_rows.append(row)
    # プレースホルダ行を削除
    rs_lines = [ln for ln in rs_lines if PLACEHOLDER_MARK not in ln]
    last_table_row = max(i for i, ln in enumerate(rs_lines) if ln.strip().startswith("|"))
    new_rs = rs_lines[: last_table_row + 1] + new_rows + rs_lines[last_table_row + 1:]

    # 4) 集計（status.md コア層更新用）
    counts = {}
    total = 0
    for ln in new_oq:
        cells = split_row(ln)
        if not cells or len(cells) < 5:
            continue
        if cells[0].startswith("謎") or set(cells[0]) <= {"-", " ", ":"}:
            continue
        m = re.search(r"第(\d+)話", cells[1])
        key = f"ch{int(m.group(1)):03d}" if m else cells[1]
        counts[key] = counts.get(key, 0) + 1
        total += 1

    print(f"dry-run={dry} moved={len(plan)} remaining_open={total}")
    ordered = sorted(counts.items(), key=lambda kv: (kv[0].startswith("ch"), kv[0]))
    dist = "/".join(f"{k}×{v}" for k, v in ordered)
    print("distribution: " + dist)

    if not dry:
        with open(OQ_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(new_oq) + "\n")
        with open(RS_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(new_rs) + "\n")
        print("written: Open_Questions.md / Resolved.md")


if __name__ == "__main__":
    main()
