# DESIGN_NOTES.md — 設計判断の記録

## 2026-10-12: org レポジトリマップ・トップ index 層

### 現状（org allusionistwiki・5 repo）
| repo | 正体 | 公開/非公開 |
|---|---|---|
| AllusionistWiki_obsidian | wiki1 vault（現行『幻想再帰…-wiki』） | 公開 |
| AllusionistWiki | wiki1 の Quartz サイト（/AllusionistWiki） | 公開 |
| AllusionistLLMWiki2_Obsidian | wiki2 vault（リバイス版） | 公開 |
| AllusionistLLMWiki2 | wiki2 の Quartz サイト（/AllusionistLLMWiki2） | 公開 |
| AllusionistLLMWiki2_Work | LLM パイプライン作業データ（facts/candidates/locks） | 公開→**非公開化推奨**（原文派生事実を含む） |

### 方針
- **トップ index 層 = org 特別 repo `allusionistwiki.github.io`**（org ルートサイト）。各 wiki のカード（概要・統計・更新）を並べるポータル。wiki 側トップにも `/`（ポータル）へのリンクを置く。
- **wiki 数 = repo 数×2 の現状を、1 wiki あたり vault 1 + サイト 1 の対に固定**（新規 wiki 増設時もこの対）。サイト repo は vault repo を **git submodule** で取り込み、content の複写をしない（単一ソースの原則）。
- 作業データ系（Work）は原文派生テキストを含むため **private 化**。公開 repo には出さない。
- 命名＝URL slug 統一: `AllusionistWiki` / `AllusionistWiki2` / `YuragiWiki`（repo 名 = サイトパス = wiki 名）。LLMWiki2 系は wiki2 として `AllusionistWiki2` へのリネームを推奨（GitHub は同一 org 内リネームで旧 URL からリダイレクトされる）。
- 相互リンク: ポータル↔wiki↔wiki は同一 origin 絶対パス（`/AllusionistWiki2/...`）。Obsidian 内は 1 vault 複数ルートの `[[...]]`。
- 将来の wiki 増設手順: ①vault repo 作成（`<WikiName>`）→ ②サイト repo（Quartz + submodule）→ ③ポータルにカード追加 → ④`tools/data/wikis.json` に登録。

## 2026-10-12: 公開サイトの複数 wiki 配信（allusionistwiki.github.io 構成）

### 決定
- **1 org 直下に wiki ごとに repo を置く project pages 構成**: `allusionistwiki.github.io/AllusionistWiki`（現行・baseUrl 設定済み）／`allusionistwiki.github.io/YuragiWiki`（新 repo `YuragiWiki`）／将来 `…/AllusionistWiki2`。
- **wiki 間リンクは同一 origin の絶対パスで張れる**（例: `/YuragiWiki/characters/トリシューラ/` ↔ `/AllusionistWiki/episodes/CH0001/`）。github.io 同一ドメインなので CORS・相対パス問題なし。
- Quartz の `[[wikilink]]` 解決は 1 repo の content ツリー内に限る。repo を跨ぐ相互リンクは **サイト URL 直書き**（frontmatter `crosswiki:` 欄 or 本文リンク）。変換表は `tools/data/wikis.json`（wiki 名 → baseUrl）を台帳とし、ツールが生成する相互リンクはここから引く。
- `yuragiwiki.github.io` 案は GitHub アカウント（slug）追加が前提で、相互リンクが cross-origin 完全 URL になるため不採用（完全独立の看板が欲しくなった時点で再検討）。
- vault 側は 1 vault 複数ルート（`wiki/`・`yuragi/`）を維持: Obsidian 内は `[[...]]` で相互参照、公開サイトでは URL 相互リンク。graphrag は vault 全体＋共有 raw を単一インデックス。

## 2026-10-12: 複数 wiki 構成 × raw 配置（マルチ wiki 戦略）

### 論点
「アリュージョニストwiki1 / wiki2 / 揺らぎwiki …」の複数 wiki 構成を予定。raw を wiki 外に置くか、アリュージョニストwiki に全部入れるか。

### 決定
1. **raw は wiki の外・共有 private repo（`AllusionistWiki_raw`）に置く**。wiki 内に raw を入れない。
   - 理由①: raw は wiki 間で共有される（揺らぎ BBS はアリュージョニスト分析の一部であり、同一原文を複数 wiki が参照する）。wiki 内配置は原文の複写・同期ズレ・権利管理の分散を招く。
   - 理由②: 公開/非公開の線は repo 単位で引く。wiki repo は全面公開・raw repo は全面 private にすると gitignore 運用が単純（raw を wiki repo に入れると「公開 repo 内の非公開ファイル」が増え、backup・同期が wiki 数だけ必要になる）。
   - 理由③: 参照はファイルパスではなく **manifest ID（ソースID + chNNNNN + ¶N）** で行う。wiki 側は raw の相対パスに依存しない → raw ツリーの移動・再編が wiki を壊さない。
2. **wiki 本体は「1 vault・複数 wiki ルート」で開始する**（`wiki/` の隣に `wiki2/`・`yuragi/` を置く）。
   - Obsidian の wikilink・graph・graphrag は vault 内でしか繋がらない。アリュージョニスト wiki1/wiki2/揺らぎwiki は相互参照が厚くなる（同じ作者・同じ世界観・BBS の交差）ため、vault を割ると知識グラフが切れる。
   - 分割の基準は「相互参照が不要になったら（別作品・別コミュニティ・別ライセンスになったら）repo/vault を切る」。
3. **共有層は vault ルートに集約**: `tools/`・`graphrag_tool/`・`tools/data/raw_manifest.json` は全 wiki 共通。graphrag の `INDEXABLE_TOP` に各 wiki ルート（`wiki`,`wiki2`,`yuragi`）と共有 raw ルート（`../AllusionistWiki_raw/raw`）を追加する。
4. **公開サイト（Quartz）**: 1 サイトで複数 wiki をルート配信（`/allusionist/`・`/yuragi/` …）。相互リンクはサイト URL で繋ぐ。

### 目標レイアウト
```
Code/
├── AllusionistWiki_obsidian/        # vault（公開・CC BY-NC-SA + MIT）
│   ├── wiki/                        # wiki1（現行アリュージョニスト）
│   ├── wiki2/                       # wiki2（将来）
│   ├── yuragi/                      # 揺らぎwiki（将来）
│   ├── tools/  graphrag_tool/       # 全 wiki 共通
│   └── CLAUDE.md                    # wiki ルート共通の規約
├── AllusionistWiki_raw/             # private repo（原文・rights reserved）
│   └── raw/（novel/{pdf,kakuyomu,syosetu} + bbs/{jbbs,mixi}）
└── AllusionistWiki/                 # Quartz サイト（複数 wiki をルート配信）
```

### 典拠・命名
- wiki からの原文参照: `[ソースID:chNNNNN¶N]`（PDF は頁 `p{leaf}`、BBS はコメント連番）。manifest（`tools/data/raw_manifest.json`）が ID→フォルダ対応の唯一の台帳。
- wiki ルート間は `[[...]]`（同一 vault 内）で繋ぎ、raw へのリンクは作らない（切れリンク防止・非公開経路の露出防止）。

## 2026-10-12: raw 一元化・マルチソース戦略（raw/ 再編）

### 背景
原文取得が PDF（→`raw/`）・カクヨム（→`kaku_raw/`）・なろう（→`syosetu_raw/`）・BBS（→`raw_Yuragi_Sinnwa/`）に分散し、ルート名・命名規則・更新手段がソースごとにバラバラになった。今後は作者作品の全ソース（カクヨム7・なろう6・BBS・PDF）を継続対象にする。

### 基本原則
1. **公開/非公開の線は不変**: 派生分析（wiki/）とツール（tools/）のみ公開。原文テキストは非公開（LICENSE.md の「原著作物は除外」＝rights reserved）。
2. **raw は単一ルート `raw/` に一元化**: graphrag は `wiki` + `raw` を再帰インデックスするため、一元化により全ソースの原文が検索対象になる（現状 kaku_raw/syosetu_raw/mixi は graphrag から見えていない）。
3. **フォルダ命名 = `<ソースID>_<小説名>`**: ソースID＝カクヨム serial ID／なろう ncode／mixi comm_id／したらば 板名。小説名は sanitize（`\/:*?"<>|`→／、60字上限）。
4. **マニフェスト**: `tools/data/raw_manifest.json` を全作品の台帳とする（source / id / title / url / folder / episodes取得数 / 最終取得日 / status）。各 `make_raw_from_*.py` が取得後に更新し、**新話検出（差分）→ 増分 ingest** の起点にする。
5. **backup**: raw は wiki の典拠基盤なのに現マシン一元的。GitHub private リポジトリ `AllusionistWiki_raw` を作り、`raw/` をそこで版管理する（公開 repo の .gitignore はそのまま）。
6. **典拠表記**: `ソースID + chNNNNN + ¶N`。¶ 索引はカクヨム（pN）・なろう（L{n}）で統一済み、PDF は頁番号（`【p{leaf}】`）、BBS はコメント連番。

### 目標ツリー
```
raw/
├── novel/
│   ├── pdf/<work_code>_<小説名>/chNNNNN__<タイトル>.md     # 現 raw/ 272話（work_code=pdf01）
│   ├── kakuyomu/<serial_id>_<小説名>/chNNNNN__<タイトル>.md
│   └── syosetu/<ncode>_<小説名>/chNNNNN_<タイトル>[_NN].md
└── bbs/
    ├── jbbs/<板名>/<NNN>_<スレ名>/Thread.md
    └── mixi/<comm_id>/<トピック名>/Topic.md + <topic_id>_topic_comment.md
```
- `RAW2/`（空・PDF中間生成物）は廃止。`kaku_raw/` `syosetu_raw/` `raw_Yuragi_Sinnwa/` ルートは消し、`raw/` に統合。
- 公開 repo の .gitignore は `raw/` 1本に簡素化（kaku_raw/・syosetu_raw/・raw_Yuragi_Sinnwa/ 行は削除）。

### 移行手順（フェーズ）
- **A. 統合**: 4ルートを目標ツリーへ移動（名前の衝突なし、graphrag は再帰 walk なのでサブフォルダ化は安全）。
- **B. 参照追随**: wiki 内の `](raw/` リンクは ch00012・ch00013 の2箇所のみ（log.md は履歴なので旧経路のまま）。CLAUDE.md §1・§2 の raw 命名規約を新構成に改定。
- **C. ツール追随**: 各 make_raw_from_*.py の出力先を新経路へ、manifest 更新処理を追加。graphrag 再構築（自動検出）。
- **D. private repo**: `AllusionistWiki_raw`（private）作成 → raw/ を push。以後 raw 変更は両 repo（private へ commit）で追跡。
- **E. 台帳**: wiki/log.md に移行記録、DESIGN_NOTES に本節、backlog 対応完了。

### 将来の拡張則
- 新ソース追加 = `make_raw_from_<source>.py` 親ツール + manifest の source 種別追加（相対パス・UTF-8・skip既存・--force・¶索引の既存慣習を踏襲）。
- 更新検出 = `tools/raw_status.py`（manifest の取得数 vs サイトの現行話数）→ 差分を backlog 化。
- 1作品1フォルダ・1話1ファイルは不変。分割は `[_NN]`（PDF/なろう）または `①②…`（カクヨムタイトル由来）を許容。
