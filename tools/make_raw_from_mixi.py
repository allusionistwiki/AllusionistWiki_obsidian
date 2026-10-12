#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""mixi_fetch.py — プレビューペイン（Hermes Electron セッション）の mixi クッキーで
コミュ「架空の神話を作ろう」(373088) の全トピック・コメントを取得して保存する。

保存: raw_Yuragi_Sinnwa/mixi/<topic_id>/Topic.md + <topic_id>_topic_comment.md
  - Topic.md: トピックID・タイトル・投稿者(名前)・日時・本文
  - comment md: コメントID・投稿者ID(名前)・日時・コメント内容（全件）
クッキー値は出力・ログに一切出さない。
"""
from __future__ import annotations

import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import urllib.request

import win32crypt  # pywin32

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
COMM = "373088"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ROOT = os.path.join(ROOT, "..", "YuragiWiki", "raw", "bbs", "mixi", COMM)
DELAY = 2.5


def appdata() -> str:
    return os.environ["APPDATA"]


def load_cookie_header() -> str:
    """Hermes Electron の Cookies DB を読み、mixi.jp 用 Cookie ヘッダを組み立てる。"""
    base = os.path.join(appdata(), "Hermes")
    with open(os.path.join(base, "Local State"), encoding="utf-8") as f:
        import base64, json
        key_b64 = json.load(f)["os_crypt"]["encrypted_key"]
    key = base64.b64decode(key_b64)
    key = key[len("DPAPI"):]
    key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    # プレビューペインは専用 partition（hermes-preview）に Cookie を持つ。両方試す。
    cands = [
        os.path.join(base, "Partitions", "hermes-preview", "Network", "Cookies"),
        os.path.join(base, "Network", "Cookies"),
    ]
    src = next((c for c in cands if os.path.exists(c)), cands[0])
    # 起動中の Electron が排他ロックしているため immutable 読み取り（コピー不要）
    uri = "file:" + src.replace("\\", "/") + "?mode=ro&immutable=1"
    con = sqlite3.connect(uri, uri=True)
    rows = con.execute(
        "SELECT host_key, name, value, encrypted_value FROM cookies "
        "WHERE host_key LIKE '%mixi%'"
    ).fetchall()
    con.close()
    pairs = []
    n_dec = 0
    for host, name, value, enc in rows:
        if value:
            pairs.append((name, value))
            continue
        if not enc:
            continue
        if enc[:3] == b"v10":
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            nonce, ct = enc[3:15], enc[15:]
            val = AESGCM(key).decrypt(nonce, ct, None).decode("utf-8", "replace")
            n_dec += 1
        else:
            val = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode("utf-8", "replace")
        pairs.append((name, val))
    print(f"[cookies] mixi cookies: {len(pairs)} (decrypted {n_dec})")
    if not pairs:
        raise SystemExit("mixi クッキーが見つかりません（ペインでログイン済みでもセッションが別の場合あり）")
    return "; ".join(f"{n}={v}" for n, v in pairs)


def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    import html as H
    return H.unescape(s)


def fetch(url: str, cookie: str, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Cookie": cookie,
                                                       "Referer": "https://mixi.jp/"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
            m = re.search(rb"charset=([\w-]+)", raw[:2048], re.I)
            enc = m.group(1).decode("ascii", "ignore").lower() if m else ""
            enc = {"euc-jp": "euc_jp", "x-shift_jis": "shift_jis", "utf8": "utf-8"}.get(enc, enc)
            for cand in [enc, "euc_jp", "shift_jis", "utf-8"]:
                if not cand:
                    continue
                try:
                    txt = raw.decode(cand)
                except (UnicodeDecodeError, LookupError):
                    continue
                if "mixi" in txt:
                    return txt
            return raw.decode("euc_jp", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 + 4 * i)
    raise RuntimeError(f"fetch failed: {url}: {last}")


def get_topics(cookie: str) -> list[dict]:
    """list_bbs.pl の HTML 内 JSON データからトピック一覧を抽出する。"""
    out = []
    page = 1
    while True:
        url = f"https://mixi.jp/list_bbs.pl?id={COMM}&type=bbs&p={page}"
        txt = fetch(url, cookie)
        ids = re.findall(r"view_bbs\.pl\?comm_id=" + COMM + r"&id=(\d+)", txt)
        titles = re.findall(r"view_bbs\.pl\?comm_id=" + COMM + r"&id=\d+\"[^>]*>([^<]{2,80})</a>", txt)
        uniq = []
        for i in ids:
            if i not in uniq:
                uniq.append(i)
        if not uniq:
            break
        for tid in uniq:
            t = next((x for x in titles if tid in txt), "")
            out.append({"id": tid, "title": t.strip()})
        # ページネーション: 「次へ」が無ければ打ち切り
        if "次のページ" not in txt and f"p={page+1}" not in txt:
            break
        page += 1
        if page > 20:
            break
        time.sleep(DELAY)
    return out


TOPIC_RE = re.compile(
    r"<div class=\"[^\"]*bbsComment[^\"]*\"[^>]*id=\"bbsComment(\d+)\"[^>]*>(.*?)</div>\s*</div>",
    re.S,
)


def parse_topic(cookie: str, tid: str) -> dict:
    url = f"https://mixi.jp/view_bbs.pl?id={tid}&comm_id={COMM}&page=all"
    txt = fetch(url, cookie)
    title = ""
    m = re.search(r"<title>\[mixi\][^|]*\|\s*([^<]+?)\s*</title>", txt)
    if m:
        title = m.group(1).strip()
    # 投稿（トピック本文）
    post = {"name": "", "date": "", "body": ""}
    m = re.search(r"<div class=\"[^\"]*bbsBody[^\"]*\"[^>]*>(.*?)</div>", txt, re.S)
    if m:
        post["body"] = strip_tags(m.group(1)).strip()
    m = re.search(r"mixi-std[^\"]*commentOwner[^\"]*\"[^>]*>([^<]+)</a>", txt)
    if m:
        post["name"] = strip_tags(m.group(1)).strip()
    m = re.search(r"(\d{4}年\d{2}月\d{2}日\s*\d{2}:\d{2})", txt)
    if m:
        post["date"] = m.group(1)
    # コメント: li 単位
    comments = []
    for m in re.finditer(r"<li[^>]*class=\"[^\"]*commentItem[^\"]*\"[^>]*>(.*?)</li>", txt, re.S):
        block = m.group(1)
        cm = re.search(r"commentId[^>]*>\s*\[?(\d+)\]?", block)
        cid = cm.group(1) if cm else ""
        nm = re.search(r"commentOwner[^>]*>([^<]*)</a>", block)
        name = strip_tags(nm.group(1)).strip() if nm else ""
        dm = re.search(r"(\d{4}年\d{2}月\d{2}日\s*\d{2}:\d{2})", block)
        date = dm.group(1) if dm else ""
        bm = re.search(r"commentBody[^>]*>(.*?)</div>", block, re.S)
        body = strip_tags(bm.group(1)).strip() if bm else ""
        comments.append({"id": cid, "name": name, "date": date, "body": body})
    return {"id": tid, "title": title, "post": post, "comments": comments, "raw_len": len(txt)}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    cookie = load_cookie_header()
    topics = get_topics(cookie)
    print(f"[topics] {len(topics)}")
    for t in topics:
        print("  ", t["id"], t["title"][:40])
    made = 0
    for t in topics:
        d = parse_topic(cookie, t["id"])
        outdir = os.path.join(OUT_ROOT, t["id"])
        os.makedirs(outdir, exist_ok=True)
        safe = re.sub(r'[\\/:*?"<>|]', "／", d["title"] or t["title"])[:60].strip()
        with open(os.path.join(outdir, "Topic.md"), "w", encoding="utf-8") as f:
            f.write(f"# {d['title']}\n")
            f.write(f"【トピックID {t['id']}】\n")
            f.write(f"【URL https://mixi.jp/view_bbs.pl?id={t['id']}&comm_id={COMM}】\n")
            f.write(f"【投稿者 {d['post']['name']}】 【日時 {d['post']['date']}】\n")
            f.write(f"【コメント数 {len(d['comments'])}】\n\n")
            f.write(d["post"]["body"] + "\n")
        with open(os.path.join(outdir, f"{t['id']}_topic_comment.md"), "w", encoding="utf-8") as f:
            f.write(f"# {d['title']} コメント一覧\n\n")
            for c in d["comments"]:
                f.write(f"## {c['id']} ：{c['name']} ：{c['date']}\n{c['body']}\n\n")
        made += 1
        print(f"[ok] {t['id']} {d['title'][:30]}: {len(d['comments'])} comments", flush=True)
        time.sleep(DELAY)
    print(f"[done] made={made} topics={len(topics)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
