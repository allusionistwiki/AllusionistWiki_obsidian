# License

本リポジトリは、内容に応じて複数のライセンスを適用します（分割ライセンス / Split Licensing）。
One-size-fits-all な単一ライセンスは適用しません。

法的根拠は各ライセンスの**正式な英文 legal code** にあります。
日本語訳は参考情報であり、法的根拠として使用しません。

---

## 1. Wiki 本文・独自解説・編纂物（レイヤーA）

次のような、当リポジトリの作者が作成・編集・選択・配列した解説文は、
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International**
略して **CC BY-NC-SA 4.0** で提供されます。

対象の例：

```text
wiki/**/*.md
wiki/episodes/**/*.md
wiki/characters/**/*.md
wiki/terminology/**/*.md
wiki/allusions/**/*.md
wiki/mysteries/**/*.md
wiki/analogies/**/*.md
wiki/reflections/**/*.md
```

また、Quartz によって生成・配信されるサイト本文中の、上記 Wiki 起源のテキストも同様に CC BY-NC-SA 4.0 と扱ってください。

### CC BY-NC-SA 4.0 の条件（要約）

- **Attribution（表示）**：作者名・著作権表示・ライセンス表示・変更の表示・実務的に可能な範囲での URI/ハイパーリンクを付与すること。
- **NonCommercial（非商用）**：商業目的での利用を禁じます（後述）。
- **ShareAlike（同一条件での再配布）**：改変・派生物を頒布する場合、同一の CC BY-NC-SA 4.0（または互換ライセンス）で頒布すること。
- **No additional restrictions（追加制限の禁止）**：ライセンスが許可する利用を法的に制限する条件や技術的措置を付加してはなりません。

### NonCommercial（NC）の具体的含义

CC BY-NC-SA 4.0 の "NC"（NonCommercial）は、「商業的利益または金銭的報酬を主たる目的とする利用」を禁じます。
次のような利用は**商業目的に該当する恐れがあり、本ライセンスでは認められません**：

- 広告収入のあるサイト・動画・ポッドキャストに本 Wiki の解説を転載・利用すること
- 投げ銭（チップ・有料会員制・Patreon 等）で収益化する媒体に本 Wiki の解説を利用すること
- 有料教材・有料記事・有料データベース・有料 API に本 Wiki の解説を組み込むこと
- 本 Wiki の解説を商業製品・商業サービスの一部として販売・提供すること

一方、次のような利用は**非商用に該当する限り**本ライセンスで認められます：

- 個人・非営利目的での私的利用・学習目的の利用
- 広告収入のない個人ブログ・非営利団体による引用・転載（表示条件を満たす場合）
- 学術研究・教育目的での利用（商業目的を主目的としない場合）

> 境界が曖昧な利用（例：収益化の可否が不明なプラットフォーム）は、権利者に直接確認してください。
> 「おそらく大丈夫だろう」という判断は法的に有効ではありません。

### 原作権利者による自動放棄（Rights Holder Auto-Waiver）

本リポジトリが定める CC BY-NC-SA 4.0 の **NC（非商用）条件は、条件付きで付与**されます。
具体的には、**原作権利者（原作者・出版社・権利者）の承諾を得ていない限り**、NC 条件が適用されます。

原作権利者が特定の利用について承諾を与えた場合、その利用に対しては **NC 条件が自動的に解除（自動放棄）** され、
**商業利用を含む自由な利用が可能**になります。本Wiki編集者は、NC 制限を原作権利者の承諾に条件付けた形で付与しており、
原作権利者の承諾が得られた時点で NC 制限は自動的に失効します。

- 原作権利者の承諾なし：CC BY-NC-SA 4.0 が適用（非商用・表示・同一条件での再配布）
- 原作権利者の承諾あり：NC 条件が自動解除され、商業利用を含む自由な利用が可能（承諾が許容する範囲で）

> 原作権利者からの承諾を得た場合は、その承諾の内容（範囲・条件・有効期間）を記録し、
> 利用時にその承諾に基づいていることを表示してください。

---

## 2. コード・スクリプト・設定ファイル（レイヤーB）

次のような、動作のためのコード・設定・CI・スクリプト類は、
**MIT License** で提供されます。

対象の例：

```text
*.py
*.sh
*.js
*.ts
*.jsx
*.tsx
*.json
*.yml
*.yaml
*.toml
*.css
Dockerfile
Makefile
package.json
package-lock.json
quartz.config.ts
quartz.layout.ts
.github/workflows/**
CLAUDE.md
fix_typo.py
move_resolved.py
typo_rules.json
graphrag_tool/**
```

ただし、次を除きます：

- 第三者が著作権を持つコード
- 上流 OSS のコード
- npm パッケージ
- Quartz 本体（`quartz/` ディレクトリは上流リポジトリのライセンスに従う）
- 原作・出版社・権利者が管理する素材
- 画像、フォント、アイコン、商標、ロゴ
- 原作本文、長文引用、スクリーンショット、PDF、EPUB など

この MIT License は、LICENSE.md で定めた範囲、つまり**コード・スクリプト・設定ファイル**に適用されます。
Wiki 本文や原作素材には適用しません。

---

## 3. ライセンス対象外の第三者素材（レイヤーC）

以下の内容は、本リポジトリの CC BY-NC-SA 4.0 または MIT License では**ライセンスされません**。

```text
raw/**
assets/third-party/**
images/**
screenshots/**
*.pdf
*.epub
*.mobi
*.azw
*.txt  ※原作本文であることが明らかなファイル
fonts/**
logos/**
trademarks/**
```

これらは、各権利者の権利に従います。
引用、フェアユース、フェアディーリング、ファン活動ガイドライン、その他法令上許される範囲でのみ利用してください。

特に `raw/` に原作小説の本文、抜粋、テキストデータ、PDF、EPUB などがある場合は、
**公開リポジトリに置かないことを強く推奨します**。
本リポジトリでは `raw/` は `.gitignore` により公開対象から除外されています。
公開リポジトリに原作本文が含まれている場合は、著作権侵害（複製権・公衆送信権・翻案権の侵害）となる恐れがあります。

---

## 4. 上流ソフトウェアについて

本リポジトリは Quartz、Node.js パッケージ、GitHub Actions、その他第三者ソフトウェアを利用する場合があります。
それらはそれぞれのオリジナルライセンスに従います。
本リポジトリの LICENSE が上流ライセンスを上書きすることはありません。

例：

- **Quartz 本体**：上流リポジトリ（jackyzha0/quartz）の LICENSE に従う（MIT）
- **npm dependencies**：各パッケージの LICENSE に従う
- **GitHub Actions**：GitHub の利用規約および各 Action のライセンスに従う

---

## 5. 帰属表示と利用の寛容性

利用の範囲に応じて、帰属表示の要件を2段階に分けます。

| 利用の範囲 | 帰属表示の要件 |
|---|---|
| **ファンの部分利用**（引用・抜粋・参照・部分的コピー・二次創作） | **出典の表示不要**（権利放棄） |
| **リポジトリのコピー**（リポジトリ全体・大規模な再配布） | **厳密な帰属表示必須**（CC BY-NC-SA 4.0 の条件） |

### ファンの部分利用（出典不要・CC帰属表示条件も不要）

ファンによる**部分利用**（非商用）については、著作権者（本Wikiの編集者）が**出典の表示を不要**とします。

- 記事の一部を引用・抜粋・参照する
- 特定のページ・用語・人物の記述を自分のブログ・SNS・二次創作に使う
- 感想・解釈・仮説（`wiki/reflections/` 解釈層）を共有・転載する
- 上記のいずれかを改変・派生させて二次創作する

これらに対しては、**出典のリンク・作者名・ライセンス名のいずれも不要**です。
**CC BY-NC-SA 4.0 の帰属表示（Attribution）条件自体も、部分利用には適用されません。**
権利を行使しません。商用利用・第三者への転売・有料提供のみ、別途権利者への確認が必要です。

> 解釈層（`wiki/reflections/`）は事実ページとは異なる解釈層であり、
> 本項の「出典不要・CC帰属表示条件不要」が特に明確に適用されます。

### リポジトリのコピー（厳密な帰属表示必須）

**リポジトリ全体・大規模な部分**をコピーして再配布する場合（ミラー・フォークの公開・
サイト全体の転載など）は、CC BY-NC-SA 4.0 の帰属表示条件を**厳密に**満たしてください。
次の**すべて**を揃えてください：

1. **作者名・Wiki名**：`AllusionistWiki contributors`（または各ページの著者名）
2. **著作権表示**：`© AllusionistWiki contributors`
3. **ライセンス名とURL**：`CC BY-NC-SA 4.0`（<https://creativecommons.org/licenses/by-nc-sa/4.0/>）
4. **出典のリンク**：リポジトリURL（<https://github.com/allusionistwiki/AllusionistWiki_obsidian>）
5. **変更の表示**：改変した場合はその旨を明記し、以前の改変の表示を保持する
6. **同一条件での再配布**：派生物を CC BY-NC-SA 4.0（または互換ライセンス）で頒布する

例（リポジトリコピー時の表示）：

```text
AllusionistWiki
© AllusionistWiki contributors
Licensed under CC BY-NC-SA 4.0.
https://creativecommons.org/licenses/by-nc-sa/4.0/
Source: https://github.com/allusionistwiki/AllusionistWiki_obsidian

This is an unofficial fan wiki. Not affiliated with the original author,
publisher, or rights holders.
Third-party materials are not included in this license.
```

### 引用・フェアユース

**引用・フェアユース・フェアディーリングの範囲での利用は、本ライセンスの条件に束縛されません。**
CC BY-NC-SA 4.0 は「例外・制限（exception or limitation）が適用される利用には適用されない」と定めています。
したがって、批評・評論・研究・教育目的での短い引用は、帰属表示の簡略化も含め自由に行えます。

### 非公式ファンWikiであること

本リポジトリは非公式のファンWikiであり、原作者・出版社・権利者とは関係ありません。
原作本文、画像、商標、第三者素材は本ライセンスに含まれません。

---

## 6. AI 生成コンテンツに関する注記

本 Wiki の一部は、LLM の助けを借りて概念抽出、用語整理、リンク生成、下書き作成が行われている可能性があります。
人間による編集、確認、典拠付けを行っていますが、誤り、過剰解釈、存在しない情報の混入が含まれる可能性があります。
事実として記載されているように見える内容も、必ず原文および権利情報を確認してください。

---

## 7. 免責

本リポジトリは非公式のファン解析 Wiki です。
原作者、出版社、権利者、開発元とは関係ありません。

本リポジトリの利用により生じた損害について、作者は責任を負いません。

```text
THE LICENSED MATERIAL IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

ライセンスされた素材は、明示黙示を問わず、保証なしで提供されます。

---

## 8. Summary

| レイヤー | 対象 | ライセンス |
|---|---|---|
| A | Wiki 本文・独自解説・要約・考察・編纂物 | CC BY-NC-SA 4.0 |
| B | コード・スクリプト・CI・設定ファイル | MIT License |
| C | 原作本文・抜粋・画像・商標・フォント・第三者素材 | ライセンス対象外（各権利者の権利に従う） |
| — | 上流 OSS（Quartz, npm, GitHub Actions） | 各々のオリジナルライセンス |

---

> **注記**：本ドキュメントは LLM の支援で作成されたものであり、法的助言ではありません。
> 最終的な法的判断は、必ず弁護士による確認を受けてください。
> 日本語訳は参考情報であり、法的根拠は各ライセンスの正式な英文 legal code にあります。
