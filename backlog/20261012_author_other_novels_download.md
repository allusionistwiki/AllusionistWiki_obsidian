# 作者の他作品ダウンロード（なろう・カクヨム）
- 受付日: 2026-10-12
- ステータス: in-progress
- 出典: ユーザー指示（原文をそのまま記載）

## 指示原文
> なろう、カクヨムの最近先生の他の小説もダウンロードしておいて。

## 補足・制約
- 対象: 『幻想再帰のアリュージョニスト』作者（なろう n9073ca / カクヨム work 16816927859268545348）の他の小説（最近のもの）
- 保存先: 原文なので raw/・kaku_raw/ と同じく非公開扱い（gitignore 対象）の新ディレクトリを想定
- カクヨム抽出は `tools/make_raw_from_kakuyomu.py`（段落アンカー焼き込み版）を work_id 一般化して流用
- 保存時に ¶索引（段落番号＝#pN アンカー）を焼き込む（2026-10-12 抽出拡張に準拠）

## 進捗
- 2026-10-12: 着手。作者特定から開始。
- 2026-10-12: 作者=最近（saikin、カクヨム @saikin / なろう mypage 227614）。カクヨム 23 作品を `tools/data/saikin_kaku_works.json`、なろう 11 作品を `tools/data/saikin_syo_works.json` に登録。
- 2026-10-12: 新ツール `tools/make_raw_from_syosetu.py` 作成・検証（n9073ca ch1: 1058段落、`<p id="L{n}">` 通し番号ベース、¶索引つき）。`.gitignore` に `kaku_raw_others/`・`syosetu_raw/` 追加（非公開）。
- 2026-10-12: バックグラウンドジョブ proc_804555e51eec 起動。フェーズ1=本編 kaku_raw 589話の ¶索引版再取得（~548話残、502で1回クラッシュしたため障害耐性版 `_temp/refetch_main_resilient.py` に差し替え）、フェーズ2=カクヨム他22作品→`kaku_raw_others/<work_id>/`＋なろう11作品→`syosetu_raw/<ncode>/`（`_temp/download_saikin_others.py`）。ログ: `_temp/refetch_main.log` / `_temp/download_others.log`。
- 次の一手: 完了通知後に失敗話（502等）の再試行、¶索引突合、log.md/status.md 更新、backlog 完了記録。
- 2026-10-12: 【訂正】プロフィールページスクレイピングの23/11作品は他作者の推薦作品を含む汚染リストだった（ユーザー指摘）。正しい作者作品は公式一覧から **カクヨム7作品**（`/users/saikin/works` の UserAccount:16816410413891167936、totalPublicWorks=7）／**なろう6作品**（`mypage.syosetu.com/mypage/novellist/userid/227614/`）。汚染データ削除（kaku_raw_others 全消去）、両 JSON を正しいリストに更新、実行中ジョブを kill して再起動（proc_1f75d30b3b32、カクヨム6作品＋なろう6作品、本編は除く）。

- 2026-10-12: フォルダ命名変更（カクヨム=小説名／なろう=ncode＋小説名）および `kaku_raw_others/` を `kaku_raw/` に統合（7作品フォルダ、衝突なし）。`.gitignore` の `kaku_raw_others/` 行は不要のため削除。
