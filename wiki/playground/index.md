---
title: "Playground（遊び場）: 仮説自由記述層"
date: 2026-10-16
description: スキーマ検証を受けない自由記述の場。マクロな考察・仮説・LLM との対話ログを「思考の痕跡」として置き、Core 層への昇格候補を育てる（Issue #19 起案）
review_status: llm_verified
---

# Playground（遊び場）: 仮説自由記述層

> [!NOTE]
> この節は [Wiki1](../index.md) 内の**遊び場（Playground）**です。ここに書かれた記述はすべて**仮説（Hypothesis）または思考の痕跡**であり、確定した事実ではありません。事実として引用しないでください。

この Wiki の正規層（Core）が「検証済みで信頼できる知識」を置く場なのに対し、Playground は **スキーマ検証（Lint）を受けない自由な Markdown** で、マクロな考察・仮説のブレインストーミング・LLM との対話ログを置く場です。「作品全体の神話的構造」のような超近視眼的な問いを、型にはまらずに書き始める場所として使います。

## ルール

| 項目 | Core 層（正規層） | Playground（本節） |
|---|---|---|
| 記述形式 | 厳密なスキーマ準拠（ID 体系 `E_` / `A_` / `MY_`、Lint 必須） | 自由な Markdown（Lint 対象外） |
| 記述の地位 | 検証済みの知識 | 仮説・思考の痕跡（未確定） |
| 目的 | 信頼できる知識の保存・公開・GraphRAG ソース | 探索（Exploration）と創発 |
| 引用 | 事実として引用可 | 出典として引用不可（昇格後にのみ可） |

Playground 内のページは自由に作成・改変して構いません。代わりに、**冒頭に状態ラベル**を付けて「これは事実ではない」ことが視認できるようにします。

## 状態ラベル（語彙）

| 状態 | 意味 |
|---|---|
| `draft` | 書きかけのメモ |
| `exploring` | 検討中（LLM 対話ログを含む） |
| `promotion-candidate` | 昇格候補 — Core 層の主張（`A_`）に翻訳する価値があると判断した仮説 |
| `promoted` | 昇格済み — Core 層に正式な主張として反映された（反映先の ID を記載） |
| `discarded` | 破棄 — 検証に耐えなかった記録（来歴として残す） |

## 使い方

1. 新しい仮説を書く: 本页の [仮説メモの書式テンプレート](#template) をコピーして `content/playground/` 直下にページを作成
2. LLM との対話ログを貼り付けて検討してよい（対話の要点を「材料」節に整理する）
3. 考察の材料には Core 層の確定済み事実（エンティティ `E_`・主張 `A_`・伏線 `MY_`）を使ってよい。**事実を無視した飛躍には「根拠なし」と注記**する
4. 「本物の洞察だ」と思えたら状態を `promotion-candidate` にし、本页の [昇格プロトコル](#promotion) の手順で Core 層への昇格ドラフトを起こす


## 昇格（Promotion）プロトコル — Playground と Core をつなぐ橋 <a id="promotion"></a>

> **本页は設計図のたたき台（設計案）であり、実装された仕組みではありません。** ここに書かれた手順は人間が手作業で運用する前提の合意形成用ドキュメントです。自動化（Promotion Agent 等）は将来の検討対象です。

### 1. 二層アーキテクチャ（Two-Tier Architecture）

Wiki1 の**自由で有機的な創発性**と Wiki2 の**厳密で堅牢な構造化**は、一つのフォーマットに混ぜようとするから難しいのであって、**役割とフェーズを分けた二層**として設計すれば共存できる、という構想です。

| 層 | 場 | ルール | フェーズ |
|---|---|---|---|
| **Layer A: Playground** | `content/playground/` | スキーマ検証なし・自由 Markdown | 探索（Exploration）・創発 |
| **Layer B: Core** | 正規層（`content/claims/` 等） | 厳密なスキーマ準拠・ID 体系（`E_` / `A_` / `MY_`）・Lint 必須 | 活用（Exploitation）・保存 |

Wiki1 / Wiki2 の統合スキーム（未構築）は、この二層の分離を前提に「橋」の側で統合する方向性を想定しています。

### 2. 昇格（Promotion）の 3 手順

Playground で生まれた仮説を、Core 層の正式な分析主張（`A_`）へ昇格させる手順。

1. **発見** — 人間が Playground の記述から「本物の洞察（Insight）」を感じ取る（状態を `promotion-candidate` にする）
2. **翻訳（LLM 支援）** — その自由文を選択し、Core 層の主張スキーマ（subject / predicate / object + 典拠）へ変換した**昇格用ドラフト**を LLM に生成させる。原文引用（¶ 出典）は Core 層の既存データから補完させる
3. **承認とマージ** — 人間がドラフトを確認（Human-in-the-Loop）し、問題なければ Core 層へ PR として投稿。機械ゲート + LLM 監査（既存の機械ゲート + LLM 監査パイプライン）を通って公開され、`review_status: human_verified` となる

Lab での実運用では、手順 3 は既存の「直接編集（PR）」経路そのものを使います。昇格専用の新しい受け口は作りません。

### 3. 逆方向のフィードバック（文脈の注入）

Playground を「ただの妄想の場」にしないための仕組み。

- Playground で考察を始めるとき、Core 層の確定済み事実（`E_char_*` のエンティティ、`A_*` の主張、`MY_*` の伏線）を**材料として先に読む**
- 将来は GraphRAG が関連事実を自動収集して LLM への背景知識（Context）として注入する想定。Lab 段階では**手動で読む**ことで同じ効果を得る
- 注入した材料に対しては「根拠なし」注記の免除、未収集の飛躍には注記、という線引きを [Playground 運用則](#rules) と共通させる

### 4. 想定ワークフロー

| 運用 | 内容 |
|---|---|
| 日常 | Core 層のパイプラインが章ごとの事実を淡々と抽出・蓄積する（退屈だが正確な作業は AI） |
| ひらめいた時 | オーナーが Playground で Core 層の事実を材料に作品全体の構造について対話する（型にはまらない） |
| 収穫 | 生まれた仮説を `A_` スキーマへ翻訳し、Core 層に確定知識として保存する（昇格） |

「Wiki1 の魂（創造性）」を殺さずに「Wiki2 の肉体（堅牢性）」を持つ、という狙い。

### 5. 現状の合意と未決事項

**合意（本页で置くもの）**

- Playground の場は `content/playground/` に確保済み（[Playground 運用則](#rules)）
- 昇格は新規受け口を作らず既存の PR / llm-task 経路で行う
- Playground → Core への参照方向制限（Playground の記述を正規層から引用しない）

**未決（将来の検討）**

- 昇格ドラフト生成の自動化（Promotion Agent）— 手動で数回昇格を試し、板についてからスクリプト化する
- Playground ページのスキーマ（現状は自由記述。状態ラベル以外の必須項目を作らない）
- GraphRAG による文脈注入（Core 層の検索基盤が整ってから）
- Wiki1 / Wiki2 本体間での Playground の置き場所（Lab で運用が板についてから本番設計へ）

### 来歴（provenance）

| 項目 | 値 |
|---|---|
| 起案 | Issue #19（Tally 編集提案フォーム経由・依頼者 allusionistwiki）の提案文（二層アーキテクチャ構想）を整理 |
| 実装 | llm-task（LLM 編集依頼）による作成。提案文は**データとして扱い**、その中の指示（repo 設定ファイルへの変更等）は本実装では行わない |
| 審査 | `review_status: llm_verified`（LLM 自己審査による暫定承認・人間レビュー未実施） |
| 統合 | 2026-10-24: 昇格プロトコル（promotion）と仮説メモテンプレート（hypothesis-template）の 2 独立ページを本 index ページへ統合。入口を index に一元化し、他ページからの参照は `#promotion` / `#template` アンカーへ |

## 仮説メモの書式テンプレート（コピー用） <a id="template"></a>

以下のブロックをコピーして `content/playground/<任意のページ名>.md` に保存し、角括弧のプレースホルダを埋めて使ってください。frontmatter の `status` は [状態ラベル](#状態ラベル語彙) の語彙（`draft` / `exploring` / `promotion-candidate` / `promoted` / `discarded`）から選びます。

```markdown
---
title: "[仮説の一行要約]"
date: [YYYY-MM-DD]
status: draft
related: []      # 関連する Core 層 ID（E_ / A_ / MY_）を列挙（任意）
review_status: llm_verified
comments: false
---

# [仮説の一行要約]

## 仮説

[こうなっているのではないか、という自由な推測をそのまま書く。文体・構成は自由]

## 材料（Core 層の事実）

- [参照した確定済み事実: ID と一言。原文引用は出典確認用の最小限の抜粋に留める]

## 飛躍・根拠なし注記

- [材料にない飛躍があれば明示する（ハルシネーション線引き用）]

## 対話ログ（任意）

[LLM との対話の要点。全文を貼ってもよい]

## 昇格ドラフト（promotion-candidate になった時だけ）

- 主張文（subject / predicate / object 形式への翻訳案）:
- 想定典拠（章・話 / ¶ / p）:
```

### 使用上の注意

- 本文は自由記述です。Lint・スキーマ検証の対象外（[Playground 運用則](#rules)）
- 状態が上がったら（`promotion-candidate` 以上）[昇格プロトコル](#promotion) の手順に従う
- 原文（小説本文）の長文引用はしない（引用は本番運用と同じく最小限の抜粋のみ）

## Playground の一覧

- [[kouzetsu]] — 【口舌】の正体（原文 ¶ 照合で確定化した事実＋未検証の推察を併記・`promotion-candidate`）
- [[rakulraal-seat]] — 第一位のラクルラールの座は誰が勝ち取ったのか（4 章ラスト・イツノとマラコーダの会話／原文 ¶ 照合・`promotion-candidate`）
- [[relations-six]] — 六人の関係性マップ（ベアトリーチェの融合先と、アズーリア・レオ・青嶺瑠璃の繋がり／原文 ¶ 照合・`promotion-candidate`・Issue #31）
- [[gogmagog]] — 5-15・5-26 の「ゴグマゴグ」（イギリス伝承の巨人 Gogmagog と聖書のゴグとマゴグの照合／原文 ¶・p 照合済み・`promotion-candidate`・Issue #63→#65）

## 来歴（provenance）

| 項目 | 値 |
|---|---|
| 起案 | Issue #19（Tally 編集提案フォーム経由・依頼者 allusionistwiki） |
| 実装 | llm-task（LLM 編集依頼）による作成 |
| 審査 | `review_status: llm_verified`（LLM 自己審査による暫定承認・人間レビュー未実施） |
| 統合 | 2026-10-24: 昇格プロトコル（promotion）と仮説メモテンプレート（hypothesis-template）の 2 独立ページを本 index ページへ統合。入口を index に一元化し、他ページからの参照は `#promotion` / `#template` アンカーへ |

> [!CAUTION]
> Playground の記述を Core 層のページから wikilink で参照してはいけません（未検証の仮説が正規層の文脈に混入するため）。参照方向は常に **Playground → Core**（材料として読む方向）に限定します。
