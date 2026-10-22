---
title: "追加と考察（Playground）: 仮説・自由記述層"
date: 2026-10-20
description: 正規層（事実ページ）に載せる前の仮説・マクロな考察・追加要望を自由に書ける場。WikiLab 実験で運用検証済みの Playground 層の本番導入版
---

# 追加と考察（Playground）

> [!NOTE]
> この層の記述はすべて**仮説（Hypothesis）または思考の痕跡**であり、確定した事実ではありません。事実として引用しないでください。正規層（episodes/ characters/ allusions/ 等）は原文典拠付きのまま維持します。

「こんな解釈はどう？」「この材料を追加したい」「作品全体の構造について考えたい」——そんな**正規層に載せる前の思考**を、スキーマ検証なしの自由な Markdown で置く場所です。良いと思えたものは下の「追加・編集の依頼」経由で正規層への反映を依頼できます。

## ルール

| 項目 | 正規層（事実ページ） | この層（追加と考察） |
|---|---|---|
| 記述形式 | 原文典拠（`quote` + `locator`）準拠 | 自由な Markdown |
| 記述の地位 | 検証済みの知識 | 仮説・思考の痕跡（未確定） |
| 引用 | 事実として引用可 | 出典として引用不可（正規層に昇格後にのみ可） |

- ページ冒頭に**状態ラベル**を付けてください: `draft`（書きかけ）/ `exploring`（検討中）/ `promotion-candidate`（正規層への反映候補）/ `promoted`（反映済み・反映先を記載）/ `discarded`（破棄・来歴として残す）
- 考察の材料に正規層の事実を使ってよい。**原文にない飛躍には「根拠なし」と注記**する
- 反映の運び方（昇格プロトコル）は [WikiLab の設計図](https://allusionistwiki.github.io/AllusionistWikiLab/playground/promotion/) を参照。現状は人間レビュー必須

## 追加・編集の依頼・報告

- **[依頼・報告（専用ページ）](../reports/index.md)** — 編集依頼・誤り・reject・情報提供の 4 入口（GitHub Issue 高速 / 匿名フォーム / Playground 自由記述）
- ページからの直接報告は、各ページ右下の「報告・依頼」欄（Desktop 表示）からも行えます

## 始め方（新規ページ作成）

1. このリポジトリの `content/playground/` に `.md` を追加（GitHub の「Add file → Create new file」でも可）
2. 冒頭に frontmatter の `title` と状態ラベルを記載
3. push すると自動で本ページの一覧に現れます（石英: 直接編集 → 機械ゲート → 自動マージ → LLM 監査）
4. 文章化が面倒なら **[編集依頼](https://github.com/allusionistwiki/AllusionistWiki/issues/new?labels=llm-task&template=reject.yml)** を出してください — llm-task（LLM 自動実装）がここで執筆します

## 一覧

- （作成されたページがここに自動で現れます）

### WikiLab 側の仮説ページ（相互リンク・原文照合済み `promotion-candidate`）

WikiLab（実験場）側に存在し、原文照合を経て `promotion-candidate` 状態にある仮説ページへの相互リンクです。これらは本リポジトリのページではなく Lab の Playground 層のページであり、**本層と同じく事実として引用は不可**です（正規層への昇格後は正規層ページを参照してください）。

| ページ | 内容 | 状態 |
|---|---|---|
| [kouzetsu](https://allusionistwiki.github.io/AllusionistWikiLab/playground/kouzetsu) | 【口舌】の正体（原文 ¶ 照合で確定化した事実と、未検証の推察） | `promotion-candidate` |
| [rakulraal-seat](https://allusionistwiki.github.io/AllusionistWikiLab/playground/rakulraal-seat) | 第一位のラクルラールの座は誰が勝ち取ったのか（4 章ラスト・イツノとマラコーダの会話／原文 ¶ 照合） | `promotion-candidate` |
| [relations-six](https://allusionistwiki.github.io/AllusionistWikiLab/playground/relations-six) | 六人の関係性マップ（ベアトリーチェの融合先と、アズーリア・レオ・青嶺瑠璃の繋がり／原文 ¶ 照合・Lab Issue #31） | `promotion-candidate` |
| [gogmagog](https://allusionistwiki.github.io/AllusionistWikiLab/playground/gogmagog) | 5-15・5-26 の「ゴグマゴグ」（イギリス伝承の巨人 Gogmagog と聖書のゴグとマゴグの照合／原文 ¶・p 照合済み・Lab Issue #63→#65） | `promotion-candidate` |

> [!INFO] 照合メモ
> ゴグマゴグについて、原文（kakuyomu・syosetu・PDF の三典拠）に 5-15「終わりの日、北の果てからゴグマゴグが押し寄せる」（5-15 未来回想、それは破綻した青写真）および 5-26「極北より来たれ死の地霊（ゴグマゴグ）」（5-26 舞台裏の死角④）の該当箇所を確認済み。

## 来歴（provenance）

| 項目 | 値 |
|---|---|
| 設計移植 | WikiLab Playground 運用（2026-10-16 起案 Issue #19）の本番導入（2026-10-20） |
| 運用検証 | https://allusionistwiki.github.io/AllusionistWikiLab/playground/index/ |
| 相互リンク節 | 「一覧」に WikiLab 側の仮説ページ 4 件（口舌・第一位の座・六人の関係性・ゴグマゴグ）への参照注記を追加（2026-10-22・Issue #1 編集依頼） |
| 典拠確認 | 4 ページの存在と `status: promotion-candidate` は Lab リポジトリ main のフロントマターおよび Lab 公開サイト一覧で確認（2026-10-22）。Lab Issue #19/#31/#63→#65/#71 の来歴および起案日 2026-10-16 は依頼本文（Issue #1）記載に基づく |
