r"""Generates the gig's .scene resources - real scene-system conversations.

TEN scenes, all built by the same builder. ALL_BUILDERS at the bottom is the
list; gen_voice reads it too, so it is the one place scenes are enumerated.
Every scene here is entered by something. Four that were not were deleted on
2026-09-05 and are in git history: gig01_legend and gig01_graves were Johnny
beats the recast could not cast, and gig01_shard_find and gig01_shard_read
were the reactions to a shard that stopped being an objective. The shard
itself is still in the world and still readable.

  gig01_elena_call  Elena's opening holocall (was an SMS thread)
  gig01_arasaka     Johnny: "Fucking Arasaka..." (comic p11)
  gig01_terminal    the office desk, V + Johnny (p22)
  (gig01_netrunner was merged back into gig01_terminal on 2026-08-14)
  gig01_nix_brief   V hires Nix (pp. 26-27)
  (gig01_nix_call became a text conversation on 2026-09-03)
  gig01_hoshino     the North Oak estate
  gig01_kill        over Hoshino's body (p45)
  gig01_malware     the estate terminal (p51)
  gig01_epilogue    Mama Welles in El Coyote Cojo
  gig01_bar         the last two lines of the comic (p63)

RECORDINGS ARE THE SOURCE NOW (2026-08-19)

The comic used to be the authority on wording, and several comments below still
explain a decision in those terms. It is not any more, because most lines are
recordings that already exist and cannot be altered: V, Johnny, Mama Welles and
Nix speak vanilla takes, so the words are whatever was recorded years ago. A
subtitle that disagrees with the audio is a bug the player can hear. So the
order of authority is the recording first, then the comic for order, beats and
intent.

Three lines are recorded differently for each body and carry a separate male
subtitle through `add_line(male=...)`: elena_call v05, hoshino vh1 and terminal
t10. Mama Welles' mija/mijo used the same mechanism first.

Do not "restore" a line to its comic wording without listening to the clip. The
transcripts that drove this pass are not in the repo; the audio is.

WHY SCENES AT ALL - and the answer got much bigger on 2026-08-13.

The original reason was dialogue CHOICES: a choice hub is written natively into
UIInteractions.DialogChoiceHubs and the confirm press is dispatched back to the
scene that owns it, so a script-injected hub has nothing to route the selection
to (docs/architecture.md).

The stronger reason is AUDIO. A scene line carries a scnlocLocstringId, and the
game resolves both its subtitle and its voiceover from that one RUID. A line
pushed from script is a caption with no RUID, so nothing can ever play audio for
it. Six beats were captions until 2026-08-13 and every one of them was silent in
game. Converting them was the only fix - there is no flag and no fallback.

STRUCTURE (verified against three real scenes, see docs/scene-playbook.md):

  scnSceneResource
    actors[] / playerActors[]  who can speak
    sceneGraph.graph[]         scnStartNode / scnSectionNode / scnChoiceNode /
                               scnHubNode / scnEndNode, wired by output sockets
    screenplayStore.lines[]    one scnscreenplayDialogLine per spoken line
    screenplayStore.options[]  one scnscreenplayChoiceOption per choice entry
    locStore                   THE TEXT ITSELF, per locale, embedded in the file
    entryPoints / exitPoints   named sockets the quest phase's scene node sees

WHERE SCENE TEXT ACTUALLY COMES FROM (this cost a playtest, 2026-08-11).
A scene line points at a `scnlocLocstringId` RUID. The embedded `locStore` in
the scene file looks like the place that RUID resolves - it even holds per-locale
text - but **the game ignores it at runtime**. It is editor data. The real
lookup is a `localizationPersistenceSubtitleEntries` resource, keyed by the same
RUID in its `stringId`, merged in by ArchiveXL under `localization: subtitles:`.

Ship a scene without one and everything works except the words: choice hubs
appear with blank rows and sections play in silence. That is exactly what the
first build did. This generator therefore emits TWO things - the scenes, and
`subtitles.json` carrying every line and option in them. Keep them in step; they
are regenerated together on purpose.

(The proof, if it is ever needed again: OneMoreLight ships
`base\localization\en-us\subtitles\quest\jackie\jackie_default.json`, and 53 of
its 56 scene locstring RUIDs appear in it as `stringId`s).

The embedded locStore is still written, because the reference scenes all have
one and it is the editor-side record of the same text. It is not what you are
reading in game.

ACTOR ACQUISITION - the decision that shapes every scene, REVISED 2026-08-13.

Scene actors still cannot be bound to entities this mod spawns at runtime:
DynamicEntitySpec has no uniqueName field (probed with the redscript compiler,
2026-08-11), and a base-game community NPC like Mama Welles has no NodeRef we
can discover offline. So every non-player speaker is a `spawnDespawn` actor the
scene spawns FOR ITS VOICE ONLY, and the body the player sees is still the one
Gig01_Encounter.reds spawns or finds.

WHAT CHANGED IS WHERE THAT VOICE ACTOR GOES. It used to be the scene marker plus
(1000, 1000, -100) - a kilometre out, a hundred metres down - copied from
Californication's trick for Judy. That was invented for SUBTITLES, which do not
care where a speaker is. **Audio does**, and it is not on/off: it attenuates.
Every world-emitter line in this gig was therefore inaudible, and the symptom
read as "silent" until playtesting described it as "low and far, almost cannot hear
it" (2026-08-13).

The rule now, and it turns on ONE field:

  holocall=True  isHolocallSpeaker - 2D through the phone. Position irrelevant.
  inner=True     Vo_Expression_InnerDialog - 2D, in V's head. Position
                 irrelevant. This is what every Johnny line uses.
  default        Vo_Expression_Spoken - POSITIONAL. The actor must be near the
                 listener or it cannot be heard.

So positional speakers are placed deliberately:

  Johnny   beside V and facing him, per beat. See BEAT_STAGING
  Hoshino  buried 2.5 m under the estate marker
  Mama     a fixed anchor 3 m from her mark, then 2.5 m down

Johnny is the one who is SEEN, so he is aimed rather than buried: an
`around_player` marker sits at V's exact position and carries V's rotation, so
+Y is forward and +X is right (measured five times, docs/backlog.md 9).

For a speaker who only has to be HEARD, straight down is still the offset of
choice, because it needs no knowledge of the marker's rotation at all and the
floor between listener and speaker costs nothing. Only Elena and Nix still use
the far-away default, and only because their lines are holocall.

Each speaker still needs a TweakXL Character record purely for the displayName
shown over its subtitles.

JOHNNY'S WORKSPOT - why a scene carries one.
`gamePhantomEntityComponent.phantomVisibleStates` is ["RootMotion","Workspot"],
and a spawned puppet standing in a plain idle is in NEITHER - so Johnny's lines
played while nobody could see him. Of the three states, Workspot is the only one
a mod can reach: root motion has no script API and MoveOnSpline needs an authored
spline. See docs/scene-playbook.md, "THE FIX".

A scene can carry its own workspot with `playAtActorLocation: 1` and NO world
node, which is what makes this usable at all - a mod-authored worldWorkspotNode
in a mod streaming sector would never resolve, the same way custom map-pin
markers never resolve. Three resources cooperate:

  workspots[]          scnWorkspotData_ExternalWorkspotResource, naming a
                       shipped base-game .workspot
  workspotInstances[]  scnWorkspotInstance, playAtActorLocation 1, no nodeRef
  a scnQuestNode       wrapping questUseWorkspotNodeDefinition with
                       scnUseSceneWorkspotParamsV1, addressing the actor by
                       spawnDespawnParams.dynamicEntityUniqueName

Every field is copied from sts_wat_kab_03_johnny.scene and sts_hey_gle_04_johnny
.scene; see add_workspot_node() for the two shapes vanilla uses and why this
generator picked the one it did.
"""
import json
import os

import sys

# This gig's generators sit in tools/gig01/, and questkit is in tools/, one
# level up. Nothing else puts it on the path. See backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The builder itself lives in tools/questkit/scene.py. This file is the GIG: its
# paths, its anchors and its dialogue. Everything imported here is engine shape
# that a second gig reuses rather than forks.
#
# Several names are imported only to be re-exported. gen_voice, gen_lipsync and
# gen_shard_ent reaches for them as gen_scenes.<name>, and keeping them
# resolvable here means the split costs those tools no changes at all.
from questkit import translations                                   # noqa: E402
from questkit import vanilla_durations                              # noqa: E402
from questkit.scene import (                                        # noqa: F401
    Scene, configure, write_subtitles, write_lipmap,
    ANCHOR_PLAYER, JOHNNY_ACTOR, JOHNNY_GHOST, JOHNNY_SOLID,
    WORKSPOT_JOHNNY, WORKSPOT_ENTRY,
    estimate_ms, line_ms, locstring_ruid, resref, cname, fnv1a64,
    yaw_to_face_player,
)

# Paths, prefixes and scene anchors are gig01_config.py, which is the one file
# a second gig re-points. Imported by name rather than with a star so that what
# this generator uses is visible here.
from gig01_config import (                                          # noqa: E402
    REPO, SOURCE, RAW_MOD, DEPOT,
    ANCHOR_OFFICE, ANCHOR_ESTATE, ANCHOR_COYOTE, ANCHOR_BAR, ANCHOR_MAMA,
)
# Hoshino's community. Imported rather than restated: the scene asks for the
# exact string the registry registers, and a typo here is a scene with no
# speaker rather than an error.
from gen_community import (                                         # noqa: E402
    ENTRY as HOSHINO_ENTRY, SPAWNSET_NAME as HOSHINO_SPAWNSET,
)

OUT_DIR = os.path.join(RAW_MOD, 'scenes')
# Subtitles take TWO resources, and getting this wrong is silent in game and
# only one line deep in the ArchiveXL log ("Resource ... failed to load").
#
# ArchiveXL's `localization: subtitles:` key merges into the base game's
# base\localization\<lang>\subtitles\subtitles.json - and that file is a
# localizationPersistenceSubtitleMap: a LIST OF FILE PATHS, not the text. So:
#
#   SUBTITLE_MAP_OUT   a localizationPersistenceSubtitleMap, one entry, pointing
#                      at the file below. THIS is what the .archive.xl registers.
#   SUBTITLE_OUT       the localizationPersistenceSubtitleEntries the map points
#                      at - the actual stringId -> text table.
#
# (Deceptious never hit this: OneMoreLight ships its entries file at a base-game
# path the base map ALREADY references, overriding it, so it needed no map).
SUBTITLE_MAP_OUT = os.path.join(RAW_MOD, 'localization', 'subtitles.json.json')
SUBTITLE_OUT = os.path.join(RAW_MOD, 'localization', 'gig01_lines.json.json')
# Depot path of the entries file, as the map has to name it.
SUBTITLE_DEPOT = DEPOT + chr(92) + 'localization' + chr(92) + 'gig01_lines.json'

# Where the scenes live once packed. gen_questphase.SCENES is the same string
# and has to stay so; the lipmap is keyed by FNV1a64 of exactly this path plus
# the scene name, so a mismatch here is a lipmap nobody ever looks up.
SCENE_DEPOT = DEPOT + chr(92) + 'scenes' + chr(92)
# The animLipsyncMapping ArchiveXL merges into base\localization\en-us.lipmap.
LIPMAP_OUT = os.path.join(RAW_MOD, 'localization', 'gig01.lipmap.json')

# THE SCENE ANCHORS ARE gig01_config.py, imported above. They were stated here
# and in gen_questphase.py, with three comments warning that the two copies had
# to be kept in step; the evidence for each one, and the two rejected
# candidates for Mama's, moved there with them.

# OFFSET_MAMA WAS HERE: (-1.668, 2.505, -3.584), her mark relative to the anchor
# and then 2.5 m down, to bury the speaker under the floor at her feet. Removed
# 2026-08-18. The measurement was sound and the burial was still wrong, for the
# reason 10k found on Hoshino: 2.5 m below a marker is not reliably below the
# floor, and the room underneath is somewhere a player can be standing.

# ...but a voiced line must be paced by its clip, not by a guess about it, or it
# cuts off or drags. tools/gig01/gen_voice.py measures every WAV it processes and
# writes this sidecar; anything in it wins over the estimate. Missing file, or a
# line absent from it, simply falls back - so the two halves of the gig (voiced
# scenes, unvoiced ones) coexist without a flag.
DURATIONS_FILE = os.path.join(SOURCE, 'audio', 'durations.json')
try:
    with open(DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED = json.load(_fh)
except (OSError, ValueError):
    MEASURED = {}

# AND THE REUSED LINES, as the shortest dub of each. tools/measure_packs.py
# measures every voice pack on this machine and tools/gigNN/measure_vanilla.py
# writes this file from the shortest, and the game stretches the slot to
# whichever take it plays; without it a reused line is paced by an
# estimate from its text, which ran short for V by up to two seconds in gig 03
# (playtest 2026-09-15) and cannot be right for more than one language at
# once. Same table, same key shape, same 350 ms pad.
# AND THE DUBBED LANGUAGES' OWN CLIPS. A vanilla cut remade in a dub is a
# clip of a different length, so a section is paced from the longest clip
# any language ships for the line (durations_<locale>.json, written by
# gen_voice's locale pass): the game stretches a slot only for its own
# lines, never for a shipped clip (questkit.vanilla_durations).
vanilla_durations.merge_locale_clips(MEASURED, os.path.join(SOURCE, 'audio'))

VANILLA_DURATIONS_FILE = os.path.join(SOURCE, 'audio', 'vanilla_durations.json')
if os.path.exists(VANILLA_DURATIONS_FILE):
    with open(VANILLA_DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED.update(json.load(_fh))

# ------------------------------------------------------------------- LIPSYNC
#
# tools/gig01/gen_lipsync.py casts a vanilla lipsync animation of about the right
# LENGTH for every line Johnny, Hoshino and Mama Welles say, and writes the
# result here. The whole mechanism is in that file's docstring; what this file
# needs from it is three things:
#
#   sets[scene][actorName]  -> {anims: depot path, voicetag: str}
#   lines["scene/key"]      -> the animation name inside that set
#
# and they turn into resouresReferences.lipsyncAnimSets, scnActorDef
# .lipsyncAnimSet.id + .voicetagId, and the dialogue line's
# female/maleLipsyncAnimationName respectively.
#
# MISSING FILE IS NOT AN ERROR. Everything below falls back to exactly what this
# generator emitted before lipsync existed - no anim set, voicetag 0, empty
# animation names - so a clone without the picks file still builds a working
# gig, silently minus the mouths.
LIPSYNC_PICKS = os.path.join(SOURCE, 'lipsync_picks.json')
try:
    with open(LIPSYNC_PICKS, encoding='utf-8') as _fh:
        _picks = json.load(_fh)
    LIPSYNC_SETS = _picks.get('sets', {})
    LIPSYNC_LINES = _picks.get('lines', {})
except (OSError, ValueError):
    LIPSYNC_SETS, LIPSYNC_LINES = {}, {}

# Scenes that reuse another scene's recordings: gen_voice points the alias's
# RUIDs at clips that already exist, and gen_lipsync copies its picks.
#
# EMPTY SINCE 2026-08-18, and the mechanism is kept because the reasoning that
# built it is still right. It held `gig01_epilogue_standin -> gig01_epilogue`,
# four lines the stand-in shared with the real epilogue. Regenerating them was
# never an option: a second take of the same words is a second performance,
# which would have left one Mama Welles sounding different depending on
# which variant played. Both the stand-in and the need for it are
# gone; see build_epilogue. A future scene that replays another's audio wants
# this, and wants it for the same reason.
SCENE_ALIASES = {}

# Hand the builder this gig's paths and sidecars. Must run before any Scene is
# constructed; everything below only builds scenes when called from main.
configure(
    out_dir=OUT_DIR,
    scene_depot=SCENE_DEPOT,
    subtitle_out=SUBTITLE_OUT,
    subtitle_map_out=SUBTITLE_MAP_OUT,
    subtitle_depot=SUBTITLE_DEPOT,
    lipmap_out=LIPMAP_OUT,
    lipmap_name='gig01.lipmap',
    durations=MEASURED,
    lipsync_sets=LIPSYNC_SETS,
    lipsync_lines=LIPSYNC_LINES,
    scene_aliases=SCENE_ALIASES,
    translations=translations.load(os.path.dirname(os.path.abspath(__file__))),
)


# =========================================================== scene 1: Elena
def build_elena():
    """The opening holocall. Beat for beat the thread it replaces, so the quest
    phase's pacing and the player's experience of the conversation survive the
    move - what is new is that it is a call, and that V answers out loud.

    RHYTHM, rebuilt 2026-08-13 (the design call, off measured numbers).

    Across 188 vanilla scenes: 560 of 1118 hubs have exactly one option, so
    single-option hubs are idiomatic and the earlier reasoning was right. What
    was wrong was the DENSITY - vanilla asks the player for input once every 3.8
    dialogue sections, this gig asked every 1.1, and `gig01_nix_brief` had more
    hubs than sections.

    The cause was structural, not a taste failure. Every V line in the gig was a
    hub OPTION, because no scene had a player actor and options need no actor.
    So the hub count was pinned to V's line count and could not come down
    without cutting his dialogue, which is not on the table. The comic was the
    source and the wording was verbatim; see RECORDINGS ARE THE SOURCE NOW at
    the top of this file for what replaced that rule.

    THE FIX IS THE PLAYER ACTOR (see add_player, which explains why the reason it
    was avoided turned out not to exist). V's lines become spoken sections. Two
    hubs survive, at the two moments V decides something:

        o03  "Alright. Start from the top."      he chooses to hear her out
        o05  "Okay. Listen to me. Go to El Coyote..."  he chooses to act

    Those are vanilla's shape exactly: press the line, then V says it. The other
    three V lines are simply spoken. 11 sections, 2 hubs - 5.5 sections per hub,
    on the roomy side of vanilla, which is right for the scene the whole gig
    hangs off.
    """
    s = Scene('gig01_elena_call', ANCHOR_OFFICE)
    elena = s.add_actor('elena_ortega', 'Character.cc_g01_elena')
    v = s.add_player()

    def E(text, key):
        return s.add_line(elena, text, key=key)

    def V(text, key):
        return s.add_line(v, text, key=key)

    start = s.start('elena_call_in')
    # COMIC pp. 3-11, in order. Nothing is cut. The wording follows the
    # recordings, which reworded eight of these lines; the comic is still the
    # order, the beats and the intent.
    s1 = s.section([
        E("V? Sorry, I didn't know you'd answer. "
          "My name's Elena Ortega.", 'e01'),
    ], holocall=True)
    # The comic's "Wrong hour for a friendly call." is V thinking out loud as the
    # phone rings, NOT an answer to a stranger introducing herself - offering it
    # as a reply read wrong (playtest, 2026-08-12). It belongs to the ring, which
    # the scene does not cover, so it is gone rather than forced.
    s2 = s.section([
        E("I'm from Heywood. My mom and Mama Welles grew up together. "
          "Jackie Welles used to help my family sometimes.", 'e02'),
    ], holocall=True)
    # She has had two turns; now he answers. V's lines are NOT holocall - he is
    # the one holding the phone, not the voice coming out of it, so his audio
    # plays from his own position and his expression is Vo_Expression_Spoken.
    #
    # SPLICED-VOICES RECAST (2026-09-02): V's side of this call is now the
    # actor's own recordings. This line is a verified TRIM of vanilla
    # `0x197527fc222ef000` per body; it answers e02's
    # "Jackie Welles used to help my family" without any rewording of Elena.
    v2 = s.section([s.add_line(
        v, "Like Mama Welles? Thought I recognized the name.",
        male="Like Mama Welles. Thought I'd recognize the name.",
        key='v02')])
    s3 = s.section([
        E("V, I think I'm in big trouble, and I don't know who else to "
          "call. I remember Jackie saying that you don't turn your back on "
          "people.", 'e03'),
    ], holocall=True)
    # HUB 1 of 2. He is deciding to take this seriously. The button stays a
    # paraphrase; the spoken line is a whole recorded vanilla take
    # (vanilla_sid supplies audio, text and both bodies).
    c3 = s.choice([s.add_option("Go on, then.", 'o03')])
    v3 = s.section([s.add_line(v, "Go on, then. Let's hear it.", key='v03',
                               vanilla_sid=0x19124b2278623000)])
    s4 = s.section([
        E("I work in finance with the community accounts and I noticed "
          "something. People's debts are just zeroing out. They're not "
          "filing disputes or appeals. They're just gone.", 'e04'),
        E("When a debtor dies, their account should freeze, but instead "
          "it's been clearing, like, immediately. I thought it was a glitch, "
          "but it's not. It's just happened too many times.", 'e05'),
        E("I wasn't authorized to see it. I only noticed because I handle "
          "reconciliations. When I told my boss, my access was revoked and "
          "security walked me out of the building. I just think something's "
          "going on.", 'e06'),
    ], holocall=True)
    # Female body: "Are you OK?", a two-cut trim of `0x198010978c3bc000`.
    # Male body: the male actor's pauses do not allow the same extraction, so
    # he uses his own whole take of `0x224f09d92d62a000`; the male subtitle
    # carries his words, same mechanism as v05's since 2026-08-19.
    v4 = s.section([s.add_line(v, "Are you OK?",
                               male="Hey, are you all right?", key='v04')])
    s5 = s.section([
        E("I... I don't know. Should I be worried that they're after me or "
          "something?", 'e07'),
    ], holocall=True)
    # THE INSTRUCTION RESTRUCTURED (2026-09-02). No recorded V take directs a
    # third person to El Coyote, so the proposal is ELENA'S: V reassures her
    # (a trimmed vanilla take), she proposes Mama Welles herself (e07b, her
    # own recording), and V confirms with
    # two whole vanilla takes. "Where do you work?" is cut: e08 already sends
    # the office location unprompted.
    # RECAST 2026-09-03. It was "Everything's gonna be OK." - a promise V has
    # no way to keep, on a woman who has just asked whether she is being
    # hunted. He now answers the question she actually asked, in a trim of his
    # own recording: `0x179c170ae1559000` (v_japantown), drop_head at the
    # first pause.
    #
    # CUT AT A WORD, NOT AT A PAUSE, and that is the point of the clip. The
    # take reads "Tell 'er to lay low somewhere. They'll be lookin' for your
    # family, friends... You understand?" - V briefing a third party - and
    # "lay low somewhere" is the half the beat needs, because Elena answers
    # it by proposing El Coyote herself.
    #
    # splice_takes cuts on the silence map and there is no pause after "Tell
    # 'er to", so a first attempt shipped only the second sentence and lost
    # the instruction. The cut is taken at the start of "lay" (0.78 s female,
    # 0.80 s male), snapped to a zero crossing and given a 15 ms fade so the
    # onset cannot click. Listened to afterwards like every other trim.
    #
    # The male body says "family and friends" where the female says "family,
    # friends" - a real difference between the two recordings, so the male
    # subtitle carries his words, same mechanism as v04's.
    v5 = s.section([s.add_line(
        v, "Lay low somewhere. They'll be lookin' for your family, "
           "friends... You understand?",
        male="Lay low somewhere. They'll be lookin' for your family and "
             "friends... You understand?", key='v05')])
    s5b = s.section([
        E("Uh, maybe... maybe I could go to El Coyote? Mama Welles would "
          "take me in.", 'e07b'),
    ], holocall=True)
    # HUB 2 of 2. He is deciding where this goes; the button stays short.
    c5 = s.choice([s.add_option("Good idea.", 'o05')])
    v5b = s.section([s.add_line(v, "Good idea.", key='v5b',
                                vanilla_sid=0x1a58ecd70c2c5000)])
    v5c = s.section([s.add_line(v, "I'll see what I can do.", key='v5c',
                                vanilla_sid=0x196fda3a803bc000)])
    s6 = s.section([
        E("Thank you, V. Sending you the location of my office.", 'e08'),
    ], holocall=True)
    # V's "Got it. Wait. That's-" USED TO BE HERE and has MOVED to
    # gig01_arasaka - see build_arasaka. It is the same line, the same take and
    # the same words; only which scene owns it changed, because it is the line
    # Johnny interrupts and he could not be on screen for it from here.
    out = s.end('elena_call_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, v2)
    s.link_section(v2, s3)
    s.link_section(s3, c3)
    s.link_choice(c3, [v3])
    s.link_section(v3, s4)
    s.link_section(s4, v4)
    s.link_section(v4, s5)
    s.link_section(s5, v5)
    s.link_section(v5, s5b)
    s.link_section(s5b, c5)
    s.link_choice(c5, [v5b])
    s.link_section(v5b, v5c)
    s.link_section(v5c, s6)
    s.link_section(s6, out)

    # JOHNNY'S CUE, RESTORED. Fired from the START of s6 ("Sending you the
    # location."), which is two sections before the call ends.
    #
    # It was briefly removed, on the theory that gig01_arasaka.scene would stage
    # its own actor when it started. playtesting covered that: "the delay between V
    # saying 'Wait ... that's' and Johnny appearing is too long... he has no time
    # to appear before the phrase is already there." He then suggested exactly
    # this fix - make him appear while Elena is still talking.
    #
    # He was diagnosing it correctly. The chain was: V's line ends -> scene exits
    # -> quest sets cc_g01_call_end -> the holocall script queues EndCall -> the
    # phone hangs up -> cc_g01_call_done -> the arasaka scene starts -> the actor
    # streams in (~2 s). His line fires 700 ms into that scene, i.e. BEFORE the
    # body arrives, and the body arrives seconds after the line it belongs to.
    #
    # Cueing the SCRIPT spawn from here removes the whole chain: he is standing
    # there, silent, from the moment Elena sends the location, and the scene that
    # follows only has to supply the words. s6 runs ~3.3 s and V's last line
    # ~2.8 s, so he has ~6 s to stream in and start his workspot.
    s.fire_event(s6, s.add_fact_node('cc_g01_johnny_cue'), start_time=0)
    return s


# ========================================================== scene 2: the Nix call
def nix_actor(s, holo):
    """Nix, either standing in the holocall studio or a kilometre underground.

    THE TWO VARIANTS EXIST SO THE GIG CANNOT STALL, and that is the only reason
    the dialogue is built twice. The video one needs a studio that has to be
    opened, streamed and lit before it can be looked at, and a beat half an hour
    into the gig that cannot start would end the playthrough there. The quest
    phase opens the studio, waits a bounded time for it, and enters the plain
    scene instead if it never arrives.

      holo=True   a body of the scene's OWN, spawned on the studio spot and
                  rendered live on the phone. It is the scene's actor rather
                  than a borrowed one, which is what makes the lipsync land
                  (gotcha 16); it is forced visible because the player is 8.5 km
                  from it and would otherwise see an empty room.
      holo=False  what has shipped since 1.2.0: the same body, a kilometre away
                  and a hundred metres down, never seen, behind a static
                  contact portrait.

    THE OFFSET AND THE YAW ARE IN THE MARKER'S FRAME, not the world's. The
    quest phase anchors the video scenes at `#holocall_marker`, the studio's own
    floor spot, so (0, 0, 0) lands him exactly on it. That marker carries its
    own rotation of about -141 degrees: yaw 180 was derived from "the camera is
    at -Y" and put him back to the lens. 0 is correct, and it was found by
    looking at him (playtest, 2026-08-23).

    It used to ACQUIRE vanilla's studio body through the `nix_holo` spawn set.
    That works, and it only works for an incoming call to a base-game contact,
    because the body only exists while vanilla's own holocall phase is staging
    one. Spawning our own is what makes the outgoing call possible and what
    keeps Nix's small talk out of both (docs/backlog.md 3d).
    """
    if holo:
        return s.add_actor('nix', 'Character.Nix', offset=(0.0, 0.0, 0.0),
                           yaw=0.0, force_visible=True)
    return s.add_actor('nix', 'Character.Nix')


def build_nix_brief(holo=False):
    """V hands Nix the ledger and hires him. Comic pp. 26-27.

    Wording follows the recordings, the comic the order and the beats.

    THIS CALL WAS MISSING and its absence was a real hole: the gig had V read a
    kill ledger and then receive a callback about it from a netrunner he had
    never spoken to. The comic has TWO Nix calls and an earlier pass collapsed
    them into one, keeping only the callback "since that is the one carrying the
    information" - which is true, and left the handover happening off-screen.

    The comic opens on NIX ("How's things, V?"), so this works as an incoming
    call exactly like the other two: Nix rings, V answers, Nix speaks first. No
    new machinery for a player-placed call.

    The send and the payment are NOT in here - they are the beat immediately
    after, driven from script (Gig01_Encounter.SendLedger), because the comic
    puts the money transfer on p30 as an on-screen toast rather than a spoken
    line.

    FULLY AUTOMATIC, same call as the other Nix scene. This one was the worst
    offender in the whole gig: four hubs against three dialogue sections, i.e.
    more prompts than conversation, because V's three consecutive p26 lines were
    three consecutive single-option hubs. They are now one V section of three
    lines, which is what they always were.
    """
    s = Scene('gig01_nix_brief_holo' if holo else 'gig01_nix_brief', ANCHOR_OFFICE)
    nix = nix_actor(s, holo)
    v = s.add_player()

    def N(text, key, vanilla_sid=None):
        return s.add_line(nix, text, key=key, vanilla_sid=vanilla_sid)

    def V(text, key):
        return s.add_line(v, text, key=key)

    start = s.start('nix_brief_in')
    # THE ONE LINE IN THIS GIG THAT IS ALREADY RECORDED.
    #
    # "How's things, V?" IS a vanilla Nix line, word for word -
    # and it exists as a `vo_holocall` take, 1.537 s, which is the
    # register this beat needs. The comic was made from in-game screenshots, so
    # it had quoted vanilla dialogue verbatim without anyone noticing until the
    # VO corpus was built (docs/backlog.md 2b).
    #
    # Pointing at vanilla's stringId gets the audio AND the text for nothing:
    # `0x30b57ed4cf7df000` is the hex in the wem's own filename,
    # `nix_scene_nix_default_f_30b57ed4cf7df000.wem`.
    s1 = s.section([N("How's things, V?", 'b01', vanilla_sid=0x30b57ed4cf7df000)],
                   holocall=True)
    # EVERY LINE IN THIS CALL IS NIX'S OR V'S OWN RECORDING (2026-09-03). The
    # generated Nix lines that carried it (b02 "That's exec-tier heat, V.",
    # b05 "I'll call you back.") and V's trimmed vb1 are retired; keys are not
    # reused. What the call has to do is small enough for real takes to cover:
    # V offers work, Nix bites, V sends the files, Nix says how long.
    #
    #   V     "So listen, Nix... got a gig with your name on it if you're
    #          game."                                   0x2cbf89b6417df01c
    #   Nix   "Whatever this is, can't be good, but... shit, V, I's dyin' to
    #          know."                                   0x2cbf89b6cc7df03c
    #   V     "Yep, send you the files in a sec."       0x190fe72d3c4b6000
    #   Nix   "Should take me, I dunno... four, five hours?"   n01, a verified
    #          head-trim of 0x2e98cf00dc7e1000 (the whole take continues
    #          "Le'ss say we meet in six at the Arasaka Memorial", which is a
    #          different gig's rendezvous)
    #   Nix   "OK, guess I'ma go back to work."         0x19fab4aca82d2000
    #
    # The four-hour estimate is why the quest phase waits four in-game hours
    # before his message lands: the wait has to match the words.
    # V's three p26 lines, in one breath rather than three button presses.
    # THE ONE SANCTIONED BREAK IN THE COMIC-VERBATIM RULE, AND IT IS SCOPED TO
    # THESE TWO LINES. playtest, 2026-08-13, having played it: "we call Nix, but
    # what's our scope? ... he calls back and says 'V you were right' but we
    # never mentioned it." The ruling was to rework V's side of this call and
    # nothing else; this wording was picked from three options.
    #
    # The reasoning, which is the general principle and not a one-off: a comic
    # can leave a logical gap between panels because the reader closes it; a
    # playable gig cannot, because the player has to know what they just asked
    # for.
    #
    # The line that went is p26's "Need to know where they are." - it asks where
    # the NAMES are, and Nix answers with one man and a signature, so his
    # "V. You were right." had nothing to be right about. The replacement states
    # the hypothesis (someone signs) and asks the question Nix actually answers.
    # Retired key vb3 is not reused: its .wem is the old take, and a key is how
    # audio finds a line.
    #
    # NIX'S LINES ARE UNTOUCHED, and so is everything else in the gig. If a
    # future change seems to need a Nix line moved, that is outside what was
    # granted - stop and ask.
    # SPLICED-VOICES RESTRUCTURE (2026-09-02). V's side of this call is now his
    # own recordings: vb1 is a verified tail-trim of `0x18a75bd1984ea000`
    # (both bodies), the second line a whole take, and the send itself is what
    # the call is for; the ledger's meaning waits for his reply. Nix answers with
    # his surviving take (b02) and "Gimme a couple hours." (nb1), a two-chunk
    # build from his own vanilla recordings, then b05. vb2/vb5/vb6/vb4, b03
    # and b04 are retired, takes unreferenced, keys not reused.
    v1 = s.section([
        s.add_line(v, "So listen, Nix... got a gig with your name on it if "
                   "you're game.", key='vb8',
                   vanilla_sid=0x2cbf89b6417df01c),
    ])
    s2 = s.section([
        s.add_line(nix, "Whatever this is, can't be good, but... shit, V, "
                   "I's dyin' to know.", key='nb3',
                   vanilla_sid=0x2cbf89b6cc7df03c),
    ], holocall=True)
    v2 = s.section([
        s.add_line(v, "Yep, send you the files in a sec.", key='vb9',
                   vanilla_sid=0x190fe72d3c4b6000),
    ])
    # ...AND THE SEND HAPPENS WHILE THE CALL IS STILL UP (2026-09-03).
    #
    # It used to run after the call hung up, on cc_g01_nixbrief_done, so V
    # announced a transfer and then made it to nobody. The design call was to
    # put the encrypt-and-send banners between his line and Nix's answer,
    # which needs two things this scene now does:
    #
    #   cc_g01_ledger_send   set FROM INSIDE the scene (add_fact_node), which
    #                        is what Gig01_Encounter watches to start the
    #                        three send beats
    #   cc_g01_ledger_sent   waited on INSIDE the scene (add_wait_fact_node),
    #                        set by the last of those beats
    #
    # The wait is the same node the base game's own office scene uses six
    # times over; the conversation simply holds until the transfer is done.
    send = s.add_fact_node('cc_g01_ledger_send')
    wait = s.add_wait_fact_node('cc_g01_ledger_sent')
    s3 = s.section([
        # HIS ACKNOWLEDGEMENT, and it lands on the data actually arriving:
        # a head-trim of "Now, let's get this show underway. Hm, hm. Most
        # data's corrupt..." cut at the sentence end.
        N("Now, let's get this show underway.", 'n02'),
        # THE ONE OTHER PRODUCED CLIP IN THIS CALL: a head-trim of his
        # recorded estimate, cut at the pause after "hours?". The call ENDS
        # here, on the number - "OK, guess I'ma go back to work." was the
        # sign-off and read as him losing interest.
        N("Should take me, I dunno... four, five hours?", 'n01'),
    ], holocall=True)
    # V ACCEPTS THE ESTIMATE, and the call ends on him rather than on a
    # number (2026-09-03). A whole recorded take, `0x1a0a078ed54e2000`
    # (mq023): dry, short, and the only thanks in his recordings that does
    # not name somebody else.
    v3 = s.section([
        s.add_line(v, "Much appreciated.", key='vb10',
                   vanilla_sid=0x1a0a078ed54e2000),
    ], tail_ms=600)
    out = s.end('nix_brief_out')

    s.link(start, s1)
    s.link_section(s1, v1)
    s.link_section(v1, s2)
    s.link_section(s2, v2)
    # V's line -> set the send fact -> hold for the transfer -> Nix answers.
    # Both quest nodes take their input on ordinal 1 ("In"); ordinal 0 is the
    # cutscene-skip path, which is silent when wired by mistake.
    s.link_section_quest(v2, send)
    s.link_quest(send, wait)
    s.link(wait, s3)
    s.link_section(s3, v3)
    s.link_section(v3, out)

    # THE VIDEO VARIANT ONLY. The plain one plays behind a contact portrait
    # with no body anywhere, and its marker is not in a sector that loads.
    if holo:
        lookat = s.add_lookat_prop('cc_g01_holocall_lookat', HOLO_LOOKAT_REF)
        for sec in s.sections():
            s.look_at(sec, nix, lookat, start_time=0)
    return s


# ========================================================= scene 3: Hoshino
# WHERE NIX LOOKS ON THE VIDEO CALL. The studio's quest sector carries one of
# these per contact, a marker entity standing exactly where that contact's
# camera is, and `wakako_holocall.scene` is where vanilla aims a caller at one.
#
# IT IS MAMA WELLES'S BECAUSE THE CAMERA IS. gen_questphase opens her lights,
# her setup and her camera for this call on purpose: the 59 setups differ in
# camera height because each is framed on its contact's pose, and
# `#nix_holocall_camera` sits at 0.75 because the real Nix sits cross-legged.
# Our Nix stands. The marker has to match the camera in use, not the character,
# or the eyes go somewhere the lens is not. Checked in the studio sector
# (`quest_ec82d0423d8f1435`): both this and `#nix_holocall_lookat` are there.
#
# NO WORKSPOT WITH IT, and that is the design call rather than an oversight.
# Gig 02 changed the pose and the eyes in one pass; here only the eyes move, so
# the framing that has shipped since 1.2.0 is untouched.
HOLO_LOOKAT_REF = '#mama_welles_holocall_lookat'


# EYES ON V, copied from gig 02's gen_scenes.py, which took it off
# `wakako_okada_default.scene`. A workspot fixes where a body is and which way
# the torso faces; the head and the eyes go on playing the idle's own drift, so
# a correctly placed speaker still looks past the player. `scnLookAtEvent` is
# what turns them, one per section at t=0 with `removePreviousAdvancedLookAts`
# set, and vanilla's own Wakako conversation carries ten of them on that shape.
#
# NOTHING RELEASES IT AT THE END. No section in that scene clears the look-at on
# its way out; the scene ending is what ends it.
def face_player(s, actor):
    """Hold an actor's eyes on V for every section of the scene.

    Call it AFTER the section links, the same rule gig 02's copy carries.
    """
    player = s.player_performer()
    for sec in s.sections():
        s.look_at(sec, actor, player, start_time=0)


def build_hoshino():
    """The estate. Two ways to open: name what he signed, or say nothing at all.
    They end in the same place - a choice of tone, not of outcome, which is the
    only kind this story supports - but they have to EARN that by getting
    different answers out of him. The branches converge on the quota line, which
    is the point of the whole gig: he is not the machine, he is a signature in
    it, and killing him changes nothing.
    """
    s = Scene('gig01_hoshino', ANCHOR_ESTATE)

    # THERE USED TO BE TWO HOSHINOS HERE. Collapsed 2026-08-13, and the note
    # below is kept because the reasoning is what closed it.
    #
    # The experiment was: h01 from a body buried 2.5 m under the floor, h02 from
    # a visible duplicate at the marker, to find out whether a HIDDEN speaker can
    # be heard at all. It was never run - and it did not need to be.
    #
    # the description of Mama Welles settled it from a different scene
    # entirely: "her voice is low and far, like almost cannot hear it". That is
    # distance attenuation, not a routing failure, which means (a) a mod
    # voiceover map IS consulted for world lines and (b) the only variable is how
    # far the speaker is from the listener. A buried actor 2.5 m down is
    # therefore audible, and the visible duplicate had no job left.
    #
    # Keep the habit: a report from one part of the build can answer an
    # experiment shipped in another. Ask "silent, or quiet?" - the two answers
    # point at completely different subsystems.
    #
    # The original note follows.
    #
    # WHY THERE ARE TWO HOSHINOS HERE, and why it is temporary.
    #
    # Playtest 2026-08-12: Elena's voiced lines played, Hoshino's did not. The
    # difference is not the audio - it is WHERE THE SOUND COMES FROM. Elena's
    # lines are `holocall=True`, so they play 2D through the phone; Hoshino's
    # play from a world emitter, and every voice-only actor in this file is
    # parked at the scene marker plus (1000, 1000, -100). A kilometre away and a
    # hundred metres down. The subtitles never cared; the audio does.
    #
    # `#q113_dvc_arasaka_estate_camera_010` sits 4.7 m from Hoshino's actual spot
    # (find_pin_anchors, 2026-08-12), so the marker is already in the right room.
    # Only the offset is wrong.
    #
    # That leaves one thing unknown - whether a hidden emitter is
    # audible, or whether world lines ignore a mod voiceover map altogether - so
    # this asks BOTH questions at once and gets the answer in one playthrough:
    #
    #   h01 -> BURIED actor, 2.5 m under the floor. Close enough to hear,
    #          under the floor so nobody sees him. This is the fix we want.
    #   h02 -> VISIBLE actor, standing at the marker. Guaranteed audible if the
    #          mechanism works at all, at the cost of a duplicate Hoshino for the
    #          length of the scene. This is the control, not a candidate.
    #
    #   both heard      -> keep h01's offset, delete the second actor
    #   only h02 heard  -> burial is occluded; try a small horizontal offset
    #                      behind the player instead, or Audioware for world lines
    #   neither heard   -> NOT a distance problem. World lines are not consulting
    #                      our vomap; the holocall map is a separate registration
    #                      and only that one is being merged
    #
    # If that question is settled, COLLAPSE THIS BACK TO ONE ACTOR. A duplicate
    # NPC on screen is a diagnostic, not a design.
    #
    # THE BURIAL IS GONE, 2026-08-17. It was `offset=(0, 0, -2.5)` from
    # ANCHOR_ESTATE, and a field report against 1.1.3 describes what that
    # produced: *"he just spawned out of no where on the first floor, though he
    # was half-way in a pillar. Once I selected one of the dialog options, he
    # disappeared and is now no where to be found."* Arriving from nowhere,
    # standing inside geometry and vanishing when the dialogue ends are all
    # properties of a scene's own actor, which is created when the scene starts
    # and deleted when it exits. The Hoshino the player fights is not that.
    #
    # 2.5 m under the anchor was only ever meant to be close enough to HEAR,
    # and burial cannot be made safe by measurement here: ANCHOR_ESTATE is a
    # security camera, so its height is a mounting height rather than a floor,
    # and its transform is not in any file this repo can read (the cooked
    # sectors store node refs as hashes; only the always-loaded name registry
    # spells the name out, and it carries no position). Whatever is 2.5 m below
    # a camera is unknown, and the road tunnels under the North Oak villa.
    #
    # So the body goes back to where every other voice-only actor in this file
    # stands: a kilometre out and a hundred metres down, which is far enough
    # that nothing can see it, walk into it or watch it disappear. That costs
    # the audio, and the sections below buy it back by making his lines 2D.
    # Elena and Nix have always worked this way.
    # AND NOW HE IS NOT SPAWNED AT ALL. THE SCENE TAKES THE BODY THAT IS THERE.
    #
    # Everything above is the history of trying to put a SECOND Hoshino
    # somewhere the player would not notice him: buried under the floor, then a
    # kilometre out and a hundred metres down, with the lines made 2D to buy
    # back the audio. The field report that closed the burial, "half-way in a
    # pillar ... once I selected one of the dialog options, he disappeared" -
    # is what a scene's own actor looks like when the player can see it.
    #
    # There is no second body now. A community this mod ships stands the real
    # Hoshino at his terminal (`gen_community.py`), the quest phase switches him
    # on when the estate objective goes up, and this actor ACQUIRES him:
    #
    #     acquisitionPlan  spawnSet
    #     entryName        the community entry
    #     reference        the string registered in spawnSetNameToCommunityID
    #
    # `specRecordId` is 0 on that path, so nothing can be spawned: he is found
    # or this scene has no speaker. Sixteen bench runs are behind it and
    # `gotchas.md` 69 is the recipe.
    #
    # THE LINES CAN GO BACK TO BEING WORLD LINES. `inner_vo` below made them
    # play 2D because the speaker was a kilometre away; the speaker is now
    # standing in front of the player, which is what that flag was compensating
    # for. Left as it is for THIS build on purpose: one change at a time, and
    # the acquisition is the change. If he is audible and located correctly in
    # play, drop the flag and hear him from his own mouth.
    hoshino = s.add_spawnset_actor('hoshino', HOSHINO_ENTRY, HOSHINO_SPAWNSET)

    # NO JOHNNY IN THIS SCENE. He used to stand here through the whole
    # negotiation, with the comic's p43 and p45 lines. the design call, 2026-08-12,
    # once he could actually be SEEN: a visible Johnny loitering beside a man
    # who cannot see him, for the length of a conversation, reads as a bug
    # rather than as a relic.
    #
    # He now appears AFTER the kill, over the body, on the dynamic-spawn route -
    # Gig01_Encounter.reds, Line(35). That is also where docs/backlog.md item 3
    # wanted to spend him ("Best spots: after Elena's call, over Hoshino's body,
    # and the last line at El Coyote"), so this moves him onto the plan rather
    # than off it.
    #
    # p45 "They always think names beat bullets." survives as that line. p43
    # "That's what blood money buys. Soft chairs." is DROPPED: it is a comment on
    # the room on the way in, and there is no longer a moment for it. Easy to
    # restore as an arrival beat if it is missed.

    start = s.start('hoshino_in')
    # COMIC pp. 44-46, in order. His two lines, then V's answer.
    #
    # An earlier pass offered "[Say nothing.]" as an alternative opener. Both
    # branches got the same reply out of him, which made it a decision with no
    # consequence - the exact thing playtesting called out. One option.
    # h01 speaks from the BURIED actor, h02 from the VISIBLE one - see the note
    # by the actor definitions. Which of these two you hear is the whole result
    # of the experiment.
    v = s.add_player()
    # No-op while BRIDGE_SCENES is empty, the same standing the Johnny beats'
    # double has. He is acquired from the world by the actor above, so his own
    # mouth moves and nothing here has to lend him one; this is kept because the
    # machinery is one constant away from being usable again. See
    # add_body_double and BRIDGE_SCENES.
    s.add_body_double(hoshino, 'hoshino_body', tag='cc_g01_hoshino')

    # HIS LINES ARE 2D, WHICH IS WHAT LETS THE BODY STAND A KILOMETRE AWAY.
    #
    # A speaker that far off is inaudible while his line is positional, and one
    # thing was known about stopping that: `inner=True` lines were audible from
    # a marker in the wrong place while `Vo_Expression_Spoken` ones were not
    # (scene-playbook, the table on line styling). `inner` sets two fields at
    # once, `voExpression` and `visualStyle`, and which of them carried the 2D
    # behaviour had never been separated.
    #
    # Separated in playtest, 2026-08-17, by routing his two lines differently in
    # one conversation: h01 with the VO expression alone, h02 with both. Both
    # were audible and both subtitles read "Hoshino: ..." in ordinary styling,
    # so `voExpression` carries it and `visualStyle: innerDialog` changed
    # nothing visible on a line whose speaker is not Johnny.
    #
    # AND `inner_vo` IS NOW OFF, because the reason for it is gone.
    #
    # Everything above is about a speaker who was a kilometre away and a hundred
    # metres down: 2D playback was how a voice reached the player from there at
    # all. He is acquired from the world now (see the actor above), so he is
    # standing in front of V, and a 2D line from a man two metres away is a line
    # that does not come from him: no direction, no distance, no falloff when
    # V walks off mid-sentence.
    #
    # Confirmed audible from the body first, playtest 2026-08-24: "He speaks and
    # his mouth moves." That is what makes this safe to drop rather than a
    # gamble; positional is the reason the acquisition was worth doing.
    #
    # IF HE IS SUDDENLY QUIET, this is the line to put back. `inner_vo=True` on
    # both sections restores exactly the previous behaviour and costs only the
    # spatial audio.
    s1 = s.section([s.add_line(hoshino, "Hmm? Are you lost, merc?", key='h01')])
    # NOT the comic's wording. p45 reads "You know who I am." - a flat
    # assertion - and playtest, 2026-08-14: "Hoshino's phrasing is weird". It is,
    # and the cause is structural rather than lexical: the comic has a page turn
    # and a close-up between this and "You lost, merc?", the gig has nothing,
    # and V has not spoken yet. A question followed by a flat assertion, with no
    # answer in between, reads as a non-sequitur; two questions from a man
    # getting silence back is natural escalation. So this repairs the beat
    # rather than only rewording it.
    #
    # Both forms are vanilla (`vo_corpus.py search "know who I am"`): three
    # civ_high barks of "Do you know who I am?" and one flat "You know who I am"
    # from Johnny wearing V's body in sq011. The question is the game's stock
    # arrogant-rich-NPC register - bluster - which is what Johnny's reply on the
    # same page ("They always think names beat bullets.") exists to puncture.
    #
    # DO NOT change this string without generating the audio in the same pass.
    # Nothing downstream compares subtitle text to the clip, so a desync here
    # would be silent.
    s2 = s.section([s.add_line(hoshino, "Do you know who I am?", key='h02')])
    # The prompt says what V is about to do; the line under it is what he
    # actually says. Relabelled 2026-09-03 with the line: "Name what he
    # signed" described the interrogation beat that no longer exists.
    c1 = s.choice([s.add_option("The debtors.", 'oh2')])
    # ...and then V SAYS it. playtest, 2026-08-13: "V reply to hoshino is silent".
    # It was a hub option and nothing else - the player pressed a line nobody
    # spoke. Same fix as Elena's two kept hubs: press it, then hear it.
    # RECAST AGAIN 2026-09-03, and this is the line the whole corpus search
    # was looking for: V naming what the man did, in V's own recorded voice,
    # without a single cut. "I know." (vh1) was the placeholder while the
    # answer was going to come from an interrogation scene that no longer
    # exists; V now arrives knowing the scheme from Nix's message, so he can
    # say what he came to say. `0x30d9a8297a405000`, q304.
    v1 = s.section([s.add_line(v, "Peeps ain't pawns to me. You'll pay for "
                               "what you did.", key='vh2',
                               vanilla_sid=0x30d9a8297a405000)])
    out = s.end('hoshino_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, c1)
    s.link_choice(c1, [v1])
    s.link_section(v1, out)

    # He looks at the man who walked into his house. Without this he delivers
    # both lines to the middle distance, which is what a community idle does
    # with a head nobody has aimed.
    face_player(s, hoshino)
    return s


# ================================================ the converted caption beats
#
# Five scenes that were scripted captions in Gig01_Encounter.Line() until
# 2026-08-13. playtesting covered the build and reported every one of them silent,
# which is what the caption route guarantees: no locstring RUID, so
# nothing for the voiceover map to key on.
#
# They all share one shape, and it is worth stating once rather than five times:
#
#   marker      ANCHOR_PLAYER. Every one of these happens wherever V is
#               standing, so a fixed NodeRef cannot site the speaker.
#   V           a player actor. Costs nothing to place - findInContext finds him
#               - and his audio therefore plays from the listener's position.
#   Johnny      a present scene actor, JOHNNY_SOLID, with a workspot. Solid
#               because a blendable appearance renders nothing unless the
#               phantom system is driving it, and these beats are not the place
#               to test that.
#   offsets     BEAT_STAGING, in V's OWN frame: +Y forward, +X right. The
#               marker's rotation IS ours to know, measured five times in game
#               (docs/backlog.md 9), so these are real directions and not
#               merely a distance. The facing is computed by yaw_to_face_player
#               and must never be typed by hand.
#
# The SCRIPT no longer spawns, places or searches for Johnny anywhere - it does
# not know he exists - but it still owns every quest fact it owned before.
# Nothing about quest progression moved into a scene.


# WHERE JOHNNY STANDS, PER BEAT, IN V'S OWN FRAME.
#
# (aside, ahead) in metres: aside is positive to the RIGHT, ahead is
# positive FORWARD. Both are measured properties of an `around_player`
# marker rather than guesses; docs/backlog.md 9 has the five runs.
#
# The numbers came from the script placement these replaced, where they were
# written the other way round as (ahead, aside) and had been hand-tuned
# against real geometry. Do not re-derive them.
#
# The facing is COMPUTED by yaw_to_face_player. Never write a yaw here: a
# fixed 180 only looks at V from dead ahead and is 32 degrees wide at
# (1.1, 1.8).
# LEFT, i.e. a negative aside. There is no vanilla convention to copy: the
# one shipped Johnny scene on an `around_player` marker anchors him to a
# world node with a zero offset, so it encodes no side. Left is the design
# call, taken after seeing both in game.
BEAT_STAGING = {
    'gig01_arasaka':    (-0.8, 2.6),   # his answer as Elena's call drops
    'gig01_terminal':   (-1.2, 0.9),   # V is nose to a screen, so mostly aside
    'gig01_shard_read': (-0.75, 2.3),   # at the office desk
    'gig01_legend':     (-0.8, 2.6),   # the crosswalk
    'gig01_graves':     (-0.8, 2.6),   # p30
    'gig01_kill':       (-0.75, 2.3),   # over Hoshino's body
    'gig01_malware':    (-1.6, 0.9),   # estate terminal: FAR left. Further
                                      # ahead put him behind the screen.
}


def _beat(name, visible_johnny=False):
    """Common opening for the beats that happen wherever V is standing.

    `offset` is in V's own frame: +Y forward, +X right, metres. `yaw` turns
    the actor once he is there; pass yaw_to_face_player(offset) to have him
    look at V. Both are measured facts about an `around_player` marker, not
    assumptions: see docs/backlog.md 9 for the five runs behind them.

    A scene actor placed this way arrives already posed, so there is nothing
    for a script to lift and nothing to hide with an effect.

    `visible_johnny` gives the actor a SOLID appearance and a workspot.

    JOHNNY IS THE SCENE'S OWN ACTOR AND THE LINE'S SPEAKER, which is what
    buys lipsync and lets a mod voiceover map key on the line. A caption
    pushed from script carries no RUID and can never be voiced.
    """

    aside, ahead = BEAT_STAGING[name]
    offset = (aside, ahead, 0.0)
    yaw = yaw_to_face_player(offset)
    s = Scene(name, ANCHOR_PLAYER)
    if visible_johnny:
        # BURIED, LIKE EVERY OTHER SPEAKER IN THIS FILE - which is the fix
        # for the entry, not a step backwards.
        #
        # playtest, 2026-08-14: *"The entry is bad. I see it on top of me for a
        # while then moves to the other location. Can he be transparent before
        # you move him and only appear during glitch?"* Exactly the right
        # instinct, and burial is how to get it.
        #
        # Transparency itself is not available: what hides him is having no
        # workspot, and today proved that also makes him UNTARGETABLE, so the
        # script can never find him to move him (the deadlock in the entry
        # above). Underground costs nothing and breaks no rule - he is a real,
        # workspotted, findable entity the whole time, just below the floor.
        #
        # So the sequence the player sees becomes: nothing, then Johnny
        # materialising in front of them with his own arrival glitch. The
        # staging spot is never on screen.
        #
        # -2.5 m is the offset the voice-only actors have used since 2026-08-13.
        # Straight down needs no knowledge of the marker's rotation, which is the
        # whole reason it was chosen there and the reason it works here.
        # JOHNNY_GHOST now the duplicate is gone. SOLID was only ever there so
        # the two Johnnys could be told apart on screen during the trial; with
        # one body the see-through apparition is the look this gig ships, and
        # the workspot that satisfies phantomVisibleStates is running either way
        # (the scene's, then the script's device).
        johnny = s.add_actor(JOHNNY_ACTOR, 'Character.Silverhand',
                             offset=offset, yaw=yaw,
                             appearance=JOHNNY_GHOST, validate=1)
    else:
        johnny = s.add_actor(JOHNNY_ACTOR, 'Character.Silverhand',
                             offset=offset, yaw=yaw)
    v = s.add_player()
    # No-op while BRIDGE_SCENES is empty - kept because the machinery is one
    # constant away from being usable again if a route to acquiring the visible
    # body is ever found. See add_body_double and BRIDGE_SCENES.
    s.add_body_double(johnny, 'johnny_body', tag='cc_g01_johnny')
    return s, johnny, v


def build_arasaka():
    """Comic p11. Elena's location lands and Johnny puts a name to it.

    One line, and it is the one that could not be sited before: this fires the
    moment Elena's call ends, and the gig can be started from anywhere in Night
    City, so there is no fixed marker within a kilometre of the player.

    The `cc_g01_johnny_cue` machinery that used to stage him a line early is
    gone with it - a scene spawns its own actor when it starts, so the lead time
    is the scene's to manage rather than a fact fired from inside Elena's call.

    ======================================================================
    THIS SCENE'S JOHNNY IS DELIBERATELY VISIBLE, AND THERE ARE TWO OF HIM.
    ======================================================================

    A DIAGNOSTIC, NOT A DESIGN - collapse it the moment it has answered. There
    is precedent for exactly this shape in this file: `build_hoshino` shipped a
    visible duplicate for one playtest in 2026-08-12 and was collapsed as soon
    as the answer arrived.

    THE QUESTION IT ANSWERS: **does our lipsync data animate anything at all?**
    Everything else about lipsync is verified offline - the lipmap merges clean,
    the RUID key is proven against 3495 vanilla entries, the animation exists in
    a shipped set - and none of that says the game applies it. The only place a
    lipsynced mouth could be SEEN was `gig01_bar`, because the bar is the one
    scene whose speaker is its own visible actor. Playtest, 2026-08-14: *"Why at
    the bar? I need to run the whole quest because the shortcut doesn't work."*
    Right - a test forty minutes in, with no shortcut, is not a test.

    So this beat gets a visible speaker, two minutes in. The scene's Johnny is
    raised out of the floor and given a workspot; the SCRIPT still spawns its
    own beside V. For about four seconds there are two Johnnys, and they are
    told apart on purpose:

        the script's   silverhand_default - the see-through, glitching ghost
        the scene's    JOHNNY_SOLID       - solid, ordinary, no FX

    **The solid one is the speaker.** If ITS mouth moves, the lipsync chain
    works end to end and the only remaining problem is the one this gig already
    knows about - getting the words onto the body the script placed (backlog 2j,
    "ONE BODY INSTEAD OF TWO"). If it does not move, the data route is dead and
    that is the written finding.

    Three details that are not free choices:

      offset (0,0,0)  he stands AT the around_player marker, which lands a few
                      metres to one side of V. Not on V, and the direction is
                      not knowable - that is the whole reason the script owns
                      placement. Fine for a diagnostic: he only has to be
                      visible, not well staged.
      validate=0      position validation OFF. A rejected spawn is no actor, and
                      an actor that does not exist cannot speak - that would
                      cost this beat its audio and its subtitle to answer a
                      question about its mouth.
      audio unchanged this line is `inner=True`, i.e. Vo_Expression_InnerDialog,
                      which plays 2D in V's head. Moving the speaker from 2.5 m
                      under the marker to standing on it cannot change how it
                      sounds.
    """
    # TEMPORARY: horizontal offset so the marker probe has a direction to
    # measure. Restore the default when the probe comes out.
    s, johnny, v = _beat('gig01_arasaka', visible_johnny=True)
    start = s.start('arasaka_in')
    # V'S LINE MOVED IN FROM gig01_elena_call, WHICH IS THE FIX FOR THE
    # TIMING - not a rewrite. Same line, same recorded take, same words.
    #
    # Playtest: *"Johnny should spawn much earlier, before V says 'wait that's'.
    # Instead it appears a while after that phrase."* He is right, and the cause
    # is structural rather than a number that can be tuned: **a scene actor
    # cannot exist before its own scene starts**, the arasaka scene starts when
    # the call ends, and "Got it. Wait. That's-" is 3.28 s of the call's last
    # line. Johnny could not be on screen for a line that finishes before he is
    # allowed to exist.
    #
    # THE SAME BUG WAS HERE ON 2026-08-13 and the note explaining it is still in
    # build_elena. It was fixed then by cueing the SCRIPT's Johnny two sections
    # early; removing that spawn on 2026-08-14 to get one body brought it
    # straight back. Read a fix before you delete the thing it fixed.
    #
    # Cueing early cannot work now: the quest phase is a linear chain and this
    # scene node can only be entered from one place (a scene node with two
    # sources does not fire - measured across 358 shipped questphases), so it
    # cannot start during the call.
    #
    # So the line comes to Johnny. The beat is now what the comic prints: he
    # glitches in beside V, V says "Got it. Wait. That's-", and Johnny finishes
    # the thought. Moving a line between scenes changes its RUID, so the clip is
    # COPIED to the new key - the same operation p25 went through on 2026-08-13,
    # and no take is regenerated.
    # SPLICED-VOICES RECAST (2026-09-02): the interrupted line is now two whole
    # recorded takes in sequence, and Johnny's entrance answers the second.
    # The take that used to carry v06 is retired and deleted.
    vsec = s.section([
        s.add_line(v, "Got it.", key='v06a', vanilla_sid=0x1ab375df4c44d000),
        s.add_line(v, "Wait... what?", key='v06b',
                   vanilla_sid=0x19d79031063bc000),
    ], lead_ms=1200)
    # V's section carries the LEAD now (900 ms), so Johnny is placed and
    # glitched in before V opens his mouth: he is put in place ~300 ms after the
    # scene starts - one 0.15 s poll to find him, one more for the workspot
    # device to stream - which leaves ~600 ms of him standing there first.
    #
    # Johnny's own section then only needs 200 ms of lead, because he is already
    # on screen and V has just been cut off mid-sentence. The 4000/3000 above
    # were measuring numbers, kept only long enough to turn round and
    # find a body that had staged itself behind him; he does not have to any
    # more (*"Position is perfect"*).
    #
    #   tail 1500   Playtest: he should *"disappear a few seconds after Arasaka"*.
    #               1000 gave him 750 ms of standing there before the glitch,
    #               which reads as being cut off. The exit fires 250 ms before
    #               this section ends, so the tail IS how long he lingers.
    #
    #               2500 shipped and measured at 2.5 s from the end of the line
    #               to him being gone - 2.25 s standing plus the 0.25 s glitch.
    #               playtest, 2026-08-14: "a bit shorter". 1500 leaves 1.25 s of
    #               standing, still clear of the 750 ms that read as a cut-off.
    #               There is no script constant to keep in step - the scene
    #               fires the exit cue itself, 250 ms before the section ends.
    # Approved in review 2026-08-29: Johnny's entrance is his own recorded
    # take, and it answers V's confusion directly.
    s1 = s.section([s.add_line(johnny, "'Cause it always is Arasaka.",
                               key='ja1', vanilla_sid=0x168590edca351000)],
                   inner=True, tail_ms=1500, lead_ms=200)
    out = s.end('arasaka_out')
    s.link(start, vsec)
    s.link_section(vsec, s1)
    s.link_section(s1, out)

    s.stage_johnny(vsec, s1)
    return s


def build_terminal():
    """Comic pp. 22 and 25, at the office terminal. Nine lines, the longest of
    the converted beats and the thesis of the whole gig ("It's a production
    line.").

    Entered when V unplugs, NOT when the copy finishes: Gig01_Encounter waits on
    IsUsingDevice going false before setting cc_g01_terminal_left. That gate is
    older than this conversion and stays exactly where it was - spawning
    anything on a player locked in a device zoom is what soft-locked the office
    once.

    Johnny's offset is the one the script used here (0.5, 1.4) rather than the
    street one: V is nose to a screen against a wall, so "ahead" is inside the
    wall. He goes almost entirely to the side.
    """
    s, johnny, v = _beat('gig01_terminal', visible_johnny=True)

    def V2(text, key, sid):
        return s.add_line(v, text, key=key, vanilla_sid=sid)

    def J2(text, key, sid):
        return s.add_line(johnny, text, key=key, vanilla_sid=sid)

    start = s.start('terminal_in')
    # THE TERMINAL EXPLAINS NOTHING NOW (2026-09-03), and that is the design
    # rather than a shortfall. V and Johnny speak only in recordings the game
    # already shipped, and no recording of either explains an insurance-kill
    # scheme; every attempt to assemble one was rejected on the grounds that
    # it read as neither of them. So the beat became what their own takes CAN
    # carry: a merc looking at corporate paperwork he cannot parse, and a
    # relic telling him who can.
    #
    # The exposition moved to two places nobody has to voice: the file on the
    # screen (gen_localization, file-6) and Nix's text message.
    #
    # FIVE WHOLE TAKES, no cuts, chosen so each answers the one before:
    #   V       "Wait... What the hell is this?"      0x196ba056ea62a000 mq018
    #   Johnny  "...what's the message say?"          0x17f1ef13bc46b000 sts_bls_ina_03
    #   V       "Sorry... just don't get it."         0x192cbefabf2a0000 q113
    #   Johnny  "Take it to Nix."                     0x1a43603dab44d000 mq015
    #   V       "Yeah."                               0x19cd487bb9521000 sq024
    #
    # Johnny's line is the load-bearing one and it constrains the SCREEN: it
    # says "you'd think every smart-ass would've encrypted their comms by
    # now", so the ledger file must be readable and merely opaque, not locked.
    # That is why file-6 lost its "[AUTHORIZATION KEY ENCRYPTED]" lines the
    # same day. The old keys t01/t03/t04/t05/t09/t10 are retired; their takes
    # stay in source/audio unreferenced and the keys are not reused.
    s1 = s.section([V2("Wait... What the hell is this?", 't11',
                       0x196ba056ea62a000)])
    s2 = s.section([J2("You'd think every smart-ass would've encrypted their "
                       "comms by now. Anyway... what's the message say?",
                       't12', 0x17f1ef13bc46b000)], inner=True)
    # RECAST 2026-09-03. It was "Sorry... just don't get it." - V grieving in
    # a late main-quest scene, so it played as pain rather than puzzlement.
    # This one is V saying exactly that to NIX in vanilla, which is who he is
    # about to call. `0x2cbf89b6cc7df030`, scene_nix_default.
    s3 = s.section([V2("Honestly, man? Got no clue...", 't16',
                       0x2cbf89b6cc7df030)])
    s4 = s.section([J2("Take it to Nix.", 't14', 0x1a43603dab44d000)],
                   inner=True)
    s5 = s.section([V2("Yeah.", 't15', 0x19cd487bb9521000)], tail_ms=800)
    out = s.end('terminal_out')

    s.link(start, s1)
    for a, b in ((s1, s2), (s2, s3), (s3, s4), (s4, s5), (s5, out)):
        s.link_section(a, b)
    s.stage_johnny(s1, s5)
    return s


def build_kill():
    """Over Hoshino's body, comic p45.

    Two lines that used to fire from two different places in Tick and had to be
    spaced 5 s apart by hand, because they shared one subtitle widget and the
    first one's HIDE would wipe the second. A scene has no such problem: each
    section owns its own time.
    """
    s, johnny, v = _beat('gig01_kill', visible_johnny=True)
    start = s.start('kill_in')
    # ONE LINE OVER THE BODY (2026-09-03). V said his piece to Hoshino's face
    # a moment ago, and a merc who has just shot a man does not summarise; the
    # beat is Johnny's, and his own recording says it in four words.
    # `0x17ba4062bf4e1000`, q112. Keys k01/k02 are retired with their takes.
    s1 = s.section([s.add_line(johnny, "Rest in peace, bastard.", key='k03',
                               vanilla_sid=0x17ba4062bf4e1000)],
                   inner=True, tail_ms=800)
    out = s.end('kill_out')
    s.link(start, s1)
    s.link_section(s1, out)
    s.stage_johnny(s1, s1)
    return s


def build_malware():
    """The estate terminal, comic p51. V's line was a HUD banner until the
    progress bar took over that corner of the screen; it is dialogue.

    THIS ONE IS GATED ON V BEING OFF THE DEVICE, which is not optional.
    Johnny used to be an ownerless subtitle here precisely because V is plugged
    into a terminal at this moment and spawning a puppet on a player locked in a
    device zoom soft-locked the office beat once. A scene stages an actor the
    same way, so it waits for the same signal: Gig01_Encounter sets
    cc_g01_malware_talk once IsUsingDevice goes false.
    """
    s, johnny, v = _beat('gig01_malware', visible_johnny=True)
    start = s.start('malware_in')
    # RESTORED AND RECAST 2026-09-03. The beat was cut that morning because
    # its only line, V's "Fuck. Never again.", is him grieving in a late
    # main-quest scene and read as pain rather than disgust, with Johnny
    # silent beside him. The design call is that the moment wants an
    # exchange: the malware is in, the payout network is coming down, and
    # the killing it paid for stops with it.
    #
    # NO RECORDING SAYS "no eddies, no bodies", which is the idea behind it.
    # What exists is the pair below, both whole takes: V closes the job flat,
    # and Johnny answers with the story's own point - the machine survives
    # the man, and will grow another one. His line was over Hoshino's body
    # until the same morning, where "Rest in peace, bastard" replaced it; it
    # belongs better here, on the network rather than on the corpse.
    #
    #   V       "Think we're done. That's it."         0x1791ffc1914b6000
    #   Johnny  "'Cause enough people had died for
    #            nothing already."                     0x180d044ca8351000
    s1 = s.section([s.add_line(v, "Think we're done. That's it.", key='w05',
                               vanilla_sid=0x1791ffc1914b6000)])
    s2 = s.section([s.add_line(johnny, "'Cause enough people had died for "
                               "nothing already.", key='w06',
                               vanilla_sid=0x180d044ca8351000)],
                   inner=True, tail_ms=1000)
    out = s.end('malware_out')
    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    s.stage_johnny(s1, s2)
    return s


# ======================================================== scene 3: epilogue
def build_epilogue():
    """THE EPILOGUE, and the real Mama Welles speaks it.

    Taking her as the scene's actor is what stops her ordinary bar conversation
    - a quest scene owns the actor it acquires. The 1.0.0 design never claimed
    her at all, which is why her chit-chat could win the approach and the player
    had to walk away and come back (backlog 7d).

    THE ONLY VARIANT SINCE 2026-08-18. A second one played when she was not in
    the bar; the gig now waits for the quest that puts her there, so the quest
    phase skips this scene outright in the case that variant covered.

    Acquisition is `sq018_01_mama_welles.scene`'s, verbatim: spawn-set entry
    `mama_welles`, reference `#mama_welles`. Her voicetag and lipsync set come
    from our own picks, keyed on the same actor name as before, so the lipmap
    entry that already ships still matches.

    NO BURIED ACTOR AND NO OFFSET. Her lines play from where she is standing,
    two metres from V, which is where vanilla plays them from. The silence in
    August was the (1000, 1000, -100) default, not the use of a real actor.

    THIS VARIANT MUST NEVER BE ENTERED WHEN SHE IS ABSENT. Nothing here spawns
    anybody; if the acquisition finds nothing there is no speaker, and a scene
    holding an actor that never acquired is what crashed the game at teardown in
    August. The quest phase picks between this and the stand-in on
    cc_g01_mama_present, which Gig01_Encounter publishes from the same probe that
    already decides whether to spawn one.
    """
    return _epilogue('gig01_epilogue')


# build_epilogue_standin WAS HERE, and it was deleted on 2026-08-18 along with
# `SpawnMamaWelles` and the `cc_g01_mama_present == 2` scene branch.
#
# It existed because Mama Welles was believed not to be dependably in El Coyote
# Cojo, "time of day and quest state" (playtesting, 2026-08-11). Half of that
# was wrong and the other half is now a start condition:
#
#   TIME OF DAY: no. Every community entry within 80 m of the bar counter uses
#   the `Day` time period, all 151 of them. That is a real finding rather than
#   an artefact of the format, because Night, Morning, Evening and explicit
#   clock times all exist in the same data and 12 of the 785 community areas in
#   `always_loaded_0` use Night. El Coyote uses none of them.
#
#   QUEST STATE: yes, and it is the same quest that owns the door. Mama has no
#   community entry at all; every node carrying her name is sq018 quest design
#   under the bar's own prefab. Gig01_Start now waits for sq018 to succeed
#   before the gig starts, so by the time V reaches the bar she is there.
#   Confirmed in play across times of day, 2026-08-18.
#
# So the fallback covered a case that the start gate has since made unreachable.
# What survives is the PROBE, not the fallback: `cc_g01_mama_present` still says
# 1 or 2, because entering the real epilogue with no Mama to acquire leaves the
# scene holding an unresolved actor, and that crashed the game at teardown in
# August. On 2, the quest phase now skips the epilogue and goes straight to the
# bar. Nobody should ever see it, and if anyone does, an ending without her
# beats a crash.
#
# Full account: docs/backlog.md 19.


def _epilogue(name):
    """El Coyote Cojo - Mama Welles only. The scene ends on V saying he is
    getting a drink; the gig then walks him to the bar, where Johnny is waiting
    for the comic's last two lines. See the note by the exit point."""
    # ANCHOR_MAMA, and it took two goes to get here. playtesting heard her:
    #   1. "silent"                        -> she was at the voice-only default,
    #                                         (1000, 1000, -100). A kilometre out.
    #   2. "very far, like on the right"   -> around_player + (0, 0, -2.5). The
    #                                         tag marker is NOT on the player, so
    #                                         the offset inherited its error.
    #   3. a fixed anchor 3 m from her mark, with the exact offset onto it.
    #
    # "Silent" and "quiet" pointed at completely different subsystems, and only
    # the second report identified the mechanism as distance. Ask which it is.
    #
    # The original note follows, because the part about ANCHOR_COYOTE is still
    # true and still the reason it is not used.
    #
    # ANCHOR_PLAYER, not ANCHOR_COYOTE, WHICH IS THE FIX FOR HER SILENCE.
    #
    # playtest, 2026-08-13: "Mama welles dialogue is silent." Her lines are the
    # only face-to-face ones in the gig that were never moved off the voice-only
    # default, so she was speaking from (1000, 1000, -100) - a kilometre out and
    # a hundred metres down. Exactly the failure that silenced Hoshino, missed
    # because "Mama Welles: 2 lines voiced and deployed" was true and said
    # nothing about whether they could be heard.
    #
    # ANCHOR_COYOTE would not have been enough on its own either: it is the base
    # game's bar marker at the pub ENTRANCE, and Mama stands 15 m from it. Around
    # the player is both simpler and correct wherever in the bar she is found -
    # the encounter script prefers the real Mama Welles and only spawns a
    # stand-in if she is absent, so her exact spot is not ours to predict.
    #
    # The anchor is now only the scene's origin: the real variant acquires her
    # from her spawn set and the stand-in's speaker is off the map entirely, so
    # nothing is measured from it. Kept because a real node in her own streaming
    # sector is the right kind of marker, and changing it buys nothing.
    s = Scene(name, ANCHOR_MAMA)
    # THE ONE IN THE BAR, and taking her is the whole point - see
    # build_epilogue(). There is no longer any other kind: the stand-in variant
    # was deleted on 2026-08-18, so this scene is only ever entered when
    # Gig01_Encounter has found her.
    mama = s.add_spawnset_actor('mama_welles', 'mama_welles', '#mama_welles')
    v = s.add_player()
    # THE REAL MAMA WELLES, so her mouth moves while the buried one speaks.
    #
    # This is the ONE body double in the gig with direct vanilla precedent, and
    # it is not an approximation of it: `mama_welles_default.scene` - the scene
    # that plays when you walk up to her in this bar and talk - acquires her
    # with exactly `spawnSet`, entry name `mama_welles`, reference
    # `#mama_welles`. Her voicetag (1704188817181679616) is read off the same
    # file and is what gen_lipsync keyed our lipmap entry with.
    #
    # NO BODY DOUBLE, and it is not an omission. One was added here for the
    # stand-in variant, whose speaker was somewhere else entirely and needed a
    # mouth in the room. The real Mama IS the speaker and IS the body, so a
    # double pointing at the same spawn set would be a second acquisition of one
    # NPC. The stand-in went on 2026-08-18 and the double went with it.

    start = s.start('epilogue_in')
    # COMIC pp. 59-63, in order. She has exactly two lines; the rest is V, and
    # Johnny answers his last one on the scripted subtitle route.
    #
    # This is the scene playtesting singled out. It previously offered "Long night."
    # OR "She okay?" - but the comic has V say BOTH, in that order, and both
    # branches led to the same reply. A fixed conversation must look fixed.
    #
    # mija/mijo: the subtitle resource carries a female and a male variant and
    # the game picks by V's body type.
    # LET HER VANILLA GREETING LAND FIRST. playtest, 2026-08-15: she still says
    # "Look who it is" - loudly - just before our first line, and the two step on
    # each other. That bark comes from her voiceset, not from the dialogue scene
    # we already blocked, and muting the voiceset has not taken (see
    # Gig01_Encounter.SetVoiceset).
    #
    # So stop fighting it and use it. 2.6 s of lead turns a collision into a
    # exchange: she notices V, then softens. "Look who it is." / "You look
    # tired, mija." is a better opening than either line alone, and it is the
    # only version of this that cannot break - it needs nothing to be suppressed.
    #
    # If the mute ever does start working, this reads as a beat of silence while
    # she looks at him, which is also fine. That asymmetry is why the number is
    # deliberately modest rather than long enough to be sure.
    #
    # POSITIONAL, not `inner_vo`. She is standing two metres from V on her own
    # mark, which is where vanilla plays these lines from. The stand-in's copy
    # of these lines was 2D because its speaker was a kilometre away; that
    # variant is gone, and with it the reason to route hers any other way.
    # MAMA WELLES IS HER OWN VOICE NOW, 2026-09-03. The two lines written for
    # her (m01 "You look tired, mija.", m02 "She's in the back.") are gone;
    # what she says here is four of her own recordings, three whole and one
    # trimmed.
    #
    # THE SCENE NO LONGER OPENS ON HER. Her vanilla bark ("Look who it is!")
    # fires from her voiceset as V walks up and cannot be suppressed
    # (Gig01_Encounter.SetVoiceset, measured); it used to collide with our
    # first line and was bought off with 2.6 s of lead. The design call was to
    # let the bark BE the greeting and start with V's question, so the lead
    # is now only the beat it takes her to look up.
    #
    # What she then says is her Misty report from `scene_mama_welles_default`,
    # read here as Elena: V asked her to take a frightened girl in, and this
    # is her telling him she did. Nothing in the words names anyone, which is
    # what makes them fit - and what keeps the ending's silence intact.
    c1 = s.choice([s.add_option("How's she doin'?", 'oe1')])
    v1 = s.section([s.add_line(v, "How's she doin'?", key='ve1',
                               vanilla_sid=0x1afcd577f85bf000)],
                   lead_ms=1400)
    s2 = s.section([
        s.add_line(mama, "I did like you said. I invited her over for dinner.",
                   key='m04', vanilla_sid=0x1b20084c292d2000),
        # A HEAD-TRIM of "She's a nice girl. We exchanged numbers." - the
        # second sentence is Misty's thread and would land as a non sequitur
        # here. Cut at the pause after "girl." and listened to before use.
        s.add_line(mama, "She's a nice girl.", key='m03'),
    ])
    # "Nova. I'll get a drink." now ENDS this scene, and it is a cue rather than
    # a sign-off: the gig hands V a new objective to walk to the bar.
    #
    # The last two lines of the comic - V's "She'll never know." and Johnny's
    # "Good. Let her sleep." - used to be a third hub and a Johnny section right
    # here. They moved OUT to the bar (playtest, 2026-08-12): V says he is getting
    # a drink, so he should get one, and Johnny should be waiting at the bar
    # rather than having stood silently through the whole conversation with Mama.
    #
    # They were scripted captions there until 2026-08-13, which meant they could
    # never carry audio; they are now their own scene, `gig01_bar` - see
    # build_bar(). Still NO JOHNNY IN THIS SCENE, for the same reason as before.
    # THE ENDING, AND IT IS FIVE WORDS (recast 2026-09-03). V asked her to
    # take in a frightened stranger and she did it; he thanks her, and she
    # answers by putting it on Jackie, which is the only reason Elena had V's
    # number in the first place. The girl in the back never learns who paid
    # for her safety, and nobody has to say so.
    #
    # It was V trailing off with "So, the girl..." and her deflecting with
    # "It's OK, V. You don't need to. I know how things are." The deflection
    # is about V's LINE OF WORK in the scene it comes from, so out of that
    # context it read as vague: *"the last phrase about 'I get it V' is not
    # very understandable"*. Both takes here say what they mean.
    #
    #   V     "Thank you."                    0x1a679e3b082cd000 (q005)
    #   Mama  "Jackie chose his friends well." 0x1b30e0ae074ea004 (sq018)
    c2 = s.choice([s.add_option("Thank you.", 'oe4')])
    v2 = s.section([s.add_line(v, "Thank you.", key='ve4',
                               vanilla_sid=0x1a679e3b082cd000)])
    s3 = s.section([s.add_line(mama, "Jackie chose his friends well.",
                               key='m06',
                               vanilla_sid=0x1b30e0ae074ea004)],
                   tail_ms=1000)
    out = s.end('epilogue_out')

    s.link(start, c1)
    s.link_choice(c1, [v1])
    s.link_section(v1, s2)
    s.link_section(s2, c2)
    s.link_choice(c2, [v2])
    s.link_section(v2, s3)
    s.link_section(s3, out)

    # NO WORKSPOT ON EITHER VARIANT, and the reason is worth writing down
    # because the first cut of this change added one.
    #
    # Johnny needs one because `phantomVisibleStates` is
    # ["RootMotion","Workspot"]: he does not RENDER outside a workspot. That is
    # a property of his apparition, not of scene actors, which is why
    # stage_johnny fires one and nothing else in this file does.
    #
    # Mama Welles is an ordinary NPC and neither variant has the problem:
    #   real     - she is standing on her own community mark, correctly placed
    #              and oriented by the game. A workspot would move her off it.
    #   stand-in - Gig01_Encounter.SpawnMamaWelles ALREADY puts a visible one on
    #              her mark with her captured yaw, because a DynamicEntitySpec
    #              carries position AND orientation directly. It has shipped that
    #              way since 2026-08-11. The scene's buried actor supplies the
    #              voice, exactly as it does for every other speaker here.
    #
    # So the fallback is the gig as it shipped, with a different scene name. No
    # device, no PlaceSceneMama, and no workspot resource path to get wrong -
    # which matters, because a wrong one is silent and looks exactly like the
    # bug you are chasing.
    return s


# ============================================================ scene 4: the bar
def build_bar():
    """The last two lines of the comic (p63), at El Coyote's counter.

    WHY THIS EXISTS: it used to be a pair of SCRIPTED CAPTIONS - text pushed onto
    the screen from Gig01_Encounter.Line(15) and Line(16) through the UIGameData
    blackboard. A caption has no scnlocLocstringId, so there is no RUID, so there
    is nothing for a voiceover map to key on and NOTHING CAN EVER PLAY AUDIO FOR
    IT. That is the whole reason Johnny and V were generated but silent.

    Two routes out were on the table. Adding Audioware playback to the script
    would make Audioware a required download for every player; rebuilding the
    beat as a scene uses the mechanism already proven four times over. playtesting
    picked the scene (2026-08-13), and this beat went first because it is small
    and because it is the emotional close of the gig - if the conversion works
    here it works everywhere.

    WHAT CHANGES OUTSIDE THIS FUNCTION:
      * Gig01_Encounter still sets `cc_g01_bar_reached` on proximity, and still
        carries the "anywhere in the bar after ~45 s" fallback. THE ENDING MUST
        ALWAYS BE REACHABLE - that trigger has already stranded the gig once and
        is deliberately untouched.
      * It no longer spawns Johnny or drives the lines. The quest phase waits on
        that fact, plays this scene, and sets `cc_g01_bar_done` afterwards.

    JOHNNY IS THE SCENE'S OWN ACTOR HERE, not the script-spawned one, because a
    world line plays from the SPEAKER'S position and every voice-only actor in
    this file is parked a kilometre away. A speaker who has to be heard face to
    face has to actually be there.

    He takes JOHNNY_SOLID, the deliberate safe bet rather than the
    interesting one: `silverhand_riot__not_blendable` has no blendable meshes, so
    it renders whether or not the phantom system is driving it, while
    silverhand_default renders nothing unless a phantomVisibleState is satisfied.
    The last beat of the gig does not get to be the experiment. (The workspot is
    still fired - it buys the arrival dissolve for free and a standing idle
    instead of a default pose).

    KNOWN OPEN POINT, and it is the one thing to watch in game: a scene's
    spawnDespawn actor is removed the moment the scene exits, so Johnny may POP
    rather than glitch out the way the script route does (StartEffectEvent
    n"johnny_teleport_start", then delete 0.25 s later - calibrated in playtest
    and confirmed good). The 1.2 s tail below gives the line air but does not fix
    the vanish itself.
    """
    s = Scene('gig01_bar', ANCHOR_BAR)
    # Offset (0,0,0): the anchor IS the spot. It sits 1.65 m from the stools V
    # walks to, at floor level, with an identity orientation - see ANCHOR_BAR.
    # validateSpawnPostion stays on (add_johnny's default, and vanilla's): he is
    # being placed in real geometry, which is the case validation is for.
    # 45 degrees anticlockwise so he faces Mama Welles rather than straight
    # out from the counter. Yaw is counter-clockwise seen from above.
    johnny = s.add_johnny(appearance=JOHNNY_SOLID, yaw=45.0)
    v = s.add_player()

    start = s.start('bar_in')
    # THE COMIC'S LINE IS "She'll never know." AND IT IS REPLACED HERE - the
    # third and last of the sanctioned exceptions, 2026-08-13: *"the final
    # dialogue with Johnny is strong in the comic but weak in the game... I just
    # want a replacement that makes more sense and recaps."*
    #
    # He is diagnosing the same thing as the shard rewrite. On the last page of
    # a comic, "she" and "never know" are both still in the reader's hand. Sixty
    # pages of gig later, a player has met Elena once, on the phone, at the very
    # start - so the pronoun has to be paid for. This line names the crime in
    # HER terms (she is the one who noticed accounts zeroing out) and closes on
    # "ledger", which is the gig's own through-line word and its title.
    #
    # JOHNNY'S ANSWER IS UNTOUCHED. "Good. Let her sleep." is the comic's, it is
    # the one take of his has been approved, and it still answers this line
    # exactly as it answered the shorter one.
    # SPLICED-VOICES RECAST (2026-09-02): V's close is his own recorded
    # reflection; the meaning shifts from her never knowing to what the road
    # here cost, which review accepted as the nearest true take. Generated
    # v02/j01 takes retired unreferenced.
    # FIVE WHOLE TAKES, 2026-09-03, and the shape is the design call: tired V,
    # bleak Johnny, V closing the book, Johnny's grudging credit, the drink.
    # Nothing is cut and nothing is generated.
    #
    #   V       "Did what we had to."                  0x197a52ce594e1000 q113
    #   Johnny  "Was in Mexico when I realized that no matter the conflict,
    #            corps always win. Ordinary people always lose."
    #                                                  0x1a72d27020386000 sq032
    #   V       "What matters is it's over now."       0x146294a9ca29e000 sq029
    #   Johnny  "Hm. Not half bad, that."              0x1b208825d42c5004 q110
    #   V       "Need a drink."                        0x19e24048145c5004 kabuki
    #
    # Johnny's first line is kept WHOLE rather than trimmed to "corps always
    # win": him remembering Mexico is in character, and a whole take cannot
    # crackle at a seam. His second is the nearest thing in his recordings to
    # telling V he did well, which is what the beat asks for.
    s1 = s.section([s.add_line(
        v, "Did what we had to.",
        key='v03', vanilla_sid=0x197a52ce594e1000)])
    # innerDialog + Vo_Expression_InnerDialog: the relic register, and what 20 of
    # 25 shipped Johnny scenes use. It also SHOWS HIS NAME - only
    # AlwaysCinematicNoSpeaker hides the name widget (subtitlesControllers.swift
    # :169) - so this is the presentation the scripted route was reaching for.
    #
    # The tail is why this section is the last one: the quest phase continues on
    # the frame the scene exits, and "Good. Let her sleep." is the last line of
    # the comic. It should land in silence, not under a completion banner. The
    # phase adds a further delay on top; both are cheap and neither gates
    # anything (never gate quest completion on presentation).
    s2 = s.section([s.add_line(johnny, "Was in Mexico when I realized that no "
                               "matter the conflict, corps always win. "
                               "Ordinary people always lose.", key='j02',
                               vanilla_sid=0x1a72d27020386000)],
                   inner=True)
    s3 = s.section([s.add_line(v, "What matters is it's over now.", key='v04',
                               vanilla_sid=0x146294a9ca29e000)])
    s4 = s.section([s.add_line(johnny, "Hm. Not half bad, that.", key='j03',
                               vanilla_sid=0x1b208825d42c5004)], inner=True)
    s5 = s.section([s.add_line(v, "Need a drink.", key='v05',
                               vanilla_sid=0x19e24048145c5004)],
                   tail_ms=1200)
    out = s.end('bar_out')

    s.link(start, s1)
    for _a, _b in ((s1, s2), (s2, s3), (s3, s4), (s4, s5), (s5, out)):
        s.link_section(_a, _b)

    # Fire at t=0 of the FIRST section, not of Johnny's own: he is meant to be
    # standing at the bar when V walks up, and materialising for his own line is
    # worse than not being there. Must come after link_section on s1 - sockets
    # are ordered and validate() enforces it.
    #
    # THE BAR KEEPS ITS SCENE ACTOR AND ITS WORKSPOT, unlike the five converted
    # beats. It is the one place where a fixed marker sites him correctly (1.65 m
    # from the stools, identity orientation), and it has been playtested and
    # approved it. Do not "make it consistent" with the others.
    s.fire_workspot(s1, s.add_workspot_node(JOHNNY_ACTOR), start_time=0)
    return s



# Every scene in the gig, in story order. ONE list, because gen_voice reads it
# too - a scene that was in the generator but not in gen_voice's copy of this
# list was silently unvoiceable, and the failure was a KeyError three tools
# downstream rather than anything that named the real problem.
#
# The two holocall BENCHES that lived at the end of this list are gone, removed
# for the 1.2.6 release. They proved the video holocall and then had nothing
# left to prove; docs/backlog.md 3d is the account and keeps everything they
# measured.
def build_nix_brief_holo():
    return build_nix_brief(holo=True)


ALL_BUILDERS = (build_elena, build_arasaka, build_terminal,
                build_nix_brief, build_hoshino, build_kill,
                build_malware, build_epilogue,
                build_bar,
                # The video twin of Nix's call. Same words, same keys, same
                # order; the actor is borrowed from the holocall studio
                # instead of spawned. See nix_actor().
                build_nix_brief_holo)



if __name__ == '__main__':
    built = [build() for build in ALL_BUILDERS]
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
