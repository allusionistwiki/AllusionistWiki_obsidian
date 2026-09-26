#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 2/3: Build the definitive chapter boundary table.

Combines the bold-title extraction (step 1) with the syosetu table of contents
to assign each of the 272 episodes a start leaf (0-based PDF page index) and a
page range [leaf_start, leaf_end].

Inputs (relative to this script's directory):
  bold_starts.json    from extract_bold_titles.py
  syosetu_toc.json    the canonical 272-episode TOC (keys: n, t, u)
Output:
  boundaries.json     list of {n, title, url, leaf_start, leaf_end}

A handful of episodes have headings that the automatic matcher cannot pair
with the TOC title (bold text is clipped at ~40 glyphs, half/full-width colon
differences, or the chapter is an embedded spin-off). Those are pinned here in
MANUAL with the verified 0-based leaf.

Run from anywhere:  python build_boundaries.py
"""
import sys, os, re, json, unicodedata
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
STARTS = os.path.join(HERE, "data", "bold_starts.json")
TOC = os.path.join(HERE, "data", "syosetu_toc.json")
OUT = os.path.join(HERE, "data", "boundaries.json")
LAST_LEAF = 8450   # last 0-based page index of the PDF

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[『』「」()（）\[\]{}①-⑩/\s]", "", s)
    return s.lower()

# syosetu ep number -> verified 0-based leaf (auto-match failures)
MANUAL = {
    146: 4968,   # チョコレートリリー Season2 Case.14 アズチョコに挑め！ (embedded in 4-33)
    177: 5865,   # チョコレートリリー 2nd 第14話 デーツ・ミーツ・ナッツ (embedded in 4-60)
    232: 7648,   # 五章キャラ一覧（暫定） (inside 5-29)
    26:  1162,   # 2-19 サイバネティクスとオカルティズムの幸福なマリアージュ (bold clipped)
    90:  3316,   # 4-12 Tournamented Celestial Gaze（the second volume） (bold clipped)
    186: 6170,   # 終節：序『The Orb Is a Harsh Mistress』 (bold clipped + half-width colon)
    191: 6290,   # 終節：救『Parable of The Barren Fig Blade』 (bold clipped)
    194: 6440,   # 終節：窮『Put My Finger Only On Your Cheek』 (bold clipped)
}

def main():
    starts = json.load(open(STARTS, encoding="utf-8"))
    toc = json.load(open(TOC, encoding="utf-8"))

    # index bold titles: normalized(main, minus 前書き/後書き) -> [leaf, ...]
    from collections import defaultdict
    idx = defaultdict(list)
    for li, t in starts:
        tt = re.sub(r"\(?(前書き|後書き)\)?$", "", t)   # drop appendix variant
        idx[norm(tt)].append(li)

    resolved, unmatched = {}, []
    for e in toc:
        n = int(e["n"])
        if n in MANUAL:
            resolved[n] = MANUAL[n]
            continue
        cand = idx.get(norm(e["t"]), [])
        if cand:
            resolved[n] = cand[0]
        else:
            unmatched.append((n, e["t"]))

    print(f"resolved: {len(resolved)}/{len(toc)}")
    if unmatched:
        print("UNMATCHED:")
        for n, t in unmatched:
            print(f"  ch{n}: {t}")

    rows = sorted(resolved.items(), key=lambda kv: kv[1])
    mono = all(rows[i][1] < rows[i + 1][1] for i in range(len(rows) - 1))
    print(f"monotonic leaves: {mono}")

    out = []
    for i, (n, leaf) in enumerate(rows):
        end = rows[i + 1][1] - 1 if i + 1 < len(rows) else LAST_LEAF
        e = next(x for x in toc if int(x["n"]) == n)
        out.append({"n": n, "title": e["t"], "url": e["u"],
                    "leaf_start": leaf, "leaf_end": end})

    gaps = [(out[i]["n"], out[i]["leaf_end"], out[i + 1]["n"], out[i + 1]["leaf_start"])
            for i in range(len(out) - 1) if out[i]["leaf_end"] + 1 != out[i + 1]["leaf_start"]]
    print(f"coverage gaps: {gaps}")
    print(f"first: leaf {out[0]['leaf_start']} ({out[0]['title'][:20]})")
    print(f"last:  leaf {out[-1]['leaf_end']} ({out[-1]['title'][:20]})")

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"saved {os.path.relpath(OUT, HERE)}")

if __name__ == "__main__":
    main()
