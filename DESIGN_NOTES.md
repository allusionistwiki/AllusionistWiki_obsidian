# DESIGN_NOTES.md — 設計判断の記録

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
