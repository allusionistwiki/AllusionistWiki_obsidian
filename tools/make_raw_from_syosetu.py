#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""make_raw_from_syosetu.py — なろう（ncode.syosetu.com）小説を raw 相当テキストで保存する。

- 作品表紙 /{ncode}/ から全話リンク（1..N）を取り、各話ページ /{ncode}/{n}/ を取得
- 本文は <div id="wrap"> 内（<div class="ns"> 区切り）。段落ごとに1行
- 段落通し番号 ¶ は「空行を含んだ行数」ではなく本文の行番号（1..P）とし、
  ヘッダに【段落数 P】、末尾に【¶索引】（¶N 先頭14字）を焼き込む
- 保存: syosetu_raw/<ncode小文字>_<小説名>/ch{NNNNN}_<タイトル>[_NN].md（分割は 250行超）
- 保存済み（同一話・同一段落数）はスキップ。--force で再生成
- 取得間隔 2.5 秒（なろうへの負荷配慮）

使い方:
  python tools/make_raw_from_syosetu.py n9073ca            # 全話
  python tools/make_raw_from_syosetu.py n9073ca --start 1 --end 50
  python tools/make_raw_from_syosetu.py n9073ca --force
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
DELAY = 2.5
SPLIT_LINES = 250
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ROOT = os.path.join(ROOT, "..", "AllusionistWiki_raw", "raw", "novel", "syosetu")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


def parse_work(page: str) -> tuple[str, list[tuple[int, str]]]:
    title = re.search(r"<title>(.*?)</title>", page, re.S).group(1).strip()
    title = title.split(" | ")[0].strip()
    eps = []

    def add(n: int, t: str) -> None:
        if n >= 1 and all(n != e[0] for e in eps):
            eps.append((n, t))

    # 表紙の相対リンク /{ncode}/{n}/ が各話リンク（絶対URL形にも対応）
    for m in re.finditer(r'href="(?:https?://ncode\.syosetu\.com)?/[a-z]+\d+[a-z]+/(\d+)/"[^>]*>(.*?)</a>', page, re.S):
        add(int(m.group(1)), strip_tags(m.group(2)).strip().splitlines()[0] if strip_tags(m.group(2)).strip() else "")
    # 目次の多ページ化（?p=N）を辿る（100話/ページ）
    ncode_m = re.search(r'href="/([a-z]+\d+[a-z]+)/\?p=', page)
    if ncode_m:
        ncode = ncode_m.group(1)
        max_p = max((int(x) for x in re.findall(r'\?p=(\d+)', page)), default=1)
        for p in range(2, max_p + 1):
            sub = fetch(f"https://ncode.syosetu.com/{ncode}/?p={p}")
            for m in re.finditer(r'href="(?:https?://ncode\.syosetu\.com)?/[a-z]+\d+[a-z]+/(\d+)/"[^>]*>(.*?)</a>', sub, re.S):
                add(int(m.group(1)), strip_tags(m.group(2)).strip().splitlines()[0] if strip_tags(m.group(2)).strip() else "")
            time.sleep(DELAY)
    eps.sort()
    return title, eps


def parse_episode(page: str) -> tuple[str, list[str]]:
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    title = m.group(1).strip().split(" | ")[0].strip() if m else ""
    # 現行テンプレ: <div class="p-novel__body"> 内の <p id="L{n}">（L1..LN 通し番号、空行含む）
    i = page.find('p-novel__body')
    j = page.find('<!-- /.p-novel__body -->', i)
    body = page[i:j] if (i >= 0 and j > i) else page
    paras: list[str] = []
    for pm in re.finditer(r'<p id="L(\d+)">(.*?)</p>', body, re.S):
        text = strip_tags(pm.group(2)).replace("\u3000", " ").strip()
        if text:
            paras.append(text)
    if paras:
        return title, paras
    # 旧テンプレ（div id="wrap" + div class="ns"）フォールバック
    w = re.search(r'<div id="wrap">(.*?)<div class="clear"></div>', page, re.S)
    body = w.group(1) if w else ""
    for seg in re.split(r'<div class="ns">', body):
        for line in strip_tags(seg).splitlines():
            line = line.replace("\u3000", " ").strip()
            if line:
                paras.append(line)
    return title, paras


def para_index(paras: list[str]) -> str:
    lines = [f"¶{i} {p[:14]}" for i, p in enumerate(paras, 1)]
    return "【¶索引】\n" + "\n".join(lines)


def sanitize(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "／", title).strip()


def write_chunks(outdir: str, n: int, title: str, paras: list[str]) -> list[str]:
    os.makedirs(outdir, exist_ok=True)
    safe = sanitize(title)[:60]
    chunks = [paras[i:i + SPLIT_LINES] for i in range(0, len(paras), SPLIT_LINES)] or [[]]
    paths = []
    for i, chunk in enumerate(chunks, 1):
        suffix = f"_{i:02d}" if len(chunks) > 1 else ""
        path = os.path.join(outdir, f"ch{n:05d}_{safe}{suffix}.md")
        head = f"# ch{n:05d} {title}（分割 {i}/{len(chunks)}）\n" if len(chunks) > 1 else f"# ch{n:05d} {title}\n"
        body = head + f"【段落数 {len(paras)}】（通し番号 1..{len(paras)}、本文先頭からの行番号）\n\n" + "\n".join(chunk)
        if i == len(chunks):
            body += "\n\n" + para_index(paras) + "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        paths.append(path)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ncode")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=10**9)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8")

    ncode = args.ncode.lower()
    work_url = f"https://ncode.syosetu.com/{ncode}/"
    title, eps = parse_work(fetch(work_url))
    print(f"[work] {ncode} {title} 全{len(eps)}話")
    outdir = os.path.join(OUT_ROOT, f"{ncode}_{sanitize(title)}")
    done = 0
    for n, t in eps:
        if n < args.start or n > args.end:
            continue
        prefix = f"ch{n:05d}_"
        existing = [f for f in os.listdir(outdir) if f.startswith(prefix)] if os.path.isdir(outdir) else []
        if existing and not args.force:
            done += 1
            continue
        url = f"https://ncode.syosetu.com/{ncode}/{n}/"
        for attempt in range(3):
            try:
                page = fetch(url)
                break
            except Exception as e:  # noqa: BLE001
                print(f"[retry {attempt+1}] ch{n:05d}: {e}")
                time.sleep(5 * (attempt + 1))
        else:
            print(f"[skip] ch{n:05d}: 取得不能")
            continue
        et, paras = parse_episode(page)
        if not paras:
            print(f"[skip] ch{n:05d}: 本文0行")
            continue
        paths = write_chunks(outdir, n, et or t, paras)
        done += 1
        print(f"[ok] ch{n:05d} {len(paras)}行 {len(paths)}分割 {et[:30]}")
        time.sleep(DELAY)
    print(f"[done] {ncode}: {done}/{len(eps)} 話処理済み → {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
