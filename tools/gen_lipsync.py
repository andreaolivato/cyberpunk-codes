r"""Picks a vanilla lipsync animation for every line the gig wants a mouth on.

    python tools\gen_lipsync.py                # pick, using the cached catalogue
    python tools\gen_lipsync.py --rebuild      # re-extract the catalogue first
    python tools\gen_lipsync.py --report       # show the picks and their error

Run it AFTER gen_voice.py (it needs durations.json) and BEFORE gen_scenes.py
(which reads the picks file this writes). The dev-loop order is therefore

    text-to-speech -> gen_voice -> gen_lipsync -> gen_scenes -> build -> deploy

============================================================================
HOW LIPSYNC WORKS IN THIS GAME - all of it verified against shipped data on
2026-08-14, none of it guessed.
============================================================================

A spoken line moves a mouth through FOUR pieces, and the mod supplies only the
last two:

1. `.anims` - a lipsync animation set. One file per ACTOR per SCENE, shipped in
   `lang_en_voice.archive` at
   `base\localization\en-us\lipsync\<the scene's own depot path>\<actor>.anims`.
   Inside is an `animAnimSet` whose `animations[]` are named `f_<stringId as 16
   hex digits>` - the same RUID that resolves the subtitle and the `.wem`. Each
   is `AdditiveFromRefPose`, 344 joints, 414 float tracks, over a head rig.

2. `base\localization\en-us.lipmap` - an `animLipsyncMapping` that says which
   set belongs to which actor of which scene. Three PARALLEL arrays:

       scenePaths[i]         FNV1a64 of the scene's depot path (proven: all
                             3495 vanilla entries match, see fnv1a64 below)
       scenePreviewPaths[i]  another hash, editor-side, never matched to
                             anything that exists - we derive one and move on
       sceneEntries[i]       { actorVoiceTags[j], animSets[j] } - parallel to
                             EACH OTHER, so voicetag j uses anims j

   ArchiveXL merges a mod file into this under `localization: lipmaps:`. That
   key has been sitting in its Config.cpp unused by this project since
   2026-08-12 (backlog 2a).

3. The scene resource's own `resouresReferences.lipsyncAnimSets[]`, indexed by
   `scnActorDef.lipsyncAnimSet.id`. **Vanilla's entries point at UNCOOKED paths
   that exist in no archive** (`...\scenes\lipsync\en\<scene>\<actor>.anims` -
   grep every archive, there are none), so the shipped game cannot be using
   them; the lipmap has to be the live channel. Ours point at REAL paths, so
   this generator feeds BOTH and lets the engine take whichever it reads.

4. `scnscreenplayDialogLine.femaleLipsyncAnimationName` /
   `maleLipsyncAnimationName` - a CName naming ONE animation inside that set.
   Free-form: the `f_`/`m_` shape is just CDPR's baking convention.

============================================================================
WHY THIS SHIPS NO ANIMATION DATA
============================================================================

A `.anims` round-trips byte-identically through WolvenKit (verified: md5 of
`johnny.anims` in and out), so BUILDING one - renaming vanilla animations to
our RUIDs and repacking - is entirely possible. It is deliberately not done.

Baking our own is out of reach (a compressed key buffer over 344 joints), so
any such file would be vanilla animation data with our labels on it, shipped
inside a Nexus download. This repo already refuses to commit extracted game
audio for the same reason.

Point 4 above makes that unnecessary. The animation NAME is ours to choose, so
a line can simply name an animation that already exists in a shipped set, and
the mod ships nothing but a reference. What this file does, therefore, is
CASTING: for every line, find the vanilla lipsync animation whose length is
closest to our clip.

The lipsync is then real mouth movement of the right length in the right voice
register - and the wrong phonemes. It is a mouth moving while someone talks,
which is what the game does for every NPC at conversational distance. Nobody
reads visemes off Johnny's face from two metres in a dark office.

CONSTRAINT THAT SHAPES THE PICK: one set per actor per scene. `lipsyncAnimSet`
is a single id, so both of Johnny's lines in `gig01_legend` must come out of
ONE vanilla file. The search therefore scores whole scenes, not lines.

============================================================================
RIG MISMATCH IS NOT A PROBLEM, and that took one file to settle
============================================================================

Every lipsync set names a `rig`, and it is a HEAD rig, per head mesh:
`base\characters\head\ma\h0_052_ma_b__older\..._skeleton.rig`. Johnny's own is
`...\main_npc\silverhand\h0_001_ma_c__silverhand_skeleton.rig`. So the obvious
worry is that borrowing one character's set for another feeds an animation to
the wrong skeleton.

`base\animations\facial\generic\interactive_scene\
generic_facial_lipsync_gestures.anims` settles it: it is the GENERIC lipsync
gesture set the game plays on arbitrary NPCs in interactive scenes, its rig is
the PLAYER's head (`h0_001_ma_c__player`), and its animations have the same 344
joints / 414 tracks as every other lipsync anim. The layout is uniform; the
`rig` field records what it was authored on, not what it may be played on.

Johnny and Mama Welles get their own sets anyway, because they exist and cost
nothing. Hoshino is our own record with no lipsync anywhere in the game, so he
borrows a Japanese-accented male civilian's - which is the case that needed
this paragraph.
"""
import argparse
import json
import os
import re
import sys

import gen_voice as gv                                   # noqa: E402
import gen_scenes as gs                                  # noqa: E402
# The catalogue extraction and the length-matching scorer live in
# tools/questkit/lipsync.py. This file is the GIG: its cast, and which of its lines
# get a mouth.
from questkit.lipsync import (                                      # noqa: F401
    configure, rebuild_cache, load_catalogue, _score, _check_actor_names,
    LIPMAP_DEPOT,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(REPO, 'mods', 'gig-01-negative-balance')
# Extracted game data. CACHE, never committed - same rule as tools/_anchor_cache
# and mods/*/source/wkit/_research. Rebuild with --rebuild; it takes ~40 s.
CACHE = os.path.join(REPO, 'tools', '_lipsync_cache')
CATALOGUE = os.path.join(CACHE, 'catalogue.json')
# ...and the small, readable, COMMITTED result: which vanilla animation each of
# our lines borrows. This is the file gen_scenes reads. It is committed because
# it is a casting decision, not extracted data - and because a fresh clone must
# be able to build the gig without a game install.
PICKS = os.path.join(MOD, 'source', 'lipsync_picks.json')

WK = os.environ.get(
    'WOLVENKIT_CLI',
    os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe'))
GAME = os.environ.get(
    'CP2077_DIR',
    r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077')
VOICE_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content', 'lang_en_voice.archive')

# ------------------------------------------------------------------ the cast
#
# character (gen_voice.CAST key) -> how to find its candidate lipsync sets.
#
#   actor    the actorName gen_scenes gives that speaker. gen_scenes looks the
#            pick up by (scene, actorName), so these two strings must agree -
#            _check_actor_names() below fails the build if they ever drift.
#   regex    passed to WolvenKit's `unbundle -r`, matched against the full
#            depot path inside lang_en_voice.archive.
#
# V IS NOT HERE AND MUST NOT BE. He is the player and the camera is behind his
# eyes; there is no mouth to move. Elena and Nix are not here either - both are
# holocall-only, and a holocall in this gig draws a static contact portrait, not
# a rendered caller (docs/scene-playbook.md, "a script-issued Video holocall
# CRASHES the game"). A lipsync set for either would animate nothing.
CHARACTERS = {
    'johnny': {
        'actor': gs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
    'mama': {
        'actor': 'mama_welles',
        'regex': r'lipsync.*\\mama_welles\.anims$',
    },
    # Hoshino is Character.cc_g01_hoshino - ours, so the game has no lipsync for
    # him at all. A Japanese-accented male civilian is the nearest thing to his
    # casting; see the rig note in the module docstring for why any male set
    # would in fact do.
    'hoshino': {
        'actor': 'hoshino',
        'regex': r'lipsync.*civ_(high|mid)_m_\d+_jap_\d+\.anims$',
    },
}

# Vanilla's own lipmap, extracted alongside the sets. It is how a source file
# gets its VOICETAG: the lipmap's actorVoiceTags[j] is parallel to animSets[j],
# so the tag that owns a set is readable straight out of it. We need that
# because our own lipmap entry has to be keyed by the same number.
LIPMAP_DEPOT = 'base\\localization\\en-us.lipmap'



configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS)


def _wanted():
    """(character, scene, [(key, wanted_ms), ...]) for everything we can voice.

    Length comes from the REAL clip via gen_voice's duration sidecar - the same
    numbers gen_scenes paces the sections from, so the animation is matched to
    the audio rather than to an estimate of it. A line with no measured clip
    falls back to gen_scenes' own estimate, which keeps the two halves of the
    gig (voiced, unvoiced) working without a flag.
    """
    durations = {}
    if os.path.exists(gv.DURATIONS):
        with open(gv.DURATIONS, encoding='utf-8') as fh:
            durations = json.load(fh)
    texts = _line_texts()
    out = []
    for char, scenes in gv.CAST.items():
        if char not in CHARACTERS:
            continue
        for scene, keys in sorted(scenes.items()):
            want = []
            for k in keys:
                ms = durations.get('%s/%s' % (scene, k))
                if ms is None:
                    text = texts.get('%s/%s' % (scene, k), '')
                    ms = gs.estimate_ms(text) if text else 2000
                want.append((k, int(ms)))
            out.append((char, scene, want))
    return out


def _line_texts():
    """Every line key the generators know about, so a duration can be estimated
    for a line that has no clip yet. Built by running the scene builders, which
    is cheap and keeps this file from owning a second copy of the script."""
    texts = {}
    for build in gs.ALL_BUILDERS:
        scene = build()
        for key, text in scene.line_text.items():
            texts['%s/%s' % (scene.name, key)] = text
    return texts



def pick(catalogue, verbose=False):
    sets, lines, report = {}, {}, []
    for char, scene, wanted in _wanted():
        actor = CHARACTERS[char]['actor']
        rx = re.compile(CHARACTERS[char]['regex'])
        best = None
        for depot, entry in catalogue.items():
            if not rx.search(depot):
                continue
            scored = _score(entry['anims'], wanted)
            if scored is None:
                continue
            err, names = scored
            if best is None or err < best[0]:
                best = (err, depot, names, entry)
        if best is None:
            raise SystemExit(
                'no lipsync set found for %s in %s - is the catalogue built? '
                '(%d candidates matched %r)'
                % (char, scene, sum(1 for d in catalogue if rx.search(d)),
                   CHARACTERS[char]['regex']))
        err, depot, names, entry = best
        if entry['voicetag'] in (None, '0'):
            raise SystemExit('%s: chosen set %s has no voicetag in the vanilla '
                             'lipmap - our lipmap entry would be unkeyed'
                             % (char, depot))
        sets.setdefault(scene, {})[actor] = {
            'anims': depot, 'voicetag': entry['voicetag']}
        for key, name in names.items():
            lines['%s/%s' % (scene, key)] = name
        report.append((scene, actor, depot, err, names, wanted))
        if verbose:
            print('%-20s %-12s err %6.0f ms  %s'
                  % (scene, actor, err, depot.rsplit('\\', 2)[-2]))
            by_key = dict(wanted)
            for key, name in sorted(names.items()):
                seconds = next(s for n, s in entry['anims'] if n == name)
                print('    %-6s want %5d ms  got %5d ms  %s'
                      % (key, by_key[key], int(seconds * 1000), name))
    return sets, lines, report




def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rebuild', action='store_true',
                    help='re-extract the catalogue from the game first')
    ap.add_argument('--report', action='store_true',
                    help='print every pick and how far off its length is')
    args = ap.parse_args()

    if args.rebuild:
        rebuild_cache()
    catalogue = load_catalogue()
    sets, lines, report = pick(catalogue, verbose=args.report)
    _check_actor_names(sets, gs.ALL_BUILDERS)

    doc = {
        '_comment': 'GENERATED by tools/gen_lipsync.py - do not hand-edit. Each '
                    'line borrows a vanilla lipsync animation of about the right '
                    'length; nothing is shipped but the reference. See that '
                    'file for the whole mechanism.',
        'sets': sets,
        'lines': lines,
    }
    os.makedirs(os.path.dirname(PICKS), exist_ok=True)
    with open(PICKS, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    worst = max(report, key=lambda r: r[3]) if report else None
    print('wrote %s (%d lines across %d scene/actor pairs)'
          % (PICKS, len(lines), sum(len(v) for v in sets.values())))
    if worst:
        print('worst length error: %s/%s, %.0f ms total over %d line(s)'
              % (worst[0], worst[1], worst[3], len(worst[4])))


if __name__ == '__main__':
    main()
