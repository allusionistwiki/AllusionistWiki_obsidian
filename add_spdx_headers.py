#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-AllusionistWiki-Code
"""
add_spdx_headers.py — 分割ライセンス用の SPDX-License-Identifier ヘッダー注入ツール

レイヤーA（Wiki本文・独自解説）→ CC BY-NC-SA 4.0
  Markdown:  <!-- SPDX-License-Identifier: CC-BY-NC-SA-4.0 -->
レイヤーB（コード・スクリプト・設定）→ コードライセンス（無保証・責任免責）
  //, #, /* */ 形式のコメントで // SPDX-License-Identifier: LicenseRef-AllusionistWiki-Code

使い方:
  python add_spdx_headers.py --dry-run        # 何が変わるかだけ表示（変更しない）
  python add_spdx_headers.py --apply          # 実際にヘッダーを挿入
  python add_spdx_headers.py --dry-run --root wiki   # 指定ディレクトリのみ

対象の判定:
  - .md          → CC-BY-NC-SA-4.0（Markdown HTMLコメント）
  - .py          → LicenseRef-AllusionistWiki-Code（# コメント）
  - .ts/.js/.jsx/.tsx → LicenseRef-AllusionistWiki-Code（// コメント）
  - .yml/.yaml   → LicenseRef-AllusionistWiki-Code（# コメント）
  - .json        → 非対応（JSONにコメント不可。SPDXはpackage.jsonのlicenseフィールドで管理）
  - .css         → LicenseRef-AllusionistWiki-Code（/* */ コメント）
  - .sh          → LicenseRef-AllusionistWiki-Code（# コメント）

既存の SPDX ヘッダーがあるファイルはスキップする（重複挿入しない）。
"""
import argparse
import os
import re
import sys

# 拡張子 → (SPDX識別子, コメント形式)
# コメント形式: 'line' = 行頭コメント, 'block' = /* */ ブロック
CODE_SPDX = 'LicenseRef-AllusionistWiki-Code'
EXT_MAP = {
    '.md':    ('CC-BY-NC-SA-4.0', 'md'),
    '.py':    (CODE_SPDX, 'py'),
    '.ts':    (CODE_SPDX, 'js'),
    '.js':    (CODE_SPDX, 'js'),
    '.jsx':   (CODE_SPDX, 'js'),
    '.tsx':   (CODE_SPDX, 'js'),
    '.yml':   (CODE_SPDX, 'py'),
    '.yaml':  (CODE_SPDX, 'py'),
    '.css':   (CODE_SPDX, 'css'),
    '.sh':    (CODE_SPDX, 'py'),
}

SPDX_RE = re.compile(r'SPDX-License-Identifier:')


def build_header(spdx_id: str, style: str) -> str:
    if style == 'md':
        return f'<!-- SPDX-License-Identifier: {spdx_id} -->\n'
    if style == 'py':
        return f'# SPDX-License-Identifier: {spdx_id}\n'
    if style == 'js':
        return f'// SPDX-License-Identifier: {spdx_id}\n'
    if style == 'css':
        return f'/* SPDX-License-Identifier: {spdx_id} */\n'
    raise ValueError(f'unknown style: {style}')


def has_spdx(text: str) -> bool:
    # 先頭20行以内にSPDXがあれば既存とみなす
    head = '\n'.join(text.splitlines()[:20])
    return bool(SPDX_RE.search(head))


def process_file(path: str, apply: bool) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext not in EXT_MAP:
        return 'skip(no-rule)'
    spdx_id, style = EXT_MAP[ext]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except (UnicodeDecodeError, OSError) as e:
        return f'skip(error:{e})'

    if has_spdx(text):
        return 'skip(has-spdx)'

    header = build_header(spdx_id, style)
    new_text = header + text
    if apply:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        return f'inserted({spdx_id})'
    return f'would-insert({spdx_id})'


def main() -> int:
    ap = argparse.ArgumentParser(description='SPDX ヘッダー注入ツール')
    ap.add_argument('--root', default='.', help='対象ディレクトリ（既定: 現在ディレクトリ）')
    ap.add_argument('--apply', action='store_true', help='実際に書き込む（既定はdry-run）')
    ap.add_argument('--dry-run', action='store_true', help='dry-run（既定）')
    args = ap.parse_args()

    apply = args.apply and not args.dry_run

    # 除外ディレクトリ
    EXCLUDE = {'.git', 'node_modules', '.obsidian', '.graphrag', 'quartz',
               '__pycache__', 'public', '.quartz-cache', 'raw', '_temp',
               '_example_pre_rebuild', '.agents', 'assets'}

    count = {'inserted': 0, 'skip': 0, 'error': 0}
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, args.root)
            try:
                result = process_file(path, apply)
            except Exception as e:
                print(f'ERROR {rel}: {e}')
                count['error'] += 1
                continue
            if result.startswith('inserted') or result.startswith('would-insert'):
                count['inserted'] += 1
                print(f'{result:20s} {rel}')
            elif result.startswith('skip(error'):
                count['error'] += 1
                print(f'{result:20s} {rel}')
            else:
                count['skip'] += 1

    mode = 'APPLY' if apply else 'DRY-RUN'
    print(f'\n[{mode}] inserted={count["inserted"]} skip={count["skip"]} error={count["error"]}')
    if not apply:
        print('（dry-run: 実際には書き込みしていません。--apply で実行してください。）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
