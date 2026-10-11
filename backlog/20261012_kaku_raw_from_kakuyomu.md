# カクヨム連載から kaku_raw/ を作成（589話・全文抽出）
- 受付日: 2026-10-12
- ステータス: in-progress
- 出典: ユーザー指示

## 指示原文
> @url:`https://kakuyomu.jp/works/16816927859268545348` →ここからkaku_rawを作成してください

## 補足・制約
- 対象: カクヨム『幻想再帰のアリュージョニスト』（最近）全 589 話・4,556,481 文字（2026-08-28 更新時点）
- 出力: `kaku_raw/chNNNNN__<タイトル>.md`（採番＝カクヨムの**公開順** publishedAt 昇順。0-x 幕間・断章は公開順に中間へ入る）
- 目次は作品ページ `__NEXT_DATA__` の Apollo state `tableOfContentsV2` から取得（`/episodes` 旧 URL は 404）。スナップショットは `tools/data/kaku_toc.json`
- 本文は各エピソードページの `div.js-episode-body` 内の `<p>` を 1 段落 1 行で保存。ヘッダ 4 行（ep ID・公開日時・章・URL）
- 再利用ツール: `tools/make_raw_from_kakuyomu.py`（相対パス・再開可能・レート制限 sleep 1.2s・`--from/--to/--force/--toc-only`）
- `kaku_raw/` は .gitignore 追加済み（raw/・RAW2/ と同じ非公開扱い）
- 採番は syosetu 基準（raw/・RAW2/ の 272 話）と**独立**（カクヨムは 1 章を①②…に分割しているため話数が異なる）。対応付けが必要な場合は別途マッピング作成

## 進捗（着手中・都度更新）
- 2026-10-12: 目次抽出検証完了（589 話・章 7 個・publishedAt 昇順で採番、連番重複なし）。ツール実装・ch00001-00003 の 3 話で抽出品質確認（本文 1 段落 1 行・ヘッダ付き）。.gitignore に kaku_raw/ 追加。次: 全 589 話のバックグラウンド取得（ログ `_temp/kaku_fetch.log`）→ 完了後 typo scan・log.md 記録・コミット（ツール＋目次 JSON＋backlog のみ。kaku_raw 本体は非公開）
