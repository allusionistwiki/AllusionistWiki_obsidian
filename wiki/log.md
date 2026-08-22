# 操作履歴（追記のみ）
## 2026-08-22（再始動・第001話生成）
- **正解フォルダ（幻想再帰のアリュージョニスト-wiki）をp1から再構成**。
  - 設計書 CLAUDE.md・spelling-verification スキルは既存。旧誤字フォルダ内容の退避済み（_example_pre_rebuild/）。
  - raw抽出：PDF leaf 4〜107（pp.4–107、pypdf）→ 
aw/001_無彩色の左手、鎧の右手_01.md。
  - 生成：episodes/ch001.md・characters/（品森晶／キール／カイン／テール／アズーリア／トッド／マフス）・world/世界槍と階層・異獣・魔将.md・llusions/徳川家康・三方原の戦い.md・nalogies/recursion-map.md・
eflections/by-episode/ch001.md。
  - lint：全 [[ ]] が実ファイルへ解決（切れ0）。index.md/log.mdを新規作成。
- 既知の問題：ch002〜ch003のwiki生成は未着手（元内容は誤字フォルダにのみ存在・要確認）。

## 2026-08-22（第002話生成）
- **第002話（１－２　死者を代弁する者, pp.108–170）完結**：episodes/ch002.md・characters/アズーリア・ヘレゼクシュ.md・characters/ヲルヲーラ.md・reflections/by-episode/ch002.md を新規生成。
- 更新：characters/品森晶（アキラ）.md（外世界人／次元移動者・誤転生仮説追加）、world/世界槍と階層・異獣・魔将.md（外世界人／次元移動者・魔導書・金鎖体系セクション追加）。
- index.md/log.md更新。ch002を✅マーク、raw/003の「未抽出」を修正（実存在を確認）。
- 既知の問題：ch003以降のwiki生成は未着手。

## 2026-08-22（第003話生成）
- **第003話（幕間　きぐるみの魔女, pp.171–182）完結**：episodes/ch003.md・characters/イェレイド.md・characters/マーネロア.md・reflections/by-episode/ch003.md を新規生成。
- 第三勢力（イェレイド／マーネロア／ガドール）の会合・エスフェイル死因（時間干涉呪術）・第五階層の自由市場／闇市場の起源・隻腕義手の男（アキラくん）の由来を記録。
- lint全確認：ch001〜ch003 の [[ ]] 切れ0、cross-sections も切れ0。`lint.py`（ワークルート直下、後で削除予定）で自動検証。
- 既知の問題：第004話以降のwiki生成は未着手（raw/に241ファイル存在）。

## 2026-08-22（第005話 ch005.md の壊れ修正・対策記録）
- **背景**：別エージェントが文脈消失前に ch005.md（episodes/ch005.md）の綴り修正中→手渡し文档で引き継ぎ。同文档の「3バグ」リストは**過小**。
- **網羅スキャンの結果、壊れは限定的（実質2カ所）**と判明。全文を作り直すより**部分修正**が速く、既存分析を保持できるためそちらを選択。
  - **23行目**：`同時` の「时」= **U+65F6（簡体字）** → U+6642「時」。あわせて散文の壊れ `初しめち財北` を rawの意味（「初めて財北を体験」）で復元→ `初の財北`。
  - **58行目**：`命を救うある也有る。` → `命を救うことも。`（rawの正解と完全一致）。
  - **誤検出の教訓**：`奇衲反擢` は表示だけ壊れているように見えたが、実バイトは `0x5947 奇 / 0x8872 襲 / 0x53cd 反 / 0x64e2 撃` = **奇襲反撃**（標準日本語）。PowerShell stdout(cp932)が文字名を壊していただけ。スキャン時 `会/与/単/長/覚/語/説` なども**標準日本語**のため誤って簡体字と判定→真に簡体字のみ（运/袭/击等、日本語では使わない文字）で再スキャンし確定。
- **最終検証**：簡体字漢字 **0件**、ASCII英語リークは意図語(leaf/raw/episode/reflections)のみ。23・58行目はコードポイントで両確認。
- **根本原因**：日本語を `shell(cp932) → Python stdout` に通すとバイトが壊れる（`gensousaiki.pdf` p1抽出時の事象と同一）。
- **対策（本次第で適用・以降も準拠）**：
  - ファイル書き込みは必ず `open(..., encoding='utf-8')` で明示エンコード。
  - 日本語リテラルは shell に渡さず、**コードポイント(`\uXXXX`)ベース**で構築・置換。
  - 確認も Python で生文字列を抽出（`find`/スライス）しコードポイント表示。
  - 公式のエンコード根本対策は spelling-verification SKILL.md の「補足」→ **`$env:PYTHONUTF8=1`** が推奨（`PYTHONIOENCODING` より包括）。同ドキュメントを根拠元として参照。

## 2026-08-22（GraphRAG ツールの導入・不具合修正）
- **Git管理**：wiki vault を git レポジトリ化（初度コミット dda7fe6）。`.gitignore` で `.graphrag/`・`__pycache__/`・`.obsidian/` を除外。`graphrag_tool/` を追跡対象に追加。
- **GraphRAG**（`graphrag_tool/graphrag_search.py`）を導入。外部APIキー不要・標準ライブラリのみ・オフライン動作。
  - 手法：BM25（Markdown チャンク）＋ リンクグラフの BFS 文脈拡張。
  - **4不具合を修正**：
    1. BM25 `__init__` で `tf[t][d]` でドキュメント用 list を dict キーに指定 → `TypeError`（crash）。df のみの計算に変更（tf は再計算関数で利用）。
    2. `math.log` を使用だが `import math` 欠落 → `NameError`。追加。
    3. `search()` が `n_files` を返さず `main()` で `KeyError`。返り値に追加。
    4. `--json` 時にステータス行が stdout に混入し JSON を壊す → `if not args.json:` で保護し純粋な JSON を出力。
  - **グラフ実体化**：本 vault は `[[...]]` ではなく `[text](url)` の markdown リンクを使用（`[[...]]` 0件）。`extract_targets()` で両方を抽出・basename 解決により辺を構築。67辺・20ノードが確認でき、リーフページからの近傍展開（depth3で8ページ）で文脈拡張が動作することを確認。
- **検証**：`python graphrag_search.py --query "..." --json` で BM25 ランキング＋グラフ拡張が正常動作。`py_compile` 通る。
- **環境メモ**：本 vault はパスの日本語（リ=U+30RIA）により shell/ツールから直接参照不可。回避策：PowerShell 変数で `$f.FullName` 取得後使用、ファイル操作は ASCII パスの作業ディレクトリへ binary copy で行う。日本語出力は `[Console]::OutputEncoding=UTF8` ＋ `Out-File -Encoding utf8`（BOM 付）または `utf-16`/`utf-8-sig` で読み取り。
## 2026-08-22（GraphRAG セマンティック融合のバグ修正・検証・環境記録）
- **_rrf() の IndexError を修正**（コミット 4fac776）。
  - **根本原因**：RRF 融合関数 _rrf() が出力リストを**エントリ数**(out = [0.0] * len(ranks_a))でサイズ指定し、**チャンクインデックス**でアクセスしていた。_to_ranks() は正スコアのドキュメントのみ省略するため、拡張クエリ（
anks_b）だけで正値を持つチャンクがインデックス外 → IndexError: list index out of range で crash。
  - **修正**：出力を**両マップの最大キー +1**でサイズ指定し、combined[i] が chunk_meta[i] と位置アラインメントすることを保証（ページマージが依存）。defaultdict 置換はアラインメントを壊すため避けた。
- **セマンティック融合の検証**（6 クエリ・BM25 のみ vs 融合 を比較）：全クエリで crash 解消。**実益あり**と確認。
  - ヲルヲーラ：専用 characters/ヲルヲーラ.md が先頭へ浮上（BM25 の場合は ch003 の奥に隠れていた）。
  - 時間干涉 因果殺し：関連する ガドール.md を追加取得（BM25 の場合は見逃し）。
  - その他は同一の関連ページ群を改善された順序で返す。
  - 手法：co-occurrence クエリ拡張 + RRF（BM25 と融合）。外部 API キー不要・標準ライブラリのみ。既定 SEMANTIC_ENABLED=True（ON）、--no-semantic で無効。
- **グラフの更新方法**（新規ドキュメント化）：
  - インデックスは初回のみ構築し .graphrag/index.json にキャッシュ。**ソース変更は content_hash() で自動検出**され、次回の実行で自動的に再構築される。
  - 手動再構築：.graphrag/ を削除して次回実行（またはクエリを再度実行）。
  - グラフ源：本 vault は [text](url) の markdown リンクを知識グラフ辺として利用（[[...]] は 0 件）。wiki/ と 
aw/ がインデックス対象、.git・.obsidian・.agents・_example_pre_rebuild・graphrag_tool は除外。
  - CLI：python graphrag_tool/graphrag_search.py --query "..." [--top N] [--depth N] [--json]（既定 depth=1）。
- **環境面の変化・新規律（本次第で適用・今後も準拠）**：
  - **エンコード根本対策**：Python の stdout を UTF-8 に固定。**$env:PYTHONUTF8=1** を推奨（PYTHONIOENCODING=utf-8 より包括）。これで 殺（U+6D89）等 cp932 で書けない文字も出力可能。
  - **編集ワークフロー**：本 vault パスは日本語（リ=U+30RIA）のため、file tool（edit_file_tool/
eplace_file）や shell のリテラルから直接参照不可。**ASCII パスの作業ディレクトリへ binary copy したコピーで編集・実行**し、完了後 Copy-Item で vault へ上書き戻し（UTF-8 を保持）。
  - **メモ**：[System.IO.File]::CopyFile はこの shell では未対応 → Copy-Item を使用。存在確認は Test-Path（Test-Item ではない）。diff/同一性確認は SHA で。

## 2026-08-22（第006話 幕間『悪夢』生成）
- **第006話（幕間『悪夢』, pp.306–310、約5ページ）完結**：episodes/ch006.md・reflections/by-episode/ch006.md を新規生成。
  - 要約：アキラの明晰夢・死の反復（地獄のような第五階層での無限ループ）→ 青い造花の庭園での自己俯瞰 → 渇望の正体を「未来へ繋いでくれたものから解放されたいという矛盾した意思」と定義 → 正体不明の声（「アクラくん、私が、頭を良くしてあげるよ」）による意識の解体・覚醒。
  - 引喩：デカルトの夢の論証／悪魔の仮説（明晰夢から cogito の不確実性へ＝【相当有力】）、馬鹿は死んだ治らない（ことわざ）、ロック的自我理論（記憶による同一性）。
  - 新キャラクターページは不要（正体不明の声は未命名・要検証で疑問ノートのみ記録）。アキラのトラウマ描写なので characters/キール.md 等への追記は範囲外と判断。
- 更新：wiki/index.md（第006話行追加＋感想を「ch001〜ch006」へ）、wiki/episodes/index.md（第006話行・arc bullet追加＋進捗「6話」へ）。
- **既知の修正**：episodes/index.md の進捗欄に `raw/` が `aw/` にバイト欠落した壊れがあったのを復元。
- lint確認：ch006/ch006 reflection の `[[ ]]` はすべて実ファイル（キール／コルセスカ等、既存ページ）へ解決。新切れリンクなし。
- 次タスク：第007話（魔女と狂犬）以降の生成。raw/ に 241 ファイル（220話＋21断章）残る。