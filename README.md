# 幻想再帰のアリュージョニスト Wiki（Obsidian vault）

「ネットミームから現代思想まで引喩が散りばめたオカルトパンク」——本作の多層アナロジー（引喩・神話参照・展開の相似/相違）を典拠付きで体系化する分析Wiki。[Obsidian](https://obsidian.md/) vaultとして運用します。

**Web公開版: https://allusionistwiki.github.io/AllusionistWiki/** （[Quartz](https://quartz.jzhao.xyz/) でビルド・[GitHub Pages](https://pages.github.com/) にデプロイ）

## 構成（2リポジトリ方式）

| リポジトリ | 役割 |
|---|---|
| `AllusionistWiki_obsidian`（本リポジトリ） | Obsidian vault本体（ソース・オブ・トゥルース）。`wiki/` がQuartzのcontentになる |
| [`AllusionistWiki`](https://github.com/allusionistwiki/AllusionistWiki) | Quartzプロジェクト＋GitHub Pagesデプロイ設定。vaultの内容はCIが取得してビルドする |

## ディレクトリ構造

```
幻想再帰のアリュージョニスト-wiki/
├── CLAUDE.md            # 設計書（schema・命名規約・ワークフロー・鉄則）
├── wiki/                # ★Obsidian vault（ここに書く。Web公開の対象）
│   ├── index.md         # トップページ（Quartzのホームページになる）
│   ├── status.md        # トップカタログ・状態管理
│   ├── log.md           # 操作履歴（追記のみ）
│   ├── episodes/        # 1話ごと：要約+人物+引喩+感想+疑問
│   ├── characters/      # 事実ページ（初出/名称/関係/典拠）
│   ├── terminology/     # 用語glossary（グループ＋単語の2階層）
│   ├── allusions/       # ★核心層：Mythology/Literature × external/internal
│   ├── mysteries/       # 未解決の謎・伏線のタスク管理
│   ├── analogies/       # ★再帰構造マップ
│   └── reflections/     # ★感想専用層（事実から分離）
├── raw/                 # 原文抽出（不変・ローカルのみ・非公開）
└── fix_typo.py          # typo一括修正ツール（typo_rules.json参照）
```

## Web公開の仕組み

1. このリポジトリにpushする（またはQuartz側で毎時スケジュール発火）
2. [`AllusionistWiki`](https://github.com/allusionistwiki/AllusionistWiki) のCIが `wiki/` を取得して `npx quartz build`
3. GitHub Pages にデプロイ（vaultのSHAが変わらなければスキップ）

> 即時反映したい場合は、Quartzリポジトリの Actions → Deploy → Run workflow を手動実行。

## 運用ルール（要約）

詳細は [CLAUDE.md](./CLAUDE.md) を参照：

- **推測や原文にない情報を足さない**。事実ページと感想層は物理的に別ディレクトリ
- 用語・人物・組織は**言及された時点でページを作成**する（後でまとめて作る禁止）
- ページ間リンクは `[[...]]` wikilink に統一。全リンクが実ファイルへ解決すること
- 事実行には典拠（pp./raw）を付与。推測はラベル付き
- typo発見時は `fix_typo.py --scan / --fix` で一括修正

## License

本リポジトリは**分割ライセンス（Split Licensing）**で提供します。

| レイヤー | 対象 | ライセンス |
|---|---|---|
| A | Wiki 本文・独自解説・要約・考察・編纂物（`wiki/**/*.md`） | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| B | コード・スクリプト・設定ファイル（`*.py`, `*.json`, `CLAUDE.md` 等） | コードライセンス（無保証・責任免責） |
| C | 原作本文・抜粋・画像・商標・フォント・第三者素材 | ライセンス対象外（各権利者の権利に従う） |

- 詳細は [LICENSE.md](./LICENSE.md) と [NOTICE.md](./NOTICE.md) を参照してください。
- 正式な英文 legal code：[LICENSE-CC-BY-NC-SA-4.0.txt](./LICENSE-CC-BY-NC-SA-4.0.txt) / [LICENSE-CODE.txt](./LICENSE-CODE.txt)
- 本リポジトリは**非公式のファンWiki**であり、原作者・出版社・権利者とは関係ありません。
- 原作「幻想再帰のアリュージョニスト」の著作権は原作者に帰属します。

> `raw/`（原文抽出テキスト）・作業用一時ファイルはローカルのみ保持し、このリポジトリには含めません（`.gitignore` 済み）。
