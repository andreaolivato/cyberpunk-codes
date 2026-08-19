r"""Scene builder: .scene resources for the Cyberpunk 2077 scene system.

The reusable half of the scene pipeline. A mod supplies its own paths, its own
anchors and its own dialogue; everything here is engine shape that does not
change between mods.

Call configure() once, at import time, before building any scene. It sets the
output paths and hands over the two sidecars a voiced mod produces
(durations.json from the voice generator, lipsync_picks.json from the lipsync
generator). Both are optional: without them a scene still builds, paced by a
character-count estimate and with no lipsync, which is what this
generator emitted before either existed.

Then build scenes with the Scene class and write the two companion resources:

    configure(out_dir=..., scene_depot=..., ...)
    scenes = [build_one(), build_two()]
    for s in scenes:
        s.write()
    write_subtitles(scenes)
    write_lipmap(scenes)

WHY THE SUBTITLE RESOURCE IS NOT OPTIONAL. A scene line points at a
scnlocLocstringId RUID, and the embedded locStore that looks like the place it
resolves is editor data the game ignores at runtime. The real lookup is a
localizationPersistenceSubtitleEntries resource keyed by the same RUID, merged
by ArchiveXL under `localization: subtitles:`. Ship a scene without one and
everything works except the words. See docs/scene-playbook.md.
"""
import json
import math
import os

# --------------------------------------------------------------- per-mod config
# Set by configure(). They are module globals rather than constructor arguments
# because every function below reads them at call time, which is how this code
# behaved when it lived in the gig's own generator, and keeping that shape is
# what makes the split provable by diffing the generated output.
OUT_DIR = None
SCENE_DEPOT = None
SUBTITLE_OUT = None
SUBTITLE_MAP_OUT = None
SUBTITLE_DEPOT = None
LIPMAP_OUT = None
LIPMAP_NAME = None
MEASURED = {}
LIPSYNC_SETS = {}
LIPSYNC_LINES = {}
SCENE_ALIASES = {}


def configure(out_dir, scene_depot, subtitle_out, subtitle_map_out,
              subtitle_depot, lipmap_out, lipmap_name,
              durations=None, lipsync_sets=None, lipsync_lines=None,
              scene_aliases=None):
    r"""Point the builder at one mod's output tree.

    out_dir           where the .scene.json files are written
    scene_depot       their path once packed, e.g. 'mod\<name>\scenes\'.
                      LOAD-BEARING: the lipmap is keyed by FNV1a64 of this path
                      plus the scene name, so a mismatch is a lipmap nobody
                      ever looks up. The quest-phase generator must use the
                      same string.
    subtitle_out      the localizationPersistenceSubtitleEntries resource
    subtitle_map_out  the localizationPersistenceSubtitleMap that names it.
                      Two resources, and getting it wrong is silent in game.
    subtitle_depot    the depot path of subtitle_out, as the map has to name it
    lipmap_out        the animLipsyncMapping resource
    lipmap_name       its ArchiveFileName header field
    durations         {'scene/key': ms} from the voice generator. Wins over the
                      character-count estimate. Missing is fine.
    lipsync_sets      {scene: {actor: {'anims': path, 'voicetag': str}}}
    lipsync_lines     {'scene/key': animation name}
    scene_aliases     {scene: source scene} for scenes that reuse another's
                      recordings, so they borrow its lipsync picks too
    """
    global OUT_DIR, SCENE_DEPOT, SUBTITLE_OUT, SUBTITLE_MAP_OUT, SUBTITLE_DEPOT
    global LIPMAP_OUT, LIPMAP_NAME, MEASURED, LIPSYNC_SETS, LIPSYNC_LINES
    global SCENE_ALIASES
    OUT_DIR = out_dir
    SCENE_DEPOT = scene_depot
    SUBTITLE_OUT = subtitle_out
    SUBTITLE_MAP_OUT = subtitle_map_out
    SUBTITLE_DEPOT = subtitle_depot
    LIPMAP_OUT = lipmap_out
    LIPMAP_NAME = lipmap_name
    MEASURED = durations or {}
    LIPSYNC_SETS = lipsync_sets or {}
    LIPSYNC_LINES = lipsync_lines or {}
    SCENE_ALIASES = scene_aliases or {}


# THE MARKER THAT FOLLOWS THE PLAYER, and it is what made the rest of the
# caption beats convertible at all.
#
# Most of Johnny's beats happen WHEREVER V IS STANDING - after Elena's call, on
# the walk out of the compound, over Hoshino's body. A fixed NodeRef cannot site
# those: a world line plays from the speaker's position, so an actor pinned to a
# car park in Arroyo is inaudible when V is across the city. That looked like a
# hard stop, and the plan was to leave those beats silent.
#
# It is not a hard stop, because vanilla has the same problem and solved it.
# `scnWorldMarker` has a `type` field, and across 358 shipped street-story
# questphases it takes TWO values: `NodeRef` (929 uses) and **`Tag` (73)**. Every
# Tag one carries `tag: "around_player"`, and five of them carry NO nodeRef at
# all (`nodeRef: 0`) - which is the proof that the tag alone is doing the work
# rather than being a hint alongside a node.
#
# So a scene can be staged at the player, and a spawnDespawn actor's spawnOffset
# is then relative to V, in V's own frame: +Y forward, +X right. Measured in
# game five times, docs/backlog.md 9. That is what makes a scene able to place
# its own speaker beside the player, which is the whole reason no script places
# anyone any more.
#
# gen_questphase.add_scene() turns this sentinel into the Tag marker; it is not
# a NodeRef and must not be written as one.
ANCHOR_PLAYER = 'around_player'

# The name every scene gives its Johnny actor. It is also his
# spawnDespawnParams.dynamicEntityUniqueName, which is the handle the workspot
# quest node addresses him by - so these two must stay the same string.
JOHNNY_ACTOR = 'Johnny'

# TWO APPEARANCES, AND THE GIG SHIPS BOTH ON PURPOSE.
#
# Visibility is gated by STATE, the see-through look by APPEARANCE, and they are
# separate mechanisms (docs/backlog.md 3b):
#
#   silverhand_default is blendable x15. A blendable mesh renders NOTHING unless
#   the phantom system is driving it, which needs a satisfied phantomVisibleState
#   - i.e. the workspot. Get it and this is the real apparition: dithered,
#   rim-lit, glitching. No published mod has ever shown it.
#
#   silverhand_riot__not_blendable is default x20 - no blendable meshes at all.
#   johnny.ent's own blendableAppearanceMatches names it as the engine's
#   substitute for silverhand_default. Solid, ordinary, no FX. This is what AMM
#   and Deceptious ship, and what "he appears at all" looks like.
#
#   **IT DOES NOT RENDER "REGARDLESS OF STATE" - THAT WAS WRONG.** This block
#   used to say so, inferred from counting mesh appearances and never tested on
#   its own: every time it had actually been seen, a workspot was running too.
#   Removing the workspot on 2026-08-14 made the SOLID Johnny vanish exactly
#   like the blendable one. So phantomVisibleStates gates the whole entity while
#   gamePhantomEntityComponent is attached, and **a workspot is mandatory for
#   either appearance**. The appearance decides what he looks like once visible;
#   it has never decided whether he is visible.
#   (AMM's blendable-free list is not a counter-example - AMM ships an .ent with
#   the phantom component deleted, so it has no state gate to satisfy).
#
# Hoshino's scene takes the ghost, the epilogue takes the solid one. That is not
# indecision - it makes ONE playthrough diagnostic:
#
#   both visible      the workspot works AND the apparition works. First ever.
#   ghost invisible,  the workspot did not satisfy the state gate. Solid is the
#     solid visible   answer; switch the epilogue's appearance into Hoshino's.
#   both invisible    something more basic is wrong - the actor is not spawning.
#                     Check ArchiveXL's log before anything else.
#
# The SOLID one goes on the epilogue deliberately: that is the last line of the
# comic and the beat the whole gig is built toward, so it gets the safe bet.
JOHNNY_GHOST = 'silverhand_default'
JOHNNY_SOLID = 'silverhand_riot__not_blendable'

# Johnny's standing idle, and the reason it is THIS one.
#
# Surveyed every shipped scene that puts Johnny in a workspot (27 scenes, 110
# workspot nodes). The requirements are: standing (he is a commentator, not
# furniture), needs no prop to sit on, and is PROVEN with playAtActorLocation: 1
# somewhere in the shipped data - a resource only ever used against a world node
# is not evidence that it works without one.
#
# Three candidates survive. All use entryId 2, which is what 108 of the 110
# nodes use:
#
#   main_characters\johnny\johnny__stand_ground__stand_around__02  <- chosen
#       Johnny's own rig, the plainest standing idle he has. palc=1 in
#       mq023_01_johnny.scene.
#   quest\side_quests\sq031\sq031_01a_smack_afterlife\
#       sq031__johnny__stand__wait_nervous__01
#       The most-used palc=1 standing Johnny in the game (7 nodes) - but
#       "wait_nervous" is a fidgety idle and the wrong register for this gig.
#   common\ground\generic__stand_ground__think__01
#       What sts_hey_gle_04_johnny.scene uses, i.e. the scene add_johnny() is
#       modelled on. Generic rather than Johnny-specific. Best fallback if the
#       chosen one reads badly in game.
#
# If the animation looks wrong, swap the path - the machinery does not change.
WORKSPOT_JOHNNY = ('base\\workspots\\main_characters\\johnny\\'
                   'johnny__stand_ground__stand_around__02.workspot')
# NOTE for anyone tempted to put a NON-JOHNNY actor in a workspot: this path is
# under `main_characters\johnny\`, so it is his rig. The generic alternative
# named a few lines above was written from memory of a shipped scene and **the
# file could not be found in the archives on 2026-08-15** - four patterns across
# four archives returned nothing, including one for the Johnny path above, which
# demonstrably works in game. So the search method is what is wrong, not
# necessarily the paths - but nothing here should carry an unverified workspot
# path, because a wrong one is SILENT: the actor simply never enters the
# workspot, which for a phantom means it never renders.
# Which entry of the .workspot to jump to. 2 in essentially all shipped data.
WORKSPOT_ENTRY = 2

# Reading pace for UNVOICED lines. With no audio the line duration IS the pacing:
# it drives both the subtitle and how long the section holds before moving on.
# ~55 ms/char lands near a comfortable read.
MS_BASE = 1200
MS_PER_CHAR = 55
MS_MAX = 12000

# Tail padding on a voiced line. The clip's own length is where the voice stops,
# which is not where the subtitle should vanish or the next speaker should start.
MS_VOICED_PAD = 350

# THE BODY DOUBLE, AND THE ONE THING IN THIS FILE THAT IS A GAMBLE.
#
# Lipsync plays on the line's SPEAKER, and that is why a speaker who has to be
# SEEN must be the scene's own actor. Johnny is, in all seven of his beats: the
# scene places him, poses him, and glitches him out, so the mouth that moves is
# the body on screen.
#
# It is still not true of everyone. A speaker who has to exist before or after
# his scene cannot be a scene actor at all - Hoshino is found and shot outside
# his, Mama Welles is a base-game NPC in a bar - so those two keep a voice-only
# actor buried 2.5 m under the floor, and a lipsync animation on that actor
# moves an invisible mouth.
#
# `scnAdditionalSpeakerRole.OnlyLipsync` is the engine's own answer, and vanilla
# ships it for exactly this shape of problem: `q000_kid_01b_meet_your_fixer` and
# `q115_03a_alt` speak their lines as the PLAYER actor and hang the lipsync on
# `v_male_tpp` / `v_female_tpp`, the third-person doubles you can actually see.
# So a line can name a second actor that receives the mouth movement and
# nothing else - no audio, no subtitle, no name.
#
# What is NOT precedented is how we would acquire that second actor. Ours is
# spawned from script by `DynamicEntitySpec`, which has no `uniqueName`, so the
# only handle it has is its TAG (`cc_g01_johnny`, `cc_g01_hoshino`).
# `gameEntityReferenceType` has a `Tag` member and `gameEntityReference` has the
# `names` array to put one in - but **across all 7067 shipped scenes, not one
# findInWorld actor uses it**: all 251 are `EntityRef` with a NodeRef. It is a
# real enum value that vanilla never exercises.
#
# Mama Welles is the exception and does not need the gamble: she is a base-game
# NPC, and `mama_welles_default.scene` - the scene that plays when you talk to
# her in that bar - acquires her with `spawnSet`, entry `mama_welles`, reference
# `#mama_welles`. That is copied verbatim.
#
# THE RISK IS A SCENE THAT NEVER STARTS. The quest phase is one linear chain
# (gen_questphase.py), so a scene that does not reach its exit point strands the
# gig for the rest of the playthrough. If an actor that cannot be acquired
# blocks scene start, that is what happens.
#
# It is shipped ON anyway, and the reasoning is about where the failure lands:
# the first bridged scene is `gig01_arasaka`, which plays about two minutes in,
# right after Elena's call. A stall there is discovered immediately and costs
# one build, not a playthrough. Set this to False and re-run the generators to
# strip every double back out; nothing else changes.
#
# ============================================================================
# IT DID NOT STALL - IT CRASHED THE GAME. Now scoped to ONE scene.
# ============================================================================
#
# it was playtested. The game died 109.8 s into the session, at (-179, -1493, 9)
# in Arroyo - 31 m from the compound entrance, which is where V is standing when
# Elena's call ends. `call_trace.log` stops at `cc_g01_dbg_johnny_ws = 4`
# (106.5 s) and `cc_g01_johnny_done = 1`, which is what the quest phase sets
# when `gig01_arasaka` EXITS, never arrives. The previous good run has it at
# 110.1 s. So the crash is inside the first bridged scene, about three seconds
# in - i.e. on or just after its one dialogue line event.
#
# Ruled out by the same logs, so nobody re-checks them:
#   * the .lipmap is fine - ArchiveXL logged "All lipsync maps merged." 46 s
#     before the crash, with no other warning
#   * no script error - red4ext's log is clean and the tick was demonstrably
#     running (it spawned Johnny and put him in the workspot)
#
# Which HALF of the bridge did it is not established, and both are gone
# together because both are this switch:
#   1. the `findInWorld` + `type: Tag` actor itself, or
#   2. `additionalSpeakers` naming an actorId whose actor never acquired - a
#      null performer dereferenced when the line plays, which fits the timing
#      exactly. Note vanilla's precedent does NOT cover this: its OnlyLipsync
#      doubles are `spawnDespawn` actors that always exist.
#
# WHAT STAYS ON is everything else - the lipsync sets, the voicetags, the
# animation names on every line. See docs/backlog.md 2j.
#
# ============================================================================
# AND IT IS NOW SCOPED TO ONE SCENE: gig01_arasaka. the design call, 2026-08-14.
# ============================================================================
#
# *"Why at the bar? I need to run the whole quest because the shortcut doesn't
# work. Make your changes to the first johnny after the call with elena."*
#
# He is right and the previous arrangement was thoughtless. `gig01_bar` is the
# only scene whose speaker IS the visible body, so it was the only place lipsync
# could be SEEN without the bridge - but it is the last beat of a forty-minute
# gig with no working shortcut to it. A test you cannot reach is not a test.
#
# So the experiment moves to the FIRST Johnny, two minutes in, and everything
# else stays bridge-free. One playthrough, one answer, and if it crashes it
# crashes before he has invested anything:
#
#   his mouth moves on "Fucking Arasaka..."  -> the bridge works. Turn the rest
#                                               on and this is finished.
#   the game crashes there again             -> the bridge is dead. Remove it,
#                                               ship lipsync only where the
#                                               speaker is visible, write it up.
#   it plays, no mouth                       -> read cc_g01_dbg_lip_johnny in
#                                               call_trace.log - 1 means our tag
#                                               is not registered, 2 means the
#                                               scene system ignored it
#
# ============================================================================
# DEAD. Tested at gig01_arasaka on 2026-08-14 and it FAILED BOTH WAYS AT ONCE.
# ============================================================================
#
# Playtest: *"No mouth movement. Crashes after saying arasaka. Plays with a still
# mouth."* And this time the trace answered it, because the diagnostic was no
# longer gated behind the beat it was measuring:
#
#     96.7  cc_g01_dbg_johnny      = 1     script spawns him
#     98.2  cc_g01_dbg_lip_johnny  = 2     <-- THE TAG IS REGISTERED
#     99.8  cc_g01_dbg_johnny_ws   = 4     he is in his workspot, visible
#    102.2  cc_g01_call_done       = 1     the scene is entered
#    (line plays, mouth still)
#    106.5  crash
#
# So `cc_g01_johnny` really does have an entity under it in
# DynamicEntitySystem at the moment the scene runs - our tag name and our timing
# are correct - and the scene still did not animate that body. The scene
# system's `findInWorld` resolver does not read the dynamic-entity tag registry.
#
# **`gameEntityReferenceType.Tag` is unusable from a scene. Do not try it again**
# without new evidence: zero of 7067 shipped scenes use it, and the one test
# that has ever been run on it found the entity present and the actor unbound.
#
# The crash is deterministic: 4.3 s after the scene is entered, both times,
# to a tenth of a second. That is scene TEARDOWN, not the line - the dangling
# additional speaker is dereferenced when the scene disposes of its actors.
#
# Empty set = no doubles anywhere. Everything else about lipsync stays.
BRIDGE_SCENES = set()


def estimate_ms(text):
    """What the line WOULD be paced at with no audio. gen_voice uses this to
    size its placeholder tones, so placeholders change nothing about timing."""
    return min(MS_MAX, MS_BASE + MS_PER_CHAR * len(text))


def line_ms(text, scene=None, key=None):
    if scene and key:
        ms = MEASURED.get('%s/%s' % (scene, key))
        if ms:
            return int(ms) + MS_VOICED_PAD
    return estimate_ms(text)


# ---------------------------------------------------------------- primitives

def yaw_to_face_player(offset):
    """The yaw that turns an actor at `offset` back to look at the player.

    ONLY MEANINGFUL ON AN `around_player` MARKER, where the offset is in V's own
    frame. All three facts below were measured in game on 2026-08-16, not
    assumed:

      * the marker sits at V's EXACT x and y (`dist` 0 cm on two runs)
      * +Y is FORWARD (an offset of (0, 2, 0) landed 2.00 m dead ahead on two
        runs facing 180 degrees apart)
      * +X is RIGHT (an offset of (1.1, 1.8, 0) landed 2.10 m away, 32 degrees
        off dead ahead, on the right-hand side)

    A FIXED 180 IS NOT THE ANSWER, and that is the trap this function exists to
    close. 180 points him at V only when he is directly ahead; at (1.1, 1.8) it
    left him looking 32 degrees wide, which is visible.

    Yaw is counter-clockwise seen from above, so a heading of theta faces
    (-sin, cos). Facing V from `offset` means facing (-x, -y), which gives
    atan2(x, -y). Straight ahead returns 180, matching the run that worked.
    """
    return math.degrees(math.atan2(offset[0], -offset[1]))


def _yaw_quat(yaw):
    """A rotation about Z, as the game writes quaternions.

    yaw 0 returns the exact integer identity the generator emitted before this
    existed, so every scene that does not set a yaw stays byte-identical and a
    rebuild shows only what actually changed.
    """
    if yaw == 0.0:
        return {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1}
    half = math.radians(yaw) / 2.0
    return {'$type': 'Quaternion', 'i': 0, 'j': 0,
            'k': math.sin(half), 'r': math.cos(half)}

def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v if v else 'None'}


def noderef(v):
    if not v:
        return {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'}
    return {'$type': 'NodeRef', '$storage': 'string', '$value': v}


def tdbid(v):
    if not v:
        return {'$type': 'TweakDBID', '$storage': 'uint64', '$value': '0'}
    return {'$type': 'TweakDBID', '$storage': 'string', '$value': v}


def resref(v=None, flags='Soft'):
    if not v:
        return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'uint64', '$value': '0'},
                'Flags': flags}
    return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string', '$value': v},
            'Flags': flags}


def entity_ref(unique_name=None, node_ref=None):
    """gameEntityReference - how a quest node names the thing it acts on.

    A scene-spawned actor is addressed by the `dynamicEntityUniqueName` it was
    given in spawnDespawnParams. That handle is the correction to the old "a
    scene actor cannot be bound to a spawned entity" note: it does not work in
    the direction script -> scene, but it works perfectly scene -> quest node.
    """
    return {'$type': 'gameEntityReference',
            'dynamicEntityUniqueName': cname(unique_name), 'names': [],
            'reference': noderef(node_ref), 'sceneActorContextName': cname(None),
            'slotName': cname(None), 'type': 'EntityRef'}


def quest_socket(name, kind):
    return {'HandleId': '@sock', 'Data': {
        '$type': 'questSocketDefinition', 'connections': [],
        'name': cname(name), 'type': kind}}


def fnv1a64(s):
    h = 0xCBF29CE484222325
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def ruid(key):
    """Stable 64-bit id for a locstring/variant/event.

    Real ids are editor timestamps; all that matters is that they are unique
    within the file and non-zero. Deriving them from a key keeps the generator
    deterministic - regenerating must not churn the whole file.
    """
    return str(0x2000000000000000 | (fnv1a64(key) & 0x0FFFFFFFFFFFFFFF))


def locstring_ruid(scene_name, key):
    """The id a line's text AND its audio both resolve through.

    Exposed as a module function because `tools/gen_voice.py` has to key its
    voiceover map on exactly these numbers. Deriving it in one place is what
    stops the scene and the audio drifting apart silently - a mismatch would not
    error, it would just play nothing.
    """
    return ruid('loc/' + scene_name + '/' + key)


def item_id(index, kind):
    """screenplay item id: low byte is the kind (1 = line, 2 = option),
    high bits are the item's INDEX IN ITS ARRAY, counted from ZERO.

    Vanilla ids run 1, 257, 513 for lines and 2, 258, 514 for options - that is
    (0 << 8) | kind, (1 << 8) | kind, ... The engine uses the high bits as an
    array index, it does not search for a matching itemId.

    Counting from one instead cost a playtest and produced three symptoms that
    looked unrelated: every hub showed the NEXT option's text, sections played a
    mix of their own lines and the following section's, and the last line in a
    scene indexed one past the end of the array and took the game down.
    """
    return {'$type': 'scnscreenplayItemId', 'id': (index << 8) | kind}


def actor_id(i):
    return {'$type': 'scnActorId', 'id': i if i is not None else 4294967295}


def node_id(i):
    return {'$type': 'scnNodeId', 'id': i}


def osock(name, ordinal, dests):
    return {
        '$type': 'scnOutputSocket',
        'destinations': [
            {'$type': 'scnInputSocketId',
             'isockStamp': {'$type': 'scnInputSocketStamp', 'name': 0, 'ordinal': d_ord},
             'nodeId': node_id(d_node)}
            for d_node, d_ord in dests
        ],
        'stamp': {'$type': 'scnOutputSocketStamp', 'name': name, 'ordinal': ordinal},
    }


# ------------------------------------------------------------------ builder
class Scene:
    def __init__(self, name, marker, category='dialoguesQuests'):
        self.name = name
        self.marker = marker
        self.category = category
        self.actors = []
        self.player_actors = []
        # Scene actors and the player actor live in separate arrays but share
        # ONE actorId space - Californication numbers its player actor 3 after
        # three scene actors 0..2, and scnscreenplayDialogLine.speaker is a
        # single scnActorId with no array discriminator.
        self.next_actor = 0
        self.nodes = []          # list of node dicts (already shaped)
        self.next_node = 1
        self.lines = []          # scnscreenplayDialogLine
        self.options = []        # scnscreenplayChoiceOption
        # key -> text, for OUR lines only. tools/gen_voice.py reads this to know
        # what to generate; line index -> key lets section() look a measured
        # duration up.
        self.line_text = {}
        self.line_key = {}
        # Keys whose line is spoken through the phone. section() fills it, and
        # gen_voice reads it to know which takes get the phone filter baked in.
        # See questkit/phone.py and docs/backlog.md 15.
        self.holocall_keys = set()
        # Lines pointed at a vanilla stringId instead of one of ours, reported
        # at write time so a reuse can never happen by accident or unnoticed.
        self.reused = []
        self.loc_vd = []
        self.loc_vp = []
        # (locstring ruid, text) for every line and option - this is what the
        # game actually reads. See the module docstring.
        self.subtitles = []
        self.entry_points = []
        self.exit_points = []
        self.performers = []
        # Workspots: the scene's own animation resources, so an actor can be put
        # into one without a world node. See add_workspot_node().
        self.workspots = []            # scnWorkspotData_ExternalWorkspotResource
        self.workspot_instances = []   # scnWorkspotInstance
        self.workspot_symbols = []     # debugSymbols.workspotsDebugSymbols
        self._ws_data_ids = {}         # depot path -> scnSceneWorkspotDataId
        # Lipsync: the sets this scene references, and who uses which.
        self.lipsync_sets = []         # depot paths, in reference order
        self.lipsync_voicetags = []    # parallel - what the .lipmap is keyed by
        # speaker actorId -> body-double actorId. section() reads this to hang
        # an OnlyLipsync additional speaker on every line that speaker says, so
        # a double can never be attached to the wrong line by hand.
        self.doubles = {}

    # -- lipsync -----------------------------------------------------------
    def _lipsync_for(self, actor_name):
        """(srrefId, voicetag) for this scene's actor, registering the set the
        first time it is asked for.

        Returns the "none" id (4294967295) and voicetag None when there is no
        pick, which is what every actor in this generator used to get.
        """
        pick = LIPSYNC_SETS.get(self.name, {}).get(actor_name)
        # An aliased scene borrows its source's picks along with its clips. The
        # picks are keyed by scene name, so without this the stand-in epilogue
        # would silently come out with no lipsync set and voicetag 0 - a
        # regression against the gig as it shipped, and one that shows up as a
        # still mouth rather than as an error.
        if not pick and self.name in SCENE_ALIASES:
            pick = LIPSYNC_SETS.get(SCENE_ALIASES[self.name], {}).get(actor_name)
        if not pick:
            return 4294967295, None
        if pick['anims'] not in self.lipsync_sets:
            self.lipsync_sets.append(pick['anims'])
            self.lipsync_voicetags.append(pick['voicetag'])
        return self.lipsync_sets.index(pick['anims']), pick['voicetag']

    # -- actors ------------------------------------------------------------
    def add_johnny(self, appearance=JOHNNY_SOLID, offset=(0.0, 0.0, 0.0),
                   yaw=0.0):
        """Johnny's relic apparition, as a PRESENT actor.

        Every value here is copied from a shipped scene where he speaks
        (the Heywood/Glen street story sts_hey_gle_04, scene
        sts_hey_gle_04_johnny.scene) - see docs/scene-playbook.md, "Johnny's
        apparition". Nothing here is invented.

        `Character.Silverhand` is confirmed four independent ways. Unlike the
        voice-only actors he spawns AT the marker with no offset and with
        position validation on, because he is meant to be seen.

        The caller picks the appearance, and that choice is the experiment - see
        JOHNNY_GHOST / JOHNNY_SOLID. It must be paired with a workspot
        (add_workspot_node + fire_workspot) or he is invisible either way.
        """
        return self.add_actor(JOHNNY_ACTOR, 'Character.Silverhand',
                              offset=offset, yaw=yaw,
                              appearance=appearance,
                              voicetag='1103967280742240508',
                              validate=1)

    def add_actor(self, actor_name, record, offset=(1000.0, 1000.0, -100.0),
                  appearance='default', voicetag='0', validate=0, yaw=0.0):
        """A speaking NPC the scene spawns itself.

        The offset puts the body a kilometre away and a hundred metres down:
        this actor exists so the line has a speaker (and therefore a name over
        the subtitle), not to be looked at. See the module docstring.
        """
        aid = self.next_actor
        self.next_actor += 1
        # A picked lipsync set brings its own voicetag, and it has to WIN over
        # the argument: vanilla's lipmap is keyed by voicetag, so the number on
        # the actor and the number in our lipmap entry must be the same one.
        # (They agree for Johnny - add_johnny passes the same value the vanilla
        # lipmap has for his sets - but agreeing by luck is not a design).
        srref, voicetag_pick = self._lipsync_for(actor_name)
        if voicetag_pick:
            voicetag = voicetag_pick
        self.actors.append({
            '$type': 'scnActorDef',
            'acquisitionPlan': 'spawnDespawn',
            'actorId': actor_id(aid),
            'actorName': actor_name,
            'animSets': [],
            'bodyCinematicAnimSets': [],
            'communityParams': {'$type': 'scnCommunityParams', 'entryName': cname(None),
                                'forceMaxVisibility': 0, 'reference': noderef(None)},
            'cyberwareAnimSets': [],
            'cyberwareCinematicAnimSets': [],
            'deformationAnimSets': [],
            'dynamicAnimSets': [],
            'facialAnimSets': [],
            'facialCinematicAnimSets': [],
            'findActorInContextParams': {
                '$type': 'scnFindEntityInContextParams',
                'contextActorName': cname(None), 'contextualName': 'Player',
                'forceMaxVisibility': 0, 'specRecordId': tdbid(None),
                'voiceVagId': {'$type': 'scnVoicetagId', 'id': '0'}},
            'findActorInWorldParams': {
                '$type': 'scnFindEntityInWorldParams',
                'actorRef': {'$type': 'gameEntityReference',
                             'dynamicEntityUniqueName': cname(None), 'names': [],
                             'reference': noderef(None), 'sceneActorContextName': cname(None),
                             'slotName': cname(None), 'type': 'EntityRef'},
                'forceMaxVisibility': 0},
            'holocallInitScn': resref(),
            # Indexes resouresReferences.lipsyncAnimSets. 4294967295 = none,
            # which is what everyone had before gen_lipsync existed and what
            # anyone still gets who is not in the picks (Elena, Nix - both
            # holocall-only, so there is no face on screen to animate).
            'lipsyncAnimSet': {'$type': 'scnLipsyncAnimSetSRRefId', 'id': srref},
            'spawnDespawnParams': {
                '$type': 'scnSpawnDespawnEntityParams',
                'alwaysSpawned': 1,
                'appearance': cname(appearance),
                'dynamicEntityUniqueName': cname(actor_name),
                'findInWorld': 0,
                'forceMaxVisibility': 0,
                'isEnabled': 1,
                'itemOwnerId': {'$type': 'scnPerformerId', 'id': 4294967040},
                'keepAlive': 0,
                'prefetchAppearance': 0,
                'spawnMarker': cname(None),
                'spawnMarkerNodeRef': noderef(None),
                'spawnMarkerType': 'Local',
                'spawnOffset': {
                    '$type': 'Transform',
                    # `yaw` IS IN THE PLAYER'S FRAME when the scene is staged
                    # on an `around_player` marker, exactly like the position
                    # beside it. MEASURED IN GAME, 2026-08-16: an actor at
                    # offset (0, 2, 0) landed 2.00 m dead ahead of V on two
                    # runs facing 180 degrees apart - bearing from V's facing
                    # 359 and 0 degrees, bearing in world terms 76 and 256.
                    #
                    # That kills the claim this file carried for months, that
                    # the marker's rotation is not knowable and a horizontal
                    # offset therefore cannot be aimed. It can. 180 turns the
                    # actor back to face V.
                    'orientation': _yaw_quat(yaw),
                    'position': {'$type': 'Vector4', 'W': 0,
                                 'X': offset[0], 'Y': offset[1], 'Z': offset[2]}},
                'spawnOnStart': 1,
                'specRecordId': tdbid(record),
                # OFF. Turning it on was a guess in an earlier pass, and it is
                # the wrong guess for this actor: the spawn point is deliberately
                # a kilometre out and a hundred metres down, which is
                # what position validation exists to reject. A rejected spawn
                # means no actor, and an actor that does not exist cannot speak.
                'validateSpawnPostion': validate},
            'spawnSetParams': {'$type': 'scnSpawnSetParams', 'entryName': cname(None),
                               'forceMaxVisibility': 0, 'reference': noderef(None)},
            'spawnerParams': {'$type': 'scnSpawnerParams', 'forceMaxVisibility': 0,
                              'reference': noderef(None)},
            'specAppearance': cname(appearance),
            # Vanilla leaves this at 0 for spawnDespawn actors and puts the
            # record only in spawnDespawnParams. Match that.
            'specCharacterRecordId': tdbid(None),
            'voicetagId': {'$type': 'scnVoicetagId', 'id': voicetag},
        })
        self.performers.append({
            '$type': 'scnPerformerSymbol',
            'editorPerformerId': ruid(self.name + '/performer/' + actor_name),
            'entityRef': {'$type': 'gameEntityReference',
                          'dynamicEntityUniqueName': cname(actor_name), 'names': [],
                          'reference': noderef(None), 'sceneActorContextName': cname(None),
                          'slotName': cname(None), 'type': 'EntityRef'},
            'performerId': {'$type': 'scnPerformerId', 'id': aid + 1},
        })
        return aid

    def add_spawnset_actor(self, actor_name, entry, ref, appearance='default'):
        """A speaking NPC the scene TAKES from the world instead of spawning.

        This is how vanilla acquires a base-game NPC who is already standing
        where the conversation happens, and taking her is the point: a quest
        scene that owns an actor is what stops that actor doing anything else.
        The epilogue's problem was never a race - our scene spawned a copy and
        never claimed the real Mama Welles at all, so her ordinary bar
        conversation stayed live and could win the approach (docs/backlog.md 7d).

        EVERY FIELD IS `sq018_01_mama_welles.scene`'s, dumped and diffed against
        add_actor above rather than reasoned out. The complete list of
        differences from a spawnDespawn actor is: acquisitionPlan, the two
        spawnSetParams fields, and four values zeroed in spawnDespawnParams
        (alwaysSpawned, appearance, dynamicEntityUniqueName, specRecordId). That
        is the whole diff; do not add to it.

        NOTHING IS SPAWNED. specRecordId is 0 on both paths, so this actor is
        found or the scene has no speaker - which is precisely why the quest
        phase must never enter this variant unless the probe says she is there.
        An actor that never acquires is what killed the body-double bridge: the
        crash came at scene TEARDOWN, 4.3 s in, both times.
        """
        aid = self.next_actor
        self.next_actor += 1
        srref, voicetag = self._lipsync_for(actor_name)
        actor_ref = {'$type': 'gameEntityReference',
                     'dynamicEntityUniqueName': cname(None), 'names': [],
                     'reference': noderef(ref), 'sceneActorContextName': cname(None),
                     'slotName': cname(None), 'type': 'EntityRef'}
        self.actors.append({
            '$type': 'scnActorDef',
            'acquisitionPlan': 'spawnSet',
            'actorId': actor_id(aid),
            'actorName': actor_name,
            'animSets': [],
            'bodyCinematicAnimSets': [],
            'communityParams': {'$type': 'scnCommunityParams', 'entryName': cname(None),
                                'forceMaxVisibility': 0, 'reference': noderef(None)},
            'cyberwareAnimSets': [],
            'cyberwareCinematicAnimSets': [],
            'deformationAnimSets': [],
            'dynamicAnimSets': [],
            'facialAnimSets': [],
            'facialCinematicAnimSets': [],
            'findActorInContextParams': {
                '$type': 'scnFindEntityInContextParams',
                'contextActorName': cname(None), 'contextualName': 'Player',
                'forceMaxVisibility': 0, 'specRecordId': tdbid(None),
                'voiceVagId': {'$type': 'scnVoicetagId', 'id': '0'}},
            'findActorInWorldParams': {'$type': 'scnFindEntityInWorldParams',
                                       'actorRef': actor_ref, 'forceMaxVisibility': 0},
            'holocallInitScn': resref(),
            'lipsyncAnimSet': {'$type': 'scnLipsyncAnimSetSRRefId', 'id': srref},
            'spawnDespawnParams': {
                '$type': 'scnSpawnDespawnEntityParams',
                'alwaysSpawned': 0,
                'appearance': cname(None),
                'dynamicEntityUniqueName': cname(None),
                'findInWorld': 0,
                'forceMaxVisibility': 0,
                'isEnabled': 1,
                'itemOwnerId': {'$type': 'scnPerformerId', 'id': 4294967040},
                'keepAlive': 0,
                'prefetchAppearance': 0,
                'spawnMarker': cname(None),
                'spawnMarkerNodeRef': noderef(None),
                'spawnMarkerType': 'Local',
                'spawnOffset': {
                    '$type': 'Transform',
                    'orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
                    'position': {'$type': 'Vector4', 'W': 0, 'X': 0, 'Y': 0, 'Z': 0}},
                'spawnOnStart': 1,
                'specRecordId': tdbid(None),
                'validateSpawnPostion': 1},
            'spawnSetParams': {'$type': 'scnSpawnSetParams', 'entryName': cname(entry),
                               'forceMaxVisibility': 0, 'reference': noderef(ref)},
            'spawnerParams': {'$type': 'scnSpawnerParams', 'forceMaxVisibility': 0,
                              'reference': noderef(None)},
            'specAppearance': cname(appearance),
            'specCharacterRecordId': tdbid(None),
            'voicetagId': {'$type': 'scnVoicetagId', 'id': voicetag},
        })
        self.performers.append({
            '$type': 'scnPerformerSymbol',
            'editorPerformerId': ruid(self.name + '/performer/' + actor_name),
            # Vanilla mirrors the acquisition reference here, the same way
            # add_body_double's spawnSet path does.
            'entityRef': dict(actor_ref),
            'performerId': {'$type': 'scnPerformerId', 'id': aid + 1},
        })
        return aid

    def add_body_double(self, speaker, actor_name, tag=None,
                        spawnset=None, spawnset_ref=None):
        """A SECOND actor for a speaker whose visible body is somebody else's.

        It never speaks. It is acquired from the world, receives the line's
        lipsync through `scnAdditionalSpeakerRole.OnlyLipsync`, which is all
        - see BRIDGE_BODY_DOUBLE at the top of this file for the mechanism,
        the vanilla precedent and the risk.

        Two ways to find it, and they are not equally safe:

          tag=      a `findInWorld` actor with `actorRef.type = Tag`, matching
                    the CName Gig01_Encounter's DynamicEntitySpec put in
                    `spec.tags`. Vanilla never uses this enum value.
          spawnset= a `spawnSet` actor, the way vanilla acquires a base-game
                    NPC standing in the world. Copied from the scene that owns
                    that NPC's ordinary conversation.

        `speaker` is the actorId whose lines this double should mouth. Nothing
        else in the scene refers to it, so if BRIDGE_BODY_DOUBLE is off, or the
        acquisition fails in game, the line plays exactly as it does today.

        The lipsync set and voicetag are copied from the speaker's own pick -
        the double has to be looking in the same animation set, or the name the
        line carries resolves to nothing.

        Returns None - adding no actor at all - when this scene is not in
        BRIDGE_SCENES, or when the speaker has no lipsync pick in this scene.
        The second case is normal: `_beat()` gives every converted beat a
        Johnny, and in `gig01_shard_find` he stands there without a line. A
        double for a speaker who never speaks would be an actor nothing refers
        to.
        """
        if self.name not in BRIDGE_SCENES:
            return None
        srref, voicetag = self._lipsync_for(
            self.actors[speaker]['spawnDespawnParams']
                       ['dynamicEntityUniqueName']['$value'])
        if srref == 4294967295:
            return None
        ref = {'$type': 'gameEntityReference',
               'dynamicEntityUniqueName': cname(None),
               'names': [cname(tag)] if tag else [],
               'reference': noderef(spawnset_ref if spawnset else None),
               'sceneActorContextName': cname(None), 'slotName': cname(None),
               'type': 'Tag' if tag else 'EntityRef'}
        aid = self.next_actor
        self.next_actor += 1
        self.actors.append({
            '$type': 'scnActorDef',
            'acquisitionPlan': 'findInWorld' if tag else 'spawnSet',
            'actorId': actor_id(aid),
            'actorName': actor_name,
            'animSets': [],
            'bodyCinematicAnimSets': [],
            'communityParams': {'$type': 'scnCommunityParams', 'entryName': cname(None),
                                'forceMaxVisibility': 0, 'reference': noderef(None)},
            'cyberwareAnimSets': [],
            'cyberwareCinematicAnimSets': [],
            'deformationAnimSets': [],
            'dynamicAnimSets': [],
            'facialAnimSets': [],
            'facialCinematicAnimSets': [],
            'findActorInContextParams': {
                '$type': 'scnFindEntityInContextParams',
                'contextActorName': cname(None), 'contextualName': 'Player',
                'forceMaxVisibility': 0, 'specRecordId': tdbid(None),
                'voiceVagId': {'$type': 'scnVoicetagId', 'id': '0'}},
            'findActorInWorldParams': {'$type': 'scnFindEntityInWorldParams',
                                       'actorRef': ref, 'forceMaxVisibility': 0},
            'holocallInitScn': resref(),
            'lipsyncAnimSet': {'$type': 'scnLipsyncAnimSetSRRefId', 'id': srref},
            # NOTHING CAN BE SPAWNED: `specRecordId` is 0, so this actor is
            # found or it is not there. The one thing that must never happen is
            # a second Johnny materialising beside the one the script placed -
            # and it did not, which is the one piece of good news from the run
            # that crashed ("there's only one Johnny").
            #
            # THE OTHER FIELDS ARE VANILLA'S, VERBATIM, and the first pass got
            # this wrong. It set spawnOnStart 0 and validateSpawnPostion 0
            # because that "says what is meant" - but a shipped findInWorld
            # actor (`bugbear_default.scene`) carries 1 and 1, and this project
            # has already paid twice for a hand-reasoned copy of something that
            # works: copy the thing that works first, not seventh. With
            # specRecordId 0 they cannot cause a spawn either
            # way, so match the shipped shape and remove the difference from the
            # list of things that could explain a crash.
            'spawnDespawnParams': {
                '$type': 'scnSpawnDespawnEntityParams',
                'alwaysSpawned': 0, 'appearance': cname(None),
                'dynamicEntityUniqueName': cname(None), 'findInWorld': 0,
                'forceMaxVisibility': 0, 'isEnabled': 1,
                'itemOwnerId': {'$type': 'scnPerformerId', 'id': 4294967040},
                'keepAlive': 0, 'prefetchAppearance': 0,
                'spawnMarker': cname(None), 'spawnMarkerNodeRef': noderef(None),
                'spawnMarkerType': 'Local',
                'spawnOffset': {
                    '$type': 'Transform',
                    'orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
                    'position': {'$type': 'Vector4', 'W': 0, 'X': 0, 'Y': 0, 'Z': 0}},
                'spawnOnStart': 1, 'specRecordId': tdbid(None),
                'validateSpawnPostion': 1},
            'spawnSetParams': {'$type': 'scnSpawnSetParams',
                               'entryName': cname(spawnset),
                               'forceMaxVisibility': 0,
                               'reference': noderef(spawnset_ref)},
            'spawnerParams': {'$type': 'scnSpawnerParams', 'forceMaxVisibility': 0,
                              'reference': noderef(None)},
            'specAppearance': cname('default'),
            'specCharacterRecordId': tdbid(None),
            'voicetagId': {'$type': 'scnVoicetagId', 'id': voicetag},
        })
        self.performers.append({
            '$type': 'scnPerformerSymbol',
            'editorPerformerId': ruid(self.name + '/performer/' + actor_name),
            # Vanilla mirrors the actor's own acquisition reference here.
            'entityRef': dict(ref),
            'performerId': {'$type': 'scnPerformerId', 'id': aid + 1},
        })
        self.doubles[speaker] = aid
        return aid

    def add_player(self):
        """V, acquired from context and never spawned. THIS IS HOW V SPEAKS.

        This used to carry a warning that adding a player actor "means the scene
        stages the player at a marker he may be a kilometre from", and that was
        the reason V had no spoken line anywhere in this gig - everything he said
        was choice-hub text, which is why our hub density was four times
        vanilla's (a hub per dialogue section, against vanilla's one per 3.8).

        THE WARNING WAS WRONG, and it is worth writing down how it was settled,
        because it was settled offline in about a minute. Round-trip a vanilla
        scene that has a player actor (sts_hey_gle_04_johnny.scene) and read the
        whole scnPlayerActorDef: acquisitionPlan, actorId, the anim-set arrays,
        findActorInContextParams, findNetworkPlayerParams, lipsyncAnimSet,
        playerName, specAppearance, specCharacterRecordId, specTemplate,
        voicetagId. **There is no spawn, marker, offset or position field of any
        kind** - unlike scnActorDef, which carries spawnDespawnParams with a
        spawnMarker and a spawnOffset. A player actor has nothing to be staged
        WITH. `findInContext` finds the player wherever he is standing.

        So this is safe in a holocall that fires while V is across the city, and
        the failure mode if a player line does not resolve its audio is a silent
        subtitle - exactly the status quo, not a regression.

        The only field that differs from vanilla's is `lipsyncAnimSet.id`:
        vanilla indexes its resouresReferences.lipsyncAnimSets, ours are empty,
        so 4294967295 (= none) is correct here. voicetagId IS vanilla's.
        """
        aid = self.next_actor
        self.next_actor += 1
        self.player_actors.append({
            '$type': 'scnPlayerActorDef',
            'acquisitionPlan': 'findInContext',
            'actorId': actor_id(aid),
            'animSets': [],
            'bodyCinematicAnimSets': [],
            'cyberwareAnimSets': [],
            'cyberwareCinematicAnimSets': [],
            'deformationAnimSets': [],
            'dynamicAnimSets': [],
            'facialAnimSets': [],
            'facialCinematicAnimSets': [],
            'findActorInContextParams': {
                '$type': 'scnFindEntityInContextParams',
                'contextActorName': cname(None), 'contextualName': 'Player',
                'forceMaxVisibility': 0,
                'specRecordId': tdbid('Character.Player_Puppet_Base'),
                'voiceVagId': {'$type': 'scnVoicetagId', 'id': '0'}},
            'findNetworkPlayerParams': {'$type': 'scnFindNetworkPlayerParams', 'networkId': 0},
            'lipsyncAnimSet': {'$type': 'scnLipsyncAnimSetSRRefId', 'id': 4294967295},
            'playerName': 'Player',
            'specAppearance': cname('default'),
            'specCharacterRecordId': tdbid('Character.Player_Puppet_Base'),
            'specTemplate': cname('(None)'),
            # Vanilla's player voicetag, read out of sts_hey_gle_04_johnny.scene.
            # Not load-bearing for our audio (the vomap resolves on the line's
            # RUID, not on a voicetag) but it costs nothing to be the same shape
            # as a real one.
            'voicetagId': {'$type': 'scnVoicetagId', 'id': '1103967280742240864'},
        })
        self.performers.append({
            '$type': 'scnPerformerSymbol',
            'editorPerformerId': ruid(self.name + '/performer/player'),
            'entityRef': {'$type': 'gameEntityReference',
                          'dynamicEntityUniqueName': cname(None), 'names': [],
                          'reference': noderef('#player'), 'sceneActorContextName': cname(None),
                          'slotName': cname(None), 'type': 'EntityRef'},
            'performerId': {'$type': 'scnPerformerId', 'id': aid + 1},
        })
        return aid

    # -- text --------------------------------------------------------------
    def _locstring(self, key, text, male=None):
        """Register one piece of text and return its locstring id.

        Two locales go in: en_us for an English game and db_db, the debug
        locale the reference mods also ship, so a differently-localised game
        still shows something rather than a blank line.
        """
        ls = locstring_ruid(self.name, key)
        # male defaults to the same string. It exists so a line can be gendered
        # for the player - Mama Welles says "mija" to a female V and "mijo" to a
        # male one, and the subtitle resource has separate variants for exactly
        # this. The embedded locStore below keeps the female wording; it is
        # editor data and not what anyone reads.
        self.subtitles.append((ls, text, male if male is not None else text))
        for locale in ('en_us', 'db_db'):
            vid = ruid('var/' + self.name + '/' + key + '/' + locale)
            self.loc_vp.append({'$type': 'scnlocLocStoreEmbeddedVariantPayloadEntry',
                                'content': text,
                                'variantId': {'$type': 'scnlocVariantId', 'ruid': vid}})
            self.loc_vd.append({'$type': 'scnlocLocStoreEmbeddedVariantDescriptorEntry',
                                'localeId': locale,
                                'locstringId': {'$type': 'scnlocLocstringId', 'ruid': ls},
                                'signature': {'$type': 'scnlocSignature', 'val': '3'},
                                'variantId': {'$type': 'scnlocVariantId', 'ruid': vid},
                                'vpeIndex': len(self.loc_vp) - 1})
        return ls

    def add_line(self, speaker, text, addressee=None, key=None, male=None,
                 vanilla_sid=None):
        """`vanilla_sid` reuses a RECORDED GAME LINE, whole.

        Pass the vanilla `stringId` (as a decimal string) and this line stops
        being ours: no subtitle entry is emitted for it, and the game resolves
        both the text and the voiceover from its own registrations. Nothing is
        shipped and nothing is redistributed - the mod just points at a number.

        Only legitimate when `text` is that vanilla line VERBATIM, because
        vanilla's text is what will appear on screen; the `text` argument then
        exists purely so this file still reads as a script. `docs/backlog.md` 2c
        lists the three lines in this gig that qualify and where they came from.
        """
        idx = len(self.lines)          # zero-based: see item_id()
        key = key or ('line%02d' % idx)
        # With no player actor there is nobody else to address. The vanilla
        # holocall brief does the same thing: its single actor is its own
        # addressee.
        if addressee is None:
            addressee = speaker
        if vanilla_sid is not None:
            ls = str(vanilla_sid)
            self.reused.append((key, ls, text))
        else:
            ls = self._locstring(key, text, male)
            # Only OUR lines can be voiced by us, and only our lines are paced
            # by the duration sidecar - a reused line is paced by the clip
            # vanilla already has, which the scene system knows about natively.
            self.line_text[key] = text
        self.line_key[idx] = key
        # THE MOUTH. A CName naming one animation inside the speaker's lipsync
        # set; gen_lipsync picked it for length. Both fields get the SAME name
        # on purpose - the `f_`/`m_` prefix is the player's body type, not the
        # speaker's, and an NPC line is one recording either way. Vanilla proves
        # it: `sts_hey_gle_04_johnny.scene` asks for `m_1A9FB7CB53406000` and
        # Johnny's set contains no `m_` animation at all (63 of 3119 catalogued
        # animations carry that prefix, all on gendered player lines). Naming
        # the `f_` one twice means a male V gets a mouth too.
        anim = LIPSYNC_LINES.get('%s/%s' % (self.name, key))
        # An aliased scene borrows the per-line picks too, not just the anim SET.
        # Missing this shipped a stand-in epilogue whose lines carried no lipsync
        # animation at all while the set resolved fine - the actor looked
        # correctly configured and her mouth still would not move.
        if not anim and self.name in SCENE_ALIASES:
            anim = LIPSYNC_LINES.get('%s/%s' % (SCENE_ALIASES[self.name], key))
        self.lines.append({
            '$type': 'scnscreenplayDialogLine',
            'addressee': actor_id(addressee),
            'femaleLipsyncAnimationName': cname(anim),
            'itemId': item_id(idx, 1),
            'locstringId': {'$type': 'scnlocLocstringId', 'ruid': ls},
            'maleLipsyncAnimationName': cname(anim),
            'speaker': actor_id(speaker),
            'usage': {'$type': 'scnscreenplayLineUsage',
                      'playerGenderMask': {'$type': 'scnGenderMask', 'mask': 3}},
        })
        return idx, text

    def add_option(self, text, key=None):
        idx = len(self.options)        # zero-based: see item_id()
        key = key or ('opt%02d' % idx)
        self.options.append({
            '$type': 'scnscreenplayChoiceOption',
            'itemId': item_id(idx, 2),
            'locstringId': {'$type': 'scnlocLocstringId',
                            'ruid': self._locstring(key, text)},
            'usage': {'$type': 'scnscreenplayOptionUsage',
                      'playerGenderMask': {'$type': 'scnGenderMask', 'mask': 3}},
        })
        return idx

    # -- nodes -------------------------------------------------------------
    def _nid(self):
        n = self.next_node
        self.next_node += 1
        return n

    def start(self, entry_name):
        nid = self._nid()
        self.nodes.append({'$type': 'scnStartNode', 'ffStrategy': 'automatic',
                           'nodeId': node_id(nid), 'outputSockets': []})
        self.entry_points.append({'$type': 'scnEntryPoint', 'name': cname(entry_name),
                                  'nodeId': node_id(nid)})
        return nid

    def end(self, exit_name):
        nid = self._nid()
        self.nodes.append({'$type': 'scnEndNode', 'ffStrategy': 'automatic',
                           'nodeId': node_id(nid), 'outputSockets': [],
                           'type': 'Terminating'})
        self.exit_points.append({'$type': 'scnExitPoint', 'name': cname(exit_name),
                                 'nodeId': node_id(nid)})
        return nid

    def hub(self):
        nid = self._nid()
        self.nodes.append({'$type': 'scnHubNode', 'ffStrategy': 'automatic',
                           'nodeId': node_id(nid), 'outputSockets': []})
        return nid

    def section(self, spoken, holocall=False, inner=False, inner_vo=False,
                tail_ms=0, lead_ms=700):
        """A block of dialogue. `spoken` is [(line_index, text), ...].

        `inner_vo` is `inner` split in half: the inner-dialog VO expression,
        which is what makes a line play 2D, without the inner-dialog subtitle
        styling, which is Johnny's relic register and belongs to him. It exists
        for a speaker who is standing in front of V and must be heard rather
        than located - see build_hoshino in gen_scenes.py.

        CONFIRMED IN GAME, 2026-08-17, and it was a candidate until then. The
        two fields were separated by routing Hoshino's two lines differently in
        one conversation: h01 with the VO expression alone, h02 with both. Both
        were audible from a speaker a kilometre away, and both subtitles read
        "Hoshino: ..." in ordinary styling. So `voExpression` carries the 2D
        behaviour on its own and `visualStyle` changes nothing visible for a
        speaker who is not Johnny. See docs/backlog.md 10k.

        Lines are laid end to end: each event's startTime is the running total,
        and sectionDuration is the sum. With no audio, these numbers are the
        only thing pacing the conversation.

        `tail_ms` extends sectionDuration past the last line without adding one.
        Only the LAST section of a scene needs it, and only when what follows the
        scene would step on the line: a scene's spawnDespawn actors are removed
        the moment it exits, and the quest phase continues on the same frame.

        `lead_ms` is the gap before the FIRST line. 700 ms by default and that
        default is load-bearing - see the note where it is used. Raise it when
        the scene has to STAGE something before anyone speaks: a spawnDespawn
        actor streams in asynchronously, and a line that fires while he is still
        arriving is a line nobody sees him say. Playtest, 2026-08-14, on the
        arasaka diagnostic: *"The second one spawned too late and behind me so I
        didn't have time to check his mouth."*
        """
        nid = self._nid()
        if holocall:
            for idx, _text in spoken:
                key = self.line_key.get(idx)
                if key is not None:
                    self.holocall_keys.add(key)
        events = []
        # LEAD-IN. A dialogue event at startTime 0 fires the instant the section
        # opens, and playtesting reported Elena's first line never appearing while the
        # rest did (2026-08-12). The section is still coming up at t=0 - and for
        # the calls the phone UI is mid-transition too - so the first line can be
        # swallowed. Everything shifts by this, which costs nothing and removes a
        # whole class of "the first line is missing".
        t = lead_ms
        for i, (idx, text) in enumerate(spoken):
            dur = line_ms(text, self.name, self.line_key.get(idx))
            # THE BODY DOUBLE, attached by who is speaking rather than by hand.
            # role OnlyLipsync means this second actor gets the mouth movement
            # and nothing else - no audio, no subtitle, no speaker name. See
            # add_body_double and BRIDGE_BODY_DOUBLE.
            double = self.doubles.get(self.lines[idx]['speaker']['id'])
            speakers = [] if double is None else [{
                '$type': 'scnAdditionalSpeaker', 'actorId': actor_id(double),
                'type': 'Normal'}]
            # Scene events are handles, not inline objects - WolvenKit refuses
            # the file outright if they are written flat.
            events.append({'HandleId': '@ev', 'Data': {
                '$type': 'scnDialogLineEvent',
                'additionalSpeakers': {'$type': 'scnAdditionalSpeakers', 'executionTag': 0,
                                       'role': 'OnlyLipsync' if speakers else 'Full',
                                       'speakers': speakers},
                'duration': dur,
                'executionTagFlags': 0,
                'id': {'$type': 'scnSceneEventId',
                       'id': ruid('ev/%s/%d/%d' % (self.name, nid, i))},
                'scalingData': None,
                'screenplayLineId': item_id(idx, 1),
                'startTime': t,
                'type': '0',
                # NOT 'regular'. A regular line needs a speaker GameObject the
                # subtitle system can reach, and ours is a voice-only actor a
                # kilometre away - so the line resolved its text and was then
                # dropped on the floor. Symptom: choice options read fine (they
                # are UI, not subtitles) while nothing the NPC says ever appears.
                #
                # alwaysCinematicNoSpeaker (scnDialogLineVisualStyle = 7) is the
                # engine's own style for a line with no speaker present. Same
                # lesson as the scripted route, which needs
                # scnDialogLineType.OwnerlessRegular for Johnny and Mama Welles
                # (architecture.md, "Spoken lines without a .scene").
                #
                # Cost: no speaker name over the line. Acceptable here - Elena's
                # name is already on the call UI, and Hoshino and Mama Welles are
                # standing in front of the player.
                # 'regular' for everyone except Johnny, who gets vanilla's
                # 'innerDialog' - the relic register, and what 20 of 25 shipped
                # Johnny scenes use.
                #
                # This was 'alwaysCinematicNoSpeaker' for a while, which displays
                # a line but HIDES the speaker name (subtitlesControllers.swift
                # :169) - so Elena and the rest read as bare floating text while
                # Johnny's lines looked like the game's own. That was the wrong
                # fix to the wrong diagnosis: lines were vanishing because
                # validateSpawnPostion was rejecting the spawn of an actor placed
                # deliberately out of the world, so there was no speaker at all.
                # Validation is off now, the actor exists, and a present speaker
                # is all 'regular' needs.
                'visualStyle': 'innerDialog' if inner else 'regular',
                'voParams': {
                    '$type': 'scnDialogLineVoParams',
                    'alwaysUseBrainGender': 0,
                    'customVoEvent': cname(None),
                    'disableHeadMovement': 0,
                    'ignoreSpeakerIncapacitation': 1,
                    # The flag that routes a line into the phone UI instead of
                    # the world. Vanilla gig-briefing holocalls set it on every
                    # line of the caller's section.
                    'isHolocallSpeaker': 1 if holocall else 0,
                    'voContext': 'Vo_Context_Quest',
                    # Spoken = face to face, Phone = through the call UI. There
                    # is no "Normal": the enum starts at Vo_Expression_Spoken.
                    'voExpression': ('Vo_Expression_Phone' if holocall else
                                     'Vo_Expression_InnerDialog'
                                     if (inner or inner_vo) else
                                     'Vo_Expression_Spoken'),
                },
            }})
            t += dur
        self.nodes.append({
            '$type': 'scnSectionNode',
            'actorBehaviors': [],
            'events': events,
            'ffStrategy': 'automatic',
            'isFocusClue': 0,
            'nodeId': node_id(nid),
            'outputSockets': [],
            'sectionDuration': {'$type': 'scnSceneTime', 'stu': max(t + tail_ms, 1)},
        })
        return nid

    def choice(self, option_indices):
        """An on-screen dialogue hub. One output socket per option, in order."""
        nid = self._nid()
        self.nodes.append({
            '$type': 'scnChoiceNode',
            'alwaysUseBrainGender': 0,
            'ataParams': {'$type': 'scnChoiceNodeNsAttachToActorParams',
                          'actorId': actor_id(None), 'visualizerStyle': 'onScreen'},
            'atgoParams': {'$type': 'scnChoiceNodeNsAttachToGameObjectParams',
                           'nodeRef': noderef(None), 'visualizerStyle': 'inWorld'},
            'atpParams': {'$type': 'scnChoiceNodeNsAttachToPropParams',
                          'propId': {'$type': 'scnPropId', 'id': 4294967295},
                          'visualizerStyle': 'inWorld'},
            'atsParams': {'$type': 'scnChoiceNodeNsAttachToScreenParams'},
            'atwParams': {'$type': 'scnChoiceNodeNsAttachToWorldParams',
                          'customEntityRadius': 0,
                          'entityOrientation': {'$type': 'Quaternion', 'i': 0, 'j': 0,
                                                'k': 0, 'r': 1},
                          'entityPosition': {'$type': 'Vector3', 'X': 0, 'Y': 0, 'Z': 0},
                          'visualizerStyle': 'inWorld'},
            'choiceFlags': '0',
            'choiceGroup': cname(None),
            'choicePriority': 0,
            'cpoHoldInputActionSection': 0,
            'customPersistentLine': {'$type': 'scnscreenplayItemId', 'id': 4294967040},
            'displayNameOverride': '',
            'doNotTurnOffPreventionSystem': 0,
            'ffStrategy': 'automatic',
            'forceAttachToScreenCondition': None,
            'hubPriority': 0,
            'interruptCapability': 'Interruptable',
            'interruptionSpeakerOverride': actor_id(None),
            'localizedDisplayNameOverride': {'unk1': '0', 'value': ''},
            'lookAtParams': {'HandleId': '@lookat', 'Data': {
                '$type': 'scnChoiceNodeNsAdaptiveLookAtParams',
                'auxiliaryRelativePoint': {'$type': 'Vector3', 'X': 0, 'Y': 0, 'Z': 0},
                'blendLimit': 0.300000012,
                'distantSlotName': cname('Chest'),
                'nearbySlotName': cname('Head'),
                'referencePointFullEffectAngle': 0,
                'referencePointFullEffectDistance': 5,
                'referencePointNoEffectAngle': 63,
                'referencePointNoEffectDistance': 0,
                'referencePoints': []}},
            'mappinParams': {'HandleId': '@mappin', 'Data': {
                '$type': 'scnChoiceNodeNsMappinParams',
                'locationType': 'Nameplate',
                'mappinSettings': tdbid('MappinUISettings.SceneDialogNPCSettings')}},
            'mode': 'attachToScreen',
            'nodeId': node_id(nid),
            'options': [{
                '$type': 'scnChoiceNodeOption',
                'blueline': 0,
                'bluelineCondition': None,
                'caption': cname(None),
                'emphasisCondition': None,
                'exDataFlags': 0,
                'gameplayAction': tdbid(None),
                'iconCondition': None,
                'iconTagIds': [],
                'isFixedAsRead': 0,
                'isSingleChoice': 0,
                'mappinReferencePointId': {'$type': 'scnReferencePointId', 'id': 4294967295},
                'questCondition': None,
                'screenplayOptionId': item_id(oi, 2),
                'timedCondition': None,
                'timedParams': None,
                'triggerCondition': None,
                'type': {'$type': 'gameinteractionsChoiceTypeWrapper', 'properties': 0},
            } for oi in option_indices],
            'outputSockets': [],
            'persistentLineEvents': [],
            'reminderCondition': None,
            'reminderParams': None,
            'shapeParams': {'HandleId': '@shape', 'Data': {
                '$type': 'scnInteractionShapeParams',
                'activationBaseLength': 1, 'activationHeight': 3, 'activationYawLimit': 160,
                'customActivationRange': 1.5, 'customIndicationRange': 1.5,
                'offset': {'$type': 'Vector3', 'X': 0, 'Y': 0, 'Z': 0},
                'preset': 'small',
                'rotation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1}}},
            'timedParams': None,
            'timedSectionCondition': None,
        })
        return nid

    # -- workspots ---------------------------------------------------------
    def _workspot_data(self, path):
        """Register a .workspot resource once and return its dataId."""
        if path in self._ws_data_ids:
            return self._ws_data_ids[path]
        # Any unique non-zero Uint32 will do; deriving it from the path keeps
        # the generator deterministic, like ruid().
        did = fnv1a64(path) & 0x7FFFFFFF
        self._ws_data_ids[path] = did
        self.workspots.append({'HandleId': '@ws', 'Data': {
            '$type': 'scnWorkspotData_ExternalWorkspotResource',
            'dataId': {'$type': 'scnSceneWorkspotDataId', 'id': did},
            # Flags "Default", not "Soft" - every shipped scene loads its
            # workspot resources eagerly, and a soft reference that has not
            # streamed in yet is an animation that does not play.
            'workspotResource': resref(path, flags='Default'),
        }})
        return did

    def add_workspot_node(self, unique_name, path=WORKSPOT_JOHNNY,
                          entry=WORKSPOT_ENTRY):
        """A node that puts a scene-spawned actor into a workspot IN PLACE.

        Vanilla ships two shapes and only one of them is usable here:

          questUseWorkspotParamsV1     points at a `workspotNode` NodeRef in a
                                       streaming sector. Unusable - a mod's own
                                       world nodes do not resolve.
          scnUseSceneWorkspotParamsV1  points at a workspotInstanceId in THIS
                                       scene, with playAtActorLocation 1 and no
                                       world node at all. This one.

        Field values are node 28 of sts_hey_gle_04_johnny.scene crossed with the
        four palc=1 nodes of sts_wat_kab_03_johnny.scene, taking the latter's
        `enableIdleMode: 1` / `maxAnimTimeLimit: 0` because we want an idle that
        loops for as long as the scene lasts rather than one that runs out.

        The node is deliberately TERMINAL: nothing hangs off its outputs. See
        fire_workspot() for why.
        """
        nid = self._nid()
        did = self._workspot_data(path)
        # Vanilla ties these three numbers together (node 28 drives instance 28)
        # and it costs nothing to match, so a dump of our file reads like a dump
        # of theirs.
        self.workspot_instances.append({
            '$type': 'scnWorkspotInstance',
            'dataId': {'$type': 'scnSceneWorkspotDataId', 'id': did},
            'localTransform': {
                '$type': 'Transform',
                'orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
                'position': {'$type': 'Vector4', 'W': 0, 'X': 0, 'Y': 0, 'Z': 0}},
            'originMarker': {
                '$type': 'scnMarker',
                'entityRef': entity_ref(),
                'isMounted': 1,
                'localMarkerId': cname(None),
                # THE POINT OF THE WHOLE EXERCISE: no world node. The workspot
                # plays wherever the actor already is.
                'nodeRef': noderef(None),
                'slotName': cname(None),
                'type': 'Global'},
            'playAtActorLocation': 1,
            'workspotInstanceId': {'$type': 'scnSceneWorkspotInstanceId', 'id': nid},
        })
        self.workspot_symbols.append({
            '$type': 'scnWorkspotSymbol',
            'wsEditorEventId': str(0x10000000 + nid),
            'wsInstance': {'$type': 'scnSceneWorkspotInstanceId', 'id': nid},
            'wsNodeId': node_id(nid),
        })
        self.nodes.append({
            '$type': 'scnQuestNode',
            'ffStrategy': 'automatic',
            # Input socket ORDINALS are positions in this list, so "In" is
            # ordinal 1 and CutDestination is 0. Linking to ordinal 0 by habit
            # would wire the node's cut-scene skip path instead of its entry.
            'isockMappings': [cname('CutDestination'), cname('In')],
            'nodeId': node_id(nid),
            'osockMappings': [cname('Success'), cname('Work Started')],
            'outputSockets': [osock(0, 0, []), osock(0, 1, [])],
            'questNode': {'HandleId': '@qn', 'Data': {
                '$type': 'questUseWorkspotNodeDefinition',
                'entityReference': entity_ref(unique_name=unique_name),
                'id': nid,
                'paramsV1': {'HandleId': '@qp', 'Data': {
                    '$type': 'scnUseSceneWorkspotParamsV1',
                    'changeWorkspot': 1,
                    'continueInCombat': 0,
                    'dangleResetSimulation': 0,
                    'enableIdleMode': 1,
                    'entryId': {'$type': 'workWorkEntryId', 'id': entry},
                    'entryTag': cname(None),
                    'exitAnimName': cname(None),
                    'exitEntryId': {'$type': 'workWorkEntryId', 'id': 4294967295},
                    'finishAnimation': 0,
                    'forceEntryAnimName': cname(None),
                    'function': 'UseWorkspot',
                    'instant': 0,
                    'isPlayer': 0,
                    'isWorkspotInfinite': 1,
                    'itemOverride': {'$type': 'workWorkspotItemOverride',
                                     'itemOverrides': [], 'propOverrides': []},
                    'jumpToEntry': 1,
                    'maxAnimTimeLimit': 0,
                    'meshDissolvingEnabled': 1,
                    'movementType': 'Walk',
                    'playAtActorLocation': 1,
                    'playerParams': {
                        '$type': 'questUseWorkspotPlayerParams',
                        'applyCameraParams': 0,
                        'cameraSettings': {'$type': 'gameTier3CameraSettings',
                                           'pitchBottomLimit': 45,
                                           'pitchSpeedMultiplier': 1,
                                           'pitchTopLimit': 60,
                                           'yawLeftLimit': 60, 'yawRightLimit': 60,
                                           'yawSpeedMultiplier': 1},
                        'cameraUseTrajectorySpace': 1,
                        'emptyHands': 0,
                        'parallaxSpace': 'Trajectory',
                        'parallaxWeight': 1,
                        'tier': 'Tier3',
                        'vehicleProceduralCameraWeight': 1},
                    'repeatCommandOnInterrupt': 0,
                    # Put him exactly where he stands rather than walking him in
                    # from wherever the spawn landed.
                    'teleport': 1,
                    'workExcludedGestures': [],
                    'workspotInstanceId': {'$type': 'scnSceneWorkspotInstanceId',
                                           'id': nid},
                    'workspotNode': noderef(None),
                }},
                'sockets': [quest_socket('CutDestination', 'CutDestination'),
                            quest_socket('In', 'Input'),
                            quest_socket('Success', 'Output'),
                            quest_socket('Work Started', 'Output')],
            }},
        })
        return nid

    # -- wiring ------------------------------------------------------------
    def _node(self, nid):
        for n in self.nodes:
            if n['nodeId']['id'] == nid:
                return n
        raise KeyError(nid)

    def link(self, src, dst, ordinal=0):
        """Plain flow: src's default output -> dst's default input."""
        node = self._node(src)
        node['outputSockets'].append(osock(0, ordinal, [(dst, 0)]))

    def link_choice(self, src, targets):
        """One socket per option, then the six empty sockets a hub always has.

        The empty ones are not decoration: a scnChoiceNode always carries socket
        names 1..6 alongside its option sockets in every scene inspected, and
        matching the shipped shape is cheaper than finding out which of them the
        engine indexes by position.
        """
        node = self._node(src)
        for i, dst in enumerate(targets):
            node['outputSockets'].append(osock(0, i, [(dst, 0)]))
        for name in range(1, 7):
            node['outputSockets'].append(osock(name, 0, []))

    def link_section(self, src, dst):
        """Section nodes carry an extra empty socket (name 1) in every shipped
        scene; keep the shape identical."""
        node = self._node(src)
        node['outputSockets'].append(osock(0, 0, [(dst, 0)]))
        node['outputSockets'].append(osock(1, 0, []))

    def add_fact_node(self, fact, value=1):
        """A node that sets a quest fact from INSIDE the scene.

        Normally this project refuses to do this - every branch ends at its own
        exit point and the quest phase does the fact work, so there is one graph
        builder to maintain instead of two. The exception earns itself: this is
        the only way to signal something that happens PART-WAY THROUGH a scene,
        and the exit point cannot say "the last choice hub is now on screen".

        Shape is vanilla's node 116 in sts_wat_kab_03_johnny.scene.
        """
        nid = self._nid()
        self.nodes.append({
            '$type': 'scnQuestNode',
            'ffStrategy': 'automatic',
            'isockMappings': [cname('CutDestination'), cname('In')],
            'nodeId': node_id(nid),
            'osockMappings': [cname('Out')],
            'outputSockets': [osock(0, 0, [])],
            'questNode': {'HandleId': '@qn', 'Data': {
                '$type': 'questFactsDBManagerNodeDefinition',
                'id': nid,
                'sockets': [quest_socket('CutDestination', 'CutDestination'),
                            quest_socket('In', 'Input'),
                            quest_socket('Out', 'Output')],
                'type': {'HandleId': '@qt', 'Data': {
                    '$type': 'questSetVar_NodeType',
                    # A plain String here, not a CName - vanilla writes
                    # "kab_03_gun_shot" as a bare string.
                    'factName': fact,
                    'setExactValue': 0,
                    'value': value,
                }},
            }},
        })
        return nid

    def fire_workspot(self, section, ws_node, start_time=0):
        """Trigger a workspot node from a section, as a SIDE BRANCH.

        Must be called AFTER link_section on the same section: sockets are
        written in (name, ordinal) order and validate() enforces it.

        Vanilla wires these two ways and the choice matters:

        MAIN FLOW (sts_hey_gle_04, node 7): start -> workspot -> "Work Started"
        -> first section. Guarantees the workspot has begun before a word is
        said, and stalls the entire scene forever if it never starts. A scene
        that never reaches its exit point is a quest phase that waits on that
        exit point for the rest of the playthrough - which is how this gig dies.

        EVENTS SOCKET (sts_wat_kab_03, all four of its playAtActorLocation
        nodes): the section carries a `scneventsSocket` event that fires output
        socket name 2 at a given time, and the workspot node hangs off it with
        nothing after it. Fire and forget: the conversation is not waiting on it.

        We take the events socket. If the workspot fails we are back to exactly
        today's behaviour - an invisible Johnny whose lines still play - instead
        of a gig that cannot be finished. Given that no published mod has ever
        made this work, failing back to the known state is worth more than
        guaranteeing the ordering.

        start_time 0 puts him in the workspot as the section opens, which for
        the FIRST section of a scene means he is visible for all of it rather
        than materialising when his turn comes.
        """
        return self.fire_event(section, ws_node, start_time)

    def stage_johnny(self, first_section, last_section, actor=JOHNNY_ACTOR):
        """Everything a visible scene actor needs, in one call.

        The name is historical: nothing here is specific to Johnny except the
        default actor. Position and facing are set on the actor itself, by
        add_johnny; this adds the two things that are per-SECTION and cannot be.

          the workspot, at t=0 of the FIRST section. It is not decoration -
          `gamePhantomEntityComponent.phantomVisibleStates` is
          ["RootMotion","Workspot"], so without one the actor is invisible AND
          untargetable. Passing the wrong section here is silent: firing an
          events socket on a valid section is valid whichever section it is.

          the exit, 250 ms before the LAST section ends. A scene deletes its
          spawnDespawn actors on the frame it exits, so without this he pops.
          Timed here because the scene is the only thing that knows its own
          length; the deleted script route computed it from placement time
          instead and fired five seconds late.

        MUST be called after every link_section on those sections - output
        sockets are written in order and validate() enforces it.

        Full recipe: docs/scene-playbook.md, "STAGING A CHARACTER WHO SPEAKS,
        LIPSYNCS AND STANDS BESIDE V".
        """
        self.fire_workspot(first_section, self.add_workspot_node(actor),
                           start_time=0)
        dur = self._node(last_section)['sectionDuration']['stu']
        exit_at = max(dur - 250, 0)
        # THE EXIT FLASH. A scene removes its spawnDespawn actors on the frame
        # it exits, so without this the apparition simply pops out of existence.
        # The old script route covered it by playing the same effect and
        # deleting the body 0.25 s later, calibrated by ear across 1.2 / 0.45 /
        # 0.25 s; that listener went with the script placement.
        #
        # The scene plays it itself now, which is better than the listener was:
        # no polling, no search for the body, and the timing is the scene's own
        # to the millisecond rather than a tick boundary. Same number as the cue
        # below, so the flash and the cue agree.
        self.fire_vfx(last_section, 'johnny_teleport_start',
                      self.performer_id(actor), start_time=exit_at)
        # The cue stays even though nothing listens to it now. It costs one
        # quest node and it is the only signal a future script could use.
        self.fire_event(last_section, self.add_fact_node('cc_g01_johnny_exit'),
                        start_time=exit_at)

    def performer_id(self, actor_name):
        """The performer id of a named scene actor.

        Performer ids are actor id + 1, which is the convention add_actor
        already writes into every scnPerformerSymbol. Looked up by name rather
        than passed in, because every stage_johnny caller has the name and none
        of them keeps the id.
        """
        for a in self.actors:
            if a['actorName'] == actor_name:
                return a['actorId']['id'] + 1
        raise SystemExit('%s: no actor named %s' % (self.name, actor_name))

    def fire_vfx(self, section, effect, performer, start_time=0, action='Play'):
        """Play a named effect on a performer, from the scene itself.

        `scneventsVFXEvent` is what vanilla uses for this, and it is used a lot:
        1161 of the 7067 shipped .scene files carry one (counted 2026-08-17 by
        extracting every scene from basegame_4_gamedata.archive). That count is
        the gotcha #17 check, not a formality - an event class existing in
        Codeware's dump is no evidence the engine implements it, and this
        project has already shipped one enum member that looked right and killed
        the game three seconds into its scene.

        Every field below is q101_07c_johnny_triggers.scene's, which plays
        `johnny_teleport_start` on Johnny twice. Two things it settles:

        effectInstanceId IS NOT ZERO. It is 4294967295 in both halves, and zero
        would be wrong rather than merely empty: zero is a real index into the
        scene's own `effectDefinitions`, so an event written with it points at a
        scene effect resource we do not ship. In that one file, 27 of 28 events
        carry the sentinel and the one that carries (0, 0) is the scene's own
        q101_pills_spill.effect, declared in effectDefinitions with effectId 0.

        A NAMED EFFECT NEEDS NO DECLARATION ANYWHERE. `johnny_teleport_start`
        does not appear in that scene's effectDefinitions at all; only the
        pills do. Effects named on an event resolve against the performer's own
        entity, which is also how the deleted script route played this one.

        A performer-attached effect leaves nodeRef at 0 and names a performer; a
        WORLD effect is the mirror image, performerId 4294967040 and a real
        nodeRef (that file's `q101_shower` on #mq000_shower). We only ever want
        the first.

        A wrong CName does nothing at all and looks identical to no event, so
        the shipped names are listed in docs/scene-playbook.md and must never be
        guessed.

        No output socket, unlike fire_event: this fires an effect, not a branch.
        """
        node = self._node(section)
        if node['$type'] != 'scnSectionNode':
            raise SystemExit('%s: fire_vfx needs a section, got %s'
                             % (self.name, node['$type']))
        node['events'].append({'HandleId': '@ev', 'Data': {
            '$type': 'scneventsVFXEvent',
            'action': action,
            'duration': 0,
            'effectEntry': {
                '$type': 'scnEffectEntry',
                'effectInstanceId': {
                    '$type': 'scnEffectInstanceId',
                    'effectId': {'$type': 'scnEffectId', 'id': 4294967295},
                    'id': 4294967295,
                },
                'effectName': cname(effect),
            },
            'executionTagFlags': 0,
            'id': {'$type': 'scnSceneEventId',
                   'id': ruid('ev-vfx/%s/%d/%s/%d'
                              % (self.name, section, effect, start_time))},
            'muteSound': 0,
            'nodeRef': noderef(None),
            'performerId': {'$type': 'scnPerformerId', 'id': performer},
            'scalingData': None,
            'sequenceShift': 0,
            'startTime': start_time,
            'type': '0',
        }})

    def fire_event(self, section, target, start_time=0):
        """Fire a terminal quest node from a section at a given time.

        Socket names 0 and 1 are the section's flow and its spare, so event
        sockets start at 2 and count up - sts_hey_gle_04 uses 2 and 3 for its two
        workspots on one section. The name is allocated here rather than passed
        in, because two callers picking the same name is silent in game.
        """
        node = self._node(section)
        if node['$type'] != 'scnSectionNode':
            raise SystemExit('%s: fire_event needs a section, got %s'
                             % (self.name, node['$type']))
        used = {s['stamp']['name'] for s in node['outputSockets']}
        name = 2
        while name in used:
            name += 1
        node['outputSockets'].append(osock(name, 0, [(target, 1)]))
        ev = {'HandleId': '@ev', 'Data': {
            '$type': 'scneventsSocket',
            'duration': 0,
            'executionTagFlags': 0,
            'id': {'$type': 'scnSceneEventId',
                   'id': ruid('ev-sock/%s/%d/%d' % (self.name, section, name))},
            'osockStamp': {'$type': 'scnOutputSocketStamp', 'name': name, 'ordinal': 0},
            'scalingData': None,
            'startTime': start_time,
            'type': '0',
        }}
        # Vanilla keeps its event array in roughly time order and puts a t=0
        # socket first (sts_wat_kab_03 section 4). Events carry explicit
        # startTimes so this is cosmetic, but it costs nothing.
        if start_time == 0:
            node['events'].insert(0, ev)
        else:
            node['events'].append(ev)

    # -- output ------------------------------------------------------------
    def build(self):
        handle = [0]

        def wrap(obj):
            """Give HandleId markers real, unique handle numbers."""
            if isinstance(obj, dict):
                if 'HandleId' in obj and str(obj['HandleId']).startswith('@'):
                    handle[0] += 1
                    return {'HandleId': str(handle[0]), 'Data': wrap(obj['Data'])}
                return {k: wrap(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [wrap(v) for v in obj]
            return obj

        graph = []
        for n in self.nodes:
            handle[0] += 1
            graph.append({'HandleId': str(handle[0]), 'Data': wrap(n)})

        starts = [node_id(e['nodeId']['id']) for e in self.entry_points]
        ends = [node_id(e['nodeId']['id']) for e in self.exit_points]

        handle[0] += 1
        scene_graph = {'HandleId': str(handle[0]), 'Data': {
            '$type': 'scnSceneGraph',
            'endNodes': ends,
            'graph': graph,
            'startNodes': starts,
        }}

        return {
            'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                       'GameVersion': 2310, 'DataType': 'CR2W',
                       'ArchiveFileName': self.name + '.scene'},
            'Data': {
                'Version': 195, 'BuildVersion': 0,
                'RootChunk': {
                    '$type': 'scnSceneResource',
                    'actors': self.actors,
                    'cookingPlatform': 'PLATFORM_PC',
                    'debugSymbols': {'$type': 'scnDebugSymbols',
                                     'performersDebugSymbols': self.performers,
                                     'sceneEventsDebugSymbols': [],
                                     'sceneNodesDebugSymbols': [],
                                     'workspotsDebugSymbols': self.workspot_symbols},
                    'effectDefinitions': [],
                    'effectInstances': [],
                    'entryPoints': self.entry_points,
                    'executionTagEntries': [],
                    'executionTags': [],
                    'exitPoints': self.exit_points,
                    'interruptionScenarios': [],
                    'localMarkers': [],
                    'locStore': {'$type': 'scnlocLocStoreEmbedded',
                                 'vdEntries': self.loc_vd,
                                 'vpEntries': self.loc_vp},
                    'notablePoints': [],
                    'playerActors': self.player_actors,
                    'props': [],
                    'referencePoints': [],
                    'resouresReferences': {
                        '$type': 'scnSRRefCollection',
                        'cinematicAnimNames': [], 'cinematicAnimSets': [],
                        'dynamicAnimNames': [], 'dynamicAnimSets': [],
                        'gameplayAnimNames': [], 'gameplayAnimSets': [],
                        # What scnActorDef.lipsyncAnimSet.id indexes. Vanilla's
                        # entries here name UNCOOKED paths that ship in no
                        # archive, so the shipped game must be resolving lipsync
                        # through the .lipmap instead; ours name real files, so
                        # this may be a live second channel. Both are emitted.
                        'lipsyncAnimSets': [
                            {'$type': 'scnLipsyncAnimSetSRRef',
                             'asyncRefLipsyncAnimSet': resref(p, 'Soft'),
                             'lipsyncAnimSet': resref(None, 'Default')}
                            for p in self.lipsync_sets]},
                    'ridResources': [],
                    'sceneCategoryTag': self.category,
                    'sceneGraph': scene_graph,
                    'sceneSolutionHash': {
                        '$type': 'scnSceneSolutionHash',
                        'sceneSolutionHash': {'$type': 'scnSceneSolutionHashHash',
                                              'sceneSolutionHashDate': ruid('hash/' + self.name)}},
                    'screenplayStore': {'$type': 'scnscreenplayStore',
                                        'lines': self.lines, 'options': self.options},
                    'version': 5,
                    'voInfo': [],
                    'workspotInstances': self.workspot_instances,
                    'workspots': wrap(self.workspots),
                },
                'EmbeddedFiles': [],
            },
        }

    def validate(self):
        """Catch the wiring mistakes that fail silently in game.

        A scene with a branch that goes nowhere does not error - it just stops,
        and the quest phase waits on an exit that never fires. Cheaper to fail
        here than to find it standing in a bar.
        """
        ids = {n['nodeId']['id'] for n in self.nodes}
        for n in self.nodes:
            nid = n['nodeId']['id']
            dests = [d['nodeId']['id'] for s in n['outputSockets']
                     for d in s['destinations']]
            for d in dests:
                if d not in ids:
                    raise SystemExit('%s: node %d points at missing node %d'
                                     % (self.name, nid, d))
            # A workspot quest node is deliberately terminal - it is a side
            # branch off a section's events socket and nothing waits on it.
            # Vanilla's are terminal too (sts_wat_kab_03 nodes 95/97/99/101).
            if n['$type'] not in ('scnEndNode', 'scnQuestNode') and not dests:
                raise SystemExit('%s: node %d (%s) has no way out'
                                 % (self.name, nid, n['$type']))
            # Output sockets are addressed by (name, ordinal) and every shipped
            # scene lists them in that order. fire_workspot appends a name-2
            # socket, so calling it before link_section would emit 2, 0, 1 -
            # which is the kind of mistake that does not error, it just quietly
            # does nothing in game.
            stamps = [(s['stamp']['name'], s['stamp']['ordinal'])
                      for s in n['outputSockets']]
            if stamps != sorted(stamps):
                raise SystemExit('%s: node %d has output sockets out of order: '
                                 '%s (link_section before fire_workspot?)'
                                 % (self.name, nid, stamps))
            if n['$type'] == 'scnChoiceNode':
                # One destination per option, or the hub shows a row that leads
                # nowhere - which reads in game as a dead click.
                if len(dests) != len(n['options']):
                    raise SystemExit('%s: choice node %d has %d options but %d '
                                     'destinations' % (self.name, nid,
                                                       len(n['options']), len(dests)))

        # Screenplay ids are ARRAY INDICES in their high bits. One past the end
        # is not an error the engine survives - it took the game down. Never
        # ship a scene without checking this.
        for n in self.nodes:
            for e in n.get('events', []):
                # Sections also carry scneventsSocket events, which have no
                # screenplay id - they fire an output socket, not a line.
                if 'screenplayLineId' not in e['Data']:
                    continue
                i = e['Data']['screenplayLineId']['id'] >> 8
                if i >= len(self.lines):
                    raise SystemExit('%s: line index %d out of range (%d lines)'
                                     % (self.name, i, len(self.lines)))
            for o in n.get('options', []):
                i = o['screenplayOptionId']['id'] >> 8
                if i >= len(self.options):
                    raise SystemExit('%s: option index %d out of range (%d options)'
                                     % (self.name, i, len(self.options)))

        # Every workspot node must address an instance that exists, and every
        # instance must name a resource that was registered. Both are silent in
        # game: the actor simply never enters the workspot.
        inst_ids = {i['workspotInstanceId']['id'] for i in self.workspot_instances}
        data_ids = set(self._ws_data_ids.values())
        for i in self.workspot_instances:
            if i['dataId']['id'] not in data_ids:
                raise SystemExit('%s: workspot instance %d references unknown '
                                 'resource' % (self.name, i['workspotInstanceId']['id']))
        for n in self.nodes:
            if n['$type'] != 'scnQuestNode':
                continue
            p = n['questNode']['Data'].get('paramsV1', {}).get('Data', {})
            if p.get('$type') != 'scnUseSceneWorkspotParamsV1':
                continue
            if p['workspotInstanceId']['id'] not in inst_ids:
                raise SystemExit('%s: workspot node %d references missing '
                                 'instance %d' % (self.name, n['nodeId']['id'],
                                                  p['workspotInstanceId']['id']))
            uniq = n['questNode']['Data']['entityReference'][
                'dynamicEntityUniqueName']['$value']
            names = {a['spawnDespawnParams']['dynamicEntityUniqueName']['$value']
                     for a in self.actors}
            if uniq not in names:
                raise SystemExit('%s: workspot node %d addresses actor "%s", '
                                 'which this scene does not spawn (have: %s)'
                                 % (self.name, n['nodeId']['id'], uniq,
                                    sorted(names)))

        reached, stack = set(), [e['nodeId']['id'] for e in self.entry_points]
        while stack:
            nid = stack.pop()
            if nid in reached:
                continue
            reached.add(nid)
            for n in self.nodes:
                if n['nodeId']['id'] == nid:
                    stack += [d['nodeId']['id'] for s in n['outputSockets']
                              for d in s['destinations']]
        if ids - reached:
            raise SystemExit('%s: nodes unreachable from any entry point: %s'
                             % (self.name, sorted(ids - reached)))
        for e in self.exit_points:
            if e['nodeId']['id'] not in reached:
                raise SystemExit('%s: exit point %s can never be reached'
                                 % (self.name, e['name']['$value']))

    def write(self):
        self.validate()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, self.name + '.scene.json')
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(self.build(), fh, indent=2)
        print('wrote %s (%d nodes, %d lines, %d options)'
              % (path, len(self.nodes), len(self.lines), len(self.options)))


def write_subtitles(scenes):
    """The resource scene lines actually resolve through.

    One entry per line and per choice option, across all three scenes, keyed by
    the same RUID the scene points at. Mirrors the shape of the reference mods'
    subtitle resources: femaleVariant carries the text, maleVariant is the
    gendered override and is set to the same string so a male V is not left
    reading a blank line.
    """
    entries = []
    seen = set()
    for scene in scenes:
        for ls, text, male in scene.subtitles:
            if ls in seen:
                raise SystemExit('duplicate locstring RUID %s ("%s") - two keys '
                                 'collided, change one' % (ls, text))
            seen.add(ls)
            entries.append({
                '$type': 'localizationPersistenceSubtitleEntry',
                'femaleVariant': text,
                'maleVariant': male,
                'stringId': ls,
            })

    doc = {
        'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                   'GameVersion': 2310, 'DataType': 'CR2W',
                   'ArchiveFileName': 'subtitles.json'},
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'JsonResource',
                'cookingPlatform': 'PLATFORM_PC',
                'root': {'HandleId': '0', 'Data': {
                    '$type': 'localizationPersistenceSubtitleEntries',
                    'entries': entries,
                }},
            },
            'EmbeddedFiles': [],
        },
    }
    os.makedirs(os.path.dirname(SUBTITLE_OUT), exist_ok=True)
    with open(SUBTITLE_OUT, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=2)
    print('wrote %s (%d subtitle entries)' % (SUBTITLE_OUT, len(entries)))

    # ...and the map that points at it, which is what ArchiveXL registers.
    doc = {
        'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                   'GameVersion': 2310, 'DataType': 'CR2W',
                   'ArchiveFileName': 'subtitles.json'},
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'JsonResource',
                'cookingPlatform': 'PLATFORM_PC',
                'root': {'HandleId': '0', 'Data': {
                    '$type': 'localizationPersistenceSubtitleMap',
                    'entries': [{
                        '$type': 'localizationPersistenceSubtitleMapEntry',
                        'subtitleFile': resref(SUBTITLE_DEPOT),
                        # The base map groups its files; "quest" is what every
                        # story subtitle file uses.
                        'subtitleGroup': cname('quest'),
                    }],
                }},
            },
            'EmbeddedFiles': [],
        },
    }
    with open(SUBTITLE_MAP_OUT, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=2)
    print('wrote %s (subtitle map -> %s)' % (SUBTITLE_MAP_OUT, SUBTITLE_DEPOT))

    # Reused vanilla lines are deliberately absent from the resource above -
    # vanilla's own registration supplies their text and audio. Print them so
    # the omission always reads as a decision rather than a hole.
    reused = [(sc.name, k, sid, t) for sc in scenes for (k, sid, t) in sc.reused]
    if reused:
        print('reusing %d recorded vanilla line(s) - no subtitle entry emitted '
              'for these, and none should be:' % len(reused))
        for name, k, sid, t in reused:
            print('  %s/%-4s stringId %s (0x%016x)  "%s"'
                  % (name, k, sid, int(sid), t))


def write_lipmap(scenes):
    r"""The resource that tells the game which lipsync set belongs to which
    actor of which scene.

    `animLipsyncMapping`, merged into `base\localization\en-us.lipmap` by
    ArchiveXL's `localization: lipmaps:` key. THREE PARALLEL ARRAYS, and the
    parallelism is the whole format:

        scenePaths[i]         FNV1a64 of the scene's depot path
        scenePreviewPaths[i]  a second hash, editor-side
        sceneEntries[i]       actorVoiceTags[j] <-> animSets[j]

    scenePaths was proven by computing FNV1a64 of the scene path derived from
    every one of vanilla's 3495 entries: 3495 of 3495 match. scenePreviewPaths
    matched nothing constructible - not `.scenepreview`, not the `versions\gold`
    twin, not a preview subfolder - so it is presumably a hash of an uncooked
    editor path that never shipped. All 3495 are distinct and none equals its
    scenePaths sibling, so ours is derived to be distinct too and nothing more
    is claimed about it.

    Registered per language for the same reason the subtitles and the voiceover
    map are: the mod is English-only, and a moving mouth beats a still one.
    NOTE the anims themselves live in `lang_en_voice.archive`, so a player who
    installed a different voice pack has no such files - the Soft references
    simply do not resolve and the mouths stay shut. Nothing else changes.
    """
    entries, paths, previews = [], [], []
    for scene in scenes:
        if not scene.lipsync_sets:
            continue
        depot = SCENE_DEPOT + scene.name + '.scene'
        paths.append(str(fnv1a64(depot)))
        previews.append(str(fnv1a64(depot + 'preview')))
        entries.append({
            '$type': 'animLipsyncMappingSceneEntry',
            'actorVoiceTags': list(scene.lipsync_voicetags),
            'animSets': [resref(p, 'Soft') for p in scene.lipsync_sets],
        })

    doc = {
        'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                   'GameVersion': 2310, 'DataType': 'CR2W',
                   'ArchiveFileName': LIPMAP_NAME},
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'animLipsyncMapping',
                'cookingPlatform': 'PLATFORM_PC',
                'languageCodeName': cname('en-us'),
                'sceneEntries': entries,
                'scenePaths': paths,
                'scenePreviewPaths': previews,
            },
            'EmbeddedFiles': [],
        },
    }
    os.makedirs(os.path.dirname(LIPMAP_OUT), exist_ok=True)
    with open(LIPMAP_OUT, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=2)
    total = sum(len(e['animSets']) for e in entries)
    print('wrote %s (%d scenes, %d lipsync sets)'
          % (LIPMAP_OUT, len(entries), total))
    if not entries:
        print('  NOTHING IS LIPSYNCED - run tools\\gen_lipsync.py first '
              '(it writes source\\lipsync_picks.json, which this reads)')

