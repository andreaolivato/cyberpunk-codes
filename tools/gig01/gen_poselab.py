r"""THE POSE LAB'S QUEST PHASE. A dev bench, and it must not reach a release.

===========================================================================
WHY IT EXISTS

The pose and guard questions both live at the North Oak estate, at the far end
of a forty-minute gig, and the quest graph changes with almost every build so a
mid-gig save cannot be reused. Testing either one cost a full playthrough.

This phase switches the community's entries from the dev menu instead, with no
gig running at all. Outside the gig the estate is also EMPTY of the encounter's
own guards, which is what makes the guard comparison clean rather than a
question of which of four identical men you are looking at.

===========================================================================
WHY A QUEST PHASE AND NOT A SCRIPT

A community entry is switched by `questCommunityTemplate_NodeType`, a quest
node. Nothing in redscript switches one, so a bench that wants to switch one
needs a graph, and this is the smallest graph that does it.

===========================================================================
THE SHAPE, AND IT IS THE ONE THE COMMUNITY BENCH ARRIVED AT

One input, then one INDEPENDENT wait per button hanging off it, in parallel. Not
a chain: any order, any subset, and a branch that never fires costs nothing.

**THE OUTPUT NODE IS NOT CONNECTED, AND THAT IS LOAD-BEARING.**
`questOutputNodeDefinition` is `type: Terminating`, and reaching it ends the
phase and takes every armed pause node with it. A bench phase whose whole job is
to sit holding armed waits must never reach its output. That cost a session on
the community bench; `gotchas.md` 68.

**EACH BUTTON FIRES ONCE PER SAVE LOAD.** A quest phase's progress is saved, so
a wait completes once and then sits there. Reload to press it again. `ALL OFF`
is therefore the one to press before switching poses, not a second press of the
previous button.

===========================================================================
REMOVING IT

    del tools\gig01\gen_poselab.py
    del mods\gig-01-negative-balance\source\wkit\raw\mod\negative_balance\quest\gig01_poselab.questphase.json

then take its `quest: phases:` entry out of the `.archive.xl`, set `POSE_LAB`
and `GUARD_TEST` to False in `gen_community.py`, and take the POSE LAB block out
of `source/cet-dev/init.lua`. No shipped generator is touched.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import questkit.questgraph as qg                                    # noqa: E402

# A FRESH BUILDER. `questgraph.b` is a module-level singleton that
# `gen_questphase.py` fills with the gig's own graph, and the helpers reach it
# through the module global at call time, so replacing it here gives this file a
# graph of its own without touching the gig's.
qg.b = qg.Builder()
qg.NID = iter(range(1000))
qg.configure(phase_name='gig01_poselab.questphase')

from questkit.questgraph import (                                   # noqa: E402
    add_input, add_output, add_pause_fact, add_setvar, add_community, add_scene,
)
from questkit.scene import ANCHOR_PLAYER                            # noqa: E402

from gig01_config import REPO, DEPOT                                # noqa: E402

SCENES = DEPOT + chr(92) + 'scenes' + chr(92)
from gen_community import (                                         # noqa: E402
    COMMUNITY_REF, PHASE, ENTRY, SPAWNSET_NAME, GUARD_TEST,
)

OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                   'raw', 'mod', 'negative_balance', 'quest',
                   'gig01_poselab.questphase.json')

# (button fact, entry name, what the tester is looking at)
#
# THE POSE VARIANTS ARE GONE. The lab answered that in one session and the three
# that failed are not kept as controls: three more entries that can be switched
# on by accident, in the same seat, is the confusion this lab existed to remove.
SWITCHES = [
    ('cc_g01_pl_hoshino', ENTRY,
     'Hoshino, sitting: the real entry the gig uses'),
    ('cc_g01_pl_g_default', 'guard_default',
     'guard, record default attitude. Challenges, never attacks'),
    ('cc_g01_pl_g_hostile', 'guard_hostile',
     'guard, made hostile to the player when found'),
    ('cc_g01_pl_g_ranged', 'guard_ranged',
     'guard, a different vanilla record, default attitude'),
]

ALL_ENTRIES = [name for _f, name, _w in SWITCHES]


def branch(source, fact, build, sockets=None):
    """One button: an independent wait off the input, then whatever it does.

    `sockets` is (in, out) for a node whose sockets are not the ordinary
    In/Out: a scene node's are its own entry and exit point names, and getting
    one wrong does not error, the graph simply never continues.
    """
    wait = add_pause_fact(fact, 0, 'Greater')
    qg.b.connect(source, (wait, 'In'))
    prev = (wait, 'Out')
    for nid in build():
        i_sock, o_sock = sockets or ('In', 'Out')
        qg.b.connect(prev, (nid, i_sock))
        prev = (nid, o_sock)


def write_talk_scene():
    """A one-line conversation that ACQUIRES the sitting Hoshino.

    Its own scene rather than a second node for `gig01_hoshino.scene`: a scene
    resource wants ONE node, and two nodes for one scene is what crashed the game
    on load in August.

    Same acquisition as the gig's (`spawnSet`, the community entry, the
    registered spawn-set name), so it tests the thing that matters here: does
    acquisition still work now that he is SITTING, does he stay sitting through
    it, and does he speak.

    The line is a RECORDED VANILLA one, so no subtitle resource is written and
    no `.archive.xl` localization entry changes. That also makes the subtitle
    itself the proof of acquisition: a `visualStyle: regular` line needs a
    speaker the subtitle system can reach, so a line that appears at all is an
    actor that was found.
    """
    from questkit import scene as scn
    scn.configure(
        out_dir=os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source',
                             'wkit', 'raw', 'mod', 'negative_balance', 'scenes'),
        scene_depot=SCENES,
        subtitle_out=NOWHERE, subtitle_map_out=NOWHERE,
        subtitle_depot=NOWHERE, lipmap_out=NOWHERE, lipmap_name='pl.lipmap')
    sc = scn.Scene('gig01_pl_talk', scn.ANCHOR_PLAYER)
    who = sc.add_spawnset_actor('hoshino', ENTRY, SPAWNSET_NAME)
    sc.actors[who]['voicetagId']['id'] = '0'
    # "How's things, V?", a real Nix take. Odd out of Hoshino, and that is the
    # point: the subtitle names its speaker, so it says who was acquired.
    line = sc.add_line(who, "How's things, V?", key='p01',
                       vanilla_sid=0x30b57ed4cf7df000)
    a = sc.start('pl_talk_in')
    b = sc.section([line], lead_ms=2500, tail_ms=1500)
    c = sc.end('pl_talk_out')
    sc.link(a, b)
    sc.link_section(b, c)
    sc.write()


NOWHERE = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                       'raw', 'mod', 'negative_balance', 'scenes',
                       '_poselab_never_written')

if __name__ == '__main__':
    # THE LAB FOLLOWS ITS COMMUNITY. `GUARD_TEST` in `gen_community.py` is the
    # one switch: with it off there are no entries to switch, and a phase full
    # of nodes addressing entries that do not exist is exactly what crashed the
    # game on 2026-08-25 (gotcha 73). Exits clean so `run_all.py` reads it as
    # nothing to do rather than as a failure.
    if not GUARD_TEST:
        print('GUARD_TEST is False in gen_community.py, so the lab is off and '
              'nothing was written. Set it True and re-run to rebuild it.')
        raise SystemExit(0)
    write_talk_scene()
    start = add_input()

    # EVERYTHING THIS PHASE OWNS GOES OFF FIRST, unconditionally, before any
    # button can be pressed.
    #
    # `entryActiveOnStart: 0` is ignored (bench run 14), so all three guards
    # spawn on save load, and all three share ONE post: three bodies inside each
    # other on every load, in a mod that is still being played. The gig phase
    # does the same for Hoshino and for the same reason.
    #
    # It also has to be THIS phase that does it. The gig phase named a lab entry
    # for one build, that entry was later renamed, and the gig went on addressing
    # a community entry that did not exist. A phase switches what it owns.
    prev = (start, 'Out')
    for _f, entry, _w in SWITCHES:
        if entry == ENTRY:
            continue          # Hoshino is the gig phase's, not this one's
        node = add_community('Deactivate', COMMUNITY_REF, entry=entry,
                             phase=PHASE)
        qg.b.connect(prev, (node, 'In'))
        prev = (node, 'Out')
    src = prev

    for fact, entry, _why in SWITCHES:
        # ON is one entry only. A per-entry action leaves the others alone,
        # measured on the community bench, so this cannot disturb whatever else
        # happens to be standing there.
        branch(src, fact, lambda e=entry: [
            add_community('Activate', COMMUNITY_REF, entry=e, phase=PHASE),
            add_setvar('cc_g01_pl_last', SWITCHES.index(
                [s for s in SWITCHES if s[1] == e][0]) + 1),
        ])

    # ALL OFF, and it is the button to press between poses rather than pressing
    # the previous one again: each wait fires ONCE per save load, so a second
    # press of the same button does nothing.
    branch(src, 'cc_g01_pl_off', lambda: [
        add_community('Deactivate', COMMUNITY_REF, entry=e, phase=PHASE)
        for e in ALL_ENTRIES
    ] + [add_setvar('cc_g01_pl_last', 0)])

    # TALK TO HIM, outside the gig. Its own tiny scene rather than a second node
    # for `gig01_hoshino.scene`: a scene resource wants ONE node, and two nodes
    # for one scene is what crashed the game on load in August. This one
    # acquires the same body the same way and says one recorded vanilla line, so
    # it tests exactly what matters here: does acquisition still work now that
    # he is SITTING, and does he stay sitting through it.
    branch(src, 'cc_g01_pl_talk', lambda: [
        add_scene(SCENES + 'gig01_pl_talk.scene', ANCHOR_PLAYER,
                  ['pl_talk_in'], ['pl_talk_out']),
    ], sockets=('pl_talk_in', 'pl_talk_out'))

    # AND THEN PROVOKE HIM, which is what the gig does after the conversation.
    # `cc_g01_hoshino_talked` is the same fact the quest graph sets on the real
    # beat, and `Gig01_Encounter` already reads it: attitude to V hostile,
    # senses on. Pressing it here drives the shipped path rather than a copy of
    # it.
    branch(src, 'cc_g01_pl_provoke', lambda: [
        add_setvar('cc_g01_hoshino_talked', 1),
    ])

    # NOT CONNECTED. See the header: reaching it would end the phase and take
    # every armed wait above with it.
    add_output()

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result = qg.b.build()
    with open(OUT, 'w', encoding='utf-8', newline=chr(10)) as fh:
        json.dump(result, fh, indent=2)
    print('wrote', OUT)
    print('nodes %d, connections %d' % (len(qg.b.nodes), len(qg.b.conns)))
    print()
    print('community %s' % COMMUNITY_REF)
    for fact, entry, why in SWITCHES:
        print('  %-24s %-18s %s' % (fact, entry, why))
    print('  %-24s %-18s %s' % ('cc_g01_pl_off', 'all of them',
                                'switch everything off'))
    print()
    print('add to the .archive.xl quest phases, and TAKE IT OUT AGAIN:')
    print('    - path: mod' + chr(92) + 'negative_balance' + chr(92) + 'quest'
          + chr(92) + 'gig01_poselab.questphase')
    print('      parent: base' + chr(92) + 'quest' + chr(92) + 'cyberpunk2077.quest')
