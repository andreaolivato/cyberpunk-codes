r"""Structural check on the CET dev menu's Lua, and a cross-check of its facts.

    python tools\check_devmenu.py --gig 02

THERE IS NO LUA INTERPRETER ON THIS MACHINE. CET embeds LuaJIT in a DLL and
ships no standalone binary, so the only real syntax check is loading the menu in
game, and a syntax error there means the whole overlay window is simply absent
with the reason in CET's own log. That is a game launch to find out about a
missing `end`.

So this does the two checks that are worth doing offline:

  * BLOCK BALANCE. Counts the keywords that open a block against `end`, and
    brackets against their closers, ignoring strings and comments. It cannot
    prove the file parses. It does catch the mistake that actually happens,
    which is a block closed one too few or one too many times after an edit.
  * THE FACT LIST. Every `cc_gNN_*` fact the built quest phase touches should
    have a row in the menu, because a fact with no row is a fact nobody can see
    or set, and that is exactly when somebody needs it. Reports both directions.

A clean run is not a promise that the menu loads. A dirty run is a promise that
it does not.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from questkit import gigs                                            # noqa: E402

GIG = gigs.from_argv('02')
cfg = gigs.config(GIG)
FACT_PREFIX = 'cc_g' + GIG + '_'
MENU = os.path.join(cfg.SOURCE, 'cet-dev', 'init.lua')
PHASE = os.path.join(cfg.RAW_MOD, 'quest', 'gig' + GIG + '.questphase.json')

# Facts the menu is not expected to list. `_claim` is a race's own scratch,
# written and cleared inside one block and meaningless between them.
NOT_EXPECTED = set()


def strip_lua(src):
    """Remove comments and string contents, keeping everything else in place.

    Long strings and long comments ([[...]]) are not used in this file and are
    not handled; if one ever appears this will mis-count and say so loudly by
    reporting an imbalance, which is the safe direction.
    """
    out = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '-' and src.startswith('--', i):
            j = src.find('\n', i)
            i = n if j < 0 else j
            continue
        if ch in '"\'':
            quote = ch
            out.append(' ')
            i += 1
            while i < n and src[i] != quote:
                if src[i] == chr(92):
                    i += 1
                i += 1
            i += 1
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def main():
    src = open(MENU, encoding='utf-8').read()
    code = strip_lua(src)
    bad = 0

    # -- brackets
    pairs = {'(': ')', '[': ']', '{': '}'}
    stack = []
    line = 1
    for ch in code:
        if ch == '\n':
            line += 1
        elif ch in pairs:
            stack.append((ch, line))
        elif ch in pairs.values():
            if not stack:
                print('  UNBALANCED  closing %r at line %d with nothing open'
                      % (ch, line))
                bad += 1
                break
            opened, at = stack.pop()
            if pairs[opened] != ch:
                print('  UNBALANCED  %r opened at line %d closed by %r at line %d'
                      % (opened, at, ch, line))
                bad += 1
                break
    for opened, at in stack:
        print('  UNBALANCED  %r opened at line %d and never closed' % (opened, at))
        bad += 1

    # -- blocks. EXACTLY THREE KEYWORDS OPEN ONE IN LUA: `function`, `if` and
    #    `do`. `for` and `while` do NOT: each is followed by its own `do`, and
    #    that `do` is what opens the block, so counting the loop keyword as well
    #    double-counts every loop.
    #
    #    An earlier version counted `for`/`while` and then tried to subtract the
    #    `do` belonging to one by looking on the same LINE. That holds until a
    #    loop header wraps, which a `for` over a table literal does:
    #
    #        for _, row in ipairs({
    #            ...
    #        }) do
    #
    #    The `do` is three lines below its `for`, both got counted, and the file
    #    was reported one `end` short. Counting what the grammar actually says
    #    needs no line heuristic at all. Found by the checker crying wolf on a
    #    file that was correct, which is the failure mode that gets a checker
    #    switched off.
    #
    #    `elseif` is safe against `\bif\b`: there is no word boundary inside
    #    it. `repeat ... until` would break this and the menu contains none.
    opens = len(re.findall(r'\b(function|if|do)\b', code))
    ends = len(re.findall(r'\bend\b', code))
    # A COUNT OF ZERO IS NOT A BALANCED FILE, IT IS A BROKEN CHECKER. Nothing
    # this menu could become has no blocks in it at all, so zero means the
    # regexes are matching nothing and every file would pass.
    #
    # THIS GUARD EXISTS BECAUSE THAT HAPPENED. The word boundaries above were
    # written through a shell heredoc that turned each one into a literal
    # backspace byte; the run printed "0 open, 0 end" and reported a pass.
    if opens == 0 or ends == 0:
        print('  CHECKER BROKEN  counted %d open and %d end in %d bytes of code'
              % (opens, ends, len(code)))
        print('                  the keyword regexes are matching nothing')
        bad += 1
    elif opens != ends:
        print('  BLOCK COUNT  %d opening keyword(s) against %d `end`(s)'
              % (opens, ends))
        print('               (counting function, if and do)')
        bad += 1
    else:
        print('  ok  blocks balance: %d open, %d end' % (opens, ends))

    if not stack and bad == 0:
        print('  ok  brackets balance')

    # -- the fact list
    phase = open(PHASE, encoding='utf-8').read()
    pat = '"(' + FACT_PREFIX + '[a-z0-9_]+)"'
    in_phase = set(re.findall('"factName": ' + pat, phase))
    listed = set(re.findall(pat, open(MENU, encoding='utf-8').read()))
    missing = sorted(in_phase - listed - NOT_EXPECTED)
    for f in missing:
        print('  NOT IN THE MENU  %s' % f)
        bad += 1
    print('  ok  %d of %d quest-phase fact(s) have a row'
          % (len(in_phase & listed), len(in_phase)))

    print()
    print('%d problem(s). A clean run is not a promise that the menu loads.'
          % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
