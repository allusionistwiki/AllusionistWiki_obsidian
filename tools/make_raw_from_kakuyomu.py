#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""make_raw_from_kakuyomu.py — カクヨム連載『幻想再帰のアリュージョニスト』の原文を kaku_raw/ に抽出する。

使い方（vault ルトから）:
  PYTHONUTF8=1 python tools/make_raw_from_kakuyomu.py            # 全話（既存はスキップ・再開可能）
  PYTHONUTF8=1 python tools/make_raw_from_kakuyomu.py --toc-only # 目次 JSON の更新のみ
  PYTHONUTF8=1 python tools/make_raw_from_kakuyomu.py --from 1 --to 50
  PYTHONUTF8=1 python tools/make_raw_from_kakuyomu.py --force    # 既存ファイルも再取得

設計:
  * 目次は作品ページの __NEXT_DATA__（Apollo state の tableOfContentsV2）から取得し、
    publishedAt 昇順（＝カクヨムの公開順＝読む順）で chNNNNN に採番する。
  * 本文は各エピソードページの <div id="a-episodeBody"> 内の <p> を 1 行 1 段落で保存。
  * 出力: kaku_raw/chNNNNN__<タイトル>.md（raw/ と同じく非公開・gitignore 対象）
  * 目次スナップショット: tools/data/kaku_toc.json
  * レート制限: リクエスト間 sleep（既定 1.2 秒）。
"""
import argparse
import html as htmlmod
import json
import os
import re
import sys
import time
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
WORK_ID = "16816927859268545348"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "kaku_raw")
TOC_JSON = os.path.join(ROOT, "tools", "data", "kaku_toc.json")


def fetch(url: str, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + 3 * i)
    raise RuntimeError(f"fetch failed: {url}: {last}")


def get_toc() -> list:
    """作品ページから目次（公開順の episode リスト）を抽出する。"""
    page = fetch(f"https://kakuyomu.jp/works/{WORK_ID}")
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        page, re.S)
    if not m:
        raise RuntimeError("__NEXT_DATA__ not found in work page")
    ap = json.loads(m.group(1))["props"]["pageProps"]["__APOLLO_STATE__"]

    def deref(x):
        if isinstance(x, dict) and "__ref" in x and len(x) == 1:
            return ap.get(x["__ref"], x)
        return x

    work = ap[f"Work:{WORK_ID}"]
    eps = []
    for ref in work["tableOfContentsV2"]:
        ch = deref(ref)
        meta = deref(ch.get("chapter"))
        ch_title = (meta.get("title") or "").strip() if isinstance(meta, dict) else ""
        for eref in ch.get("episodeUnions") or []:
            e = deref(eref)
            eps.append({
                "id": e.get("id"),
                "title": e.get("title") or "",
                "publishedAt": e.get("publishedAt") or "",
                "chapterTitle": ch_title,
            })
    eps.sort(key=lambda e: e["publishedAt"])
    for i, e in enumerate(eps, 1):
        e["n"] = i
    os.makedirs(os.path.dirname(TOC_JSON), exist_ok=True)
    with open(TOC_JSON, "w", encoding="utf-8") as f:
        json.dump(eps, f, ensure_ascii=False, indent=1)
    return eps


TAG_RE = re.compile(r"<[^>]+>")
IMG_RE = re.compile(r"<img\b[^>]*src=\"([^\"]+)\"[^>]*>")
P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S)


def extract_body(page: str) -> list:
    """a-episodeBody div 内の <p> を 1 段落 1 行のリストで返す。"""
    m = re.search(r'<div[^>]*class="[^"]*js-episode-body[^"]*"[^>]*>', page)
    if not m:
        raise RuntimeError("episode body div not found")
    # div のネストを追跡して閉じ位置を特定
    seg_start = m.end()
    depth = 1
    pos = seg_start
    while depth > 0:
        nxt = re.search(r"<(/?)div\b", page[pos:])
        if not nxt:
            raise RuntimeError("episode body div not closed")
        depth += -1 if nxt.group(1) == "/" else 1
        pos = pos + nxt.end()
    seg = page[seg_start:pos]

    lines = []
    for pm in P_RE.finditer(seg):
        raw = pm.group(1)
        # 画像は [IMAGE: url] プレースホルダへ
        raw = IMG_RE.sub(lambda mm: f"[IMAGE: {htmlmod.unescape(mm.group(1))}]", raw)
        # <br> は段落内改行 → 改行のまま
        raw = re.sub(r"<br\s*/?>", "\n", raw)
        txt = htmlmod.unescape(TAG_RE.sub("", raw))
        txt = txt.replace("\r\n", "\n")
        lines.append(txt)
    # 末尾の連続空行を整理
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def sanitize_title(title: str) -> str:
    t = title.strip().strip("\u3000").strip()
    t = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "／", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t or "無題"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--toc-only", action="store_true")
    ap.add_argument("--from", dest="frm", type=int, default=1)
    ap.add_argument("--to", dest="to", type=int, default=10**9)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--sleep", type=float, default=1.2)
    args = ap.parse_args()

    eps = get_toc()
    print(f"[toc] {len(eps)} episodes -> {TOC_JSON}")
    if args.toc_only:
        return 0

    os.makedirs(OUT_DIR, exist_ok=True)
    made = skipped = 0
    for e in eps:
        n = e["n"]
        if n < args.frm or n > args.to:
            continue
        fname = f"ch{n:05d}__{sanitize_title(e['title'])}.md"
        path = os.path.join(OUT_DIR, fname)
        if os.path.exists(path) and not args.force:
            skipped += 1
            continue
        url = f"https://kakuyomu.jp/works/{WORK_ID}/episodes/{e['id']}"
        page = fetch(url)
        paras = extract_body(page)
        header = [
            f"【kakuyomu ep{e['id']}】",
            f"【公開 {e['publishedAt']}】",
            f"【章 {e['chapterTitle']}】" if e["chapterTitle"] else "【章 （なし）】",
            f"【URL {url}】",
            "",
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(header + paras) + "\n")
        made += 1
        if made % 10 == 0:
            print(f"[fetch] {n}/{len(eps)}: {fname} ({len(paras)} paras)")
        time.sleep(args.sleep)
    print(f"[done] made={made} skipped={skipped} total={len(eps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
