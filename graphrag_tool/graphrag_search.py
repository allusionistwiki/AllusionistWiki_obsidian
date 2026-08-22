#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GraphRAG — 幻想再帰のアユージョニスト-wiki 向け（依存なし版 / no API key）

本スクリプトは Python 標準ライブラリのみを使用し、外部 API キー不要・オフラインで動作します。

手法
----
1. 知識グラフ (Graph) : Obsidian の [[WikiLink]] をそのまま知識グラフとして利用する。
     - ノード : インデックス済み Markdown ファイル（= エンティティ/ページ）
     - エッジ : [[...]] リンクによる相互接続
   （＝ ユーザーが Obsidian で既に構築したグラフを流用できるのが最大の特徴）
2. 検索 (Retrieval) : BM25 を Markdown チャンクに適用。日本語は「エンティティ辞書の
   最長一致」＋「文字 bigram」でトークン化し、品詞解析器なしで部分一致をカバーする。
3. 文脈拡張 (Augmentation) : 取得ページのグラフ近傍を BFS で展開し、関連エンティティと
   ともに統合コンテキストを構築する（＝ RAG の文脈強化）。

Usage
-----
  python graphrag_search.py --query "アキラ は なぜ 敗北 した の ?"
  python graphrag_search.py --query "市場 の 起源" --top 8 --depth 2
  python graphrag_search.py --query "..." --json        # JSON 出力（プログラム利用用）

Index の再構築は初回のみ（`.graphrag/index.json` にキャッシュ。ソース変更で自動検出）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from collections import defaultdict, Counter, deque

# --------------------------------------------------------------------------- #
# 設定
# --------------------------------------------------------------------------- #
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # wiki vault ルート（スクリプトの親）
INDEX_DIR = os.path.join(REPO_ROOT, ".graphrag")                # 生成出力（gitignore 対象）
INDEX_PATH = os.path.join(INDEX_DIR, "index.json")

# インデックスから除外するディレクトリ
SKIP_DIRS = {".git", ".obsidian", ".agents", "_example_pre_rebuild", "graphrag_tool"}
# インデックス対象のトップフォルダ
INDEXABLE_TOP = ("wiki", "raw")

# Semantic retrieval (co-occurrence expansion + RRF) default ON. --no-semantic to disable.
SEMANTIC_ENABLED = True

MAX_CHUNK_CHARS = 512          # チャンク最大長
DEFAULT_DEPTH = 1              # グラフ近傍展開の深さ（ hops ）


# --------------------------------------------------------------------------- #
# トークン化（エンティティ辞書 最長一致 + 文字 bigram）
# --------------------------------------------------------------------------- #
class JapaneseTokenizer:
    """API 不要の日本語トークナイザー。

    - 既知エンティティ（[[links]]・見出しから構築）を最長一致で優先トークン化
    - それ以外は文字 bigram に分割し、OOO／部分一致をカバー
    """

    def __init__(self, entities):
        # 先頭文字別・長さ降順のインデックス（最長一致用）
        self._by_first = defaultdict(list)
        for e in entities:
            if len(e) >= 2:
                self._by_first[e[0]].append(e)
        for v in self._by_first.values():
            v.sort(key=len, reverse=True)

    def tokenize(self, text):
        tokens, i, n = [], 0, len(text)
        while i < n:
            ch = text[i]
            if ch.isspace():
                i += 1
                continue
            matched = None
            for cand in self._by_first.get(ch, ()):
                if text.startswith(cand, i):
                    matched = cand
                    break
            if matched:
                tokens.append(matched)
                i += len(matched)
                continue
            # fallback: 文字 bigram（末尾 1 文字）
            tokens.append(text[i:i + 2])
            i += 1
        return tokens


# --------------------------------------------------------------------------- #
# ファイル走査・チャンキング
# --------------------------------------------------------------------------- #
def iter_markdown_files():
    for top in INDEXABLE_TOP:
        base = os.path.join(REPO_ROOT, top)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                if fn.endswith(".md"):
                    yield os.path.join(root, fn)


def rel(path):
    return os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")


def chunk_text(text):
    """段落（空行 / 全角空白区切り）で分割し、MAX_CHUNK_CHARS まで結合。"""
    # 全角空白「  」区切りを改換として扱う
    norm = text.replace("　　", "\n").replace("　", " ")
    pieces = [p.strip() for p in re.split(r"\n\s*\n", norm) if p.strip()]
    chunks, cur = [], []
    cur_len = 0
    for p in pieces:
        if cur and cur_len + len(p) > MAX_CHUNK_CHARS:
            chunks.append("\n".join(cur))
            cur, cur_len = [], 0
        cur.append(p)
        cur_len += len(p)
    if cur:
        chunks.append("\n".join(cur))
    return [c for c in chunks if c]


# --------------------------------------------------------------------------- #
# グラフ（[[links]] 抽出）
# --------------------------------------------------------------------------- #
LINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")


def extract_targets(text):
    """リンク先ターゲットを抽出する（[[wiki]] と [text](url) の両方）。

    - [[...]]   : 内部ページ名（|alias は除去）
    - [text](url): マークダウンリンクの URL。http/mailto/anchor/data は除外。
    """
    targets = []
    for m in LINK_RE.finditer(text):
        t = m.group(1).split("|", 1)[0].strip()
        if t:
            targets.append(t)
    for m in MD_LINK_RE.finditer(text):
        url = m.group(1).strip()
        if "://" in url or url.startswith(("#", "mailto:", "data:")):
            continue
        url = url.split("#", 1)[0].strip()          # anchor 除去
        if url and not url.endswith("/"):           # ディレクトリ直リンクはスキップ
            targets.append(url)
    return targets


def _resolve_target(target, by_basename):
    """リンク先 target をインデックス済みノード(rel path)に解決する。"""
    t = target.split("#", 1)[0].strip()
    if not t:
        return None
    bn = t.rstrip("/").split("/")[-1]             # ベース名（.md 付き/無し両方）
    if bn in by_basename:
        return by_basename[bn]
    if bn + ".md" in by_basename:
        return by_basename[bn + ".md"]
    return None


# --------------------------------------------------------------------------- #
# BM25
# --------------------------------------------------------------------------- #
class BM25:
    def __init__(self, doc_tokens):
        self.docs = doc_tokens
        self.N = len(doc_tokens) or 1
        self.dl = [len(d) for d in doc_tokens]
        self.avgdl = sum(self.dl) / self.N
        # df（出現ドキュメント数）のみ計算。tf は _recompute で別途再計算するため不要。
        df = Counter()
        for d in doc_tokens:
            for t in set(d):
                df[t] += 1
        self.df = df
        self.idf = {}
        for t, df_t in df.items():
            self.idf[t] = math.log(1 + (self.N - df_t + 0.5) / (df_t + 0.5))

    def score(self, qtoks):
        # BM25 スコアは _recompute / 独立関数 _bm25_scores で計算する。
        return self._recompute(qtoks)

    def _recompute(self, qtoks):
        k1, b = 1.5, 0.75
        scores = [0.0] * self.N
        # term -> docfreq counter (build once lazily via closure below)
        for t in qtoks:
            idf = self.idf.get(t)
            if idf is None:
                continue
            for i, d in enumerate(self.docs):
                f = d.count(t)
                if f == 0:
                    continue
                dl_norm = k1 * (1 - b + b * self.dl[i] / self.avgdl)
                scores[i] += idf * (f * (1.5 + 0.5)) / (f + dl_norm)
        return scores


def _bm25_scores(bm25_obj, qtoks):
    """BM25(Ok) スコアを正しく返す独立関数（上記クラスは簡易実装のため）."""
    k1, b = 1.5, 0.75
    N = bm25_obj.N
    scores = [0.0] * len(bm25_obj.docs)
    for t in qtoks:
        idf = bm25_obj.idf.get(t)
        if idf is None:
            continue
        for i, d in enumerate(bm25_obj.docs):
            f = d.count(t)
            if f == 0:
                continue
            dl_norm = k1 * (1 - b + b * bm25_obj.dl[i] / bm25_obj.avgdl)
            scores[i] += idf * (f * (1.5 + 0.5)) / (f + dl_norm)
    return scores


# --------------------------------------------------------------------------- #
# インデックス構築・キャッシュ
# --------------------------------------------------------------------------- #
def content_hash():
    h = hashlib.sha256()
    for f in sorted(iter_markdown_files()):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                h.update(rel(f).encode("utf-8"))
                h.update(b"\0")
                h.update(fh.read().encode("utf-8"))
                h.update(b"\0")
        except OSError:
            continue
    return h.hexdigest()


def build_index():
    """インデックス（チャンク・トークン・グラフ）を構築して返す。"""
    files = list(iter_markdown_files())

    # 1) エンティティ辞書：見出し ＋ 全[[links]]ターゲット
    entities = set()
    link_targets = set()
    raw_text = {}
    for f in files:
        try:
            txt = open(f, encoding="utf-8").read()
        except OSError:
            continue
        raw_text[rel(f)] = txt
        for ln in txt.splitlines():
            m = re.match(r"\s*#{1,6}\s+(.+)", ln)
            if m:
                entities.add(m.group(1).strip())
            for target in extract_targets(ln):
                link_targets.add(target)
    entities.update(t for t in link_targets if len(t) >= 2)

    # 2) チャンク・トークン化
    chunks, chunk_docs, chunk_meta = [], [], []
    tok = JapaneseTokenizer(entities)
    for rp in files:
        txt = raw_text.get(rel(rp), "")
        for c in chunk_text(txt):
            chunks.append(c)
            chunk_docs.append(tok.tokenize(c))
            chunk_meta.append((rp, c))

    # 3) グラフ（ファイル間リンク）：[text](url) と [[wiki]] の両方から辺を構築
    by_basename = {}
    for f in files:
        bn = os.path.basename(rel(f))
        by_basename.setdefault(bn, rel(f))
    adj = defaultdict(set)
    edge_count = 0
    for rp in files:
        a = rel(rp)
        try:
            txt = raw_text.get(a, "")
        except OSError:
            continue
        for ln in txt.splitlines():
            for target in extract_targets(ln):
                b = _resolve_target(target, by_basename)
                if b and b != a:
                    adj[a].add(b)
                    edge_count += 1

    # Co-occurrence model (distributional semantics / query expansion, stdlib only).
    COC_TOP = 64
    _cooccur = defaultdict(Counter)
    for _docs in chunk_docs:
        _terms = [t for t, _ in Counter(_docs).most_common(80)]
        for _a in _terms:
            for _b in _terms:
                if _a != _b:
                    _cooccur[_a][_b] += 1
    cooccur = {t: {nb: cnt for nb, cnt in c.most_common(COC_TOP)}
               for t, c in _cooccur.items()}

    idx = {
        "hash": content_hash(),
        "chunks": chunks,
        "chunk_docs": chunk_docs,
        "chunk_meta": chunk_meta,          # [(rel_path, first_lines)]
        "adj": {k: sorted(v) for k, v in adj.items()},
        "entities": sorted(entities),
        "edge_count": edge_count,
        "n_files": len(files),
        "cooccur": cooccur,
    }
    return idx


def load_or_build():
    os.makedirs(INDEX_DIR, exist_ok=True)
    if os.path.exists(INDEX_PATH):
        try:
            saved = json.load(open(INDEX_PATH, encoding="utf-8"))
            if saved.get("hash") == content_hash():
                return saved, False
        except (OSError, json.JSONDecodeError):
            pass
    idx = build_index()
    with open(INDEX_PATH, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=0)
    return idx, True


# --------------------------------------------------------------------------- #
# 検索・文脈拡張
# --------------------------------------------------------------------------- #
def expand_graph(adj, seeds, depth):
    seen, frontier = set(seeds), list(seeds)
    result = set()
    for _ in range(depth):
        nxt = []
        for node in frontier:
            for nb in adj.get(node, ()):
                if nb not in seen:
                    seen.add(nb)
                    result.add(nb)
                    nxt.append(nb)
        frontier = nxt
        if not frontier:
            break
    return result


def _cooccur_expand(qtoks, cooccur, top_k=8, min_weight=1):
    """Expand query with top co-occurring terms (distributional, stdlib only)."""
    out = list(dict.fromkeys(qtoks))
    extra = {}
    for t in qtoks:
        for nb, w in cooccur.get(t, {}).items():
            if w < min_weight or nb in qtoks:
                continue
            extra[nb] = extra.get(nb, 0) + min(int(w), 99)
    for nb, _ in Counter(extra).most_common(top_k):
        out.append(nb)
    return out


def _to_ranks(scores):
    """Rank positive scores descending (1-based)."""
    ranked = sorted(range(len(scores)), key=lambda i: -scores[i])
    ranks = {}
    r = 0
    for i in ranked:
        if scores[i] <= 0:
            break
        r += 1
        ranks[i] = r
    return ranks


def _rrf(ranks_a, ranks_b=None, k=60):
    """Reciprocal Rank Fusion over one or two rank maps.

    Keys are chunk *indices*, so size the output to cover the highest index in
    either map (not the entry count) to keep combined[i] position-aligned with
    chunk_meta[i].
    """
    keys = list(ranks_a.keys())
    if ranks_b:
        keys += list(ranks_b.keys())
    size = max(keys) + 1 if keys else 0
    out = [0.0] * size
    for i, r in ranks_a.items():
        out[i] += 1.0 / (k + r)
    if ranks_b:
        for i, r in ranks_b.items():
            out[i] += 1.0 / (k + r)
    return out


def snippet(text, n=160):
    return (text[:n] + "…") if len(text) > n else text


def search(query, depth=None):
    idx, built = load_or_build()
    if depth is None:
        depth = DEFAULT_DEPTH

    bm25 = BM25(idx["chunk_docs"])
    tok = JapaneseTokenizer(idx["entities"])
    qtoks = tok.tokenize(query)
    scores = _bm25_scores(bm25, qtoks)

    # Semantic expansion (co-occurrence query expansion) + RRF fusion.
    # Disabled or no model -> identical to plain BM25.
    combined = list(scores)
    if SEMANTIC_ENABLED and idx.get("cooccur"):
        eqtoks = _cooccur_expand(qtoks, idx["cooccur"])
        combined = _rrf(_to_ranks(scores), _to_ranks(_bm25_scores(bm25, eqtoks)), k=60)

    # 同一チャンク（同一ファイル）のスコアをマージしてページランクも兼ねる
    page_score = defaultdict(float)
    for i, s in enumerate(combined):
        if s > 0:
            page_score[idx["chunk_meta"][i][0]] += s

    ranked_pages = sorted(page_score.items(), key=lambda x: -x[1])
    top_pages = [p for p, _ in ranked_pages[:5]]

    # グラフ近傍で文脈拡張
    neighbors = expand_graph(idx["adj"], top_pages, depth)
    augmented = list(neighbors - set(top_pages))

    return {
        "built": built,
        "query": query,
        "n_chunks": len(idx["chunks"]),
        "n_edges": idx["edge_count"],
        "n_files": idx["n_files"],
        "top_pages": [{"path": p, "score": round(s, 3),
                       "snippet": snippet(idx["chunk_meta"][i][1])}
                      for i, (p, s) in enumerate(
                          sorted(((idx["chunk_meta"][i][0], combined[i])
                                  for i in range(len(combined)) if combined[i] > 0),
                                 key=lambda x: -x[1])[:6])],
        "augmented": augmented,
    }


# --------------------------------------------------------------------------- #
# メイン
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="GraphRAG for 幻想再帰のアユージョニスト-wiki")
    ap.add_argument("--query", "-q", required=True, help="検索クエリ（日本語）")
    ap.add_argument("--top", type=int, default=6, help="表示するトップ結果数")
    ap.add_argument("--depth", type=int, default=DEFAULT_DEPTH,
                    help=f"グラフ近傍展開の深さ（default={DEFAULT_DEPTH}）")
    ap.add_argument("--json", action="store_true", help="出力をJSONにする")
    import sys as _sys
    if "--no-semantic" in _sys.argv or os.environ.get("GRAG_NO_SEMANTIC") == "1":
        global SEMANTIC_ENABLED
        SEMANTIC_ENABLED = False
    args = ap.parse_args()

    res = search(args.query, depth=args.depth)

    if not args.json:
        if res["built"]:
            print(f"[index] 新規構築: {res['n_chunks']}チャンク / "
                  f"{res['n_edges']}エッジ / {res['n_files']}ファイル")
        else:
            print(f"[index] キャッシュ使用: {res['n_chunks']}チャンク / "
                  f"{res['n_edges']}エッジ")

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    print(f"\n■ クエリ: {args.query}")
    print(f"▶ 関連チャンク (Top{min(args.top, len(res['top_pages']))})")
    for i, r in enumerate(res["top_pages"][:args.top], 1):
        print(f"  {i}. [{r['path']}] score={r['score']}")
        for ln in snippet(r['snippet'], 200).split("\n")[:3]:
            print(f"       {ln.strip()}")
    if res["augmented"]:
        print(f"\n▶ 関連エンティティ（グラフ近傍 depth={args.depth}）")
        for p in res["augmented"][:args.top]:
            print(f"   • {p}")


if __name__ == "__main__":
    main()
