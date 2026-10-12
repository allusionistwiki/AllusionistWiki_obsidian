# raw 一元化・マルチソース移行

- 受付日: 2026-10-12
- ステータス: pending
- 優先度: 高（継続対象の基盤）

## 指示原文（verbatim）
> これらも今後対象にしていこうと思いますが、レポジトリ構成、rawファイル構成の戦略を立ててください

戦略は `DESIGN_NOTES.md`（2026-10-12 節）に記録済み。本カードは**移行実行**の受付。

## 実施項目
- [ ] A. ルート統合: `kaku_raw/`→`raw/novel/kakuyomu/`、`syosetu_raw/`→`raw/novel/syosetu/`、`raw_Yuragi_Sinnwa/`→`raw/bbs/`、現 `raw/*`→`raw/novel/pdf/pdf01_幻想再帰のアリュージョニスト/`、`RAW2/` 廃止
- [ ] B. 参照追随: wiki/episodes/ch00012・ch00013 の `](raw/` 2箇所、CLAUDE.md §1・§2・§4① の raw 命名規約改定
- [ ] C. ツール追随: make_raw_from_{pdf,kakuyomu,syosetu,jbbs,mixi}.py の出力先＋`tools/data/raw_manifest.json` 更新処理追加、graphrag 再構築確認
- [ ] D. private repo `AllusionistWiki_raw`（GitHub private）作成 → raw/ を push（要ユーザー承認: 組織作成権限）
- [ ] E. .gitignore 簡素化（`raw/` 1本）、wiki/log.md 記録、本カード削除

## 進捗
- 2026-10-12: 戦略策定・DESIGN_NOTES.md 作成・本カード作成。実行はユーザー承認待ち。
- 2026-10-12: マルチ wiki 戦略を DESIGN_NOTES.md に追記（raw は wiki 外の共有 private repo、wiki は 1 vault 複数ルート開始、参照は manifest ID 基準）。本カードの移行先は `../AllusionistWiki_raw/raw/`（vault 外 private repo）に確定。
