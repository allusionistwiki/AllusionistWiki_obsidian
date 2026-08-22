---
name: spelling-verification
display-name: 綴り間違い検証（Spelling Verification）
description: 日本語作品のwiki作業で、視覚的に区別不能なコードポイント差異（アキラ/アクラ、small-る等）による綴り間違いを検査・統一する前に使用。
user-invocable: true
---

# 綴り間違い対策（Spelling Verification）

## なぜ必要か
本作『幻想再帰のアリュージョニスト』のwiki作業では、「視覚的には同じだがコードポイントのみ異なる」
日本語文字の混入が頻発する。目視では発見不可で、最終確認で見落としやすい。代表例：

- ア U+30AD (a) vs ア U+30AF (ku) → 「アキラ」vs「アクラ」
- る U+308B (小) vs る U+308D (大) → 「きぐみ魔女」の small-る
- ュ/オ の小文字カナ、半角/全角長音の混在

## 方針（最優先）
1. **断定しない**：源原文と既存表記が異なる名称（アキラ／アクラ等）は、改名せず【要検証】として記録のみ。
   勝手に統一しない（→ 事実と解釈の混入になる）。詳細は `glossary.md` の「プロジェクトの判断」参照。
2. **コードポイントで比較する**：文字列リテラルや PowerShell の日本語処理は信頼できない。
   必ず本スクリプト（または `[char]`/コードポイント比較）を使う。
3. glossary.md は「方針・一覧」専用。正確なコードポイントは `check_spelling.py` の出力を根拠にする
   （表を手動で写して正統値にしない）。

## 手順（最終確認时必须／新規生成後）
1. スクリプトを実行してコードポイントレベルで検査する：
   ```powershell
   $env:PYTHONUTF8=1                       # UTF-8 を確実に効かせる（根本対策・下「補足」参照）
   python .agents/skills/spelling-verification/scripts/check_spelling.py .
   ```
2. 出力の「**要注意**」セクションで、同一ファイル内で見た目が同じ文字が複数コードポイントで
   出現している箇所を特定する（そこが綴り不整合の候補）。
3. `glossary.md` の監視一覧と照合し、方針通りならOK、方針未決定なら【要検証】として記録。
4. 誤りがあれば、glossary.md の判断に従って修正（断定不要な箇所は改名せず記録のみ）。

## 補足（作業上の陷阱）
- PowerShell で日本語リテラルを書くと不一致することがある → `[char]0xXXXX` で構築する、または
  ファイル名をディスクから抽出する。
- **文字コード（根本対策・推奨）**：Python の stdout は Windows では locale（cp932）が既定で、
  `chcp 65001` でもパイプ先には反映されない。確実に UTF-8 にするには `$env:PYTHONUTF8=1`（Python
  UTF-8 モード）を先に設定すること（stdout もファイル I/O も UTF-8 で統一）。ターミナル表示まで
  揃えるなら `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` を併用する（Windows 10
  ビルド 1803〜）。`$env:PYTHONIOENCODING="utf-8"` よりも包括的で確実。
- 疑義文字ペアと監視一覧は `glossary.md` にまとめている。

## ファイル構成
- `scripts/check_spelling.py` — コードポイントレベルの検査ツール（中核）
- `glossary.md` — 正統綴りの方針・監視一覧・プロジェクト判断
