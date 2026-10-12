#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""make_raw_from_jbbs.py — したらば（jbbs.shitaraba.net）BBS の全スレッドを保存する。

- 対象: movie/7039（『ゆらぎの神話』BBS）。スレ一覧は movie/7039/ のアンカーメニュー（1..N）
- 各スレ: read.cgi/movie/7039/<ts>/ 全文（1〜1000）＋ 1000超は archive/<ts>/dat/1000.html,2000.html…
- 保存: raw_Yuragi_Sinnwa/BBS/<NNN>_<スレ名>/Thread.md
  - 冒頭: スレID・スレ名・取得URL・レス数
  - 各レス: ## <res番号> <名前> <日時> の見出し＋本文（行頭「: 」除去、<br>→改行）
- 保存済み（Thread.md あり・--force 無し）はスキップ。取得間隔 2 秒
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
DELAY = 2.0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ROOT = os.path.join(ROOT, "..", "YuragiWiki", "raw", "bbs", "jbbs", "movie-7039")
BBS = "movie/7039"


def decode_page(raw: bytes) -> str:
    """charset を meta/HTTP ヘッダから判定してデコードする（したらばは EUC-JP 等）。"""
    m = re.search(rb"charset=([\w-]+)", raw[:2048], re.I)
    enc = m.group(1).decode("ascii", "ignore").lower() if m else ""
    enc = {"euc-jp": "euc_jp", "x-shift_jis": "shift_jis", "shift-jis": "shift_jis",
           "iso-2022-jp": "iso-2022-jp", "utf8": "utf-8"}.get(enc, enc)
    for cand in [enc, "euc_jp", "shift_jis", "utf-8"]:
        if not cand:
            continue
        try:
            txt = raw.decode(cand)
        except (UnicodeDecodeError, LookupError):
            continue
        if "＜" in txt or "：" in txt or "：" in txt or "【" in txt:
            return txt
    return raw.decode("euc_jp", "replace")


def fetch(url: str, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return decode_page(r.read())
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 + 4 * i)
    raise RuntimeError(f"fetch failed: {url}: {last}")


def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


def get_thread_list() -> list[dict]:
    """subject.cgi（スレッド一覧・全件）からスレ番号・スレ名・read.cgi URL を抽出する。

    旧ソースの movie/7039/ アンカーメニューは最新スレしか載らず抜けるため、
    全件一覧の subject.cgi を主、アンカーメニューをフォールバックとする。
    """
    pat = re.compile(
        r"(\d+):\s*<a href=\"[^\"]*?/bbs/read\.cgi/" + re.escape(BBS) + r"/(\d+)/l50\">\s*"
        r"(.+?)\((\d+)\)\s*</a>",
        re.S,
    )
    out = []
    page = fetch(f"https://jbbs.shitaraba.net/bbs/subject.cgi/{BBS}/")
    for m in pat.finditer(page):
        out.append({
            "ts": m.group(2),
            "no": int(m.group(1)),
            "title": m.group(3).strip(),
            "res": int(m.group(4)),
        })
    if not out:  # フォールバック: アンカーメニュー（最新スレのみ）
        page = fetch(f"https://jbbs.shitaraba.net/{BBS}/")
        pat2 = re.compile(
            r'href="[^"]*?/bbs/read\.cgi/' + re.escape(BBS) + r'/(\d+)/l50">(\d+)</a>\s*:\s*'
            r'<a rel="nofollow" href="#\d+">([^<(]+)\((\d+)\)</a>',
            re.S,
        )
        for m in pat2.finditer(page):
            out.append({
                "ts": m.group(1),
                "no": int(m.group(2)),
                "title": m.group(3).strip(),
                "res": int(m.group(4)),
            })
    out.sort(key=lambda x: x["no"])
    return out


BLOCK_RE = re.compile(r'<dt id="comment_(\d+)">(.*?)</dt>\s*<dd>(.*?)</dd>', re.S)
NAME_RE = re.compile(r'<b>(.*?)</b>', re.S)
DATE_RE = re.compile(r'(\d{2,4}/\d{1,2}/\d{1,2}\([^)]*\)\s*\d{1,2}:\d{2}:\d{2})')
ID_RE = re.compile(r'ID\s*:\s*([\w+/=]{8,12})')


def parse_res(page: str) -> list[dict]:
    """各 <dt id="comment_N">…</dt><dd>…</dd> を独立に解析する。

    名前は <b>…</b>（<font> 直下でも <a href="mailto:"> 直下でも）、
    日時は dt 内、ID はブロック全体から拾う（font 前提の旧正規表現は
    mailto 名前付きレスを落としていた）。
    """
    res = []
    for m in BLOCK_RE.finditer(page):
        head = m.group(2)
        body = strip_tags(m.group(3)).strip()
        body = re.sub(r"\n{3,}", "\n\n", body)
        nm = NAME_RE.search(head)
        dm = DATE_RE.search(head)
        idm = ID_RE.search(m.group(0))
        res.append({
            "no": int(m.group(1)),
            "name": strip_tags(nm.group(1)).strip() if nm else "",
            "date": dm.group(1).strip() if dm else "",
            "id": idm.group(1) if idm else "",
            "body": body,
        })
    return res


def fetch_thread(ts: str) -> list[dict]:
    res = parse_res(fetch(f"https://jbbs.shitaraba.net/bbs/read.cgi/{BBS}/{ts}/"))
    # 1000超は過去ログ倉庫の dat ページ
    start = 1000
    while True:
        url = f"https://jbbs.shitaraba.net/bbs/archive/{BBS}/{ts}/dat/{start}.html"
        try:
            page = fetch(url)
        except RuntimeError:
            break
        part = parse_res(page)
        if not part:
            break
        res.extend(part)
        start += 1000
    # 重複除去（no 基準で初出のみ・出現順維持）
    seen = set()
    out = []
    for r in res:
        if r["no"] in seen:
            continue
        seen.add(r["no"])
        out.append(r)
    out.sort(key=lambda r: r["no"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", type=int, default=0, help="このスレ番号1件のみ（検証用）")
    args = ap.parse_args()
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8")

    threads = get_thread_list()
    print(f"[list] {len(threads)} threads")
    made = skipped = failed = 0
    for t in threads:
        if args.only and t["no"] != args.only:
            continue
        safe = re.sub(r'[\\/:*?"<>|]', "／", t["title"])[:60].strip()
        outdir = os.path.join(OUT_ROOT, f"{t['no']:03d}_{safe}")
        path = os.path.join(outdir, "Thread.md")
        if os.path.exists(path) and not args.force:
            skipped += 1
            continue
        try:
            res = fetch_thread(t["ts"])
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"[fail] {t['no']} {t['title'][:30]}: {e}", flush=True)
            continue
        os.makedirs(outdir, exist_ok=True)
        lines = [
            f"# {t['no']}: {t['title']}",
            f"【スレID {t['ts']}】",
            f"【URL https://jbbs.shitaraba.net/bbs/read.cgi/{BBS}/{t['ts']}/】",
            f"【取得レス数 {len(res)}（一覧表示 {t['res']}）】",
            "",
        ]
        for r in res:
            head = f"## {r['no']} ：{r['name']}"
            if r["id"]:
                head += f"（ID:{r['id']}）"
            head += f" ：{r['date']}"
            lines.append(head)
            lines.append(r["body"])
            lines.append("")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        made += 1
        print(f"[ok] {t['no']:03d} {t['title'][:30]}: {len(res)}res", flush=True)
        time.sleep(DELAY)
    print(f"[done] made={made} skipped={skipped} failed={failed} total={len(threads)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
