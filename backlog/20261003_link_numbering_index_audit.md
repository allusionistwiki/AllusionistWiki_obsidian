# 20261003 — wikiリンク・～話表記・index登録の整合性監査と修正計画

- **受付日**: 2026-10-03
- **ステータス**: pending（ユーザー承認待ち）
- **指示原文（verbatim）**: 「wikiリンクの不整合　～話の不整合　インデックス系への登録漏れが多数存在します。現状と問題点を調べ修正計画を立ててください」

## 監査結果（2026-10-03 実測・log.md 除く）

### A. wikiリンク
- basename 解決切れ: **0**（Phase 6a で解消済み）
- **basename 重複 225 件**:
  - chNNNNN 204 件（episodes/ と reflections/by-episode/ の同名）→ 裸の `[[chNNNNN]]` 16 件が曖昧（Obsidian の解決順に依存）
  - **characters/ と terminology/単語（一覧）/ の同一語 18 ペア**（アーザノエル・イアテム・エーラマーン・カタルマリーナ・グレイシス・グレンデルヒ＝ライニンサル・セレクティ・トバルカイン・ドラトリア・ナタリエル・ヘリステラ・マロゾロンド・ラクルラール・リーエルノーレス・レストロオセ・冥道の幼姫（セレス）・牙猪・白のメートリアン）。内容は DIFFER（両ページに固有記述あり）
  - allusions のグランギニョル 1 件（M_External と L_External に重複）
  - `_index`×6・`index`×6（フォルダ index・想定内）
- **曖昧な裸リンク 441 件**（19 ターゲット。上位: グレンデルヒ＝ライニンサル 92・ラクルラール 70・イアテム 51・冥道の幼姫 38・マロゾロンド 33・カタルマリーナ 27・レストロオセ 23）

### B. ～話表記
- `第N話` トークン **3732 件**（旧話番号 147 種、すべて ch_mapping.json に解決先あり・stale 0）
  - episodes/reflections 本文内: 724 件 → **ユーザー指示によりスキップ対象**（旧「第～話」見出し記事は書き直さない）
  - **外側 3008 件**（recursion-map 584・Open_Questions 442・Foreshadowing 231・episodes/index 223・status 182・Resolved 156・terminology/index 27・characters 各所）→ 旧番号のまま新 syosetu 番号体系と不整合
- 見出し: episodes 旧式 148/221・reflections 旧式 120/204（スキップ対象）

### C. index 登録漏れ
- terminology/index.md: 単語ページ 842 件中 **128 件未登録**
- allusions `_index`: M_External 88 件中 **14 件**、L_External 137 件中 **22 件** 未登録
- episodes/index.md: 221 件中 **29 行欠落**（ch00013/040/041/044/049/055/058/107/112–115/118/198–205/207/212–218）
- status.md 進捗行: **53 話欠落**（ch00012/013/039/040/041/043/044/048/049/054/055/057/058/092–119 一部/146/177/198–205/207/212–218）
- **groups/ からのリンク: 842 語中 788 語がどのグループページからも参照されていない**（§3 の 2 階層運用が形骸化）
- characters/（320 ページ）に対応する index ページが存在しない

## 修正計画（承認後実施）

### Phase A — リンク曖昧性解消（441+16 件）
1. 18 重複ペアの**主ページを指定**: 人物・勢力は characters/ を主、用語語義は terminology/ を主と判定（ペアごとに内容比較して決定）。従側は「主ページへリンクする節」へ縮約し、固有記述は主ページへ統合（原文典拠は維持）
2. 残る裸リンクは**パス修飾**（`[[characters/イアテム]]` 等）で解決先を確定。allusions 内の裸 `[[chNNNNN]]` 8 件は `[[episodes/chNNNNN]]` へ
3. グランギニョル重複は 1 ページへ統合（L_External 主）＋もう一方は削除しリンク更新
4. 検証: 曖昧裸リンク 0・basename 重複（ch を除く）0・切れ 0

### Phase B — 外側の「第N話」表記の正規化（3008 件）
1. ch_mapping.json（old_ch→new_ch）＋ pp 参照は boundaries.json leaf 境界で解決し、`第N話` → `[[episodes/chNNNNN]]`（alias は既存表記を維持）へ置換。対象: recursion-map・Open_Questions・Resolved・Foreshadowing・episodes/index・status・terminology/index・characters 等の**記事本文外**
2. episodes/reflections 本文（724 件）は**スキップ**（ユーザー指示）
3. 検証: 外側の `第N話` 残 0・linkcheck BROKEN 0

### Phase C — index 登録の補完
1. terminology/index.md に未登録 128 語を追記（漢字/カタカナ表へ）
2. allusions `_index` に 36 件追記（M_External 14・L_External 22）
3. episodes/index.md に欠落 29 行、status.md に欠落 53 行を追加（raw リンク・pp 範囲は boundaries.json から生成）
4. groups/ の再建: 842 語を 4 グループ（呪術と力体系／宇宙論と世界構造／種と勢力・外世界人／組織と市場）へ keyword 分類で自動割当 → 人手レビュー → 不足グループの新設（§3「グループは生き物」）。788 語のリンクをグループページへ追記
5. characters/index.md 新規作成（320 ページ一覧）
6. 検証: 全ページが最低 1 つの index/group から到達可能（孤立 0）

### Phase D — 最終 lint・記録
- fix_typo --scan クリーン・linkcheck BROKEN 0・status 更新・backlog 完了記録・log.md 追記・commit/push

### 実施順と目安
A → B → C → D（A の統合判断が B のリンク解決先に影響するため A 先行）。各 Phase 完了ごとに commit/push。

## 進捗
- 2026-10-03: 監査完了、計画記載。
- 2026-10-03: **Phase A 完了・push（`adffdd87`）** — 18 重複ペア characters/ 主統合（ユーザー方針: 全部 characters/ 主）、曖昧裸リンク 438 件パス修飾、裸 [[chNNNNN]] 16 件 episodes/ 化、グランギニョル統合。曖昧 0・切れ 0
- 2026-10-03: **Phase B+C 完了・push（`89270de6`）** — 外側 第N話 2965 件を [[episodes/chNNNNN|第NNNNN話]] 化（unresolved 0）／terminology/index +146・allusions _index +35・episodes/index +24 行・status +53 行・characters/index.md 新規 320 件・groups/ 再建 842 語（その他・雑 新設 414 語）。検証: 切れ 0・外側 第N話 0・groups 未リンク 0・typo クリーン。※コミットメッセージは Phase B 表記だが Phase C 変更も同コミットに含む
- 残: Phase D（最終 lint 完了・backlog 削除）— 本件完了確認後に実施。groups/「その他・雑」414 語の人手レビューは任意タスク
