r"""Syntax-check the CET Lua before it reaches the game.

    python tools\check_lua.py                 # every init.lua in the repo
    python tools\check_lua.py <path> [...]    # just these

WHY IT IS NOT JUST A PARSER CALL. `luaparser` accepted a file the game refused
with "unfinished string near '"'". A string literal that had been broken across
a real newline parsed clean here and failed in `sol`, so the CET mod did not
load at all and its window simply was not there. Nothing announced it except
the mod's own log, which nobody thinks to read when the symptom is "I do not see
the button".

So this does two passes:

1. `luaparser`, which catches ordinary mistakes.
2. A quote-balance check per line, which catches the one the parser missed. A
   line with an odd number of unescaped double quotes has a string running off
   the end of it.

The second pass is the one that earns its place. Run this before copying any
Lua into the game folder.
"""
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def unbalanced(path):
    """Lines whose double quotes do not close. Comments are skipped, and so are
    escaped quotes, which are what a naive count gets wrong."""
    out = []
    for i, line in enumerate(io.open(path, encoding='utf-8'), 1):
        stripped = line.strip()
        if stripped.startswith('--'):
            continue
        # Drop escaped quotes before counting, so \" does not read as a quote.
        counted = re.sub(r'\.', '', line)
        if counted.count('"') % 2 == 1:
            out.append((i, stripped[:70]))
    return out


def check(path):
    problems = []
    try:
        from luaparser import ast
        ast.parse(io.open(path, encoding='utf-8').read())
    except ImportError:
        print('  (luaparser not installed, only the quote check ran)')
    except Exception as exc:
        problems.append('parse error: %s' % exc)
    for line_no, text in unbalanced(path):
        problems.append('line %d: a string does not close -> %s' % (line_no, text))
    return problems


def main():
    targets = sys.argv[1:]
    if not targets:
        for root, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
            for f in files:
                if f.endswith('.lua'):
                    targets.append(os.path.join(root, f))
    bad = 0
    for path in targets:
        problems = check(path)
        rel = os.path.relpath(path, REPO)
        if problems:
            bad += 1
            print('FAIL  %s' % rel)
            for p in problems:
                print('        %s' % p)
        else:
            print('  ok  %s' % rel)
    print()
    if bad:
        raise SystemExit('%d file(s) would not load in game.' % bad)
    print('every Lua file is loadable')


if __name__ == '__main__':
    main()
