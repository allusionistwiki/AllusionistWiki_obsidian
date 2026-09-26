# 仮 CH を正規 ch 基準（syosetu 272 話）に順次変換 ＋ ch220 相当まで episode 生成
- 受付日: 2026-09-26
- ステータス: in-progress
- 出典: ユーザー指示（順次変換・1話間隔 push・最新話まで継続）

## 指示原文
> 先にch⇒CH変換を実施したので、まず正しい順序・分割が何かを調べ、今の仮CHから正しいch基準に順次変換。
> 1話間隔でpushして、最新話まで更新を続けて。

## 補足・制約
- 正規 ch 基準 = syosetu 272 エピソード（`tools/data/syosetu_toc.json`、URL `https://ncode.syosetu.com/n9073ca/{1..272}/`）
- 旧 CH→syosetu マッピング（167 件）は `tools/data/wiki_to_syosetu.json`
- RAW2/ は 272 ファイル生成済み（`chNNN__タイトル.md`・二重アンダースコア・PDF 由来・gitignore）
- 現行 wiki は仮 CH（`CH0001.md`–`CH0167.md`）のまま。これを正規 ch 基準に**順次**変換する
- 1 話生成ごとに push（ユーザー常設指示）
- 捏造禁止：raw に存在しない主張は書かない。人物ページの頁番号は必ず raw で検証

## 進捗（着手中・都度更新）
- 2026-09-26: 正本調査完了（syosetu 272 話・PDF bold 縦書きタイトル 317 件→前書き/後書き変種 46 件除去→272 話）。RAW2/ 272 ファイル生成・ch146/ch177 境界 off-by-one 修正済み・ch120 前書き開始は OK 承認済み。
- 2026-09-26: tools/ 集約・相対パス化・CLAUDE.md 反映・backlog/ 機構導入 完了（コミット済み）。
- 次の一手: 仮 CH（CH0001–CH0167）を正規 ch 基準に順次変換を開始。変換ルール（バンドル 9 件・1:1 158 件）を `tools/data/wiki_to_syosetu.json` と突き合わせ、1 話ずつ wiki/episodes/・reflections/ を正規話番号へ改名・中身の典拠頁を RAW2 基準に修正しつつ進める。
