#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""inject_para_anchors.py — kaku_raw/ の各ファイルに段落アンカー ¶N を焼き込む。

カクヨム本文の <p id="pN"> は URL アンカー (#pN) になる。kaku_raw の本文行は
抽出時 <p> 1 個 = 1 行（1 段落）で作られているため、行番号 N（先頭行=1）が
そのまま #pN と対応する。このツールは:

  1. 各 kaku_raw ファイルのヘッダに 【段落数 N】 を追記し、
  2. 末尾にアンカー索引ブロックを焼き込む:
       【¶索引】
       ¶1 <先頭12字>
       ¶2 <先頭12字>
       ...
  3. 本文行は変更しない（不変・追記のみ）。

使い方（vault ルートから）:
  PYTHONUTF8=1 python tools/inject_para_anchors.py            # 全ファイル
  PYTHONUTF8=1 python tools/inject_para_anchors.py --check    # dry-run（件数・既存焼き込み確認）
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "..", "AllusionistWiki_raw", "raw", "novel", "kakuyomu",
                       "16816927859268545348_幻想再帰のアリュージョニスト")
INDEX_MARK = "【¶索引】"


def split_body(text: str) -> list:
    """ヘッダ（【…】行と空行）を飛ばし、本文の段落行リストを返す。

    抽出時の形式: 1 段落 = 1 行（段落内 <br> は改行のまま複数行になり得る）。
    段落内改行（行頭が全角スペースでない継続行）は前の段落に吸収する。
    """
    lines = text.split("\n")
    # ヘッダ末尾（最初の空行まで）をスキップ
    i = 0
    while i < len(lines) and (lines[i].startswith("【") or lines[i] == ""):
        i += 1
    paras = []
    for ln in lines[i:]:
        if ln == "":
            continue
        if paras and not ln.startswith("　") and not ln.startswith(" "):
            paras[-1] += "\n" + ln  # 段落内改行の継続行
        else:
            paras.append(ln)
    return paras


def preview(p: str, n: int = 12) -> str:
    t = p.replace("\n", "⏎").strip()
    return t[:n] if t else "（空）"


def process(path: str, check: bool) -> str:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if INDEX_MARK in text:
        return "skip(already)"
    body_start = text.index("\n【") if False else None  # noop
    paras = split_body(text)
    if check:
        return f"paras={len(paras)}"
    # 段落数ヘッダ行を最終ヘッダ行の後に挿入
    lines = text.split("\n")
    last_hdr = 0
    for i, ln in enumerate(lines):
        if ln.startswith("【"):
            last_hdr = i
    lines.insert(last_hdr + 1, f"【段落数 {len(paras)}】")
    # 索引ブロックを末尾に追記
    idx = [INDEX_MARK]
    for n, p in enumerate(paras, 1):
        idx.append(f"¶{n} {preview(p)}")
    out = "\n".join(lines).rstrip("\n") + "\n\n" + "\n".join(idx) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return f"paras={len(paras)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--from", dest="frm", type=int, default=1)
    ap.add_argument("--to", dest="to", type=int, default=10**9)
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(OUT_DIR) if f.endswith(".md"))
    done = skipped = 0
    for fn in files:
        m = re.match(r"ch(\d{5})__", fn)
        if not m:
            continue
        n = int(m.group(1))
        if n < args.frm or n > args.to:
            continue
        r = process(os.path.join(OUT_DIR, fn), args.check)
        if r == "skip(already)":
            skipped += 1
        else:
            done += 1
        if done % 50 == 0 and done:
            print(f"[{'check' if args.check else 'fix'}] {done} files, last {fn}: {r}")
    print(f"[done] mode={'check' if args.check else 'write'} processed={done} skipped={skipped} total={len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
