# -*- coding: utf-8 -*-
"""
fix_typo.py — wiki 内のtypo・簡体字混入を再帰的にスキャン／一括置換する。

使い方:
  python fix_typo.py --scan <dir>        # ドライラン（何が変わるかの報告のみ）
  python fix_typo.py --fix <dir>         # 実際に置換して上書き
  python fix_typo.py --check <file>      # 単一ファイルの簡体字混入チェック
  python fix_typo.py --report <dir>      # 簡潔なサマリーレポート

環境変数:
  PYTHONUTF8=1  または sys.stdout.reconfigure(encoding='utf-8') でUTF-8固定。

拡張方法:
  既定の置換ルールは外部JSONファイル typo_rules.json に定義する。
  形式: [ [検索文字列, 置換文字列, 説明], ... ]。長い文字列を先に（部分一致の衝突防止）。
  別ファイルを指定する場合は --rules custom_rules.json で外部JSON指定も可能。
"""

import os, sys, re, argparse, json
from pathlib import Path
from collections import defaultdict

# ──────────────────────────────────────────────
# 置換ルールは外部JSONファイル（typo_rules.json）から読み込む。
# 形式: [ [検索文字列, 置換文字列, 説明], ... ]。長い文字列を先に（部分一致対策）。
# 既定ファイルは本スクリプトと同じディレクトリの typo_rules.json。
# ──────────────────────────────────────────────
DEFAULT_RULES_FILE = Path(__file__).resolve().parent / "typo_rules.json"


def load_rules(path: Path) -> list:
    """JSONルールファイルを読み込み、(検索, 置換, 説明) のタプルリストを返す。"""
    with open(path, encoding='utf-8') as f:
        rules = json.load(f)
    return [(s, r, c) for s, r, c in rules]


def get_default_rules() -> list:
    """既定の置換ルールを外部JSONから取得。ファイルが無ければ空リスト（警告）。"""
    if DEFAULT_RULES_FILE.exists():
        return load_rules(DEFAULT_RULES_FILE)
    print(f"⚠ 既定ルールファイルが見つかりません: {DEFAULT_RULES_FILE}", file=sys.stderr)
    return []

# 簡体字専用文字のリスト（日本語のJIS第1・2水準には存在しない）
# これらが混入していたら確実に簡体字混入
SIMPLIFIED_ONLY_CHARS = {
    '\u65F6': '时',   # 時 (簡体形)
    '\u5355': '单',   # 単 (簡体形)
    '\u8BCD': '词',   # 詞 (簡体形)
    '\u4EF7': '价',   # 價 (簡体形)
    '\u9009': '选',   # 選 (簡体形)
    '\u6742': '杂',   # 雜 (簡体形)
    '\u52A1': '务',   # 務 (簡体形)
    '\u961F': '队',   # 隊 (簡体形)
    '\u4E49': '义',   # 義 (簡体形)
    '\u53D1': '发',   # 發/髮 (簡体形)
}

# 簡体と日本語で同一字形の文字（候・人・体・会・社 など）。
# これらは簡体字混入の判定対象から除外する（検出しない・置換もしない）。
# 単字では簡体/日本語の区別が付かないため、必ず SIMPLIFIED_ONLY_CHARS と併用する。
EXCLUDED_SAME_FORM_CHARS = {
    '\u5019': '候',   # 候 — 簡体と日本語で同一
    '\u4EBA': '人',   # 人 — 簡体と日本語で同一
    '\u56FD': '国',   # 国 — 簡体と日本語で同一
    '\u4F53': '体',   # 体 — 簡体と日本語で同一
    '\u4F1A': '会',   # 会 — 簡体と日本語で同一
    '\u793E': '社',   # 社 — 簡体と日本語で同一
}


def scan_file(filepath: Path, replacements: list) -> dict:
    """単一ファイルのtypoを検出し、置換マップを返す。"""
    try:
        text = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError) as e:
        return {'error': str(e), 'lines': 0}

    lines = text.splitlines()
    found = defaultdict(int)
    issues = []

    for i, line in enumerate(lines, 1):
        for search, replace, comment in replacements:
            count = line.count(search)
            if count > 0:
                found[comment.split(':')[0]] += count
                issues.append((i, line.strip()[:200], search, replace, comment))

    # 簡体字専用文字の検出
    simp_found = {}
    for ch, name in SIMPLIFIED_ONLY_CHARS.items():
        if ch in text:
            simp_found[name] = text.count(ch)

    return {
        'lines': len(lines),
        'replacements': dict(found),
        'simplified_chars': simp_found,
        'issues': issues,
    }


def scan_directory(target: Path, replacements: list, recursive=True) -> dict:
    """ディレクトリ内の全.mdファイルをスキャン。"""
    if not target.exists():
        print(f"❌ 存在しません: {target}", file=sys.stderr)
        sys.exit(1)

    if target.is_file():
        return scan_file(target, replacements)

    results = {}
    total_files = 0
    files_with_issues = 0

    files = sorted(target.rglob('*.md')) if recursive else sorted(target.glob('*.md'))

    for f in files:
        r = scan_file(f, replacements)
        if 'error' in r:
            results[str(f)] = r
            continue
        if r['replacements'] or r['simplified_chars']:
            results[str(f)] = r
            files_with_issues += 1
        total_files += 1

    return {
        'total_files': total_files,
        'files_with_issues': files_with_issues,
        'files': results,
    }


def apply_replacements(text: str, replacements: list) -> str:
    """置換ルールを適用して新しいテキストを返す。"""
    for search, replace, _ in replacements:
        text = text.replace(search, replace)
    return text


def fix_directory(target: Path, replacements: list, recursive=True) -> dict:
    """ディレクトリ内の全.mdファイルを置換して上書き。"""
    if not target.exists():
        print(f"❌ 存在しません: {target}", file=sys.stderr)
        sys.exit(1)

    if target.is_file():
        text = target.read_text(encoding='utf-8')
        new_text = apply_replacements(text, replacements)
        target.write_text(new_text, encoding='utf-8')
        return {'files': [str(target)], 'total_changes': sum(1 for s, _, _ in replacements if s in text)}

    files_fixed = []
    total_changes = 0

    files = sorted(target.rglob('*.md')) if recursive else sorted(target.glob('*.md'))

    for f in files:
        text = f.read_text(encoding='utf-8')
        new_text = apply_replacements(text, replacements)
        if new_text != text:
            f.write_text(new_text, encoding='utf-8')
            files_fixed.append(str(f))
            for s, r, _ in replacements:
                total_changes += text.count(s) - new_text.count(s)

    return {'files': files_fixed, 'total_changes': total_changes}


def format_report(scan_result: dict, replacements: list, mode: str):
    """レポートを整形して出力。"""
    print(f"\n{'='*60}")
    print(f"  fix_typo.py — {mode}レポート")
    print(f"{'='*60}\n")

    if 'total_files' in scan_result:
        # ディレクトリモード
        print(f"スキャン済みファイル: {scan_result['total_files']}件")
        print(f"問題ありファイル:     {scan_result['files_with_issues']}件\n")

        if not scan_result['files']:
            print("✅ 問題なし！すべてのファイルがクリーンです。")
            return

        # 全体の集計
        total_counts = defaultdict(int)
        for f_result in scan_result['files'].values():
            for k, v in f_result.get('replacements', {}).items():
                total_counts[k] += v
            for k, v in f_result.get('simplified_chars', {}).items():
                total_counts[f'[簡体字] {k}'] += v

        if total_counts:
            print("── 全体集計 ──")
            for k, v in sorted(total_counts.items(), key=lambda x: -x[1]):
                print(f"  {k}: {v}件")
            print()

        # ファイル別詳細
        print("── ファイル別詳細 ──")
        for fpath, f_result in sorted(scan_result['files'].items()):
            if not f_result.get('replacements') and not f_result.get('simplified_chars'):
                continue

            rel = fpath
            print(f"\n  📄 {rel} ({f_result['lines']}行)")

            if f_result.get('simplified_chars'):
                print(f"     ⚠ 簡体字検出:")
                for ch, count in f_result['simplified_chars'].items():
                    print(f"       {ch} (U+{ord(ch):04X}): {count}件")

            if f_result.get('replacements'):
                print(f"     🔍 置換候補:")
                for term, count in f_result['replacements'].items():
                    print(f"       {term}: {count}件")

            if f_result.get('issues'):
                print(f"     📝 該当行（抜粋）:")
                for line_no, line, search, replace, comment in f_result['issues'][:5]:
                    print(f"       L{line_no}: ...{line}...")
                    print(f"         → '{search}' → '{replace}' ({comment})")
                if len(f_result['issues']) > 5:
                    print(f"       ... 他 {len(f_result['issues']) - 5}件")
    else:
        # 単一ファイルモード
        f_result = scan_result
        print(f"📄 {scan_result.get('target', 'unknown')} ({f_result['lines']}行)\n")

        if f_result.get('simplified_chars'):
            print("⚠ 簡体字検出:")
            for ch, count in f_result['simplified_chars'].items():
                print(f"  {ch} (U+{ord(ch):04X}): {count}件")

        if f_result.get('replacements'):
            print("\n🔍 置換候補:")
            for term, count in f_result['replacements'].items():
                print(f"  {term}: {count}件")

        if not f_result.get('replacements') and not f_result.get('simplified_chars'):
            print("✅ クリーン（問題なし）")

    print(f"\n{'='*60}\n")


def format_summary(scan_result: dict):
    """簡潔なサマリーレポート。"""
    print(f"\n{'='*60}")
    print(f"  fix_typo.py — サマリー")
    print(f"{'='*60}\n")

    if 'total_files' not in scan_result:
        print("ディレクトリスキャンの結果を期待しています。")
        return

    print(f"スキャン済み: {scan_result['total_files']}ファイル")
    print(f"問題あり:     {scan_result['files_with_issues']}ファイル\n")

    if not scan_result['files']:
        print("✅ クリーン！")
        return

    # 全体集計
    total_counts = defaultdict(int)
    for f_result in scan_result['files'].values():
        for k, v in f_result.get('replacements', {}).items():
            total_counts[k] += v
        for k, v in f_result.get('simplified_chars', {}).items():
            total_counts[f'[簡体字] {k}'] += v

    if total_counts:
        print("── 全体集計 ──")
        for k, v in sorted(total_counts.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}件")
    else:
        print("✅ クリーン！")

    # 上位5ファイル
    file_counts = {}
    for fpath, f_result in scan_result['files'].items():
        count = len(f_result.get('replacements', {})) + len(f_result.get('simplified_chars', {}))
        if count > 0:
            file_counts[fpath] = count

    if file_counts:
        top = sorted(file_counts.items(), key=lambda x: -x[1])[:5]
        print(f"\n── 上位5ファイル ──")
        for fpath, count in top:
            print(f"  {fpath}: {count}種")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='wiki 内のtypo・簡体字混入をスキャン／一括置換',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  # スキャン（何が変わるかの報告）
  python fix_typo.py --scan C:/path/to/wiki

  # 一括置換（実際にファイルを上書き）
  python fix_typo.py --fix C:/path/to/wiki

  # 単一ファイルチェック
  python fix_typo.py --check C:/path/to/file.md

  # 簡潔なサマリーレポート
  python fix_typo.py --report C:/path/to/wiki

  # カスタムルールでスキャン（JSONファイル指定）
  python fix_typo.py --scan <dir> --rules custom_rules.json

  # JSON出力（後処理用）
  python fix_typo.py --scan <dir> --json
        """
    )
    parser.add_argument('--scan', metavar='<dir>', help='ディレクトリを再帰スキャン（ドライラン）')
    parser.add_argument('--fix', metavar='<dir>', help='ディレクトリを一括置換（上書き）')
    parser.add_argument('--check', metavar='<file>', help='単一ファイルの簡体字チェック')
    parser.add_argument('--report', metavar='<dir>', help='簡潔なサマリーレポート')
    parser.add_argument('--rules', metavar='<json>', help='カスタム置換ルールJSONファイル')
    parser.add_argument('--json', action='store_true', help='結果をJSONで出力')
    args = parser.parse_args()

    # 置換ルール読み込み（既定は外部JSON typo_rules.json、--rules で上書き）
    replacements = get_default_rules()
    if args.rules:
        replacements = load_rules(Path(args.rules))

    if args.scan:
        target = Path(args.scan)
        result = scan_directory(target, replacements)
        if args.json:
            # issuesは巨大なのでJSON出力から除外
            clean = {k: v for k, v in result.items()}
            if 'files' in clean:
                clean['files'] = {k: {kk: vv for kk, vv in v.items() if kk != 'issues'}
                                  for k, v in clean['files'].items()}
            print(json.dumps(clean, ensure_ascii=False, indent=2))
        else:
            format_report(result, replacements, 'スキャン')

    elif args.fix:
        target = Path(args.fix)
        result = fix_directory(target, replacements)
        print(f"✅ {result['total_changes']}件の置換を {len(result['files'])}ファイルに適用")
        if result['files']:
            print("\n変更済みファイル:")
            for f in result['files']:
                print(f"  {f}")

    elif args.check:
        target = Path(args.check)
        result = scan_file(target, replacements)
        result['target'] = str(target)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            format_report(result, replacements, 'チェック')

    elif args.report:
        target = Path(args.report)
        result = scan_directory(target, replacements)
        format_summary(result)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
