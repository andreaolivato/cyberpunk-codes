r"""Casts a lipsync animation onto every line in this gig that has a mouth on
screen, and writes source/lipsync_picks.json.

    python tools\gig03\gen_lipsync.py            # cast, using the cached catalogue
    python tools\gig03\gen_lipsync.py --rebuild  # re-extract the catalogue first
    python tools\gig03\gen_lipsync.py --report   # print every pick and its error

THE MOD SHIPS NO ANIMATION DATA. A scene line's animation NAME is free-form, so
a line points at an animation the game already owns. `docs/backlog.md` 2j has
the whole chain and it was expensive to establish:

    .anims set -> base\localization\<lang>.lipmap (ArchiveXL key `lipmaps`)
               -> scnActorDef.lipsyncAnimSet -> the line's
                  female/maleLipsyncAnimationName

===========================================================================
EVERY LINE IN THIS GIG IS A REUSED VANILLA LINE, WHICH MAKES THIS THE EASY CASE
===========================================================================

Vanilla baked a lipsync animation for each of its own recordings, named
`f_<stringId>` after the line it was baked for. A line this gig reuses whole
therefore already HAS a perfect animation, and
`questkit.lipsync._exact` finds it: it ranks candidate sets by how many of a
scene's lines they can serve EXACTLY before it looks at length at all.

The three cut lines (take_vanilla.py) are the exception: a cut clip is not
the recording its animation was baked for, so those are cast by length, the
way gig 02 casts its recorded takes.

WITHOUT THIS FILE THE MOUTHS DO NOT MOVE. A line with no pick goes out with an
empty animation name and nothing errors: the actor is configured correctly, the
set resolves, and the face just sits there. That is what gig 02 shipped on its
first video holocall, and it is what this gig shipped until 2026-09-10:
playtest, "holo works, but there's no lipsync".

===========================================================================
THREE MOUTHS ARE SEEN, AND V'S IS NOT ONE OF THEM
===========================================================================

Dino on the phone, Dino at his bar, and Johnny beside V and at the door. V IS
NOT HERE AND MUST NOT BE: V is the player, the camera is behind V's eyes, and
there is no mouth to move.

Dino's three scenes all use the actorName `dino`, so one cast entry per scene
covers his body wherever it sits.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import lipsync                                        # noqa: E402
from questkit.lipsync import (                                      # noqa: E402
    configure, load_catalogue, pick, rebuild_cache,
)
import questkit.scene as qs                                          # noqa: E402

import gen_scenes as gs                                              # noqa: E402
import take_vanilla                                                  # noqa: E402
from gig03_config import REPO, SOURCE                                # noqa: E402

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     '_lipsync_cache')
# ITS OWN CATALOGUE FILE, named after the gig exactly as the config module is.
# `rebuild_cache()` writes over whatever the catalogue held, and it extracts only
# the sets THIS gig's regexes match, so a shared file would let one gig's
# rebuild silently re-cast another gig's picks from a pool that no longer holds
# what they were cast from.
CATALOGUE = os.path.join(CACHE, 'catalogue_gig03.json')

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
WK = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
VOICE_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content',
                             'lang_en_voice.archive')

PICKS = os.path.join(SOURCE, 'lipsync_picks.json')

# ------------------------------------------------------------------ the cast
#
#   actor    the actorName gen_scenes gives that speaker. gen_scenes looks the
#            pick up by (scene, actorName), so the two strings must agree.
#   regex    passed to WolvenKit's `unbundle -r`, matched against the full depot
#            path inside lang_en_voice.archive.
#
# DINO'S POOL IS HIS OWN SETS. Every line of his is one of his own
# recordings, so the set that holds one line's animation usually holds the
# others', and the exact path does the rest. A set is named after the voice
# tag its VO files carry (Regina's were `regina_reggie_jones.anims`, her tag),
# and Dino's tag is `dino_dyno_dinovic`, so the regex reaches every set of
# his. Rebuild the catalogue (`--rebuild`) after changing this: the cached one
# holds only the sets the old regexes matched.
CHARACTERS = {
    'johnny': {
        'actor': qs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
    'dino': {
        'actor': 'dino',
        'regex': r'lipsync.*\\dino_dyno_dinovic\.anims$',
    },
}

configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS)

# Which speaker owns which actorName, so a scene's reused lines can be split by
# character without gen_scenes having to say so twice.
ACTOR_TO_CHAR = {qs.JOHNNY_ACTOR: 'johnny', 'dino': 'dino'}

# THE SHIPPED CLIPS. They carry no `vanilla_sid` in the scene, because the game
# must play OUR phone-treated clip rather than its own dry one, so they are not
# in `scene.reused` and the two walks below would not see them. A WHOLE take
# still has vanilla's own animation, exactly right, named from the same table
# gen_voice ships it from. A JOINED line has none (gotcha 59: a cut is neither
# recording) and is cast by length, which is what gig 02 does for its recorded
# takes.
WHOLE_TAKES = {(scene, key): sid for scene, key, sid in take_vanilla.TAKES}
SHIPPED = take_vanilla.shipped()


def _scenes():
    return [build() for build in gs.ALL_BUILDERS]


def _by_character(scenes):
    """(character, scene, [(key, ms), ...]) for every line with a mouth.

    Length is an estimate from the line's own text rather than a measured clip,
    and that is fine here BECAUSE nothing falls back to it: every line is a
    whole reused take, so `_exact` serves all of them and the length is never
    the thing being ranked on. It is passed because `pick` wants it.
    """
    out = []
    for scene in scenes:
        per_actor = {}
        for key, _sid, text in scene.reused:
            actor = scene.reused_actor.get(key)
            char = ACTOR_TO_CHAR.get(_actor_name(scene, actor))
            if char is None:
                continue
            per_actor.setdefault(char, []).append((key, gs.estimate_ms(text)))
        for sc, key in SHIPPED:
            if sc != scene.name:
                continue
            ms = gs.MEASURED.get('%s/%s' % (sc, key))
            if ms is None:
                raise SystemExit('%s/%s ships a clip but has no measured '
                                 'length; run gen_voice.py first' % (sc, key))
            # WHOSE MOUTH: the line's speaker, read off the scene rather than
            # assumed. Johnny has one shipped clip and Dino two.
            char = ACTOR_TO_CHAR.get(_actor_name(scene, _speaker_of(scene, key)))
            if char is None:
                raise SystemExit('%s/%s ships a clip for a speaker with no '
                                 'lipsync pool' % (sc, key))
            per_actor.setdefault(char, []).append((key, ms))
        for char, want in sorted(per_actor.items()):
            out.append((char, scene.name, want))
    return out


def _speaker_of(scene, key):
    """The actor index behind a line key, for a line that is not reused."""
    for idx, k in scene.line_key.items():
        if k == key:
            return scene.lines[idx]['speaker']['id']
    return None


def _actor_name(scene, actor_index):
    """The actorName behind a scene.reused_actor value.

    `add_line` records the actor the caller passed, which is the index the
    scene builder handed back, so the name has to be read out of the actor
    definition rather than assumed.

    READ THE `actorName` FIELD, which every actor has whatever its acquisition
    plan is. This used to dig into `spawnDespawnParams.dynamicEntityUniqueName`,
    which exists only on an actor the SCENE spawns: the moment Regina became a
    community entry, every one of her flat lines came back with no speaker and
    the mouth check failed the build. Gig 02 has always read this field.
    """
    if actor_index is None:
        return None
    try:
        return scene.actors[actor_index]['actorName']
    except (IndexError, KeyError, TypeError):
        return None


# SCENES CAST BY LENGTH ALONE, exact hits ignored. An actor gets ONE set per
# scene, and the picker takes the set with the most exact hits and casts the
# rest by length from what that set has left. In the loud bar scene two of
# Dino's four lines are cuts (1.2 s and 1.8 s) and the only set holding the
# other two exactly is a debrief with nothing shorter than 4.2 s to spare, so
# they came out with mouths moving three to five seconds past the words
# (10.6 s of error over the scene, 2026-09-15). His bark set has a dozen
# animations under 2.5 s; length casting from it puts a mouth of the right
# duration on every line, none of them exact. The right duration on four
# lines beats the right visemes on two.
LENGTH_ONLY = {'gig03_dino_bar_loud'}


def _exact_names(scenes):
    """(character, scene) -> {key: 'f_<stringId hex>'}.

    UPPERCASE HEX, the same as gig 02. `questkit.lipsync` now resolves a hit
    to the set's own spelling, so the case here no longer decides whether the
    mouth moves, but writing it the same way as the other gigs keeps the two
    comparable. Six lines shipped lowercase against an uppercase set and were
    silent: playtest, 2026-09-10, "the phrase 'you'll steal it for me' doesn't
    have lipsync".

    THE CUTS ARE NOT IN HERE, the same as gig 02's trims: a cut clip is
    shorter than the recording its animation was baked for and the mouth
    would still be moving after the words stop. They carry no `vanilla_sid`,
    so `scene.reused` never lists them and they fall to length casting.
    """
    out = {}
    for scene in scenes:
        if scene.name in LENGTH_ONLY:
            continue
        for key, string_id, _text in scene.reused:
            char = ACTOR_TO_CHAR.get(
                _actor_name(scene, scene.reused_actor.get(key)))
            if char is None:
                continue
            out.setdefault((char, scene.name), {})[key] = (
                'f_%016X' % int(string_id))
        for (sc, key), sid in WHOLE_TAKES.items():
            if sc == scene.name:
                char = ACTOR_TO_CHAR.get(
                    _actor_name(scene, _speaker_of(scene, key)))
                out.setdefault((char, sc), {})[key] = 'f_%016X' % sid
    return out


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

    scenes = _scenes()
    wanted = _by_character(scenes)
    sets, lines, report = pick(catalogue, wanted, verbose=args.report,
                               exact=_exact_names(scenes))

    doc = {
        '_comment': 'GENERATED by tools/gig03/gen_lipsync.py. Do not hand-edit. '
                    'Every line here is a whole reused vanilla take, so each one '
                    'borrows the animation vanilla baked for it; nothing is '
                    'shipped but the reference.',
        'sets': sets,
        'lines': lines,
    }
    os.makedirs(os.path.dirname(PICKS), exist_ok=True)
    with open(PICKS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    print('wrote %s (%d lines across %d scene/actor pairs)'
          % (PICKS, len(lines), sum(len(v) for v in sets.values())))
    worst = max(report, key=lambda r: r[3]) if report else None
    if worst:
        print('worst length error: %s/%s, %.0f ms total over %d line(s)'
              % (worst[0], worst[1], worst[3], len(worst[4])))


if __name__ == '__main__':
    main()
