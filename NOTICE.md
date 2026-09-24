# NOTICE

本リポジトリは分割ライセンス（Split Licensing）で提供されています。

## License summary

- **Wiki 本文・独自解説・要約・考察・編纂物**：CC BY-NC-SA 4.0
- **コード・スクリプト・CI・設定ファイル**：MIT License
- **原作本文・抜粋・画像・商標・フォント・第三者素材**：ライセンス対象外（各権利者の権利に従う）
- **上流 OSS**：各々のオリジナルライセンスに従う

詳細は `LICENSE.md` を参照してください。

---

## CC BY-NC-SA 4.0

Wiki 本文は次に従います。

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

<https://creativecommons.org/licenses/by-nc-sa/4.0/>

全文（正式な英文 legal code）：

`LICENSE-CC-BY-NC-SA-4.0.txt`

---

## MIT License

コード・設定ファイルは次に従います。

MIT License

Copyright (c) 2026 AllusionistWiki contributors

全文：

`LICENSE-MIT.txt`

---

## Third-party materials

本リポジトリには、次のような第三者素材が含まれる、または含まれていた可能性があります。

- 原作小説の本文、抜粋、要約元資料
- 画像、イラスト、表紙、スクリーンショット
- ロゴ、商標、キャラクター名称
- フォント、アイコン、CSSライブラリ
- Quartz 本体
- Node.js / npm パッケージ
- GitHub Actions 上の第三者 Action

これらの素材は、本リポジトリの CC BY-NC-SA 4.0 または MIT License では**ライセンスされません**。
各権利者の権利に従い、法令上許される範囲、または権利者の許諾範囲内でのみ利用してください。

特に `raw/` ディレクトリに原作本文や長文引用がある場合は、
**公開リポジトリから削除するか、非公開リポジトリに移動してください**。
本リポジトリでは `raw/` は `.gitignore` により公開対象から除外されています。

---

## Upstream software

本プロジェクトは Quartz 等のオープンソースソフトウェアを利用する場合があります。

上流ソフトウェアは、それぞれの上流リポジトリに記載されたライセンスに従います。
本 NOTICE は上流ライセンスを変更・置換するものではありません。

確認方法例：

```bash
# npm dependencies のライセンスを確認する場合
npx license-checker --summary

# または
npm ls --depth=0
```

### 依存関係のライセンス要約

本リポジトリ（Obsidian vault）は npm パッケージに依存しません（純 Markdown vault）。
`npx license-checker` は実行対象がありません。

Web 公開版（`AllusionistWiki` リポジトリ）の依存関係のライセンス要約は、
そちらの `NOTICE.md` を参照してください。

---

## AI-assisted content notice

本 Wiki は、LLM の助けを借りて概念抽出、用語整理、リンク生成、本文作成が行われています。
一部人間による編集、確認を行っていますが、誤り、過剰解釈、存在しない情報の混入が含まれております。
誤りを見つけたら積極的に連絡いただけるとありがたいです。

---

## Disclaimer

```text
THIS SOFTWARE AND DOCUMENTATION ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

本リポジトリの内容は、明示黙示を問わず、いかなる保証もなく提供されます。
本リポジトリの利用により生じた損害について、作者は責任を負いません。
本リポジトリは非公式のファン活動であり、原作者、出版社、権利者、開発元とは関係ありません。

---

> **注記**：本ドキュメントは LLM の支援で作成されたものであり、法的助言ではありません。
> 最終的な法的判断は、必ず弁護士による確認を受けてください。
