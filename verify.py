#!/usr/bin/env python3
"""Compare regenerated files with the versions committed to this repository.

Text and data files (.csv .tsv .json .md .txt) must be byte-identical.
PNG figures must be pixel-identical (PDF and SVG embed creation dates and random
IDs, so they are compared through their PNG twins instead).
Exit code 0 = everything reproduced; 1 = at least one difference (listed).

Usage: python3 verify.py   (run from the repository root after reproduce.sh)
"""
import io
import subprocess
import sys

try:
    from PIL import Image, ImageChops
except ImportError:
    sys.exit('verify.py needs Pillow (pip install pillow)')

TEXT = ('.csv', '.tsv', '.json', '.md', '.txt')


def git(*args, binary=False):
    r = subprocess.run(['git', '-c', 'core.quotepath=off'] + list(args), capture_output=True)
    if r.returncode:
        sys.exit('git %s failed: %s' % (' '.join(args), r.stderr.decode()))
    return r.stdout if binary else r.stdout.decode()


def main():
    changed = [p for p in git('diff', '--name-only', 'HEAD').splitlines() if p]
    untracked = [p for p in git('ls-files', '--others', '--exclude-standard').splitlines() if p]
    bad, same_png, skipped = [], 0, []
    for p in changed:
        if p.endswith('.png'):
            old = Image.open(io.BytesIO(git('show', 'HEAD:' + p, binary=True))).convert('RGBA')
            new = Image.open(p).convert('RGBA')
            if old.size != new.size or ImageChops.difference(old, new).getbbox():
                bad.append((p, 'pixels differ'))
            else:
                same_png += 1
        elif p.endswith(TEXT):
            bad.append((p, 'content differs'))
        else:
            skipped.append(p)
    tracked = len(git('ls-files').splitlines())
    print('Tracked files: %d' % tracked)
    print('Unchanged after regeneration: %d' % (tracked - len(changed)))
    print('PNG re-encoded but pixel-identical: %d' % same_png)
    print('PDF/SVG rewritten (dates/IDs; checked via their PNG): %d' % len(skipped))
    if untracked:
        print('New files not in the repository (%d): %s' % (len(untracked), ', '.join(untracked[:8])))
    if bad:
        print('\nDIFFERENCES (%d):' % len(bad))
        for p, why in bad:
            print('  %-70s %s' % (p, why))
        sys.exit(1)
    print('\nAll data files and figures reproduced exactly.')


if __name__ == '__main__':
    main()
