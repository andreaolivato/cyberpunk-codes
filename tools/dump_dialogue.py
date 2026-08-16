r"""Dumps every SPOKEN line in the gig, as plain readable text.

There was no such file before, and the words are not readable where they live:
`gen_scenes.py` builds fourteen `.scene` graphs in which a line is an index into
an array, keyed by a 64-bit RUID. This walks them and lays the script out.

SPOKEN is the whole filter, and it is the same line the audio pipeline draws:
a scene line is the only kind that can carry a `.wem`, so this file is exactly
the set of lines that have (or want) a voice. The SMS threads, the office
terminal, the shard and the HUD are READ, not said - they live in
`gen_localization.py` as a flat dict of LocKeys and are off by default.
`--screens` appends them under their own heading, still separated.

It is a READER, not a generator - it writes nothing the game loads, so it can
be re-run any time without touching the build. It goes to the generators rather
than to their output, so it cannot drift from what actually ships: if a line
changes in the generator, it changes here on the next run.

`gen_scenes` is imported, which is safe - it only builds when run as main.
`gen_localization` is NOT, and must not be: it writes its resource at module
level, so importing it would have this reader silently rewrite a game file
every time someone wanted to read the script. Its STRINGS dict is parsed out
with `ast` instead, which resolves implicit string concatenation and escapes
exactly as Python would without executing anything.

Scene order is `gen_scenes.ALL_BUILDERS`, which is story order. Within a scene
the order is the node graph's, walked as authored - sections and choice hubs
interleaved the way the player meets them. Branches are laid out flat: a choice
hub prints all of its options, then the text continues. That is the one thing
this file cannot show faithfully, because a graph is not a page.

    python .\tools\dump_dialogue.py [-o path] [--screens]
"""
import argparse
import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gen_scenes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'docs',
                           'dialogue.txt')
LOC_SRC = os.path.join(REPO, 'tools', 'gen_localization.py')

WIDTH = 78

# LocKeys that are UI furniture rather than anything anyone says or reads.
# Objectives and pin captions are the player's HUD; they are listed in their own
# short section at the end instead of being mixed in with the prose.
HUD_PREFIXES = ('obj-', 'pin-', 'gig-title', 'poi-')


def wrap(text, indent, first=None):
    """Hanging-indent wrap. `first` is the prefix on line one (the speaker).

    The prefix is taken as already-spaced: nothing is inserted between it and
    the first word, so a caller that pads "ELENA:" out to the indent width gets
    its continuation lines aligned under the text rather than one short of it.

    NEWLINES IN THE TEXT ARE KEPT. The terminal file and the shard are laid out
    on screen with their own line breaks - "SUBJECT: ORTEGA, M." sits on its own
    line, which is the point of it - so a naive `text.split()` reflows a
    formatted document into a paragraph and quietly misreports what the player
    sees. Each source line is wrapped on its own; a blank one stays blank.
    """
    pad = ' ' * len(indent)
    out = []
    prefix = indent if first is None else first
    for para in text.split('\n'):
        if not para.strip():
            out.append('')
            prefix = pad
            continue
        line, fresh = prefix, True     # no word on this line yet
        for word in para.split():
            if not fresh and len(line) + 1 + len(word) > WIDTH:
                out.append(line)
                line = pad + word
            else:
                line += word if fresh else ' ' + word
            fresh = False
        out.append(line)
        prefix = pad
    return '\n'.join(out)


def rule(title, char='='):
    return '%s\n%s\n%s' % (char * WIDTH, title, char * WIDTH)


# ---------------------------------------------------------------- scenes
def speaker_names(scene):
    """actorId -> display name. Scene actors and the player share one id space
    across two arrays (see Scene.add_actor), so both are folded into one map."""
    names = {}
    for a in scene.actors:
        names[a['actorId']['id']] = a['actorName']
    for p in scene.player_actors:
        names[p['actorId']['id']] = 'V'
    return names


def line_texts(scene):
    """locstring ruid -> text, over our lines AND the reused vanilla ones.

    A reused line carries a vanilla stringId instead of a RUID of ours and is
    deliberately absent from the subtitle resource - the text is still recorded
    on `scene.reused` so the script reads whole. Mark those, because they are
    the only lines in the gig this project did not write.
    """
    texts = {ls: (text, False) for ls, text, _male in scene.subtitles}
    for _key, ls, text in scene.reused:
        texts[ls] = (text, True)
    return texts


def gendered(scene):
    """locstring ruid -> the male-V variant, where it differs from the female
    one. Mama Welles's "mija"/"mijo" is the only case, and it would silently
    vanish from a dump that only read one variant."""
    return {ls: male for ls, text, male in scene.subtitles if male != text}


def dump_scene(scene, out):
    names = speaker_names(scene)
    texts = line_texts(scene)
    male = gendered(scene)

    out.append('')
    out.append(rule(scene.name, '-'))

    # A scene's flavour is not on the scene, it is on the events inside it - so
    # read the first dialogue event and report how the player experiences this
    # one. Holocall = phone UI, innerDialog = the relic register (Johnny).
    kinds = set()
    for node in scene.nodes:
        for ev in node.get('events', []):
            vo = ev['Data'].get('voParams')
            if not vo:
                continue
            if vo['isHolocallSpeaker']:
                kinds.add('holocall')
            elif vo['voExpression'] == 'Vo_Expression_InnerDialog':
                kinds.add('inner voice')
            else:
                kinds.add('face to face')
    if kinds:
        out.append('(%s)' % ', '.join(sorted(kinds)))
    out.append('')

    said = 0
    for node in scene.nodes:
        if node['$type'] == 'scnSectionNode':
            for ev in node['events']:
                data = ev['Data']
                if data['$type'] != 'scnDialogLineEvent':
                    continue
                idx = data['screenplayLineId']['id'] >> 8
                line = scene.lines[idx]
                ls = line['locstringId']['ruid']
                text, reused = texts.get(ls, ('<missing text>', False))
                who = names.get(line['speaker']['id'], '?')
                tag = '  [vanilla recording, reused]' if reused else ''
                out.append(wrap(text + tag, ' ' * 14, '%-13s ' % (who.upper() + ':')))
                if ls in male:
                    out.append(wrap('(male V: %s)' % male[ls], ' ' * 14, ' ' * 14))
                said += 1
            if node['events']:
                out.append('')
        elif node['$type'] == 'scnChoiceNode':
            out.append('              -- V chooses --')
            for opt in node['options']:
                oi = opt['screenplayOptionId']['id'] >> 8
                ls = scene.options[oi]['locstringId']['ruid']
                text = texts.get(ls, ('<missing text>', False))[0]
                out.append(wrap(text, ' ' * 18, ' ' * 14 + '> '))
            out.append('')

    if not said:
        out.append('              (no spoken lines - staging only)')
        out.append('')


# ---------------------------------------------------------- localization
def loc_strings(src):
    """gen_localization's STRINGS dict, without importing the module.

    See the module docstring for why importing is not an option. `ast` gives the
    real values - adjacent string literals are folded by the parser, so the
    multi-line entries come out as the single strings the game gets.
    """
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Assign)
                and any(getattr(t, 'id', None) == 'STRINGS' for t in node.targets)):
            return ast.literal_eval(node.value)
    raise SystemExit('no STRINGS dict in %s - did it get renamed?' % LOC_SRC)


def loc_sections(src, strings):
    """[(heading, [(key, text), ...]), ...] in the order gen_localization
    authors them.

    The groupings are the `# --- heading ---` comments already in that file, so
    the dump inherits the structure someone already thought about instead of
    inventing a worse one. The source is scanned for KEYS only - each one's text
    comes from the parsed dict, so a regex is never the thing deciding what a
    line says.
    """
    sections, heading, items = [], 'misc', []
    for line in src.splitlines():
        m = re.match(r"\s*# ---+ (.+?) -+$", line)
        if m:
            if items:
                sections.append((heading, items))
            heading, items = m.group(1).strip(), []
            continue
        m = re.match(r"\s*'([a-z0-9-]+)':", line)
        if m and m.group(1) in strings:
            items.append((m.group(1), strings[m.group(1)]))
    if items:
        sections.append((heading, items))

    seen = {k for _h, its in sections for k, _t in its}
    missed = [k for k in strings if k not in seen]
    if missed:
        sections.append(('ungrouped', [(k, strings[k]) for k in missed]))
    return sections


def dump_localization(out, strings, sections):
    hud = []
    for heading, items in sections:
        body = []
        for key, text in items:
            if key.startswith(HUD_PREFIXES):
                hud.append((key, text))
                continue
            block = wrap(text, ' ' * 14, '%-13s ' % key)
            body.append(block)
            if '\n' in block:          # a laid-out document needs air after it
                body.append('')
        if not body:
            continue
        out.append('')
        out.append(rule(heading, '-'))
        out.append('')
        out.extend(body)

    if hud:
        out.append('')
        out.append(rule('objectives, pins and titles (HUD text, not spoken)', '-'))
        out.append('')
        for key, text in hud:
            out.append(wrap(text, ' ' * 14, '%-13s ' % key))


# ---------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-o', '--out', default=DEFAULT_OUT)
    ap.add_argument('--screens', action='store_true',
                    help='also dump the text the player READS - SMS threads, '
                         'the office terminal, the shard, the HUD. Off by '
                         'default: this file is the spoken script.')
    args = ap.parse_args()

    scenes = [build() for build in gen_scenes.ALL_BUILDERS]

    out = []
    out.append(rule('NEGATIVE BALANCE - spoken dialogue'))
    out.append('')
    out.append('Every SPOKEN line in the gig, in story order, dumped from the')
    out.append('generator that builds it (tools/gen_scenes.py) by')
    out.append('tools/dump_dialogue.py. Do not edit this file - edit the')
    out.append('generator and re-run, or the game and this text disagree.')
    out.append('')
    out.append('Screen text is NOT here: the SMS threads, the office terminal,')
    out.append('the shard and the HUD are read, not said. `--screens` adds them.')
    out.append('')
    out.append('Branching is flattened: a choice hub lists every option, then')
    out.append('the transcript continues. The player sees one path.')
    out.append('')
    for scene in scenes:
        dump_scene(scene, out)

    strings = None
    if args.screens:
        with open(LOC_SRC, encoding='utf-8') as fh:
            loc_src = fh.read()
        strings = loc_strings(loc_src)
        out.append('')
        out.append(rule('SCREEN TEXT - PHONE MESSAGES, SHARDS, TERMINAL, HUD'))
        out.append('')
        out.append('Read, not spoken. Nothing here carries audio.')
        dump_localization(out, strings, loc_sections(loc_src, strings))
    out.append('')

    lines = sum(len(s.lines) for s in scenes)
    opts = sum(len(s.options) for s in scenes)
    tally = '%d spoken lines, %d dialogue options, %d scenes' % (
        lines, opts, len(scenes))
    if strings is not None:
        tally += ', %d screen strings' % len(strings)
    out.append(rule(tally))
    out.append('')

    with open(args.out, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('wrote %s (%s)' % (args.out, tally))


if __name__ == '__main__':
    main()
