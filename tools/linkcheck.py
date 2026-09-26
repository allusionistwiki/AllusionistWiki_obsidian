# -*- coding: utf-8 -*-
"""wikilink checker: verify [[...]] targets resolve to real files in wiki/."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # vault root (script in tools/)
WIKI = os.path.join(ROOT, 'wiki')

# collect all basenames (without .md) and full relative paths
basenames = {}   # basename -> [relpath]
for dirpath, dirs, files in os.walk(WIKI):
    for f in files:
        if f.endswith('.md'):
            base = f[:-3]
            rel = os.path.relpath(os.path.join(dirpath, f), WIKI).replace('\\', '/')
            basenames.setdefault(base, []).append(rel)

link_re = re.compile(r'\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]')

targets = sys.argv[1:] if len(sys.argv) > 1 else [WIKI]
broken = {}
total = 0
for t in targets:
    full = os.path.join(ROOT, t) if not os.path.isabs(t) else t
    files = []
    if os.path.isdir(full):
        for dirpath, dirs, fs in os.walk(full):
            files += [os.path.join(dirpath, f) for f in fs if f.endswith('.md')]
    elif os.path.isfile(full):
        files = [full]
    else:
        print('MISSING TARGET:', t); continue
    for fp in sorted(files):
        with open(fp, encoding='utf-8') as fh:
            text = fh.read()
        relfp = os.path.relpath(fp, WIKI).replace('\\', '/')
        for m in link_re.finditer(text):
            total += 1
            target = m.group(1).strip()
            if not target or 'http' in target:
                continue
            ok = False
            if '/' in target:
                # path-qualified: file must exist at wiki/<target>.md (or basename under that folder)
                cand = os.path.join(WIKI, target + '.md')
                ok = os.path.isfile(cand)
                if not ok:
                    sub = basenames.get(target.split('/')[-1], [])
                    ok = any(rel.startswith(target.rsplit('/', 1)[0] + '/') for rel in sub)
            else:
                ok = target in basenames
            if not ok:
                broken.setdefault(target, []).append(relfp)

print(f'links checked: {total}')
if broken:
    print(f'BROKEN ({len(broken)} unique targets):')
    for k in sorted(broken):
        extra = f'+{max(0,len(broken[k])-3)} more' if len(broken[k]) > 3 else ''
        print(' ', k, '<-', broken[k][:3], extra)
else:
    print('ALL LINKS RESOLVE (checked files only)')
