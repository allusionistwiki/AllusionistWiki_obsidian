# -*- coding: utf-8 -*-
"""scan_raw_sentences.py — raw/ を ch00001 から順次読み、character 名が現れる**文**だけを
抽出するローケーター（分類判断は行わない。判断は人が原文文を読んで行う）。

出力: tools/data/raw_char_sentences.json
{
  "episodes": ["ch00001", ...],
  "sentences": {ep: [ {"chars": [正式ページ名..], "text": "原文文"}, ... ]}
}
抽出条件（いずれか）:
  - 文内に character 名が2つ以上
  - 文内に character 名1つ以上 ＋ 所属・関係を示す語
  - その character の初出文（各話で初出現時、1件）
- 名前は最長一致（ロウ・カーイン > カーイン）。
- 別名: 末尾括弧部（品森晶（アキラ）→ アキラ）と括弧前（タマ（白黒兎）→ タマ）。
- raw 本文は読み取りのみ（不変）。

使い方: PYTHONUTF8=1 python tools/scan_raw_sentences.py
"""
import os, re, json, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # vault root
RAW = os.path.join(ROOT, "raw")
CHDIR = os.path.join(ROOT, "wiki", "characters")
OUT = os.path.join(ROOT, "tools", "data", "raw_char_sentences.json")

REL_WORDS = [
    "の部下","の一員","配下","に従う","に仕える","に属する","に組み入れ","所属",
    "血族","血筋","家系","一族","家督","騎士団","団員","隊長","総団長","団長",
    "弟子","師匠","護衛","仲間","味方","盟友","宿敵","同期","眷属","使徒",
    "軍勢","評議会","十二賢者","四姉妹","六王","九姉","魔将","首領","教主","大公",
    "王の","王妃","王子","姫","女王","直属","結社","教団","家門","派閥","陣営","勢力",
    "名を","自称","異名","二つ名","序列","席","呼ば","呼び","正体","真の","本物",
]

def main():
    names = sorted(
        f[:-3] for f in os.listdir(CHDIR)
        if f.endswith(".md") and f != "index.md" and os.path.isfile(os.path.join(CHDIR, f))
    )
    alias = {}
    for n in names:
        m = re.match(r'^(.+)（([^（）]+)）$', n)
        if m:
            for a in (m.group(1), m.group(2)):
                if a != n and a not in names:
                    alias.setdefault(a, n)
    match_names = sorted(set(names) | set(alias.keys()), key=len, reverse=True)
    pat = re.compile("|".join(re.escape(n) for n in match_names))
    rel_pat = re.compile("|".join(REL_WORDS))

    files = sorted(glob.glob(os.path.join(RAW, "ch*.md")))
    episodes, sentences = [], {}
    seen = set()
    total = 0

    for i, fp in enumerate(files):
        ep = os.path.basename(fp).split("__")[0]
        episodes.append(ep)
        text = open(fp, encoding="utf-8").read()
        rows = []
        for sent in re.split(r'(?<=[。！？\n])', text):
            s = sent.strip()
            if len(s) < 6:
                continue
            found = []
            for m in pat.finditer(s):
                key = alias.get(m.group(0), m.group(0))
                if key not in found:
                    found.append(key)
            if not found:
                continue
            first_sents = [c for c in found if c not in seen]
            for c in found:
                seen.add(c)
            if len(found) >= 2 or rel_pat.search(s) or first_sents:
                rows.append({"chars": found, "text": s[:240]})
        sentences[ep] = rows
        total += len(rows)
        if (i + 1) % 40 == 0:
            print(f"  scanned {i+1}/{len(files)}", file=sys.stderr)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"episodes": episodes, "sentences": sentences},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print("episodes:", len(episodes), "sentences extracted:", total)

if __name__ == "__main__":
    main()
