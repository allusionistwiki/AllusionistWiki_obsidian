#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 3/3: Generate RAW2/chNNN__タイトル.md files DIRECTLY from the source PDF.

Pipeline (all relative to this script's directory):
  1. extract_bold_titles.py  -> bold_starts.json
  2. build_boundaries.py     -> boundaries.json   (272 episodes, 0-based leaf ranges)
  3. make_raw_from_pdf.py    -> RAW2/chNNN__タイトル.md   (this script)

Source of truth:
  PDF : ../gensousaiki.pdf
  Chapter boundaries: boundaries.json
      (272 syosetu episodes, each with 0-based leaf_start / leaf_end,
       derived from the PDF's bold vertical chapter titles)

Output format (matches existing raw/ convention, CLAUDE.md §2/§4):
    【p{leaf}】
    {printed page number line}
    {chapter body text}
    【p{leaf+1}】
    ...
  where  leaf = 0-based_index + 1  (i.e. 【p4】 for 0-based index 3,
  printed page 3).  The first line of pypdf's extract_text() is the
  printed page number, so it is emitted verbatim after the header.

Naming:  chNNN__タイトル.md   (NNN = syosetu episode number, 3-digit padded)
         DOUBLE underscore separates the number from the title, distinct
         from the old raw/NNN_タイトル.md page-chunk files.

Usage:
    python make_raw_from_pdf.py [--outdir RAW2]
      --outdir  destination folder (default: RAW2, relative to this script)

Requires: pypdf  (pip install pypdf)
"""
import sys, os, re, json, argparse
sys.stdout.reconfigure(encoding='utf-8')
from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))          # .../tools
VAULT = os.path.dirname(HERE)                              # vault root
CODE  = os.path.dirname(VAULT)                             # parent holding the PDF
PDF = os.path.normpath(os.path.join(CODE, "gensousaiki.pdf"))
BOUNDS = os.path.join(HERE, "boundaries.json")

# Windows-illegal filename chars -> full-width equivalents (keep title readable)
_ILLEGAL = {'\\': '＼', '/': '／', ':': '：', '*': '＊', '?': '？',
            '"': '”', '<': '＜', '>': '＞', '|': '｜'}

def safe_title(t):
    t = t.replace('\n', ' ')
    for bad, good in _ILLEGAL.items():
        t = t.replace(bad, good)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--outdir', default=os.path.join(VAULT, 'RAW2'))
    args = ap.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    bounds = json.load(open(BOUNDS, encoding='utf-8'))
    reader = PdfReader(PDF)
    npages = len(reader.pages)
    print(f"PDF pages: {npages}   chapters: {len(bounds)}   outdir: {os.path.relpath(outdir, HERE)}")

    written = 0
    skipped_empty = []
    cache = {}
    def page_text(i):
        if i not in cache:
            cache[i] = (reader.pages[i].extract_text() or '').rstrip('\n')
        return cache[i]

    for b in bounds:
        n = b['n']
        ls = b['leaf_start']
        le = min(b['leaf_end'], npages - 1)   # clamp to last valid 0-based index
        fname = f"ch{n:03d}__{safe_title(b['title'])}.md"
        path = os.path.join(outdir, fname)

        parts = []
        for i in range(ls, le + 1):
            txt = page_text(i)
            parts.append(f"【p{i+1}】\n{txt}")
        body = '\n'.join(parts) + '\n'

        if not body.strip():
            skipped_empty.append(fname)
            continue
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(body)
        written += 1

    print(f"written: {written}")
    if skipped_empty:
        print(f"skipped (empty): {skipped_empty}")
    print(f"files in {os.path.basename(outdir)}: {len([f for f in os.listdir(outdir) if f.endswith('.md')])}")

if __name__ == '__main__':
    main()
