r"""Casts a vanilla lipsync animation onto every line in this gig that has a
mouth on screen, and writes source/lipsync_picks.json.

    python tools\gig02\gen_lipsync.py            # cast, using the cached catalogue
    python tools\gig02\gen_lipsync.py --rebuild  # re-extract the catalogue first
    python tools\gig02\gen_lipsync.py --report   # print every pick and its error

THE MOD SHIPS NO ANIMATION DATA. The animation NAME a scene line carries is
free-form, so a line points at an animation the game already owns, chosen for
having about the right length. Casting is by LENGTH only: the phonemes come from
an unrelated line, and it reads as real lip sync at conversational distance. The
whole chain is in tools/questkit/lipsync.py.

===========================================================================
ONLY TWO MOUTHS IN THIS GIG ARE SEEN
===========================================================================

Johnny, who is staged beside V in eleven scenes, and Wakako, who is in close-up
on V's phone for the two video calls. Everyone else is a voice with its body a
kilometre away, so a lipsync set for them would drive a face nobody is looking
at. See gen_scenes.py for why the gig is shaped that way.

Wakako's office scene is cast anyway, and that is not a mistake: her actor there
carries the same actorName as the two calls, so one cast entry covers all three
and there is no name that appears in only one scene for the cast check to trip
over. Nothing plays it.

===========================================================================
THIS GIG HAS ITS OWN CATALOGUE FILE, AND THAT MATTERS
===========================================================================

`rebuild_cache()` extracts exactly the sets the CAST's regexes match and writes
them over whatever the catalogue held before. Gig 01's cast is male-only, so a
gig 02 rebuild into the shared file would replace its catalogue with one holding
no `civ_*_m_*_jap_*` sets, and gig 01's Hoshino would be re-cast off a pool that
no longer contains what he was cast from. Silently, on the next run of a
generator nobody thought they had touched.

So the file is named after the gig, exactly as the config module is. Both
catalogues are extraction scratch: gitignored, and about forty seconds to
rebuild.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_scenes as gs                                             # noqa: E402
import gen_voice as gv                                              # noqa: E402
from questkit.lipsync import (                                      # noqa: E402
    configure, rebuild_cache, load_catalogue, pick, _check_actor_names,
    LIPMAP_DEPOT,
)
from gig02_config import REPO, SOURCE                               # noqa: E402

CACHE = os.path.join(REPO, 'tools', '_lipsync_cache')
# NAMED AFTER THE GIG. See the module docstring: a shared catalogue is a
# rebuild that silently re-casts another gig.
CATALOGUE = os.path.join(CACHE, 'catalogue_gig02.json')
# The small, readable, COMMITTED result: which vanilla animation each of our
# lines borrows. gen_scenes reads this. Committed because it is a casting
# decision rather than extracted data, and because a fresh clone has to be able
# to build the gig with no game installed.
PICKS = os.path.join(SOURCE, 'lipsync_picks.json')

WK = os.environ.get(
    'WOLVENKIT_CLI',
    os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe'))
GAME = os.environ.get(
    'CP2077_DIR',
    r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077')
VOICE_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content',
                             'lang_en_voice.archive')

# ------------------------------------------------------------------ the cast
#
# character (a gen_voice.CAST key) -> how to find its candidate lipsync sets.
#
#   actor    the actorName gen_scenes gives that speaker. gen_scenes looks the
#            pick up by (scene, actorName), so the two strings must agree, and
#            _check_actor_names() fails the run if they ever drift.
#   regex    passed to WolvenKit's `unbundle -r`, matched against the full depot
#            path inside lang_en_voice.archive.
#
# V IS NOT HERE AND MUST NOT BE. He is the player, the camera is behind his
# eyes, and there is no mouth to move.
#
# EVERYONE ELSE IS HERE NOW, and the note that used to sit on this line said
# why they were not: "their bodies are a kilometre away". That was true of the
# arrangement this gig shipped first, where a speaker was an invisible actor
# off-map and the body on screen was a separate script spawn. Six of them are
# the body on screen now, acquired from this gig's community, so six of them
# have a mouth to move. See docs/scene-playbook.md.
#
# THE POOLS ARE ACCENT-AND-GENDER CLASSES, NOT ONE SET EACH, and that is
# deliberate for the reason Wakako's note gives below: casting picks the
# animation nearest each line's length, so a small pool lands long. Borrowing
# across characters is safe - every lipsync anim in the game has the same 344
# joints and 414 tracks.
CHARACTERS = {
    'johnny': {
        'actor': gs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
    # WAKAKO DRAWS FROM EVERY FEMALE CIVILIAN SET WITH A JAPANESE OR CHINESE
    # ACCENT, not from one set of her own, and the reason is pool size rather
    # than casting.
    #
    # THE PARAGRAPH THAT STOOD HERE WAS WRONG. It said the game ships no
    # lipsync set for Wakako Okada. It ships one per scene she speaks in, named
    # `wakako_okada.anims` under that scene's folder (`sq023_03_call`,
    # `wakako_okada_default`, the `sts_wbr_jpn_*` debriefs), and since
    # 2026-09-03 the pattern below admits them, which is what gives her reused
    # lines the exact mouth vanilla baked for them. The female civilian pool
    # stays for the cut lines, which are shorter than their baked animation.
    #
    # ONE SET SERVES A WHOLE SCENE, and her face is in CLOSE-UP on the phone,
    # which is the hardest test any mouth in this gig gets. Gig 01 measured what
    # a small pool does there: Nix's own seven sets hold between 1 and 31
    # animations each, a four-line scene was casting from at most 31 candidates,
    # and it landed 386 ms long on an 880 ms line, with the mouth still moving
    # half a second after the words stopped. Johnny lands inside 30 ms on almost every
    # line, and he is not cast better, he has 209 sets.
    #
    # Borrowing across characters is safe: the `rig` field records what an
    # animation was authored on, not what it may be played on, and vanilla plays
    # a player-rigged set on arbitrary NPCs. Every lipsync anim in the game has
    # the same 344 joints and 414 tracks.
    'wakako': {
        'actor': 'wakako',
        # AND HER OWN SCENES' SETS, 2026-09-03: her reused lines were baked
        # in the sets those scenes use, which are named for whoever else was in
        # the room, so a pool limited to female civilians could never hold
        # them and every reused line fell through to no animation at all.
        'regex': r'lipsync.*(civ_(low|mid|high)_f_\d+_(jap|chn)_\d+|wakako.*)\.anims$',
    },

    # ---- the five strangers outside Afterlife, 2026-09-03 ------------------
    #
    # EACH ONE IS A REAL VANILLA VOICE speaking one of its own recorded lines,
    # so the pool is that voice's own sets and the exact animation is in it.
    'queue_a': {'actor': 'queue_a', 'regex': r'lipsync.*civ_mid_m_21_enus_25\.anims$'},
    'queue_b': {'actor': 'queue_b', 'regex': r'lipsync.*civ_mid_m_34_afam_25\.anims$'},
    'queue_c': {'actor': 'queue_c', 'regex': r'lipsync.*civ_mid_m_04_enus_30\.anims$'},
    'queue_d': {'actor': 'queue_d', 'regex': r'lipsync.*civ_high_f_09_afam_30\.anims$'},
    'queue_e': {'actor': 'queue_e', 'regex': r'lipsync.*civ_mid_m_42_mex_40\.anims$'},

    # ---- the six acquired from the community ------------------------------
    #
    # THE ACCENT IS THE CHARACTER'S, not the pool's convenience. Yoko and Ideka
    # work in Japantown and Kabuki; Huscle is Wakako's doorman and Toji is a
    # Tyger Claw. The merc is a Wraith and Char is a Night City netrunner, so
    # both draw from the American pools.
    #
    # The trailing `.*` matters: some voice tags carry a district after the age
    # (`civ_mid_f_62_jap_40_kabuki`) and a pattern ending at `_\d+` misses every
    # one of those.
    # A MAN SINCE 2026-09-06 (the recorded voice is a man's), so the male
    # American pool.
    'merc': {
        'actor': 'merc',
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(enus|afam)_.*\.anims$',
    },
    'char': {
        'actor': 'char',
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(enus|afam)_.*\.anims$',
    },
    'yoko': {
        'actor': 'yoko',
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(jap|chn)_.*\.anims$',
    },
    'ideka': {
        'actor': 'ideka',
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(jap|chn)_.*\.anims$',
    },
    'huscle': {
        'actor': 'huscle',
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(jap|chn)_.*\.anims$',
    },
    'toji': {
        'actor': 'toji',
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(jap|chn)_.*\.anims$',
    },
}

configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS)


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


# PORTED FROM GIG 01, 2026-09-03, the day this gig started reusing vanilla
# lines. Without `_reused` a reused line has no clip of ours, is in neither
# CAST nor durations.json, and ships with an empty animation name and a
# still face; gig 01 found it on its first video call. `_exact_names` is
# what gives a reused line its own baked animation where the set allows.
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
        '_comment': 'GENERATED by tools/gig02/gen_lipsync.py. Do not hand-edit: '
                    'Each line borrows a vanilla lipsync animation of about the '
                    'right length; nothing is shipped but the reference.',
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
