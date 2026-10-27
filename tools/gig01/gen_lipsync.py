r"""Gives every line the gig wants a mouth on its lipsync animation.

    python tools\gig01\gen_lipsync.py                # make what changed, assemble the sets
    python tools\gig01\gen_lipsync.py --remake       # make every new mouth again
    python tools\gig01\gen_lipsync.py --rebuild      # re-extract the catalogue first
    python tools\gig01\gen_lipsync.py --report       # list every line and its animation

Run it AFTER gen_voice.py (it reads the clips and the voiceover map) and BEFORE
gen_scenes.py (which reads the picks file this writes). The dev-loop order is
therefore

    recorded wav -> gen_voice -> gen_lipsync -> gen_scenes -> build -> deploy

============================================================================
HOW LIPSYNC WORKS IN THIS GAME - all of it verified against shipped data on
2026-08-14, none of it guessed.
============================================================================

A spoken line moves a mouth through FOUR pieces, and the mod supplies all four:

1. `.anims` - a lipsync animation set. One file per ACTOR per SCENE. Vanilla's
   ship in `lang_en_voice.archive` at
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

   ArchiveXL merges a mod file into this under `localization: lipmaps:`.

3. The scene resource's own `resouresReferences.lipsyncAnimSets[]`, indexed by
   `scnActorDef.lipsyncAnimSet.id`. **Vanilla's entries point at UNCOOKED paths
   that exist in no archive** (`...\scenes\lipsync\en\<scene>\<actor>.anims` -
   grep every archive, there are none), so the shipped game cannot be using
   them; the lipmap has to be the live channel. Ours point at REAL paths, so
   this generator feeds BOTH and lets the engine take whichever it reads.

4. `scnscreenplayDialogLine.femaleLipsyncAnimationName` /
   `maleLipsyncAnimationName` - a CName naming ONE animation inside that set.

============================================================================
WHAT THIS SHIPS
============================================================================

An actor who says only whole vanilla lines in a scene, all in one vanilla
set, points at that set as before. Every other actor gets one `.anims` per
scene, at
`mod\negative_balance\localization\en-us\lipsync\<scene>\<actor>.anims`.
It holds two kinds of animation:

- MADE. A line the gig ships a clip for (Hoshino, and every cut vanilla
  take) gets a mouth made from that clip and its words by the lipsync
  animator, named `f_<the line's RUID>`. The visemes are the words actually
  spoken.
- COPIED. A whole vanilla line plays the animation CDPR baked for that
  recording, moved byte for byte out of whichever vanilla set holds it,
  under its own name. Any number of vanilla sets can feed one actor's file.
  questkit.lipsync._check_copies proves every copy is byte for byte.

The made animations are committed under `source\lipsync\`, so a build that
changed no clip and no words needs neither the animator nor its aligner.
The assembled file, which carries the copies, is built from the installed
game into the raw tree and is never committed. The mechanics are in
questkit.lipsync, "our own mouths".

Every dub's lipmap names the same English file. The made animations come
from the English clips, and the copies are the English recordings' mouths.

============================================================================
RIG MISMATCH IS NOT A PROBLEM, and that took one file to settle
============================================================================

Every lipsync set names a `rig`, and it is a HEAD rig, per head mesh.
`base\animations\facial\generic\interactive_scene\
generic_facial_lipsync_gestures.anims` is the GENERIC lipsync gesture set the
game plays on arbitrary NPCs in interactive scenes; its rig is the PLAYER's
head (`h0_001_ma_c__player`), and its animations have the same 344 joints /
414 tracks as every other lipsync anim. The `rig` field records what a set was
authored on, not what it may be played on, so the one head the animator
writes into every set it makes does not matter either.
"""
import argparse
import json
import os
import sys

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_voice as gv                                   # noqa: E402
import gen_scenes as gs                                  # noqa: E402
# The catalogue, the line split and the set assembly live in
# tools/questkit/lipsync.py. This file is the GIG: its cast.
from questkit.lipsync import (                                      # noqa: F401
    configure, rebuild_cache, load_catalogue, _check_actor_names,
    mouth_lines, build_mouths, voicetag, LIPMAP_DEPOT,
)
from gig01_config import RAW, MOD_NAME                   # noqa: E402

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
MOD = os.path.join(REPO, 'mods', 'gig-01-negative-balance')
# Extracted game data. CACHE, never committed - same rule as tools/_anchor_cache
# and mods/*/source/wkit/_research. Rebuild with --rebuild; it takes ~40 s.
CACHE = os.path.join(REPO, 'tools', '_lipsync_cache')
CATALOGUE = os.path.join(CACHE, 'catalogue.json')
# The small, readable, COMMITTED result: which animation and which set each
# line uses. gen_scenes reads it, so a clone can generate the scenes without a
# game install. Packing the archive still needs the assembled sets.
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
# character -> who gets a mouth, and where their vanilla animations are.
#
#   actor    the actorName gen_scenes gives that speaker. gen_scenes looks the
#            pick up by (scene, actorName), so these two strings must agree -
#            _check_actor_names() below fails the build if they ever drift.
#   regex    passed to WolvenKit's `unbundle -r`, matched against the full
#            depot path inside lang_en_voice.archive. The catalogue it builds
#            is where a whole vanilla line's own animation is found, so it
#            has to reach the character's own sets.
#
# V IS NOT HERE AND MUST NOT BE. He is the player and the camera is behind his
# eyes; there is no mouth to move.
#
# ELENA IS NOT HERE EITHER: her call draws a static contact portrait, and she
# is UNKNOWN CALLER by design, so there is no face to animate.
#
# NIX IS HERE: a mod that sets `holo_nix_calls_v_start_activate` gets Nix
# rendered live on the phone (docs/backlog.md 3d), and both of his calls in
# this gig are video.
#
# Hoshino is Character.cc_g01_hoshino, ours, and every line of his is a
# recording of ours, so every animation he has is made. His regex finds no
# vanilla set, which is correct.
CHARACTERS = {
    'johnny': {
        'actor': gs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
    'mama': {
        'actor': 'mama_welles',
        'regex': r'lipsync.*\\mama_welles\.anims$',
    },
    'hoshino': {
        'actor': 'hoshino',
        'regex': r'lipsync.*\\hoshino\.anims$',
    },
    'nix': {
        'actor': 'nix',
        'regex': r'lipsync.*\\nix\.anims$',
    },
}

# Vanilla's own lipmap, extracted alongside the sets by --rebuild.
LIPMAP_DEPOT = 'base\\localization\\en-us.lipmap'


configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rebuild', action='store_true',
                    help='re-extract the catalogue from the game first')
    ap.add_argument('--remake', action='store_true',
                    help='make every new mouth again, even where the clip and '
                         'the words did not change')
    ap.add_argument('--report', action='store_true',
                    help='list every line, made or copied, and its animation')
    args = ap.parse_args()

    if args.rebuild:
        rebuild_cache()
    catalogue = load_catalogue()
    scenes = [build() for build in gs.ALL_BUILDERS]
    actors = {c['actor'] for c in CHARACTERS.values()}
    lines = mouth_lines(scenes, actors, gv.VOMAP_OUT, RAW, catalogue)
    sets, names = build_mouths(lines, MOD, 'mod' + chr(92) + MOD_NAME,
                               {a: voicetag(a) for a in actors},
                               remake=args.remake)
    _check_actor_names(sets, gs.ALL_BUILDERS)
    if args.report:
        for r in lines:
            print('%-22s %-6s %-6s %s' % (r['scene'], r['key'],
                                          'made' if 'audio' in r else 'copied',
                                          r['name']))

    doc = {
        '_comment': 'GENERATED by tools/gig01/gen_lipsync.py - do not hand-edit. Each '
                    'actor of each scene has its own lipsync set, made from the '
                    'gig\'s clips and copied from vanilla for whole vanilla lines. '
                    'See that file for the whole mechanism.',
        'sets': sets,
        'lines': names,
    }
    os.makedirs(os.path.dirname(PICKS), exist_ok=True)
    with open(PICKS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    made = sum('audio' in r for r in lines)
    print('wrote %s (%d lines: %d made, %d copied, across %d scene/actor pairs)'
          % (PICKS, len(lines), made, len(lines) - made,
             sum(len(v) for v in sets.values())))


if __name__ == '__main__':
    main()
