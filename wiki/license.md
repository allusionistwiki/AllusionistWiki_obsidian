---
title: ライセンス
description: 本Wikiの分割ライセンス（CC BY-NC-SA 4.0 / CC0 / 第三者素材除外）の説明
---

# ライセンス

本Wikiは、内容に応じて複数のライセンスを適用する**分割ライセンス（Split Licensing）**で提供されます。
One-size-fits-all な単一ライセンスは適用しません。

## 3層構成

| レイヤー | 対象 | ライセンス |
|---|---|---|
| **A** | Wiki本文・独自解説・要約・考察・編纂物 | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **B** | コード・スクリプト・設定ファイル | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)（パブリックドメイン） |
| **C** | 原作本文・抜粋・画像・商標・フォント・第三者素材 | ライセンス対象外（各権利者の権利に従う） |

> 上流ソフトウェア（Quartz本体・npm依存・GitHub Actions）は、それぞれの上流ライセンスに従います。

---

## レイヤーA：Wiki本文（CC BY-NC-SA 4.0）

当Wikiの作者が作成・編集・選択・配列した解説文（episodes/・characters/・terminology/・allusions/・mysteries/・analogies/・reflections/）は、**CC BY-NC-SA 4.0** で提供されます。

### 利用の範囲による帰属表示

| 利用の範囲 | 帰属表示の要件 |
|---|---|
| **ローカル利用**（個人・私的利用・ローカルでの閲覧・編集・バックアップ） | **無制限で許可**（帰属表示不要・条件なし） |
| **ファンの部分利用**（引用・抜粋・参照・部分的コピー・二次創作） | **出典の表示不要**（権利放棄） |
| **リポジトリのコピー**（リポジトリ全体・大規模な再配布） | **厳密な帰属表示必須**（CC BY-NC-SA 4.0 の条件） |

- **ローカル利用**：個人での閲覧・編集・カスタマイズ・バックアップ・オフライン利用には、いかなる条件も付しません。
- **ファンの部分利用**：引用・抜粋・参照・二次創作には、出典リンク・作者名・ライセンス名のいずれも不要です。CC BY-NC-SA 4.0 の帰属表示条件自体も適用されません。
- **リポジトリのコピー**：ミラー・フォーク公開・サイト全体の転載など、リポジトリ全体・大規模な部分を再配布する場合は、CC BY-NC-SA 4.0 の帰属表示条件を厳密に満たしてください（作者名・著作権表示・ライセンス名とURL・出典リンク・変更の表示・同一条件での再配布）。

### 非商用（NC）の含意

CC BY-NC-SA 4.0 の "NC"（NonCommercial）は、「商業的利益または金銭的報酬を主たる目的とする利用」を禁じます。
次のような利用は**商業目的に該当する恐れがあり、本ライセンスでは認められません**：

- 広告収入のあるサイト・動画・ポッドキャストに本Wikiの解説を転載・利用すること
- 投げ銭（チップ・有料会員制・Patreon等）で収益化する媒体に本Wikiの解説を利用すること
- 有料教材・有料記事・有料データベース・有料APIに本Wikiの解説を組み込むこと
- 本Wikiの解説を商業製品・商業サービスの一部として販売・提供すること

### 原作権利者による自動放棄（Rights Holder Auto-Waiver）

CC BY-NC-SA 4.0 の **NC（非商用）条件は、条件付きで付与**されます。
**原作権利者（原作者・出版社・権利者）の承諾を得ていない限り**、NC条件が適用されます。
原作権利者が特定の利用について承諾を与えた場合、その利用に対しては **NC条件が自動的に解除（自動放棄）** され、**商業利用を含む自由な利用が可能**になります。

### LLM 生成への材料利用（新規リポジトリ・Wiki 作成）

本Wikiの内容を **LLM（AI）による新規リポジトリ・Wiki・サイトの作成に材料として利用**する場合、
**主要構成物（主要な材料・構成要素）として使用した場合は、サイト（AllusionistWiki）を材料に使用したことを明記すること**を条件とします。

- 本Wikiの内容を主要な情報源として、LLM に新しい Wiki・分析サイト・解説リポジトリを生成させる場合
- 本Wikiの構造・用語・分析を新しいリポジトリの骨格として利用する場合
- 本Wikiの内容が生成物の実質的な大部分を占める場合

これらの場合、新しいリポジトリ・サイトには**次のすべてを明記**してください：

1. **材料利用の明記**：「本コンテンツの全部または一部は、AllusionistWiki を材料として生成されています」
2. **出典リンク**：<https://allusionistwiki.github.io/AllusionistWiki/>
3. **ライセンス表示**：本Wikiの内容は CC BY-NC-SA 4.0 で提供されています

> **「主要構成物」と「部分的参照」の区別**：
> - **主要構成物**：本Wikiの内容が新著作の主要な情報源である、または実質的な大部分を占める ⇒ **明記必須**
> - **部分的参照**：ごく一部を引用・参照するにとどまる ⇒ 本項の対象外（「ファンの部分利用」を参照）

### 引用・フェアユース

**引用・フェアユース・フェアディーリングの範囲での利用は、本ライセンスの条件に束縛されません。**
CC BY-NC-SA 4.0 は「例外・制限（exception or limitation）が適用される利用には適用されない」と定めています。

---

## レイヤーB：コード・スクリプト・設定（CC0 1.0 Universal）

動作のためのコード・設定・CI・スクリプト類（*.py・*.ts・*.js・*.json・*.yml・CLAUDE.md・fix_typo.py 等）は、**CC0 1.0 Universal（パブリックドメイン）** で提供されます。

CC0 により、著作権を**公衆に献納**します。使用・複製・改変・再配布・サブライセンス・販売の**いかなる利用も無制限に許可**され、**帰属表示も不要**です。商用利用も完全に許可されます。

> 上流Quartz本体（`quartz/`）・npm依存・GitHub Actionsは、それぞれの上流ライセンス（MIT等）に従います。

---

## レイヤーC：第三者素材（ライセンス対象外）

原作小説の本文・抜粋・画像・商標・フォント・スクリーンショット・PDF・EPUBなどの第三者素材は、本Wikiの CC BY-NC-SA 4.0 または CC0 では**ライセンスされません**。
各権利者の権利に従い、引用・フェアユース・フェアディーリング・ファン活動ガイドライン・その他法令上許される範囲でのみ利用してください。

特に `raw/`（原作本文の抽出テキスト）は公開リポジトリに含めず、ローカルのみ保持しています。

---

## AI生成コンテンツに関する注記

本Wikiは、LLMの助けを借りて概念抽出、用語整理、リンク生成、本文作成が行われています。
一部人間による編集、確認を行っていますが、誤り、過剰解釈、存在しない情報の混入が含まれております。
誤りを見つけたら積極的に連絡いただけるとありがたいです。

---

## 免責

本リポジトリは非公式のファン解析Wikiです。原作者、出版社、権利者、開発元とは関係ありません。
本リポジトリの利用により生じた損害について、作者は責任を負いません。

```text
THE LICENSED MATERIAL IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 正式なライセンス文書

詳細は、リポジトリ内の正式なライセンス文書（英文legal code）を参照してください。

| ファイル | 内容 |
|---|---|
| [LICENSE.md](https://github.com/allusionistwiki/AllusionistWiki_obsidian/blob/main/LICENSE.md) | 分割ライセンスの全体説明（日英併記） |
| [NOTICE.md](https://github.com/allusionistwiki/AllusionistWiki_obsidian/blob/main/NOTICE.md) | 上流帰属表示・第三者素材除外・依存関係要約 |
| [LICENSE-CC-BY-NC-SA-4.0.txt](https://github.com/allusionistwiki/AllusionistWiki_obsidian/blob/main/LICENSE-CC-BY-NC-SA-4.0.txt) | CC BY-NC-SA 4.0 の正式な英文legal code |
| [LICENSE-CC0.txt](https://github.com/allusionistwiki/AllusionistWiki_obsidian/blob/main/LICENSE-CC0.txt) | CC0 1.0 Universal の正式な英文legal code |

> **注記**：本ページはLLMの支援で作成されたものであり、法的助言ではありません。
> 最終的な法的判断は、必ず弁護士による確認を受けてください。
> 日本語訳は参考情報であり、法的根拠は各ライセンスの正式な英文legal codeにあります。
