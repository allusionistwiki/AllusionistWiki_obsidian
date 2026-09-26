#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1/3: Extract bold vertical chapter titles from the source PDF.

The novel's chapter headings are rendered as BOLD vertical text on the right
margin of the opening page of each chapter. We detect them by grouping bold
spans into vertical columns (rounded X) and keeping the topmost qualifying
column per page.

Input : ../gensousaiki.pdf   (relative to this script's directory)
Output: bold_starts.json     (list of [leaf_index, title] pairs, 0-based leaf)

Requires: pymupdf  (pip install pymupdf)
Run from anywhere:  python extract_bold_titles.py
"""
import sys, os, re, json, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))          # .../tools
VAULT = os.path.dirname(HERE)                              # vault root
CODE  = os.path.dirname(VAULT)                             # parent holding the PDF
PDF = os.path.normpath(os.path.join(CODE, "gensousaiki.pdf"))
OUT = os.path.join(HERE, "data", "bold_starts.json")

import pymupdf

# a chapter heading mentions one of these structural markers
TITLE_PAT = re.compile(
    r'(断章|幕間|第.{1,3}章|\d+[-－]\d+|アポテオーズ|祝祭前夜|終節|転章|取義|イベント|の左手|の右手)'
)

def norm(s):
    return unicodedata.normalize('NFKC', s)

def main():
    doc = pymupdf.open(PDF)
    starts = []
    for li in range(doc.page_count):
        d = doc[li].get_text("dict")
        # group bold spans into vertical columns by rounded X
        cols = {}
        for blk in d["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln.get("spans", []):
                    if (sp["flags"] & 16) == 0:      # keep bold only
                        continue
                    x = round(sp["bbox"][0])
                    cols.setdefault(x, []).append(sp)
        best = None
        for x, spans in cols.items():
            spans = sorted(spans, key=lambda s: s["bbox"][1])   # top -> bottom
            txt = "".join(sp["text"] for sp in spans)
            t = norm(txt).strip()
            if not t:
                continue
            if TITLE_PAT.search(t) and 3 < len(t) < 45:
                ytop = min(s["bbox"][1] for s in spans)
                if best is None or ytop < best[0]:
                    best = (ytop, t)
        if best:
            starts.append([li, best[1]])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(starts, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"bold-title candidates: {len(starts)}")
    print(f"saved {os.path.relpath(OUT, HERE)}")

if __name__ == "__main__":
    main()
