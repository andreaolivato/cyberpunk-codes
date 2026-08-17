r"""Generates the gig's .scene resources - real scene-system conversations.

FIFTEEN scenes, all built by the same builder. ALL_BUILDERS at the bottom is
the list; gen_voice reads it too, so it is the one place scenes are enumerated.

  gig01_elena_call  Elena's opening holocall (was an SMS thread)
  gig01_arasaka     Johnny: "Fucking Arasaka..." (comic p11)
  gig01_terminal    the office desk, V + Johnny (p22)
  gig01_shard_find  V finds the shard in the desk (p23)
  gig01_shard_read  V, after the shard reader closes (p24)
  (gig01_netrunner was merged back into gig01_terminal on 2026-08-14)
  gig01_nix_brief   V hires Nix (pp. 26-27)
  gig01_legend      the crosswalk (p28)
  gig01_nix_call    Nix names Hoshino (pp. 29-30)
  gig01_hoshino     the North Oak estate
  gig01_kill        over Hoshino's body (p45)
  gig01_malware     the estate terminal (p51)
  gig01_epilogue    Mama Welles in El Coyote Cojo
  gig01_bar         the last two lines of the comic (p63)

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

# The builder itself lives in tools/questkit/scene.py. This file is the GIG: its
# paths, its anchors and its dialogue. Everything imported here is engine shape
# that a second gig reuses rather than forks.
#
# Several names are imported only to be re-exported. gen_voice, gen_lipsync and
# gen_shard_ent reaches for them as gen_scenes.<name>, and keeping them
# resolvable here means the split costs those tools no changes at all.
from questkit.scene import (                                        # noqa: F401
    Scene, configure, write_subtitles, write_lipmap,
    ANCHOR_PLAYER, JOHNNY_ACTOR, JOHNNY_GHOST, JOHNNY_SOLID,
    WORKSPOT_JOHNNY, WORKSPOT_ENTRY,
    estimate_ms, line_ms, locstring_ruid, resref, cname, fnv1a64,
    yaw_to_face_player,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                       'raw', 'mod', 'negative_balance', 'scenes')
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
SUBTITLE_MAP_OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                                'raw', 'mod', 'negative_balance', 'localization',
                                'subtitles.json.json')
SUBTITLE_OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                            'raw', 'mod', 'negative_balance', 'localization',
                            'gig01_lines.json.json')
# Depot path of the entries file, as the map has to name it.
SUBTITLE_DEPOT = 'mod\\negative_balance\\localization\\gig01_lines.json'

# Where the scenes live once packed. gen_questphase.SCENES is the same string
# and has to stay so; the lipmap is keyed by FNV1a64 of exactly this path plus
# the scene name, so a mismatch here is a lipmap nobody ever looks up.
SCENE_DEPOT = 'mod\\negative_balance\\scenes\\'
# The animLipsyncMapping ArchiveXL merges into base\localization\en-us.lipmap.
LIPMAP_OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                          'raw', 'mod', 'negative_balance', 'localization',
                          'gig01.lipmap.json')

# Scene markers. These are the same base-game NodeRefs the map pins anchor to,
# and they are known to resolve (the pins work in-game). A scene location is
# only a placement origin - the player does not have to be anywhere near it,
# which is what makes it usable for a holocall.
ANCHOR_OFFICE = '#std_arr_parking_spwn_179'
ANCHOR_ESTATE = '#q113_dvc_arasaka_estate_camera_010'
ANCHOR_COYOTE = '#loc_sq022_el_coyote_cojo_bar_marker'
# The bar beat needs its OWN anchor, and not the one above.
#
# ANCHOR_COYOTE is at (-1260.280, -983.960, 12.040) - the base game's bar marker,
# which sits at the pub's ENTRANCE, 10.4 m from the stools V walks to. That is
# fine for a holocall (a scene marker is only a placement origin) and fine for
# the epilogue, whose only actor is a kilometre away by design. It is wrong the
# moment an actor has to stand next to the player: a 10 m offset would put
# Johnny in the doorway.
#
# `#hey_rey_food_01_mp` is (-1256.635, -998.972, 12.158) - 1.65 m from
# CCGig01Places.BarStools(), at floor level, in the same streaming sector, with
# an IDENTITY orientation (so a spawn offset is not silently rotated). Found with
# find_pin_anchors.py on the stool coordinates; it was the nearest globally-named
# node of 63 candidates within 25 m.
ANCHOR_BAR = '#hey_rey_food_01_mp'

# ...AND ITS LIMIT, learned 2026-08-13 from Mama Welles.
#
# `around_player` does NOT put the marker on the player. playtesting, hearing her from
# a buried actor at offset (0, 0, -2.5) from an around_player marker: "still
# feels very far, like on the right of where I am." Far and directional - so the
# marker lands a few metres off to one side, and an offset measured from it
# inherits that error.
#
# Johnny is unaffected from an identical setup, and the difference is the only
# thing that differs between them: HIS LINES ARE `inner=True`
# (Vo_Expression_InnerDialog) and evidently play 2D, in V's head. Hers are
# Vo_Expression_Spoken and are positional. So:
#
#   inner dialog   position does not matter. around_player is fine.
#   spoken         position is everything. Use a real anchor near the speaker.
#
# Mama's own spot is known - captured off the live NPC, and it is also where the
# stand-in spawns if the base-game one is absent - so she gets a fixed anchor and
# an exact offset onto it.
#
# `#sq018_pepevodka` is (-1260.510, -1001.310, 13.141), 3.0 m from her mark, and
# crucially its orientation is IDENTITY - so the offset below is not silently
# rotated. Two nearer candidates (`#sq018_03d_infinite_drink` at 2.9 m,
# `#q000_kid_01b_vodka_shot` at 3.9 m) were rejected for having real rotations.
ANCHOR_MAMA = '#sq018_pepevodka'
# (her mark) - (the anchor), then 2.5 m down: under the floor at her feet.
OFFSET_MAMA = (-1.668, 2.505, -3.584)

# ...but a voiced line must be paced by its clip, not by a guess about it, or it
# cuts off or drags. tools/gen_voice.py measures every WAV it processes and
# writes this sidecar; anything in it wins over the estimate. Missing file, or a
# line absent from it, simply falls back - so the two halves of the gig (voiced
# scenes, unvoiced ones) coexist without a flag.
DURATIONS_FILE = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source',
                              'audio', 'durations.json')
try:
    with open(DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED = json.load(_fh)
except (OSError, ValueError):
    MEASURED = {}

# ------------------------------------------------------------------- LIPSYNC
#
# tools/gen_lipsync.py casts a vanilla lipsync animation of about the right
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
LIPSYNC_PICKS = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source',
                             'lipsync_picks.json')
try:
    with open(LIPSYNC_PICKS, encoding='utf-8') as _fh:
        _picks = json.load(_fh)
    LIPSYNC_SETS = _picks.get('sets', {})
    LIPSYNC_LINES = _picks.get('lines', {})
except (OSError, ValueError):
    LIPSYNC_SETS, LIPSYNC_LINES = {}, {}

# Scenes that reuse another scene's recordings. `gig01_epilogue_standin` is the
# same four lines as `gig01_epilogue` - the variant played when Mama Welles is
# not in the bar - so it must NOT be voiced separately: gen_voice points its
# RUIDs at the clips that already exist, and gen_lipsync copies its picks.
#
# Regenerating them was never an option. The voiceover map keys stringId -> wem
# path, so two RUIDs may share one file; and a re-run of the TTS is a re-roll of
# the voice itself (BUILDING.md), which would leave one Mama Welles
# sounding like a different woman depending on whether she happened to be in the
# bar that night.
SCENE_ALIASES = {'gig01_epilogue_standin': 'gig01_epilogue'}

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
    without cutting his dialogue, which is not on the table - the comic is the
    source and it is verbatim.

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
    # COMIC pp. 3-11, in order. Nothing is cut and nothing is reworded.
    s1 = s.section([
        E("V? Sorry. I didn't know if you'd answer. My name's Elena Ortega.", 'e01'),
    ], holocall=True)
    # The comic's "Wrong hour for a friendly call." is V thinking out loud as the
    # phone rings, NOT an answer to a stranger introducing herself - offering it
    # as a reply read wrong (playtest, 2026-08-12). It belongs to the ring, which
    # the scene does not cover, so it is gone rather than forced.
    s2 = s.section([
        E("I'm from Heywood. Jackie Welles used to help my family.", 'e02'),
    ], holocall=True)
    # She has had two turns; now he answers. V's lines are NOT holocall - he is
    # the one holding the phone, not the voice coming out of it, so his audio
    # plays from his own position and his expression is Vo_Expression_Spoken.
    v2 = s.section([V("Ortega... yeah. Mama Welles mentioned you.", 'v02')])
    s3 = s.section([
        E("I didn't know who else to call. Jackie said you don't turn your back "
          "on people.", 'e03'),
    ], holocall=True)
    # HUB 1 of 2. He is deciding to take this seriously.
    c3 = s.choice([s.add_option("Start from the top.", 'o03')])
    v3 = s.section([V("Alright. Start from the top.", 'v03')])
    s4 = s.section([
        E("I work with community accounts. People's debts are just zeroing out. "
          "No disputes. No appeals.", 'e04'),
        E("When a debtor dies, their account should freeze. Instead, it clears. "
          "Immediately. I thought it was a glitch. It's not. Too many times.", 'e05'),
        E("I wasn't authorized to see this. I only noticed because I handle "
          "reconciliations. My access was revoked afterward.", 'e06'),
    ], holocall=True)
    v4 = s.section([V("Hold on. Are you safe right now?", 'v04')])
    s5 = s.section([E("I... don't know.", 'e07')], holocall=True)
    # HUB 2 of 2. Her answer is the hinge of the scene and this is where he stops
    # listening and starts running it.
    # THE BUTTON IS A PARAPHRASE, NOT THE LINE. See _beat's note and the survey
    # in scene-playbook.md: this used to be the whole 103-character line, and
    # playtest, 2026-08-13: "the choice on which I need to press F is very long
    # because it contains the whole string that is then said by V".
    c5 = s.choice([s.add_option("Go to Mama Welles.", 'o05')])
    v5 = s.section([V(
        "Okay. Listen to me. Go to El Coyote. Stay with Mama Welles. "
        "I'll check what I can. Where do you work?", 'v05')])
    s6 = s.section([E("Sending you the location.", 'e08')], holocall=True)
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
    s.link_section(s5, c5)
    s.link_choice(c5, [v5])
    s.link_section(v5, s6)
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
def build_nix():
    """Nix decrypts the ledger and names Hoshino. Was an SMS thread.

    Character.Nix is REAL - captured off the live NPC in Afterlife with the dev
    menu's [CAPTURE THE NPC I'M LOOKING AT] (hash 0x44F307AA, length 13). Do not
    "tidy" the capitalisation: TweakDBIDs are case-sensitive and a wrong one
    fails silently.

    FULLY AUTOMATIC - no hubs at all (playtest, 2026-08-13). This is a briefing:
    the player is receiving information, not steering anything, and 27 of 188
    vanilla scenes have no hub whatsoever, so "both ends just play" is a normal
    pattern rather than a shortcut.

    Nothing is cut. V's two lines were hub options and are now spoken lines.

    THEY WERE BRIEFLY VANILLA REUSE, AND THAT WAS WRONG TWICE OVER. backlog.md
    2c had "Where." and "On my way." listed as verbatim vanilla V takes, so they
    shipped pointed at vanilla stringIds - real performance, gender-correct,
    nothing generated. Playtest, 2026-08-13: "Where and On my way sound too
    excited. Need to be much more calm/bland."

    He was hearing a real defect, not a preference. `0x1a29d24a3944d000`
    (v_mq035) is not "Where." at all - **its text is "Where?!"** - and with
    `vanilla_sid` the TEXT comes from vanilla too, so the subtitle was showing an
    exclamation the comic never wrote. Searching all 13,289 of V's recorded lines
    finds no "Where." anywhere; the nearest is "Where?", which still breaks the
    comic-verbatim rule.

    So both are generated now, in the voice and settings approved in playtest. That
    also keeps the scene consistent: every other V line in the gig is generated,
    and one real-actor take among them would stand out more than it gained.

    KEEP THE LESSON: when reusing a vanilla line, verify the CORPUS TEXT, not the
    key it was filed under. `vo_corpus.py search` prints it, and an audition
    would have caught this in one listen.
    """
    s = Scene('gig01_nix_call', ANCHOR_OFFICE)
    nix = s.add_actor('nix', 'Character.Nix')
    # JOHNNY, ADDED 2026-08-13 for his two restored p30 lines. He is voice only
    # here, which is deliberate: his lines are inner=True, and inner dialog
    # plays 2D, confirmed in game - so this actor never needs to be
    # anywhere in particular, and the scene's ANCHOR_OFFICE, which is a fixed
    # node in Arroyo while the call can be answered anywhere in Night City, does
    # not matter for him. Buried 2.5 m like every other Johnny actor in the gig
    # so there is no chance of a second one being visible.
    v = s.add_player()

    def N(text, key):
        return s.add_line(nix, text, key=key)

    start = s.start('nix_call_in')
    # COMIC pp. 29-30, in order.
    # NIX'S LINES WERE OUT OF SCOPE UNTIL THE SCOPE WAS WIDENED, 2026-08-13:
    # *"'V. You were right. Hoshino's the choke point' is wrong. We never
    # mentioned it, so what is V right about?"*: and he wrote the replacement.
    #
    # This is the SECOND time the comic-verbatim rule has been bent and the
    # first time it has been bent on a character who is not V. Both were his
    # call and both are recorded; see backlog.md 5c for the running list. The
    # rule still holds everywhere it has not been explicitly lifted.
    #
    # What changed and why it is right: "You were right" now answers something
    # the player heard. V's claim is on the brief call ("Someone's signing off
    # on every one of these") and again at the shard ("They're paying mercs"),
    # so Nix's first act is to confirm the SCHEME - which is what V asserted -
    # and only then produce the name, which is the payoff nobody spoiled.
    # "Hoshino's the choke point." is retired: it named him before the sentence
    # that introduces him, and it says the same thing as n03 immediately after.
    s1 = s.section([
        N("V. You were right.", 'n01'),
        N("Arasaka pays mercs to flatline debtors after insuring them.", 'n05'),
        N("One exec signs off on all of it. Hoshino.", 'n06'),
        N("Nothing pays without his sign-off. Ever.", 'n03'),
    ], holocall=True)
    c1 = s.section([s.add_line(v, "Where.", key='on1')])
    s2 = s.section([
        N("North Oak. Private Arasaka residence.", 'n04'),
    ], holocall=True)
    # p30's OTHER two lines, restored 2026-08-13. The gig cut from the address
    # straight to the objective, which landed flat - and "On my way." had been
    # invented into the exact gap where these two were missing. the design kept the
    # invented line (an explicit design call, do not "fix" it later for not being
    # in the comic) and asked for these back, so the beat now runs address ->
    # Johnny -> V, which is the comic's own order.
    # JOHNNY'S p30 PAIR HAS MOVED OUT, to build_graves() below, and "On my
    # way." is GONE. playtest, 2026-08-14, giving the flow the design wants:
    #
    #     nix says the address -> call closes -> Johnny appears -> his lines
    #     -> he disappears -> next objective
    #
    # It cannot be done from inside this scene. The call's chrome does not hang
    # up until the SCENE EXITS - the quest phase sets cc_g01_nixcall_end on the
    # exit socket - so anything still in here happens while the phone is up. He
    # was also never appearing at all, which is the same one-window-per-staging
    # bug the shard beat had: the crosswalk scene consumed this window's staging
    # and nothing re-armed for the call.
    # THE CALL ENDS HERE. There used to be one more Nix line - "So do it from
    # inside his network, killing him just makes them promote someone" - and it
    # was INVENTED. The design asked whether it was in the comic; it is not.
    #
    # Nix has exactly six lines in all 63 pages and they are all now used:
    #   "How's things, V?" / "That's exec-tier heat, V." /
    #   "I can dig, but who's paying?" / "Heh. That'll take a minute." +
    #   "I'll call you back."                                    (pp. 26-27)
    #   "V. You were right." + "Hoshino's the choke point." +
    #   "Nothing pays without his sign-off." + "Ever." /
    #   "North Oak. Private Arasaka residence."                  (pp. 29-30)
    #
    # It was there to motivate the malware objective, and that turned out not to
    # need motivating: the comic has V do it anyway (pp. 49-51), and p51's
    # "No more payouts." is already the last line of UploadStep. The objective
    # text carries the rest.
    out = s.end('nix_call_out')

    s.link(start, s1)
    s.link_section(s1, c1)
    s.link_section(c1, s2)
    s.link_section(s2, out)
    return s


# =================================================== scene 2a: the Nix brief
def build_graves():
    """Comic p30, Johnny in the street AFTER Nix hangs up.

    Split out of gig01_nix_call on 2026-08-14. the design wanted the beat to read
    as: Nix gives the address, the call closes, Johnny appears, says his piece,
    goes. The first three of those cannot happen inside the call scene at all -
    the phone does not hang up until that scene EXITS, because the quest phase
    sets cc_g01_nixcall_end on its exit socket. So the lines had to come out
    into their own beat, entered on cc_g01_nixcall_done.

    Same take, no regeneration: the clips were COPIED to the new keys and
    md5-verified, exactly as p25's and V's "Wait. That's-" were.

    "On my way." went with the split rather than moving - it was cut. It was
    a reused vanilla line (add_line's vanilla_sid), so nothing is orphaned by
    dropping it: no subtitle entry and no .wem were ever ours.
    """
    s, johnny, _v = _beat('gig01_graves', visible_johnny=True)
    start = s.start('graves_in')
    s1 = s.section([
        s.add_line(johnny, "Of course it is.", key='j30a'),
        s.add_line(johnny, "Arasaka owns the hill and the graves.", key='j30b'),
    # lead_ms 2200, up from 1200. Playtest: he starts the line while still
    # materialising. Delaying the first line is the smallest fix there is
    # and touches only this beat.
    ], inner=True, tail_ms=2000, lead_ms=2200)
    out = s.end('graves_out')
    s.link(start, s1)
    s.link_section(s1, out)
    s.stage_johnny(s1, s1)
    return s


def build_nix_brief():
    """V hands Nix the ledger and hires him. Comic pp. 26-27, verbatim.

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
    s = Scene('gig01_nix_brief', ANCHOR_OFFICE)
    nix = s.add_actor('nix', 'Character.Nix')
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
    v1 = s.section([
        V("Bad. Arasaka's running a kill ledger.", 'vb1'),
        # NOT the comic's wording. p26 reads "Cracked the logs. Got names." and
        # this is a second, narrower break in the verbatim rule - Playtest,
        # 2026-08-14. It matches what the player actually did: they read the
        # ledger on the office terminal and sent that ledger to Nix, which is
        # also what his conversation title ("That ledger you sent me.") and vb5
        # already say. The "names" claim was the one thing in V's side of this
        # call that the gig never showed him getting.
        V("Cracked the logs. Downloaded the ledger.", 'vb2'),
        V("Someone's signing off on every one of these.", 'vb5'),
        # playtest, 2026-08-14: *"remove 'and how we make it stop'"*. The second
        # half was doing no work - the line before it already states the
        # hypothesis, and "find me the name" is the whole ask Nix answers.
        # NEW TAKE REQUIRED: the clip still says both halves, so vb6's audio is
        # regenerated and auditioned before this ships.
        V("Find me the name.", 'vb6'),
    ])
    s2 = s.section([
        N("That's exec-tier heat, V.", 'b02'),
        N("I can dig, but who's paying?", 'b03'),
    ], holocall=True)
    v2 = s.section([V("I am.", 'vb4')])
    s3 = s.section([
        N("Heh. That'll take a minute.", 'b04'),
        N("I'll call you back.", 'b05'),
    ], holocall=True)
    out = s.end('nix_brief_out')

    s.link(start, s1)
    s.link_section(s1, v1)
    s.link_section(v1, s2)
    s.link_section(s2, v2)
    s.link_section(v2, s3)
    s.link_section(s3, out)
    return s


# ========================================================= scene 3: Hoshino
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
    hoshino = s.add_actor('hoshino', 'Character.cc_g01_hoshino')

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
    # The Hoshino the player is looking at is the one Gig01_Encounter spawned at
    # CCGig01Places.Hoshino() with tag `cc_g01_hoshino` - he has to exist long
    # before this scene, because V has to find him and then shoot him. This
    # double is the only way his mouth can move; see add_body_double.
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
    # Both lines therefore use `inner_vo`: the field that does the work, and
    # none of the relic register that belongs to Johnny.
    s1 = s.section([s.add_line(hoshino, "Mmm? You lost, merc?", key='h01')],
                   inner_vo=True)
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
    # would be silent - this line is why Hoshino was moved to ElevenLabs.
    s2 = s.section([s.add_line(hoshino, "Do you know who I am?", key='h02')],
                   inner_vo=True)
    c1 = s.choice([s.add_option("Name what he signed.", 'oh1')])
    # ...and then V SAYS it. playtest, 2026-08-13: "V reply to hoshino is silent".
    # It was a hub option and nothing else - the player pressed a line nobody
    # spoke. Same fix as Elena's two kept hubs: press it, then hear it.
    v1 = s.section([s.add_line(v, "I know what you signed. I know who paid "
                               "for it.", key='vh1')])
    out = s.end('hoshino_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, c1)
    s.link_choice(c1, [v1])
    s.link_section(v1, out)
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
    vsec = s.section([s.add_line(v, "Got it. Wait. That's-", key='v06')],
                     lead_ms=1200)
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
    s1 = s.section([s.add_line(johnny, "Fucking Arasaka...", key='ja1')],
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

    def V(text, key):
        return s.add_line(v, text, key=key)

    def J(text, key):
        return s.add_line(johnny, text, key=key)

    start = s.start('terminal_in')
    s1 = s.section([V("That's not debt collection.", 't01')])
    s2 = s.section([J("It's a production line.", 't02')], inner=True)
    s3 = s.section([V("Insure them. Flatline them. Get the eddies.", 't03')])
    s4 = s.section([J("Welcome to corporate efficiency.", 't04')], inner=True)
    # p22 ends here; p25 is the pair working out what to do with it, which is
    # what makes the sequence close properly - names with no addresses is why a
    # netrunner is needed, so the decision comes out of the evidence.
    s5 = s.section([V("Yeah. With a body count.", 't05')], tail_ms=800)
    # COMIC p25, BACK WHERE IT STARTED. This was split into its own
    # `gig01_netrunner` scene on 2026-08-13 so it could sit AFTER the shard -
    # and the same day the design reverted the ORDER ("put it back in the previous
    # order, so the netrunner one runs BEFORE the shard") without the split
    # being undone with it. It has been two scenes with nothing between them
    # ever since: no fact gate, no player action, the quest phase stepping
    # straight from one to the next.
    #
    # That cost nothing while the SCRIPT owned Johnny's body and it persisted
    # across both. Now the scene owns him, so the seam is a glitch-out and
    # glitch-in in the middle of one continuous conversation - playtest, 2026-08-14:
    # *"Why did you need to split the scene with johnny between 'corporate
    # efficiency' and 'we need to find a netrunner'? There's no choice or action
    # in the middle."* There was not. Merged back.
    #
    # THE REAL BREAK IS THE SHARD, and it still is: this scene ends, V finds and
    # reads the shard, and Johnny REAPPEARS for "Figures." as gig01_shard_read.
    # That is a genuine gap with player action in it and it stays a separate
    # scene.
    s6 = s.section([V("We need a netrunner to find who's responsible.", 't10')])
    s7 = s.section([J("We know one.", 't09')], inner=True, tail_ms=800)
    out = s.end('terminal_out')

    s.link(start, s1)
    for a, b in ((s1, s2), (s2, s3), (s3, s4), (s4, s5), (s5, s6), (s6, s7),
                 (s7, out)):
        s.link_section(a, b)
    s.stage_johnny(s1, s7)
    return s


def build_shard_find():
    """Comic p23, the office desk. One line, and it is the cue for the shard
    reader: Gig01_Shard opens the overlay when this scene exits.

    V ONLY - Johnny has no line on p23 and does not get an invented one. `_beat`
    is still the right constructor: it buries a Johnny actor nobody hears, and
    keeping the five office beats on one constructor is worth more than saving
    one unused actor definition.
    """
    # NO JOHNNY ACTOR IN THIS SCENE, WHICH IS THE FIX FOR HIS BLINK.
    #
    # It used to use `_beat`, which stages a Johnny actor whether the scene has
    # a line for him or not - and p23 is V alone, so this one never did. The
    # trace showed what that cost (2026-08-13): `cc_g01_dbg_johnny_ws` drops
    # from 4 to 2 the moment cc_g01_shard_found fires, i.e. the instant this
    # scene starts, and only returns to 4 on the next encounter tick. The
    # scene's own spawnDespawn Johnny takes the script's apparition over, pulls
    # him out of his workspot, and he stops rendering until the tick puts him
    # back - Playtest: "he disappears while I read the shard, then reappears."
    #
    # A scene that has nothing for him to say has no business staging him.
    # gig01_shard_read still does, because "Figures." is his.
    s = Scene('gig01_shard_find', ANCHOR_PLAYER)
    v = s.add_player()
    start = s.start('shard_find_in')
    s1 = s.section([s.add_line(v, "A data shard... might contain more info",
                               key='sf1')], tail_ms=400)
    out = s.end('shard_find_out')
    s.link(start, s1)
    s.link_section(s1, out)
    return s


def build_shard_read():
    """Comic p24, after the reader closes. The two lines that give the ledger
    its meaning - and, since 2026-08-13, the setup for the Nix call: V now says
    on the call that someone signs off on all of it, and this is where he learns
    what "all of it" is FOR.

    One section, both lines: they are one thought, and the comic prints them as
    two balloons of the same breath.
    """
    s, johnny, v = _beat('gig01_shard_read', visible_johnny=True)
    start = s.start('shard_read_in')
    # THE FIRST LINE IS NOT COMIC-VERBATIM, WHICH IS THE DESIGN SECOND
    # SANCTIONED EXCEPTION (2026-08-13, after playing the beat): *"the phrases
    # after the shard should be more explicit... 'They are employing mercs. We
    # do the killing.' Something like this that feels canon and explains later
    # parts."*
    #
    # p24's "So that's where we fit." is a line the READER completes, because
    # the reader has just read the note in full on the facing page. A player who
    # skimmed the same note in a popup has not, so "where we fit" refers to
    # nothing they are holding on to. The replacement says the thing out loud
    # and sets up two later beats: the mercs are why V and Johnny are implicated
    # at all, and it is the claim Nix confirms on the callback.
    #
    # "We do the killing." is UNTOUCHED and still verbatim - it is the half that
    # lands, and its clip is unchanged.
    s1 = s.section([
        s.add_line(v, "They're not sending their own. They're paying mercs.",
                   key='sr3'),
        s.add_line(v, "We do the killing.", key='sr2'),
    ])
    # JOHNNY GETS THE LAST WORD ON THE SHARD, added 2026-08-13 on the
    # instruction. He has stood through the whole beat without a line, which was
    # deliberate - pp. 23-24 are V alone - but it left him standing there with
    # nothing to do and then vanishing. One word closes the beat and gives his
    # exit a reason.
    #
    # "Figures." is Johnny to the bone: he is never surprised by Arasaka, and
    # every other line of his in this gig is the same shrug at a longer length
    # ("It's a production line.", "That's Arasaka.", "Of course it is.").
    # 2000 ms, not the usual 800. "Figures." is 0.7 s - the shortest line in the
    # gig - and playtesting saw Johnny vanish just before it. A scene's spawnDespawn
    # actors are removed the moment it exits and the quest phase continues on the
    # same frame, so on a line this short the tail is most of what is holding him
    # there at all. There is a matching add_delay in the quest phase.
    s2 = s.section([s.add_line(johnny, "Figures.", key='j24')],
                   inner=True, tail_ms=2000)
    out = s.end('shard_read_out')
    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    s.stage_johnny(s1, s2)
    return s


def build_legend():
    """Comic p28, on the crosswalk while Nix digs. V asks the question the gig
    is built around and Johnny answers it.

    "A legend picks who pays" is the closest this gig gets to Johnny saying what
    he believes, so it gets the last section to itself.
    """
    s, johnny, v = _beat('gig01_legend', visible_johnny=True)
    start = s.start('legend_in')
    # "a merc", not "you", 2026-08-13. the change, and it is the same
    # thread as the shard rewrite: the note V has just read says Arasaka hires
    # INDEPENDENT MERCENARY OPERATORS, Nix confirms it on the callback, and this
    # is the moment V works out that the word means him. "How do you become a
    # legend" is a question about fame; "how does a merc become a legend" is a
    # question about what he is being paid to do, which is the one the gig is
    # actually about.
    s1 = s.section([
        s.add_line(v, "Is this how a merc becomes a legend in Night City?", key='l05'),
        s.add_line(v, "Killing to pad Arasaka's books?", key='l02'),
    ])
    s2 = s.section([s.add_line(johnny, "No.", key='l03')], inner=True)
    s3 = s.section([s.add_line(johnny, "A legend picks who pays", key='l04')],
                   inner=True, tail_ms=800)
    out = s.end('legend_out')
    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, out)
    s.stage_johnny(s1, s3)
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
    s1 = s.section([s.add_line(v, "Ledger's closed.", key='k01')])
    s2 = s.section([s.add_line(johnny, "They always think names beat bullets.",
                               key='k02')], inner=True, tail_ms=800)
    out = s.end('kill_out')
    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    s.stage_johnny(s1, s2)
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
    s1 = s.section([s.add_line(v, "No more payouts.", key='w01')])
    s2 = s.section([s.add_line(johnny, "No money, no bodies.", key='w02')],
                   inner=True, tail_ms=800)
    out = s.end('malware_out')
    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    s.stage_johnny(s1, s2)
    return s


# ======================================================== scene 3: epilogue
def build_epilogue():
    """SHE IS IN THE BAR: the real Mama Welles speaks, which is the fix.

    Taking her as the scene's actor is what stops her ordinary bar conversation
    - a quest scene owns the actor it acquires. The old design never claimed her
    at all (see build_epilogue_standin), which is why her chit-chat could win the
    approach and the player had to walk away and come back.

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
    return _epilogue('gig01_epilogue', real_mama=True)


def build_epilogue_standin():
    """SHE IS NOT IN THE BAR: our own Mama, exactly as the gig shipped.

    Same words, same keys, same buried voice-only actor this beat has always
    used - the only difference from the 1.0.0 epilogue is the scene's name. It
    is kept because she is not dependably in El Coyote Cojo (time of day and
    quest state, playtesting 2026-08-11), and a fallback that changes nothing is the
    one least likely to break the ending.

    Buried 2.5 m is the offset that needs no knowledge of the marker's rotation,
    the same trick every voice-only speaker in this file uses. She is heard and
    not seen: the visible Mama Welles in this variant is the stand-in
    Gig01_Encounter spawns on her own captured mark, and the scene supplies only
    the voice and the name over the subtitle.
    """
    return _epilogue('gig01_epilogue_standin', real_mama=False)


def _epilogue(name, real_mama):
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
    # Buried 2.5 m: close enough to hear, under the floor so there is no second
    # Mama Welles standing in the room. Same offset as Hoshino's h01.
    s = Scene(name, ANCHOR_MAMA)
    if real_mama:
        # The one in the bar. Taking her is the whole point - see
        # build_epilogue().
        mama = s.add_spawnset_actor('mama_welles', 'mama_welles', '#mama_welles')
    else:
        mama = s.add_actor('mama_welles', 'Character.Mama_Welles',
                           offset=OFFSET_MAMA)
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
    # If the encounter script spawned its STAND-IN instead (it only does that
    # when the base-game Mama is absent), the spawn set has nobody in it, the
    # acquisition finds nothing, and her lines play exactly as they do now.
    # ...and ONLY for the stand-in. When the real Mama is the actor there is no
    # second body to lipsync - she is the body - and a double pointing at the
    # same spawn set would be a second acquisition of one NPC. (Moot while
    # BRIDGE_SCENES is empty, which is why it is spelled out rather than left to
    # be discovered if the bridge is ever switched back on).
    if not real_mama:
        s.add_body_double(mama, 'mama_welles_body',
                          spawnset='mama_welles', spawnset_ref='#mama_welles')

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
    s1 = s.section([s.add_line(mama, "You look tired, mija.",
                               male="You look tired, mijo.", key='m01')],
                   lead_ms=2600)
    c1 = s.choice([s.add_option("Long night. She okay?", 'oe1')])
    # ...and V says it. playtest, 2026-08-13: "Missing V replies to Mama Welles as
    # audio". Both of his lines here were hub options - UI text that nobody
    # speaks - which is the same gap that left him silent to Hoshino.
    v1 = s.section([s.add_line(v, "Long night. She okay?", key='ve1')])
    s2 = s.section([s.add_line(mama, "She's in the back.", key='m02')])
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
    c2 = s.choice([s.add_option("Nova. I'll get a drink.", 'oe2')])
    v2 = s.section([s.add_line(v, "Nova. I'll get a drink.", key='ve2')])
    out = s.end('epilogue_out')

    s.link(start, s1)
    s.link_section(s1, c1)
    s.link_choice(c1, [v1])
    s.link_section(v1, s2)
    s.link_section(s2, c2)
    s.link_choice(c2, [v2])
    s.link_section(v2, out)

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
    s1 = s.section([s.add_line(
        v, "She'll never know how many people died for a clean ledger.",
        key='v02')])
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
    s2 = s.section([s.add_line(johnny, "Good. Let her sleep.", key='j01')],
                   inner=True, tail_ms=1200)
    out = s.end('bar_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)

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
ALL_BUILDERS = (build_elena, build_arasaka, build_terminal, build_shard_find,
                build_shard_read, build_nix_brief,
                build_legend, build_nix, build_graves, build_hoshino, build_kill,
                build_malware, build_epilogue, build_epilogue_standin,
                build_bar)


if __name__ == '__main__':
    built = [build() for build in ALL_BUILDERS]
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
