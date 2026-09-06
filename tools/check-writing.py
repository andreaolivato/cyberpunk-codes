r"""Fail the writing that keeps coming back.

    python tools\check-writing.py            # everything, grouped by file
    python tools\check-writing.py --player   # only what a player reads
    python tools\check-writing.py --quiet    # exit code only

WHY THIS EXISTS

A style guide is a habit, and a habit does not survive a long session. On
2026-09-05 one convoluted sentence about the voices ("V, Johnny, Mama Welles and
Nix are heard only in lines the game already recorded for them") was written
once and copied into fourteen files before anyone read it aloud. Playtest, the
same day: "why do you write so complex lines". It was not the first time, and
the rule had been written down for weeks.

So the rules that CAN be checked are checked here, and `build-release.ps1`
refuses to build a zip until the player-facing half passes.

TWO AUDIENCES, TWO STANDARDS

  PLAYER   the changelog, the mod page, the shipped READMEs. No word a player
           would have to look up, and short sentences. This is the strict half.
  MODDER   the playbooks, the architecture notes, the code comments. Technical
           words are fine where the technical word is the right one; the shape
           rules still apply.

WHY THE TWO HALVES ARE CHECKED DIFFERENTLY

The player files are small, entirely rewritten for this release, and read by
people who did not build the thing. They are checked whole and they must pass.

The modder documents are years of accumulated writing, and a decision on
2026-08-16 was that committed prose keeps its spaced hyphens rather than being
swept. So only the lines you have ADDED since the last commit are checked
there. That is the writing that has not been read yet, which is the writing
this exists to catch. `--all` overrides it when a real pass is wanted.

WHAT IT CANNOT DO

It cannot tell you a sentence is bad. Every rule here is a string match, so it
finds the tells that have actually bitten this project and nothing else. A
sentence can pass every check and still be unreadable. Read it aloud.

THIS FILE HOLDS THE STRINGS IT BANS, DELIBERATELY. Exclude it from any bulk
edit over the prose: a sweep that rewrites the patterns turns the check into
one that passes everything, silently.
"""
import argparse
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ the files
# STRICT: what a player reads, and only that. The mod page is split, because
# its "Under the hood" section is deliberately written for modders and says so;
# public/README.md is the repo's own front page and is modder-facing too. Both
# were in this list for one draft and produced 30 false hits, which is how a
# check gets switched off.
#
# The changelog is checked FROM THE TOP DOWN TO THE SECOND VERSION HEADING.
# Older entries shipped and are not rewritten, so flagging them is noise.
# Named by shape rather than by path, so a checkout that has no mod-page copy
# simply checks the changelog and moves on.
PLAYER_GLOBS = [
    ('CHANGELOG.md', 'newest'),
    ('docs/release/*/*changelog*.bbcode', 'newest'),
    ('docs/release/*/*description*.bbcode', 'player-half'),
]

# Everything else written as prose. The numbered registers are excluded: they
# are records rather than documents, they must never be swept, and their
# entries are frozen once closed. A file that is not present is skipped, so a
# checkout with fewer docs checks what it has.
MODDER_DIRS = ['docs', 'mods/gig-01-negative-balance/docs']
MODDER_SKIP_SUFFIX = ('gotchas.md', 'backlog.md', 'dialogue.txt')
MODDER_EXTRA = ['BUILDING.md', 'CONTRIBUTING.md', 'public/README.md',
                'mods/gig-01-negative-balance/source/scripts/README.md']

# ------------------------------------------------------------------ the rules
# Words a player has no reason to know. Checked in PLAYER files only.
JARGON = [
    'stringId', 'string id', 'RUID', 'vanilla_sid', 'locVoiceoverMap',
    'questphase', 'quest phase', 'lipmap', 'streamingsector', 'streaming sector',
    'TweakDB', 'TweakDBID', 'LocKey', 'wem', 'corpus', 'quest graph',
    'workspot', 'NodeRef', 'mappin', 'cr2w', 'archive.xl', 'depot',
    'generator', 'repo', 'commit', 'regenerate', 'the pipeline',
]
# ...except where the word genuinely is the plainest one, or names a thing the
# player installs. Each of these is a decision, not a tidy-up.
JARGON_OK = re.compile(r'zzz-never-matches', re.I)

# Constructions that read as machine-written. These are the ones that have
# actually appeared here, not a general passive detector: a general one flags
# half of every technical document and gets switched off.
LIMP = [
    'are heard only', 'is heard only', 'are performed by', 'is performed by',
    'are addressed by', 'is addressed by', 'are carried by', 'is carried by',
    'it is worth noting', 'it should be noted', 'it is important to',
    'serves to ', 'acts as a ', 'in order to ',
    # Sentences that point at their own content instead of delivering it.
    # "The one thing that decides the performance: he is not frightened" is
    # "he is not frightened".
    'the one thing that decides', 'the thing to know is',
    'the part worth reading', 'what is worth knowing',
]

# Figures of speech standing in for a plain statement. A line does not "sit
# wide of" a comic, it is different from it. Nothing physical is happening in
# any of these, so the metaphor makes the reader translate for nothing. This
# list only holds the ones already caught here: a new one gets through, which
# is why the rule is also written down for a person to apply.
FIGURATIVE = [
    'wide of the', 'sit a little wide', 'sits a little wide',
    'close rather than exact', 'lands harder', 'lands as',
    'left the dialogue', 'set against what', 'is set against',
    'reads as an', 'reads as a ',
]

# The stock phrases a finding gets wrapped in when nobody is reading carefully.
# Checked everywhere, because they read as generated wherever they appear.
TELLS = [
    'that bite', 'will bite you', 'the catch is', 'the trap here',
    'watch out for', "here's where it gets tricky", 'the gotcha is',
    'worth knowing by shape', 'does not survive contact with',
    'that is the whole trick', 'everyone misses',
    'two things that', 'three things that',
]

# "literally" is allowed before a verbatim quote and nowhere else.
INTENSIFIERS = ['genuinely', 'literally']

# Built from code points, not typed: a file that ships must not itself contain
# the characters it bans, or it flags its own source.
DASH = re.compile('%s|%s|(?<=[a-z]) - (?=[a-z])' % (chr(0x2014), chr(0x2013)))
# A house rule: never tell the reader a thing is other than it appears.
# The clause withholds the fact for a beat and the next sentence always
# carries the meaning without it. Verbatim quotes are exempt by the same
# convention as the punctuation check.
THAN_IT = re.compile(
    r'(more|less|narrower|wider|simpler|smaller|bigger|worse|better|harder|easier)\s+than\s+(it|you|one)\b'
    r'|than (it|you)(\s+would|\s+might|\'d)?\s+(looks?|sounds?|seems?|reads?|think|expect)'
    r'|\bcounter-?intuitively\b|\bsurprisingly\b', re.I)
INSIDE = re.compile(r'[a-z]\.\)|[a-z]\."(?!\w)')
SENTENCE = re.compile(r'[^.!?\n]+[.!?]')

PLAYER_MAX_WORDS = 35
MODDER_MAX_WORDS = 50


def strip_markup(text):
    """Drop the parts no reader reads as prose: code, tables, bbcode tags."""
    out = []
    in_fence = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('```') or s.startswith('[code]') or s.startswith('[/code]'):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith('|') or s.startswith('    ') or s.startswith('#'):
            continue
        line = re.sub(r'\[/?[a-z0-9=#\-\.:/@\?&]+\]', '', line, flags=re.I)   # bbcode
        line = re.sub(r'`[^`]*`', 'X', line)                                  # inline code
        line = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line)                  # md links
        out.append(line)
    return '\n'.join(out)


def slice_for(raw, mode):
    """The part of a file this check applies to."""
    if mode == 'newest':
        heads = [m.start() for m in
                 re.finditer(r'^##\s+\d|^\[size=4\]\[b\]\d', raw, re.M)]
        return raw[heads[0]:heads[1]] if len(heads) > 1 else raw
    if mode == 'player-half':
        # Split on the page's own section headings and drop the one written for
        # modders. Finding the heading text with str.find is not enough: the
        # words appear in the prose too.
        parts = re.split(r'(\[size=4\]\[b\][^\[]+\[/b\]\[/size\])', raw)
        keep, head = [], ''
        for chunk in parts:
            if chunk.startswith('[size=4]'):
                head = chunk
                continue
            if 'Under the hood' in head:
                head = ''
                continue
            keep.append(chunk)
            head = ''
        return ''.join(keep)
    return raw


def check(path, player, mode='all'):
    rel = os.path.relpath(path, REPO).replace(os.sep, '/')
    try:
        raw = io.open(path, encoding='utf-8').read()
    except OSError:
        return []
    raw = slice_for(raw, mode)
    text = strip_markup(raw)
    hits = []

    def add(kind, detail, line_no):
        hits.append((line_no, kind, detail))

    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        low = line.lower()
        for phrase in TELLS:
            if phrase in low:
                add('tell', phrase, i)
        for word in INTENSIFIERS:
            if re.search(r'\b%s\b' % word, low) and '"' not in line:
                add('intensifier', word, i)
        for phrase in LIMP:
            if phrase in low:
                add('limp', phrase.strip(), i)
        for phrase in FIGURATIVE:
            if phrase in low:
                add('figurative', phrase.strip(), i)
        if DASH.search(line):
            add('dash', 'em dash or spaced hyphen used as an aside', i)
        if THAN_IT.search(line):
            add('tease', 'says a thing is other than it appears', i)
        if INSIDE.search(line):
            add('punctuation', 'full stop inside a quote or bracket', i)
        if player:
            for word in JARGON:
                for m in re.finditer(r'\b%s\b' % re.escape(word), line, re.I):
                    span = line[max(0, m.start() - 12):m.end() + 12]
                    if JARGON_OK.search(span):
                        continue
                    add('jargon', word, i)
                    break

    cap = PLAYER_MAX_WORDS if player else MODDER_MAX_WORDS
    for para in re.split(r'\n\s*\n', text):
        flat = ' '.join(para.split())
        for sentence in SENTENCE.findall(flat):
            n = len(sentence.split())
            if n > cap:
                line_no = 1 + raw[:raw.find(sentence.strip()[:40])].count('\n') \
                    if sentence.strip()[:40] in raw else 0
                add('long', '%d words (max %d): %s...' % (n, cap, sentence.strip()[:60]),
                    line_no)
    return [(rel, ln, kind, detail) for ln, kind, detail in hits]


def collect(player_only):
    import glob as _glob
    files = []
    for pattern, mode in PLAYER_GLOBS:
        for hit in sorted(_glob.glob(os.path.join(REPO, pattern.replace('/', os.sep)))):
            files.append((hit, True, mode))
    if not player_only:
        for d in MODDER_DIRS:
            full = os.path.join(REPO, d)
            for name in sorted(os.listdir(full)) if os.path.isdir(full) else []:
                if not name.endswith('.md') or name.endswith(MODDER_SKIP_SUFFIX):
                    continue
                files.append((os.path.join(full, name), False, 'all'))
        for f in MODDER_EXTRA:
            files.append((os.path.join(REPO, f), False, 'all'))
    return files


def added_lines():
    """{path: {line numbers added since HEAD}}, so committed prose is left alone."""
    import subprocess
    out = subprocess.run(['git', 'diff', 'HEAD', '-U0'], cwd=REPO,
                         capture_output=True, text=True, encoding='utf-8').stdout
    added, path = {}, None
    for line in out.splitlines():
        if line.startswith('+++ b/'):
            path = line[6:]
            added.setdefault(path, set())
        elif line.startswith('@@') and path:
            m = re.search(r'\+(\d+)(?:,(\d+))?', line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2) or 1)
                added[path].update(range(start, start + count))
    return added


def main():
    ap = argparse.ArgumentParser(description='Check the writing rules that can be checked.')
    ap.add_argument('--player', action='store_true',
                    help='only the changelog, mod page and shipped READMEs')
    ap.add_argument('--all', action='store_true',
                    help='check every line of the modder docs, not only new ones')
    ap.add_argument('--quiet', action='store_true', help='exit code only')
    args = ap.parse_args()

    new_lines = {} if args.all else added_lines()
    all_hits = []
    for path, player, mode in collect(args.player):
        hits = check(path, player, mode)
        if not player and not args.all:
            keep = new_lines.get(hits[0][0]) if hits else None
            hits = [h for h in hits if keep and h[1] in keep]
        all_hits.extend(hits)

    if not args.quiet:
        current = None
        for rel, line_no, kind, detail in all_hits:
            if rel != current:
                print('\n%s' % rel)
                current = rel
            print('  %-13s line %-5s %s' % (kind, line_no or '?', detail))
        print()
        if all_hits:
            print('%d thing(s) to fix. Read each one: the check finds the tell, '
                  'not the sentence.' % len(all_hits))
        else:
            print('Writing checks pass.')
    return 1 if all_hits else 0


if __name__ == '__main__':
    sys.exit(main())
