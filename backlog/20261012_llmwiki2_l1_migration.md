# LLMWiki2 → L1 層移行

- 受付日: 2026-10-12
- ステータス: pending
- 優先度: 中（次フェーズの本体）

## 指示原文（verbatim）
> ちなみにLLMWiki2も今の公開層は解析フック程度にしかならないので、L1層に移行する予定です
> L1層（機械抽出メイン）→L2層（名前統合、prefix修正）→L3層（整合性検証）→L4層（LLM単話内容整理）→L5層（各話統合内容整理）→L6層（内容統合）→L7層（公開層、人間訂正、整理）くらいかなと
> 公開はL1～L7まですべて公開する

## 実施項目
- [ ] L0〜L7 階層モデルの確定（DESIGN_NOTES にドラフト記録済み — 層名・産出物・層間入力の仕様）
- [ ] LLMWiki2 現行公開サイト（claims 等）の L1 格下げ: 公開 URL を wiki 配下の L1 層（例 `/AllusionistWiki/l1/`）へ移し、トップ index 入口は L7（現行公開 wiki）に置く
- [ ] L1 産出物の置き場確定: LLMWiki2_Work（facts/candidates/locks）を L1 データとして公開維持（repo 構成はサイト repo 統合時に決定）
- [ ] L2〜L6 の産出物フォルダ規約（`work/L1/ … work/L6/`、repo は wiki あたり1個・層はフォルダで切る）と各層のスキーマ（layer / derived_from / run 版）
- [ ] LLMWiki2_Obsidian / LLMWiki2 / LLMWiki2_Work の repo 再配置（マージ先: wiki1 vault への合流 or 独立維持）
- [ ] ポータル（allusionistwiki.github.io）のカードを L1〜L7 公開構造に更新

## 進捗
- 2026-10-12: 受付。階層モデル・全層公開方針を DESIGN_NOTES.md に記録。実行は L1 層設計の詰めから。
- 2026-10-12: 層構成評価を DESIGN_NOTES に追記（層=データスナップショット／Work は 1 repo・層フォルダ／lineage 第一級／フィードバック辺許容）。
- 2026-10-12: **Work repo 実装**: `allusionistwiki/AllusionistWiki_work`（公開）作成・push。L1 ベースライン run `20261012T0000_baseline`（= LLMWiki2_Work@054f7a2a をそのまま取り込み、run.json 来歴付き）、L2〜L6 スケルトン、`work/index/runs-index.json`（run ID 参照）＋ `L1/latest.txt`。旧 LLMWiki2_Work repo は履歴として公開維持（新 repo が継承）。
- 次の一手: L2（名前統合）の初 run 実行（設計は Work repo L2/README 完了済）、L3〜L6 の run 設計、human_verified 昇格の進行。
