r"""One guarded site: a table of captured posts becomes a shipped community.

`gen_estate_guards.py` and `gen_compound_guards.py` are each a roster and
nothing else. Everything they both do lives here: the checks that a table of
posts is usable, the cross-check against the redscript that looks the entries
up, and writing the three files out.

===========================================================================
WHY THE POSTS ARE CAPTURED AND NOT DERIVED

Neither site has authored guard posts. Both were searched: within 120 m of the
compound the game has five `worldAISpotNode`s, all 50 to 90 m away and belonging
to another quest, and the residence has two.

So both sites used to place guards by asking the navmesh for somewhere walkable
near an anchor, and the navmesh kept giving nearly the same answer. That is
where the huddle came from at both. It is not a bug in the query: sightlines,
cover, who watches the gate and who watches the yard are decisions, and a query
cannot make one.

The posts are walked in game instead, one CAPTURE HERE per post, standing where
the guard belongs and facing the way he should face.

===========================================================================
THE TWO CHECKS THAT EARNED THEIR PLACE

**Two men in one doorway.** The captures are a walk, so two posts a metre apart
are usually a re-capture that was meant to replace the first rather than stand
beside it.

**A post on top of somebody the game already stands there.** `roof01` at the
residence was captured 1.0 m from a base-game sniper, which is not a
coincidence: two sets of people picked the same good spot. It was only caught by
capturing that NPC in game and reading his record back. The cached sectors hold
some of the game's own spots and this checks against them, but the cache is a
subset and the sniper was not in it, so the check reduces the risk and cannot
retire it.

===========================================================================
AND THE ONE THAT IS ABOUT DRIFT, NOT ABOUT PLACES

The entry names exist twice, here and in the redscript that looks them up,
because redscript cannot import Python. A restated list is a list that drifts,
and a lookup naming an entry that does not exist is SILENT: it returns fewer
bodies, which is exactly what a post that has not streamed in yet looks like.
So the generator reads the redscript and refuses to write when the two disagree.
Gotchas 73 and 76.
"""
import io
import json
import math
import os
import re

from questkit import community

# ------------------------------------------------------------------ the pose
#
# ARMS CROSSED, STANDING AROUND. A guard on post, which is what these are.
#
# THE SHELF IS WHAT MATTERS, not the animation. That is gotcha 72's finding: of
# four sit variants at one seat, the only one that took came from `common\` and
# the three from `master\` did not, at either height. This is on the same
# `common\ground\` shelf as the standing idle sixteen bench runs used, so it is
# the proven shelf with a different animation on it rather than a new gamble.
#
# It is also in the game's own data: `generic__stand_ground_arms_crossed__
# stand_around__02` is one of the 64 distinct workspots the cached sectors
# attach to AI spots.
#
# WHAT IT REPLACED, and why: `generic__stand_ground__look_at_products__03`, the
# idle Hoshino stood in before he sat down. It is a shop browser. One man
# waiting on a terrace reads fine in it; a whole detail studying an
# invisible shelf does not.
#
# IF THE POSE DOES NOT TAKE AT ALL, that is survivable here in a way it was not
# for the couch: a community places the body and does not reliably put it into
# the spot's workspot (gotcha 72), and a guard who is simply standing is still a
# guard standing at his post facing the right way. Two alternatives on the same
# shelf if it reads badly: `generic__stand_ground__wait__03` and the
# `look_at_products__03` above.
def _idle(name):
    return community.depot('base', 'workspots', 'common', 'ground',
                           name + '.workspot')


STAND = _idle('generic__stand_ground_arms_crossed__stand_around__02')

# ------------------------------------------------------------ THE OTHER IDLES
#
# A detail where every single man is doing the identical thing reads as a row of
# statues, and playtest asked for a few of them to look less alike without
# becoming more dangerous. A workspot is only what he is DOING; it is not the
# attitude and not the senses, so none of this touches how they fight.
#
# EVERY PATH HERE WAS READ OUT OF THE GAME'S OWN SHIPPED SECTORS, and that is
# not caution for its own sake: a wrong workspot path is SILENT. The actor never
# enters it, and an NPC standing because his workspot failed looks exactly like
# an NPC standing because it worked (gotcha 72). The count after each is how
# many of the cached sectors' AI spots use it.
#
# All from `common\ground\`, which is the shelf that matters: of four sit
# variants tried at one seat, only the `common\` one took and the three
# `master\` ones did not.
IDLES = {
    # DISCIPLINED. An elite detail on duty.
    'arms_crossed': STAND,
    'wait': _idle('generic__stand_ground__wait__03'),
    'think': _idle('generic__stand_ground__think__01'),
    'stand_around': _idle('generic__stand_ground__stand_around__03'),
    # OFF DUTY-ISH. Ordinary security on a long shift, and deliberately not
    # given to the residence's detail: the two sites are meant to read as
    # different tiers, and the records alone used to carry that.
    'smoke': _idle('generic__stand_ground_cigarette__smoke__01'),
    'smoke2': _idle('generic__stand_ground_cigarette__smoke__02'),
    'phone': _idle('generic__stand_ground__phone_talk__03'),
    'coffee': _idle('generic__stand_ground_coffee__drink__01'),
    'inspect': _idle('generic__stand_ground__look_at_products__01'),
}

PHASE = 'default'
PERIOD = 'Day'
APPEARANCE = 'default'

# NO SPAWN SET on either site. That table is the join a SCENE walks to acquire a
# body (gotcha 69), and no scene speaks to a guard.
SPAWNSET = None


def entries(posts, idles=None, routes=None):
    """`posts` is the roster. `idles` maps a post name to a key in IDLES, and
    `routes` maps a post name to a list of other post names it walks between.

    A post named in `routes` becomes ONE guard walking a beat rather than
    several standing still, so the men at the other points on the route are not
    listed separately. See `guard_site.route_posts`.
    """
    idles = idles or {}
    routes = routes or {}
    # THE FULL TABLE, so a leg can be looked up. The legs are dropped from the
    # ROSTER below, not from the map: the beat's owner still has to know where
    # they are.
    by_name = {name: (x, y, z, yaw) for name, _r, x, y, z, yaw in posts}
    legs = route_posts(routes)
    out = []
    for name, record, x, y, z, yaw in posts:
        if name in legs:
            continue
        if name in routes:
            legs = [name] + list(routes[name])
            points = [((by_name[n][0], by_name[n][1], by_name[n][2]),
                       by_name[n][3]) for n in legs]
            out.append(community.Entry(name, record, APPEARANCE, None, None,
                                       IDLES[idles.get(name, 'arms_crossed')],
                                       route=points))
        else:
            out.append(community.Entry(
                name, record, APPEARANCE, (x, y, z), yaw,
                IDLES[idles.get(name, 'arms_crossed')]))
    return out


def route_posts(routes):
    """Every post name that is a LEG of somebody else's beat.

    Those men do not stand there any more, so the roster drops them: the beat's
    owner walks through their spot instead.
    """
    legs = set()
    for owner, rest in (routes or {}).items():
        legs.update(rest)
    return legs


def build(sector, posts, idles=None, routes=None, extras=None,
          area_class=None):
    return community.Community(sector, entries(posts, idles, routes),
                               spawnset=SPAWNSET, phase=PHASE, period=PERIOD,
                               extra=extras, area_class=area_class)


def check_idles(posts, idles):
    """Every name in `idles` has to be a post that exists.

    `entries()` reads the table with `idles.get(name, 'arms_crossed')`, so a key
    naming a post that has been removed is SILENT: the man simply stands with
    his arms crossed and nothing says the line was ignored. Four of the
    compound's thirteen were in that state after the stealth thin cut the roster
    from forty-six to thirty, and nothing reported it.

    Same shape as `check_redscript` below and the same reason (gotcha 76): a
    list restated beside another list is a list that drifts, so the generator
    reads both and refuses to write.
    """
    names = {name for name, _r, _x, _y, _z, _yaw in posts}
    return ['the idle for %s names a post that does not exist' % key
            for key in sorted(idles or {}) if key not in names]


def check_posts(posts, keep_clear=None):
    """Is this table of posts usable? Both checks describe a real way to get it
    wrong, and both have caught one.

    `keep_clear` is (position, radius, why) for somewhere no guard may stand:
    the residence passes the couch Hoshino waits on, because a guard inside the
    space in front of him is a guard in shot during his conversation.
    """
    problems = []
    seen = {}
    for name, _r, x, y, z, _yaw in posts:
        if name in seen:
            problems.append('%s is listed twice' % name)
        seen[name] = (x, y, z)

    names = list(seen)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = seen[names[i]], seen[names[j]]
            gap = math.dist(a, b)
            if gap < 1.5:
                problems.append('%s and %s are %.2f m apart, which is two men '
                                'standing in each other'
                                % (names[i], names[j], gap))

    if keep_clear:
        centre, radius, why = keep_clear
        for name, pos in seen.items():
            gap = math.dist(pos, centre)
            if gap < radius:
                problems.append('%s is %.1f m from %s' % (name, gap, why))
    return problems


def check_stand_down(posts, stand_down):
    """Every post that stands down when the gig is eased has to be a post that
    exists, and none may be named twice.

    The quest phase turns these entries off one node each, right after it turns
    the whole detail on, and a spawn-manager node naming a community entry that
    does not exist is not an error the game reports: a renamed entry of exactly
    this kind loaded without a warning on 2026-08-25 and then crashed the game
    (gotcha 73). So the list is checked here against the roster it thins, and
    the generator refuses to write when the two disagree, which is the same
    guard `check_idles` and `check_redscript` put on their lists (gotcha 76).
    """
    names = [name for name, _r, _x, _y, _z, _yaw in posts]
    problems = ['%s stands down but is not a post here' % key
                for key in stand_down if key not in names]
    seen = set()
    for key in stand_down:
        if key in seen:
            problems.append('%s stands down twice' % key)
        seen.add(key)
    if stand_down and len(stand_down) >= len(names):
        problems.append('every post stands down, which empties the site')
    return problems


def check_against_game(posts, cache_dir, radius=1.5):
    """Is any post standing where the base game already stands somebody?

    Reads the cached sectors for AI spots and population spawners near the
    posts. A hit is not automatically wrong, it is worth a look: the residence's
    `roof01` was exactly this and was dropped.

    Silent when the cache is not there, because it is gitignored and a modder
    reading this repo will not have it. A check that cannot run must not stop a
    build; it just stops being a check.
    """
    if not os.path.isdir(cache_dir):
        return []
    pts = [(n, (x, y, z)) for n, _r, x, y, z, _yaw in posts]
    lo = [min(p[1][i] for p in pts) - 60 for i in range(3)]
    hi = [max(p[1][i] for p in pts) + 60 for i in range(3)]

    spots = []
    for fname in sorted(os.listdir(cache_dir)):
        if not fname.endswith('.streamingsector.json'):
            continue
        try:
            root = json.load(io.open(os.path.join(cache_dir, fname),
                                     encoding='utf-8'))['Data']['RootChunk']
        except Exception:
            continue
        nodes = root.get('nodes', [])
        for inst in root.get('nodeData', {}).get('Data', []):
            idx = inst.get('NodeIndex')
            if idx is None or idx >= len(nodes):
                continue
            kind = nodes[idx]['Data'].get('$type', '')
            if kind not in ('worldAISpotNode', 'worldPopulationSpawnerNode'):
                continue
            p = inst.get('Position', {})
            pos = (p.get('X', 0.0), p.get('Y', 0.0), p.get('Z', 0.0))
            if any(pos[i] < lo[i] or pos[i] > hi[i] for i in range(3)):
                continue
            spots.append((nodes[idx]['Data'].get('debugName', {})
                          .get('$value', '?'), pos))

    notes = []
    for name, pos in pts:
        for dbg, sp in spots:
            gap = math.dist(pos, sp)
            if gap < radius:
                notes.append('%s is %.2f m from the game\'s own %s'
                             % (name, gap, dbg))
    return notes


def check_redscript(posts, reds_path, func, community_ref):
    """The names here and the names in the redscript must be the same list.

    See the header. Gotcha 76, and it is proved to bite: renaming one post makes
    this refuse to write.
    """
    problems = []
    if not os.path.exists(reds_path):
        return ['%s is not there, so the entry names cannot be cross-checked'
                % reds_path]
    text = io.open(reds_path, encoding='utf-8').read()

    marker = 'func %s()' % func
    if marker not in text:
        return ['%s has no %s(), so nothing looks these entries up'
                % (os.path.basename(reds_path), func)]
    body = text.split(marker, 1)[1].split('];', 1)[0]
    in_reds = re.findall(r'n"([A-Za-z0-9_]+)"', body)

    here = [name for name, _r, _x, _y, _z, _yaw in posts]
    if in_reds != here:
        missing = [n for n in here if n not in in_reds]
        extra = [n for n in in_reds if n not in here]
        if missing:
            problems.append('%s is missing: %s' % (func, ', '.join(missing)))
        if extra:
            problems.append('%s names entries that do not exist here: %s'
                            % (func, ', '.join(extra)))
        if not missing and not extra:
            problems.append('%s has the same names in a different order, which '
                            'is harmless but means one of the two lists was '
                            'edited without the other' % func)

    if community_ref not in text:
        problems.append('%s does not name %s' % (os.path.basename(reds_path),
                                                 community_ref))
    return problems


def write(out_dir, sector, posts, reds_path, func, cache_dir=None,
          keep_clear=None, idles=None, routes=None, extras=None,
          area_class=None, stand_down=None):
    """Check everything, then write the three files. Prints what it did.

    `stand_down` is the list of posts the quest phase switches off again when
    the gig is eased (see `gen_questphase.thin_detail`). It changes nothing
    written here: every post is an entry whatever the mode, and the phase is
    what leaves some of them empty.
    """
    com = build(sector, posts, idles, routes, extras, area_class)
    keep = [p for p in posts if p[0] not in route_posts(routes)]
    # The POSITION checks run over every point that will be occupied, beats
    # included. The NAME check runs over the entries, because a leg of a beat is
    # not an entry and the redscript must not name one.
    faults = check_posts(posts, keep_clear)
    faults += check_idles(posts, idles)
    faults += check_redscript(keep, reds_path, func, com.community_ref)
    faults += check_stand_down(keep, stand_down or [])
    if faults:
        for fault in faults:
            print('POSTS: ' + fault)
        raise SystemExit('the posts are not usable; nothing written')

    if cache_dir:
        for note in check_against_game(posts, cache_dir):
            print('LOOK AT THIS: ' + note)

    os.makedirs(out_dir, exist_ok=True)
    for name, doc in com.files():
        path = os.path.join(out_dir, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', path)

    lo, hi = com.streaming_box()
    counts = {}
    for e in com.entries:
        counts[e.record] = counts.get(e.record, 0) + 1
    print()
    print('community  %s' % com.community_ref)
    print('   id      %s' % com.community_id)
    walkers = [e for e in com.entries if e.patrols()]
    print('   %d entries, %d of them walking a beat'
          % (len(com.entries), len(walkers)))
    for e in walkers:
        print('     %-9s %d points' % (e.name, len(e.points)))
    if stand_down:
        print('   %d of them stand down when the gig is eased: %s'
              % (len(stand_down), ', '.join(stand_down)))
    used = {}
    for e in com.entries:
        used[e.workspot.rsplit(chr(92), 1)[-1]] = \
            used.get(e.workspot.rsplit(chr(92), 1)[-1], 0) + 1
    for w in sorted(used):
        print('     %2d  %s' % (used[w], w))
    for record in sorted(counts):
        print('     %2d  %s' % (counts[record], record))
    print('   box     %.0f %.0f %.0f  to  %.0f %.0f %.0f'
          % (lo[0], lo[1], lo[2], hi[0], hi[1], hi[2]))
    print()
    print('add to the .archive.xl streaming blocks:')
    print('    - %s' % com.block_path())
    return com
