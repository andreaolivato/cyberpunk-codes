r"""Picks a vanilla lipsync animation for every line the gig wants a mouth on.

    python tools\gig01\gen_lipsync.py                # pick, using the cached catalogue
    python tools\gig01\gen_lipsync.py --rebuild      # re-extract the catalogue first
    python tools\gig01\gen_lipsync.py --report       # show the picks and their error

Run it AFTER gen_voice.py (it needs durations.json) and BEFORE gen_scenes.py
(which reads the picks file this writes). The dev-loop order is therefore

    recorded wav -> gen_voice -> gen_lipsync -> gen_scenes -> build -> deploy

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
import sys

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_voice as gv                                   # noqa: E402
import gen_scenes as gs                                  # noqa: E402
# The catalogue extraction and the length-matching scorer live in
# tools/questkit/lipsync.py. This file is the GIG: its cast, and which of its lines
# get a mouth.
from questkit.lipsync import (                                      # noqa: F401
    configure, rebuild_cache, load_catalogue, pick, _check_actor_names,
    LIPMAP_DEPOT,
)

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
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
# eyes; there is no mouth to move.
#
# ELENA IS NOT HERE EITHER, and for the reason this entry used to give for Nix
# as well: her call draws a static contact portrait, so a lipsync set would
# animate nothing. She is also UNKNOWN CALLER by design, so there is no face to
# animate even if there were a body.
#
# NIX IS HERE AS OF 2026-08-22, and the entry that excluded him was written
# against a claim that has since been measured false. It said a holocall in
# this gig "draws a static contact portrait, not a rendered caller". A mod that
# sets `holo_nix_calls_v_start_activate` gets Nix rendered live on the phone,
# no crash, no dialogue options (docs/backlog.md 3d). So there is a mouth after
# all, and both of his calls in this gig are video as of 1.2.6.
#
# His sets are the game's own: `base\quest\holocalls\nix\lipsync\en\...\nix.anims`
# and its siblings, so the shapes are the real actor's rather than a stand-in's.
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
    # NIX DRAWS FROM EVERY MALE CIVILIAN SET, not only his own seven.
    #
    # His face is in CLOSE-UP on the phone, which is a harder test than any
    # other mouth in this gig gets, and his own sets cannot pass it. The game
    # ships seven of them, holding 1, 2, 5, 18, 19, 21 and 31 animations, and
    # ONE SET has to serve a whole scene. A four-line scene was therefore
    # casting from at most 31 candidates and landing 386 ms long on an 880 ms
    # line: the mouth still moving half a second after the words stop, which
    # is what reads as broken. Playtest, 2026-08-23: *"really really bad
    # compared to what we did with Johnny"*, and *"especially for the shorter
    # sentences"*, which is exactly where a small pool fails first.
    #
    # Johnny lands inside 30 ms on almost every line. He is not cast better,
    # he has 209 sets. The difference is the size of the pool and nothing
    # else.
    #
    # Male civilians are 1192 sets and they are the right register: ordinary
    # conversational speech rather than a performance. His own seven stay in
    # the pool, so a scene that happens to fit them still gets the real
    # actor's mouth. Borrowing is safe for the reason in the module docstring
    # (the `rig` field records what an animation was authored on, not what it
    # may be played on), and Hoshino has borrowed a civilian's since 1.2.0.
    'nix': {
        'actor': 'nix',
        'regex': r'lipsync.*\\(nix|civ_(low|mid|high)_m_\d+_[a-z]+_\d+)\.anims$',
    },
}

# Vanilla's own lipmap, extracted alongside the sets. It is how a source file
# gets its VOICETAG: the lipmap's actorVoiceTags[j] is parallel to animSets[j],
# so the tag that owns a set is readable straight out of it. We need that
# because our own lipmap entry has to be keyed by the same number.
LIPMAP_DEPOT = 'base\\localization\\en-us.lipmap'



configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS)


def _vanilla_ms(catalogue, string_id):
    """How long a REUSED vanilla line runs, taken from its own lipsync animation.

    Exact and free. A line the gig reuses whole is identified by vanilla's
    `stringId`, and vanilla baked a lipsync animation for that very line named
    `f_<the stringId in 16 hex digits>`. Its length IS the clip's length -
    measured 1533 ms against the 1537 ms recorded by hand for "How's things,
    V?", so there is nothing to estimate and nothing to keep in step.
    """
    want = ('f_%016X' % int(string_id)).upper()
    for entry in catalogue.values():
        for name, seconds in entry['anims']:
            if name.upper() == want:
                return int(seconds * 1000)
    return None


def _reused(catalogue):
    """(scene, actorName, key, ms) for every vanilla line this gig reuses whole.

    THESE FELL OUT OF THE CASTING ENTIRELY AND SHIPPED WITH A DEAD MOUTH.
    Playtest 2026-08-23, on the first video holocall: *"just the first phrase
    when he says how's things v, he's completely immobile, no mouth movement at
    all. The rest are all good."*

    The cause is that a reused line has no clip of ours, so it is not in
    gen_voice's CAST and not in durations.json, and _wanted() below is built
    from exactly those two. No entry, no pick, and `scnscreenplayDialogLine`
    goes out with an empty animation name. Nothing errors: the actor is
    configured correctly, the set resolves, and the face just sits there.

    It only became visible because his face is now in close-up on the phone.
    The same line has been mouthless behind a contact portrait since 1.2.0,
    where there was nothing to see.

    A REUSED LINE NOW GETS ITS OWN PERFECT ANIMATION WHERE IT CAN, 2026-09-03,
    and the paragraph that stood here saying it could not was right only while
    reuse was rare. It read: one `.anims` set serves a whole scene, the set
    holding `f_<stringId>` is the contact's own conversation set, and that
    tiny pool made everything else bad (backlog 2j), so the line was cast by
    length like any other.

    The recast inverted the arithmetic. Most lines are vanilla reuse now, so
    the set that holds one line's own animation usually holds the others' too,
    and questkit.lipsync._exact ranks sets by how many of them it can serve
    exactly before it looks at length at all. 11 of 21 picks are the line's
    own animation as of this writing; the rest are trims (whose clip is
    shorter than the animation vanilla baked), the invented characters (who
    have no vanilla animation to be exact about), and lines whose source scene
    lost the tie to a set that served more of their scene-mates.
    """
    out = []
    for build in gs.ALL_BUILDERS:
        scene = build()
        for key, string_id, text in scene.reused:
            speaker = scene.reused_actor.get(key)
            if speaker is None or speaker >= len(scene.actors):
                continue
            ms = _vanilla_ms(catalogue, string_id)
            if ms is None:
                print('  warning: no vanilla lipsync animation for %s/%s '
                      '(stringId %s); pacing it by estimate instead'
                      % (scene.name, key, string_id))
                ms = gs.estimate_ms(text)
            out.append((scene.name, scene.actors[speaker]['actorName'], key, ms))
    return out


def _exact_names():
    """(character, scene) -> {key: 'f_<stringId>'} for every line reused WHOLE.

    Vanilla baked a lipsync animation for each of its own recordings, named
    after the line's stringId, so a line this gig reuses whole already HAS a
    perfect animation. See questkit.lipsync._exact for the one condition (an
    actor gets one set per scene, so they must all come from the same vanilla
    scene) and what happens when it is not met.

    TRIMS ARE DELIBERATELY EXCLUDED. A cut clip is shorter than the recording
    the animation was baked for, so the exact animation would outrun it - the
    mouth still moving after the words stop, which is the exact failure the
    length casting exists to avoid. Those keys are in CAST (they ship audio of
    ours) and are cast by length like any other produced clip.
    """
    produced = {'%s/%s' % (sc, k)
                for _c, scenes in gv.CAST.items()
                for sc, keys in scenes.items() for k in keys}
    out = {}
    for build in gs.ALL_BUILDERS:
        scene = build()
        for key, string_id, _text in scene.reused:
            if '%s/%s' % (scene.name, key) in produced:
                continue
            speaker = scene.reused_actor.get(key)
            if speaker is None or speaker >= len(scene.actors):
                continue
            actor = scene.actors[speaker]['actorName']
            char = next((c for c, cfg in CHARACTERS.items()
                         if cfg['actor'] == actor), None)
            if char is None:
                continue
            out.setdefault((char, scene.name), {})[key] = (
                'f_%016X' % int(string_id))
    return out


def _wanted(catalogue):
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
    reused = _reused(catalogue)
    out = []
    for char, scenes in gv.CAST.items():
        if char not in CHARACTERS:
            continue
        actor = CHARACTERS[char]['actor']
        for scene, keys in sorted(scenes.items()):
            want = []
            for k in keys:
                ms = durations.get('%s/%s' % (scene, k))
                if ms is None:
                    text = texts.get('%s/%s' % (scene, k), '')
                    ms = gs.estimate_ms(text) if text else 2000
                want.append((k, int(ms)))
            # A reused vanilla line is spoken by the same mouth and comes out of
            # the same set, so it has to be cast alongside the rest of the scene
            # rather than left out of the list the set is chosen from.
            want += [(k, ms) for sc, ac, k, ms in reused
                     if sc == scene and ac == actor]
            out.append((char, scene, want))
    # ...and a scene whose ONLY line for this character is a reused one would
    # otherwise never reach the picker at all, because CAST is keyed by what
    # gen_voice generates audio for.
    seen = {(c, sc) for c, sc, _ in out}
    for char, cfg in CHARACTERS.items():
        extra = {}
        for sc, ac, k, ms in reused:
            if ac == cfg['actor'] and (char, sc) not in seen:
                extra.setdefault(sc, []).append((k, ms))
        for sc, want in sorted(extra.items()):
            out.append((char, sc, want))
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



# `pick` used to live here. It is questkit.lipsync.pick now: the search, the
# scoring and the two failures worth stopping on are the same for any gig, and
# what this file supplies is the cast (CHARACTERS, through configure) and the
# lines that want a mouth (_wanted).


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
    sets, lines, report = pick(catalogue, _wanted(catalogue),
                           verbose=args.report, exact=_exact_names())
    _check_actor_names(sets, gs.ALL_BUILDERS)

    doc = {
        '_comment': 'GENERATED by tools/gig01/gen_lipsync.py - do not hand-edit. Each '
                    'line borrows a vanilla lipsync animation of about the right '
                    'length; nothing is shipped but the reference. See that '
                    'file for the whole mechanism.',
        'sets': sets,
        'lines': lines,
    }
    os.makedirs(os.path.dirname(PICKS), exist_ok=True)
    with open(PICKS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    worst = max(report, key=lambda r: r[3]) if report else None
    print('wrote %s (%d lines across %d scene/actor pairs)'
          % (PICKS, len(lines), sum(len(v) for v in sets.values())))
    if worst:
        print('worst length error: %s/%s, %.0f ms total over %d line(s)'
              % (worst[0], worst[1], worst[3], len(worst[4])))


if __name__ == '__main__':
    main()
