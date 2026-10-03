# -*- coding: utf-8 -*-
"""scan_raw_mentions.py — raw/ 全話を1話から順次読み、character 名出現の逐話証拠を構築する。

出力 (tools/data/raw_char_mentions.json):
{
  "episodes": ["ch00001", ...],                       # 読み込み順
  "chars": {name: {"eps": [ep...], "counts": {ep: n}, "first": ep, "total": n}},
  "cooc": {"A|B": n}                                  # 同一話共起回数（無向、A<B）
}
- 名前は最長一致（ロウ・カーイン > カーイン）。
- raw 本文は不変（読み取りのみ）。
"""
import os, re, json, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
CHDIR = os.path.join(ROOT, "wiki", "characters")
OUT = os.path.join(ROOT, "tools", "data", "raw_char_mentions.json")

names = sorted(
    f[:-3] for f in os.listdir(CHDIR)
    if f.endswith(".md") and f != "index.md" and os.path.isfile(os.path.join(CHDIR, f))
)
# 別名: 末尾の括弧部を除いた形（raw 側は「クレアノーズ」等が本体表記）
alias = {}
for n in names:
    base = re.sub(r'（[^（）]*）$', '', n)
    if base != n and base not in names:
        alias.setdefault(base, n)
match_names = sorted(set(names) | set(alias.keys()), key=len, reverse=True)
# 名前は最長一致（regex alternation は左→右なので長さ降順）
pat = re.compile("|".join(re.escape(n) for n in match_names))

episodes = sorted(os.path.basename(p) for p in glob.glob(os.path.join(RAW, "ch*.md")))
chars = {n: {"eps": [], "counts": {}, "first": None, "total": 0, "ctx": []} for n in names}
cooc = {}

for i, fn in enumerate(episodes):
    ep = fn.split("__")[0]
    text = open(os.path.join(RAW, fn), encoding="utf-8").read()
    found = {}
    for m in pat.finditer(text):
        key = alias.get(m.group(0), m.group(0))
        found[key] = found.get(key, 0) + 1
        if len(chars[key]["ctx"]) < 3:  # 初出前後の文脈を最大3件保持
            s = max(0, m.start() - 100); e = min(len(text), m.end() + 100)
            chars[key]["ctx"].append(text[s:e].replace("\n", " "))
    for n, c in found.items():
        d = chars[n]
        d["eps"].append(ep)
        d["counts"][ep] = c
        d["total"] += c
        if d["first"] is None:
            d["first"] = ep
    ks = sorted(found)
    for a_i in range(len(ks)):
        for b_i in range(a_i + 1, len(ks)):
            k = ks[a_i] + "|" + ks[b_i]
            cooc[k] = cooc.get(k, 0) + 1
    if (i + 1) % 40 == 0:
        print(f"  scanned {i+1}/{len(episodes)}", file=sys.stderr)

json.dump({"episodes": [f.split('__')[0] for f in episodes], "chars": chars, "cooc": cooc},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("episodes:", len(episodes), "chars:", len(names), "cooc pairs:", len(cooc))
zero = [n for n in names if chars[n]["total"] == 0]
print("zero-mention chars:", len(zero), zero[:10])
