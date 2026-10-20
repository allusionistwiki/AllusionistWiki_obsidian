---
title: "依頼・報告 — 誤り / reject / 編集依頼 / 情報提供"
date: 2026-10-20
description: 本番 Wiki への報告・依頼の専用入口。4 種別（誤り / reject / 編集依頼 / 情報提供）を GitHub Issue（高速・推奨）と匿名フォームから受け付け、自動パイプライン（トリアージ→LLM 実装→機械ゲート→LLM 監査）で処理します
---

# 依頼・報告

本番 Wiki への**報告・依頼の専用ページ**です。種別は 4 種のみ:**誤り / reject / 編集依頼 / 情報提供**。

受付後は自動パイプラインで処理されます:
起票 → 自動トリアージ（判定コメント） → `llm-task` ラベルで LLM 実装（編集依頼） → 機械ゲート → 自動マージ → LLM 監査（スパムは自動 revert） → 起票者へコメント。

## GitHub トラック（推奨・高速）

ログインが必要ですが、来歴がすべて残るため最速・最確実です。

- ⎇ **[新しい Issue — 誤り・reject・編集依頼・情報提供](https://github.com/allusionistwiki/AllusionistWiki/issues/new?template=reject.yml)**
  本文の「対象ページ URL」「主張 ID」に該当ページの情報を記載してください（各ページの「報告・依頼」欄から起票すると自動入力されます）
- ⎇ **[Issue 一覧（処理状況を見る）](https://github.com/allusionistwiki/AllusionistWiki/issues)**
- ⎇ **[自動実装された編集（PR / マージ履歴）](https://github.com/allusionistwiki/AllusionistWiki/pulls?q=is%3Apr+label%3Allm-task)**

## 匿名フォーム（ログイン不要）

- ✉ **[Tally フォーム（匿名で報告・依頼）](https://tally.so/r/dbWbZq)**
  投稿は自動で GitHub Issue 化され、上のパイプラインに乗ります。

## 自由記述（考察・仮説をそのまま置きたいとき）

- **[追加と考察（Playground）](../playground/index.md)** — 正規層に載せる前の仮説・マクロ考察を、依頼を通さず直接自由に書く場です。

## 種別の意味

| 種別 | 内容 | 主な処理 |
|---|---|---|
| 誤り | 原文と矛盾する記述の指摘 | 修正依頼へトリアージ → 自動/人間修正 |
| reject | 記述の削除・降格要求 | 根拠確認 → 削除 or 維持の判定 |
| 編集依頼 | ページの追加・改稿依頼 | `llm-task` 自動実装 → 自動マージ・監査 |
| 情報提供 | 典拠付きの追加情報 | 正規層への反映候補としてトリアージ |

> [!NOTE]
> 本番ページ（allusions/characters 他）への編集もこのチェーンで受け付けます。ただし解析ページの正（ソース・オブ・トゥルース）は vault 側です。自動実装が vault 再生成に先行して表示される場合があり、最終確定は vault 側への反映を持ちます。

パイプライン設計の実験・検証場: [WikiLab design-ops](https://allusionistwiki.github.io/AllusionistWikiLab/design-ops/)
