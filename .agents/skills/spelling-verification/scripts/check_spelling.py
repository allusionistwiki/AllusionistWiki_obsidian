# -*- coding: utf-8 -*-
"""
綴り間違い検査スクリプト（コードポイントレベル）
==============================================

目的：「見た目は同じだがコードポイントのみ異なる」日本語文字の混入を検出する。
      目視では発見不可で、最終確認見落としやすい誤りを自動で洗い出す。

代表例（本作で頻発）：
  - ア U+30AD (a)  vs  ア U+30AF (ku)   → 「アキラ」vs「アクラ」
  - る U+308B (小) vs  る U+308D (大)   → 「きぐみ魔女」の small-る
  - ュ U+30E5 (小) vs  ユ U+30F5 (大)   → イュレイド の small-ユ
  - ォ U+30C7 (小) vs  オ U+30F7 (大)   → イェレイド の small-オ
  - ー U+30FC (全) vs  ﾠ U+FF70 (半)    → 半角/全角長音

使用法：
  python check_spelling.py [パス ...]                 # 既定は再帰探索（省略時は cwd）
  python check_spelling.py --json                     # 構造化出力（別ツール連携用）

留意点：
  - PowerShell の Python は標準出力が cp932 のことがある。日本語出力エラー時は
    $env:PYTHONIOENCODING="utf-8" を設定すること。報告はコードポイント主体で行う。
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── 疑義ある文字のグループ（見た目が同じ・コードポイントのみ異なる）──────────
CONFUSABLE_GROUPS = [
    {
        "label": "ア (a vs ku)",
        "look": "ア",
        "points": {"0x30AD": "ア a（例：アキラ）", "0x30AF": "ア ku（例：アクラ）"},
    },
    {
        "label": "る (小 vs 大)",
        "look": "る",
        "points": {"0x308B": "る 小文字", "0x308D": "る 大文字"},
    },
    {
        "label": "ユ (小 vs 大)",
        "look": "ユ",
        "points": {"0x30E5": "ユ 小文字", "0x30F5": "ユ 大文字"},
    },
    {
        "label": "オ (小 vs 大)",
        "look": "オ",
        "points": {"0x30C7": "オ 小文字", "0x30F7": "オ 大文字"},
    },
    {
        "label": "長音符号",
        "look": "ー",
        "points": {"0x30FC": "ー 全角", "0xFF70": "ｰ 半角（長音符）"},
    },
]

# ── 対象拡張子 ──────────────────────────────────────────────────────────────
EXTENSIONS = {".md"}


def iter_files(paths):
    for base in paths:
        p = Path(base)
        if p.is_file():
            yield p
        elif p.is_dir():
            for cur, _dirs, files in os.walk(p):
                for fn in files:
                    if Path(fn).suffix in EXTENSIONS:
                        yield Path(cur) / fn


def read_text(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def hex_cp(ch):
    return "0x%04X" % ord(ch)


def look_of(cp_hex):
    for g in CONFUSABLE_GROUPS:
        if cp_hex in g["points"]:
            return g["look"]
    return "?"


def _iter_codepoints(text, codepoint):
    lineno = 1
    col = 1
    for ch in text:
        if ord(ch) == codepoint:
            yield (lineno, col, ch)
        if ch == "\n":
            lineno += 1
            col = 1
        else:
            col += 1


def scan(text, groups):
    """テキスト内の疑义文字を、コードポイントごとに集計して返す。
    戻り値: (lineno, col, char) のリスト
    """
    hits = []
    for g in groups:
        for ch_hex, _desc in g["points"].items():
            codepoint = int(ch_hex, 16)
            hits.extend(_iter_codepoints(text, codepoint))
    return hits


def main():
    ap = argparse.ArgumentParser(description="綴り間違い（コードポイント）検査")
    ap.add_argument("paths", nargs="*", default=["."], help="検査対象のファイル/ディレクトリ")
    ap.add_argument("--json", action="store_true", help="構造化出力")
    args = ap.parse_args()

    paths = args.paths or ["."]
    files = list(iter_files(paths))

    results = []
    for fp in files:
        text = read_text(fp)
        hits = scan(text, CONFUSABLE_GROUPS)
        if not hits:
            continue
        # (行, 列) ごとに出現したコードポイントを記録
        by_pos = {}
        for lineno, col, ch in hits:
            cp = hex_cp(ch)
            by_pos.setdefault((lineno, col), []).append(cp)
        results.append({"file": str(fp), "lines": len(text.splitlines()), "occurrences": by_pos})

    if args.json:
        print(json.dumps(results, ensure_ascii=False))
        return 0

    total = sum(len(r["occurrences"]) for r in results)
    if not total:
        print("疑義ある文字は見つかりませんでした。")
        return 0

    # ── 人間向け報告（コードポイント優先、日本語は最小限）──────────────────────
    print("【綴り検査】疑義文字の出現をコードポイントで報告します\n")
    for r in sorted(results, key=lambda x: x["file"]):
        occ = r["occurrences"]
        counts = {}
        for _pos, cps in occ.items():
            for c in cps:
                counts[c] = counts.get(c, 0) + 1
        cp_str = ", ".join("%s x%d" % (c, counts[c]) for c in sorted(counts))
        print("%s  (%d行, %d件)  [%s]" % (r["file"], r["lines"], len(occ), cp_str))

    # ── 同一ファイル内でコードポイントが分裂している項目を強調────────────────
    print("\n【要注意】同一ファイル内で見た目が同じ文字が複数コードポイントで出現:")
    flagged = False
    for r in results:
        cps_in_file = {}
        for _pos, cps in r["occurrences"].items():
            for c in cps:
                cps_in_file.setdefault(c, 0)
                cps_in_file[c] += 1
        if len(cps_in_file) > 1:
            flagged = True
            detail = ", ".join("%s(0x..%s) x%d" % (look_of(c), c[2:], n)
                               for c, n in sorted(cps_in_file.items()))
            print("  %s : %s" % (r["file"], detail))
    if not flagged:
        print("  なし（各ファイルで統一されています）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
