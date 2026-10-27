r"""Lipsync: the vanilla-animation catalogue, and each line's mouth.

The reusable half of the lipsync pipeline. Two routes live here:

  * OUR OWN MOUTHS, at the end of this file. Each actor of each scene gets a
    set the mod ships: mouths made from the gig's clips by the lipsync
    animator, plus copies of CDPR's animations for whole vanilla lines.
  * CASTING, everything before that. A line points at an animation the game
    already owns, chosen for having about the right length, and the mod ships
    no animation data. The route every gig used until 2026-10-26.

THE CHAIN, established the expensive way and worth not re-deriving:

    a vanilla .anims set
      -> base\localization\<lang>.lipmap   (ArchiveXL key `lipmaps`)
      -> scnActorDef.lipsyncAnimSet
      -> the line's female/maleLipsyncAnimationName

  * `lipmap.scenePaths[i]` is FNV1a64 of the scene's depot path. All 3495
    vanilla entries were verified against that, 3495 of 3495.
  * `sceneEntries[i].actorVoiceTags[j]` is parallel to `animSets[j]`.
  * Vanilla's `resouresReferences.lipsyncAnimSets` name paths that exist in NO
    archive, so the lipmap must be the live channel.
  * Rig mismatch does not matter. Every lipsync anim in the game has the same
    344 joints and 414 tracks, and vanilla plays a player-rigged set on
    arbitrary NPCs.

Casting is by LENGTH only, so the phonemes come from an unrelated line. It
reads as real lip sync at conversational distance; the worst error across gig 01
is 270 ms over two lines.
"""
import json  # noqa: F401
import os
import re  # noqa: F401
import shutil  # noqa: F401
import subprocess  # noqa: F401
import sys  # noqa: F401
import tempfile  # noqa: F401

# --------------------------------------------------------------- per-mod config
CACHE = None
CATALOGUE = None
WK = None
VOICE_ARCHIVE = None
CHARACTERS = None
EXTRA_ARCHIVES = []
LIPMAP_DEPOT = r'base\localization\en-us.lipmap'


def configure(cache, catalogue, wolvenkit, voice_archive, characters,
              lipmap_depot=None, extra_archives=None):
    """cache/catalogue are extraction scratch, so they are gitignored and cheap
    to rebuild. wolvenkit is the CLI, voice_archive the game's lang_*_voice
    archive: both are read, never written.

    characters is the gig's cast, {name: {'actor':..., 'regex':...}}.
    rebuild_cache needs it to know which .anims to pull out of the archive, and
    it is REQUIRED even though only that one path uses it: a machine with a warm
    cache never calls rebuild_cache, so a missing cast is invisible until
    somebody clones the repo.

    extra_archives are more voice archives to read sets from, for a gig that
    reuses Phantom Liberty lines: their animations are in
    `archive/pc/ep1/lang_en_voice.archive` (gotcha 118). Opt-in, because the
    vanilla lipmap read for voicetags covers the base game only, and the
    casting route stops on a set with no voicetag."""
    global CACHE, CATALOGUE, WK, VOICE_ARCHIVE, LIPMAP_DEPOT, CHARACTERS
    global EXTRA_ARCHIVES
    CACHE, CATALOGUE, WK, VOICE_ARCHIVE = cache, catalogue, wolvenkit, voice_archive
    CHARACTERS = characters
    EXTRA_ARCHIVES = list(extra_archives or [])
    if lipmap_depot:
        LIPMAP_DEPOT = lipmap_depot


def _run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('WolvenKit failed: %s\n%s\n%s'
                         % (' '.join(args), r.stdout[-2000:], r.stderr[-2000:]))
    return r.stdout


def rebuild_cache():
    """Extract every candidate .anims plus the vanilla lipmap, and boil them
    down to {depot path -> {rig, voicetag, anims: [[name, seconds], ...]}}.

    The intermediate .anims and their JSON are thrown away: only the catalogue
    survives, which is ~1 MB of names and floats instead of ~20 MB of animation
    buffers we have no licence to keep lying around.
    """
    if not os.path.exists(WK):
        raise SystemExit('WolvenKit CLI not found at %s (set WOLVENKIT_CLI)' % WK)
    if not os.path.exists(VOICE_ARCHIVE):
        raise SystemExit('lang_en_voice.archive not found at %s (set CP2077_DIR)'
                         % VOICE_ARCHIVE)
    os.makedirs(CACHE, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='cc-lipsync-')
    try:
        raw = os.path.join(tmp, 'raw')
        flat = os.path.join(tmp, 'flat')
        out = os.path.join(tmp, 'json')
        for d in (raw, flat, out):
            os.makedirs(d, exist_ok=True)

        # Fail loudly on an unconfigured cast. An empty dict here would give
        # an empty regex, which matches EVERY line in the voice archive: it
        # still lands on the right picks, just after extracting tens of
        # thousands of files. A misconfiguration that only shows up as
        # slowness is worse than one that stops.
        if not CHARACTERS:
            raise SystemExit('questkit.lipsync: no cast. Pass characters= to '
                             'configure() before rebuilding the catalogue.')
        rx = '|'.join('(%s)' % c['regex'] for c in CHARACTERS.values())
        print('extracting lipsync sets...')
        for archive in [VOICE_ARCHIVE] + EXTRA_ARCHIVES:
            _run(WK, 'unbundle', archive, '-o', raw, '-r', rx)
        print('extracting the vanilla lipmap...')
        _run(WK, 'unbundle', VOICE_ARCHIVE, '-o', raw, '-r', r'en-us\.lipmap$')

        # Flatten: the CLI serialises a DIRECTORY in one pass (~0.05 s/file),
        # but writes every output into the same folder, so basenames collide -
        # 216 files all called johnny.anims. Encode the path into the name.
        n = 0
        for root, _dirs, files in os.walk(raw):
            for f in files:
                if not f.endswith('.anims'):
                    continue
                rel = os.path.relpath(os.path.join(root, f), raw)
                shutil.copy(os.path.join(root, f),
                            os.path.join(flat, rel.replace(os.sep, '__')))
                n += 1
        print('serialising %d sets...' % n)
        _run(WK, 'convert', 'serialize', flat, '-o', out)

        # ...and the lipmap, on its own (different folder, no name clash).
        lm_in = os.path.join(raw, LIPMAP_DEPOT)
        lm_out = os.path.join(tmp, 'lipmap_json')
        os.makedirs(lm_out, exist_ok=True)
        _run(WK, 'convert', 'serialize', lm_in, '-o', lm_out)
        voicetags = _voicetags(os.path.join(lm_out, 'en-us.lipmap.json'))

        cat = {}
        for f in sorted(os.listdir(out)):
            if not f.endswith('.anims.json'):
                continue
            with open(os.path.join(out, f), encoding='utf-8') as fh:
                root = json.load(fh)['Data']['RootChunk']
            depot = f[:-len('.json')].replace('__', os.sep).replace(os.sep, '\\')
            cat[depot] = {
                'rig': root['rig']['DepotPath']['$value'],
                'voicetag': voicetags.get(depot),
                'anims': [[e['Data']['animation']['Data']['name']['$value'],
                           e['Data']['animation']['Data']['animBuffer']['Data']['duration']]
                          for e in root['animations']],
            }
        with open(CATALOGUE, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(cat, fh, indent=1)
        total = sum(len(v['anims']) for v in cat.values())
        print('wrote %s (%d sets, %d animations)' % (CATALOGUE, len(cat), total))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _voicetags(lipmap_json):
    """anims depot path -> the voicetag that owns it, out of vanilla's lipmap.

    A set can appear under more than one scene; the voicetag is a property of
    the CHARACTER, so they agree and the first one wins.
    """
    with open(lipmap_json, encoding='utf-8') as fh:
        root = json.load(fh)['Data']['RootChunk']
    tags = {}
    for entry in root['sceneEntries']:
        for tag, s in zip(entry['actorVoiceTags'], entry['animSets']):
            tags.setdefault(s['DepotPath']['$value'], tag)
    return tags


def load_catalogue():
    if not os.path.exists(CATALOGUE):
        rebuild_cache()
    with open(CATALOGUE, encoding='utf-8') as fh:
        return json.load(fh)



# Below this, a line is treated as "as short as it gets" for the relative
# weighting in _score. See the note there.
SHORT_FLOOR_MS = 400


def _score(anims, wanted_ms):
    """Assign each wanted line a DISTINCT animation from one set, greedily,
    longest line first.

    Returns (relative cost, {key: name}, total error in ms) or None. The first
    is what sets are ranked on and the third is what the report prints, because
    milliseconds are what a human can judge.

    Longest first because the long lines are the ones with few candidates - a
    set full of short animations has plenty to spare for a short line, and
    picking for those first strands the long one on whatever is left over.

    Overshoot is penalised 1.5x. A lipsync animation that outlasts its clip
    leaves the mouth moving in silence, which reads as broken; one that runs
    short just stops, which reads as the speaker finishing a sentence.

    SETS ARE RANKED ON RELATIVE ERROR, lines on absolute. The per-line choice
    is the nearest animation either way, because dividing by a length that is
    fixed for that line cannot reorder its candidates. What it changes is which
    SET wins, and that is the decision that was being made badly: summing
    milliseconds says a 400 ms miss on a four second line is as bad as a 400 ms
    miss on an 880 ms one, and it is not. The first is a mouth a fraction out of
    step, the second is a mouth still moving half a second after the words have
    stopped. Playtest 2026-08-23, on the first video holocall in the gig:
    *"really really bad... especially for the shorter sentences"*.

    The floor stops a very short line dominating the whole scene's score. 400 ms
    is about the shortest line this project has, so below it the weighting stops
    getting harsher.
    """
    pool = sorted(anims, key=lambda a: -a[1])
    if len(pool) < len(wanted_ms):
        return None
    used, names, err, rel = set(), {}, 0, 0.0
    for key, ms in sorted(wanted_ms, key=lambda kv: -kv[1]):
        best, best_cost = None, None
        for i, (name, seconds) in enumerate(pool):
            if i in used:
                continue
            delta = seconds * 1000.0 - ms
            cost = delta * 1.5 if delta > 0 else -delta
            if best_cost is None or cost < best_cost:
                best, best_cost = i, cost
        used.add(best)
        names[key] = pool[best][0]
        err += best_cost
        rel += best_cost / max(ms, SHORT_FLOOR_MS)
    return rel, names, err



def _check_actor_names(sets, builders):
    """The picks are keyed by (scene, actorName) and gen_scenes looks them up by
    the same pair. A rename on either side would silently switch lipsync off,
    which is the class of failure this project keeps paying for - so
    prove the names exist before writing the file."""
    # Read `actorName`, which every actor carries, NOT the spawnDespawn unique
    # name. An actor acquired with add_spawnset_actor leaves spawnDespawnParams
    # zeroed - Mama Welles is acquired that way, copying her own vanilla scene -
    # so reading it there yields 'None' and this guard rejects a picks file that
    # is correct. It did exactly that, and the tool could not be re-run at all
    # until 2026-08-16.
    have = {}
    for build in builders:
        scene = build()
        have[scene.name] = {a['actorName'] for a in scene.actors}
    for scene, actors in sets.items():
        if scene not in have:
            raise SystemExit('picks name scene %r, which no builder produces' % scene)
        for actor in actors:
            if actor not in have[scene]:
                raise SystemExit('picks name actor %r in %s, which that scene '
                                 'does not have (it has: %s)'
                                 % (actor, scene, sorted(have[scene])))


def _exact(catalogue, rx, wanted, exact_names):
    """The set that gets the most lines their REAL animation, then the best
    lengths for the rest.

    THE BEST LIPSYNC IS THE ONE VANILLA BAKED FOR THE LINE. A line this gig
    reuses whole plays vanilla's own recording, and vanilla baked a lipsync
    animation for that recording, named `f_<stringId>` inside the anim set of
    the scene it was recorded for. Length matching puts a mouth of the right
    duration on the words; this puts the RIGHT MOUTH on them, visemes and all.

    The constraint that makes it partial: `scnActorDef.lipsyncAnimSet` is ONE
    id, so an actor gets one set for a whole scene. All of their reused lines
    coming from one vanilla scene is the happy case and gives a fully exact
    scene. Where they come from two - our terminal borrows Johnny from two
    different conversations - the best available answer is the set that
    covers the most of them exactly and casts the others by length, which is
    what this returns.

    This used to be impossible in practice and the note that said so was
    right at the time: one reused line among generated ones meant choosing
    between the exact animation for it and decent lengths for the others.
    The recast inverted that. Most lines are reused now.

    TRIMS ARE NOT IN `exact_names` (see the caller): a cut clip is shorter
    than the recording its animation was baked for, so the exact animation
    would outrun it.

    Returns (depot, {key: name}, entry, err, hits) or None.
    """
    if not exact_names:
        return None
    best = None
    for depot, entry in catalogue.items():
        if not rx.search(depot):
            continue
        # THE SET'S OWN SPELLING WINS, not the caller's. The animation name a
        # line ships is looked up case-sensitively at run time, so a name that
        # matches only case-insensitively casts nothing and the mouth does not
        # move. `_exact_names` builds `f_<stringId hex>` and the case of that
        # hex is a format-string choice in each gig's generator, which is not
        # something a pick should depend on. Gig 03 shipped six lines spelled
        # lowercase against an uppercase set and every one of them was silent:
        # playtest, 2026-09-10, "the phrase 'you'll steal it for me' doesn't
        # have lipsync". See gotcha 114.
        have = {n.upper(): (n, sec) for n, sec in entry['anims']}
        names = {k: have[n.upper()][0]
                 for k, n in exact_names.items() if n.upper() in have}
        if not names:
            continue
        spare = [(n, sec) for n, sec in entry['anims']
                 if n.upper() not in {v.upper() for v in names.values()}]
        rest = [(k, ms) for k, ms in wanted if k not in names]
        if len(spare) < len(rest):
            continue
        err, ok = 0.0, True
        cast = {}
        for key, ms in sorted(rest, key=lambda kv: -kv[1]):
            pick_i, pick_cost = None, None
            for i, (_n, sec) in enumerate(spare):
                delta = sec * 1000.0 - ms
                cost = delta * 1.5 if delta > 0 else -delta
                if pick_cost is None or cost < pick_cost:
                    pick_i, pick_cost = i, cost
            if pick_i is None:
                ok = False
                break
            cast[key] = spare.pop(pick_i)[0]
            err += pick_cost
        if not ok:
            continue
        # COUNT THE HITS BEFORE MERGING THE CAST ONES IN. A reused line this
        # set does NOT hold falls through to length casting and lands in
        # `names` too, so counting after the merge counted it as exact: every
        # set then scored the same and the ranking collapsed to length alone,
        # which is the thing this function exists to outrank.
        hits = len(names)
        names.update(cast)
        # Most exact hits wins; ties go to the smaller length error on the
        # lines that had to be cast.
        rank = (-hits, err)
        if best is None or rank < best[0]:
            best = (rank, depot, names, entry, err, hits)
    if best is None:
        return None
    _rank, depot, names, entry, err, hits = best
    return depot, names, entry, err, hits


def pick(catalogue, wanted_lines, verbose=False, exact=None):
    """Cast a vanilla lipsync set for every line that wants a mouth.

    `wanted_lines` is the gig's own list of (character, scene, [(key, ms), ...]).
    The character names index CHARACTERS, so configure() has to have run.

    Two conditions stop the run rather than shipping something subtly wrong: no
    set matching a character's regex at all (usually a cold catalogue), and a
    chosen set whose voicetag the vanilla lipmap does not carry, which would
    make our own lipmap entry unkeyed and silently do nothing.
    """
    sets, lines, report = {}, {}, []
    for char, scene, wanted in wanted_lines:
        actor = CHARACTERS[char]['actor']
        rx = re.compile(CHARACTERS[char]['regex'])
        # EXACT FIRST. See _exact: if one set holds vanilla's own animation
        # for every reused line in this scene, that is not an approximation
        # of the lipsync, it IS the lipsync.
        hit = _exact(catalogue, rx, wanted,
                     (exact or {}).get((char, scene), {}))
        if hit is not None:
            depot, names, entry, err, hits = hit
            if entry['voicetag'] in (None, '0'):
                raise SystemExit('%s: exact set %s has no voicetag' % (char, depot))
            sets.setdefault(scene, {})[actor] = {
                'anims': depot, 'voicetag': entry['voicetag']}
            for key, name in names.items():
                lines['%s/%s' % (scene, key)] = name
            report.append((scene, actor, depot, err, names, wanted))
            if verbose:
                print('%-20s %-12s %d exact, err %5.0f ms  %s'
                      % (scene, actor, hits, err,
                         depot.rsplit(chr(92), 2)[-2]))
            continue
        best = None
        for depot, entry in catalogue.items():
            if not rx.search(depot):
                continue
            scored = _score(entry['anims'], wanted)
            if scored is None:
                continue
            rel, names, err = scored
            if best is None or rel < best[0]:
                best = (rel, depot, names, entry, err)
        if best is None:
            raise SystemExit(
                'no lipsync set found for %s in %s - is the catalogue built? '
                '(%d candidates matched %r)'
                % (char, scene, sum(1 for d in catalogue if rx.search(d)),
                   CHARACTERS[char]['regex']))
        _rel, depot, names, entry, err = best
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


# ------------------------------------------------------------ our own mouths
#
# Everything above casts a vanilla animation by LENGTH. What follows replaces
# that for the lines the gig ships audio for: the lipsync animator makes a
# mouth from the clip and its words, and each actor of each scene gets one
# .anims of the mod's own, holding
#
#   * the animations made from our clips, named f_<line RUID>, and
#   * a copy of CDPR's own animation for every whole vanilla line, under its
#     vanilla name, out of whichever vanilla set holds it.
#
# The second half is what lifts the one-set-per-scene limit `_exact` works
# around: the copies can come from any number of vanilla sets.
#
# Two stores, on purpose:
#
#   mods/<gig>/source/lipsync/<scene>/<actor>.anims   COMMITTED. Only the
#       made animations, so only data made from our own recordings. Remade
#       only when a line's clip or words change (made.json records both), so
#       a build that changed no line needs neither the animator nor its
#       aligner.
#   raw/mod/<mod>/localization/en-us/lipsync/<scene>/<actor>.anims   BUILT,
#       gitignored. The committed animations plus the vanilla copies, so it
#       needs the game installed. CDPR's animation data is never committed.

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def animator():
    """(python, folder) of the lipsync animator.

    LIPSYNC_ANIMATOR names its folder. Otherwise a folder beside this repo
    whose name starts with cyberpunk2077-lipsync-animator, preferring one with
    its own venv. That venv's Python is used when there is one, because that
    is where its dependencies are and it finds the aligner by itself."""
    import glob
    folder = os.environ.get('LIPSYNC_ANIMATOR')
    if not folder:
        found = sorted(glob.glob(os.path.join(os.path.dirname(_REPO),
                                              'cyberpunk2077-lipsync-animator*')),
                       key=lambda f: not os.path.exists(
                           os.path.join(f, '.venv', 'Scripts', 'python.exe')))
        folder = found[0] if found else None
    if not folder or not os.path.isdir(folder):
        raise SystemExit('lipsync animator not found: set LIPSYNC_ANIMATOR to '
                         'its folder')
    py = os.path.join(folder, '.venv', 'Scripts', 'python.exe')
    return (py if os.path.exists(py) else sys.executable), folder


def _animate(sets):
    """One `anims --sets` run. Every `out` is written to a temporary name and
    moved into place only after the whole run succeeds, so a failed run leaves
    the previous files as they were."""
    py, folder = animator()
    tmp = tempfile.mkdtemp(prefix='cc-mouths-')
    sets = list(sets)                   # the caller's list keeps its paths
    try:
        final = []
        for i, s in enumerate(sets):
            final.append(s['out'])
            s = dict(s, out=os.path.join(tmp, '%03d.anims' % i))
            sets[i] = s
        spec = os.path.join(tmp, 'sets.json')
        with open(spec, 'w', encoding='utf-8') as fh:
            json.dump(sets, fh, indent=1)
        cmd = [py, '-m', 'lipsync_animator', 'anims', '--sets', spec]
        for archive in EXTRA_ARCHIVES:
            cmd += ['--archive', archive]
        r = subprocess.run(cmd, cwd=folder, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit('lipsync animator failed:\n%s\n%s'
                             % (r.stdout[-3000:], r.stderr[-3000:]))
        for s, out in zip(sets, final):
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.move(s['out'], out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _sha(path):
    import hashlib
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def mouth_lines(scenes, actors, vomap_json, raw_dir, catalogue):
    """Every line spoken by one of `actors` that can have a mouth, as dicts:

        made   {scene, actor, key, name, audio, text}   a clip the mod ships
        copied {scene, actor, key, name, from}          a whole vanilla line

    A line is MADE when the English voiceover map gives its RUID a clip of
    ours, which is true of the recorded characters and of every cut vanilla
    take. It is COPIED when it is a whole vanilla line, whose animation
    `f_<stringId>` is looked up in the catalogue and copied under the set's
    own spelling (gotcha 114).

    The speaker is matched by actorId, never by position: scene actors and
    V share one id space."""
    with open(vomap_json, encoding='utf-8') as fh:
        root = json.load(fh)['Data']['RootChunk']
    clips = {e['stringId']: (e['femaleResPath']['DepotPath']['$value'],
                             e['maleResPath']['DepotPath']['$value'])
             for e in root['root']['Data']['entries']}
    index = {}
    for depot, entry in sorted(catalogue.items()):
        for n, _sec in entry['anims']:
            index.setdefault(n.upper(), (depot, n))
    out = []
    for scene in scenes:
        names = {a['actorId']['id']: a['actorName'] for a in scene.actors}
        reused = {k: t for k, _sid, t in scene.reused}
        for idx, line in enumerate(scene.lines):
            actor = names.get(line['speaker']['id'])
            if actor not in actors:
                continue
            key = scene.line_key[idx]
            ruid = line['locstringId']['ruid']
            name = 'f_%016X' % int(ruid)
            row = {'scene': scene.name, 'actor': actor, 'key': key}
            if ruid in clips:
                fem, male = clips[ruid]
                # One recording per line is all the scene line can name today:
                # both lipsync names get the same animation.
                if fem != male:
                    raise SystemExit('%s/%s has a different clip for each V; '
                                     'make an m_ animation for it first'
                                     % (scene.name, key))
                row.update(name=name, audio=os.path.join(raw_dir, fem),
                           text=scene.line_text.get(key) or reused.get(key))
                if not os.path.exists(row['audio']):
                    raise SystemExit('%s/%s: clip %s is not in the raw tree; '
                                     'run gen_voice first' % (scene.name, key, fem))
            elif key in reused:
                hit = index.get(name.upper())
                if hit is None:
                    print('  warning: %s/%s reuses %s and no vanilla set in the '
                          'catalogue has its animation; it gets no mouth'
                          % (scene.name, key, name))
                    continue
                row.update({'from': hit[0], 'name': hit[1]})
            else:
                continue                          # not voiced, nothing to move
            out.append(row)
    return out


def build_mouths(lines, mod_dir, mod_depot, voicetags, remake=False):
    """Make what changed, assemble every actor's set, return the picks.

    `mod_depot` is the mod's depot folder (`mod\\negative_balance`).
    `voicetags` is {actorName: voicetag}; any non-zero number works as long
    as it differs between the speakers of one scene.

    Returns (sets, names) in the shape gen_scenes reads from
    lipsync_picks.json."""
    store = os.path.join(mod_dir, 'source', 'lipsync')
    record_path = os.path.join(store, 'made.json')
    record = {}
    if os.path.exists(record_path):
        with open(record_path, encoding='utf-8') as fh:
            record = json.load(fh)

    groups = {}
    for row in lines:
        groups.setdefault((row['scene'], row['actor']), []).append(row)

    # 1. Remake the committed sets whose clips or words changed.
    remade, new_record = [], {}
    for (scene, actor), rows in sorted(groups.items()):
        made = [r for r in rows if 'audio' in r]
        if not made:
            continue
        gid = '%s/%s' % (scene, actor.lower())
        path = os.path.join(store, scene, actor.lower() + '.anims')
        want = {r['name']: {'key': r['key'], 'text': r['text'],
                            'audio': os.path.relpath(r['audio'], mod_dir)
                                       .replace(os.sep, '/'),
                            'audio_sha256': _sha(r['audio'])} for r in made}
        new_record[gid] = want
        have = record.get(gid, {}) if os.path.exists(path) else {}
        stale = [r for r in made if remake or have.get(r['name']) != want[r['name']]]
        if not stale:
            continue
        keep = [n for n in want if n in have and not any(r['name'] == n for r in stale)]
        entry = {'out': path,
                 'lines': [{'name': r['name'], 'audio': r['audio'], 'text': r['text']}
                           for r in stale]}
        if keep:
            entry['copy'] = [{'from': path, 'names': keep}]
        remade.append(entry)
        print('  remaking %s: %d of %d line(s)' % (gid, len(stale), len(made)))
    if remade:
        _animate(remade)
    # Sets nobody wants any more go, so the store is exactly the record.
    for gid in set(record) - set(new_record):
        p = os.path.join(store, *gid.split('/')) + '.anims'
        if os.path.exists(p):
            os.remove(p)
    os.makedirs(store, exist_ok=True)
    with open(record_path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(new_record, fh, indent=1, sort_keys=True)

    # 2. Assemble every actor's set: ours, plus the vanilla copies.
    raw = os.path.join(mod_dir, 'source', 'wkit', 'raw')
    sets, names, build, stamp = {}, {}, [], {}
    for (scene, actor), rows in sorted(groups.items()):
        depot = chr(92).join([mod_depot, 'localization', 'en-us', 'lipsync',
                              scene, actor.lower() + '.anims'])
        out = os.path.join(raw, depot)
        copy = []
        made = [r['name'] for r in rows if 'audio' in r]
        by_set = {}
        for r in rows:
            if 'from' in r:
                by_set.setdefault(r['from'], []).append(r['name'])
        # Only game lines, all in one vanilla set: point at that set, as
        # before the animator. Nothing is copied or shipped for this actor,
        # and each dub's lipmap gets that dub's own set (write_lipmap).
        if not made and len(by_set) == 1:
            sets.setdefault(scene, {})[actor] = {
                'anims': next(iter(by_set)), 'voicetag': str(voicetags[actor])}
            for r in rows:
                names['%s/%s' % (scene, r['key'])] = r['name']
            continue
        copy += [{'from': d, 'names': n} for d, n in sorted(by_set.items())]
        # Vanilla sources first: the set takes the head of the first set it
        # copies from, so a mixed set keeps the character's own.
        if made:
            copy.append({'from': os.path.join(store, scene, actor.lower() + '.anims'),
                         'names': made})
        entry = {'out': out, 'lines': [], 'copy': copy}
        # Rebuild only what changed: the spec plus the committed file's bytes.
        key = json.dumps(['tool-copy-1', copy,
                          _sha(copy[-1]['from']) if made else None])
        stamp[depot] = key
        sets.setdefault(scene, {})[actor] = {'anims': depot,
                                             'voicetag': str(voicetags[actor])}
        for r in rows:
            names['%s/%s' % (scene, r['key'])] = r['name']
        build.append((depot, entry))
    for scene, actors in sets.items():
        tags = [a['voicetag'] for a in actors.values()]
        if len(set(tags)) != len(tags) or '0' in tags:
            raise SystemExit('%s: voicetags must be non-zero and differ: %s'
                             % (scene, actors))

    stamp_path = os.path.join(CACHE, 'mouths_%s.json' % os.path.basename(mod_dir))
    old = {}
    if os.path.exists(stamp_path):
        with open(stamp_path, encoding='utf-8') as fh:
            old = json.load(fh)
    todo = [e for d, e in build
            if remake or old.get(d) != stamp[d] or not os.path.exists(e['out'])]
    if todo:
        print('  assembling %d set(s)' % len(todo))
        _animate(todo)
        _check_copies(todo)
    # Built sets of scenes or actors that no longer speak go too.
    lip_root = os.path.join(raw, mod_depot, 'localization', 'en-us', 'lipsync')
    wanted = {os.path.normcase(os.path.join(raw, d)) for d, _e in build}
    for root, _dirs, files in os.walk(lip_root):
        for f in files:
            p = os.path.join(root, f)
            if f.endswith('.anims') and os.path.normcase(p) not in wanted:
                os.remove(p)
    os.makedirs(CACHE, exist_ok=True)
    with open(stamp_path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(stamp, fh, indent=1, sort_keys=True)
    return sets, names


def _check_copies(entries):
    """Every copied animation must have its source's bytes, exactly.

    The animator's `copy` once re-imported each animation against one fixed
    male head instead of moving it: the keys changed, a frame went, and in
    game every copied line moved the neck, longer on the men outside
    Afterlife and shorter on Yoko (playtest, 2026-10-26). It has been fixed
    since. This check stops the build if that ever comes back."""
    tmp = tempfile.mkdtemp(prefix='cc-check-')
    try:
        files, flat = {}, os.path.join(tmp, 'in')
        os.makedirs(flat)

        def add(path):
            if path not in files:
                files[path] = 'f%03d.anims' % len(files)
                shutil.copy(path, os.path.join(flat, files[path]))

        for e in entries:
            add(e['out'])
            for c in e['copy']:
                src = c['from']
                if not os.path.isabs(src):
                    src = _unbundle_sets([src], os.path.join(CACHE, 'sets'))[src]
                c['_local'] = src
                add(src)
        _run(WK, 'convert', 'serialize', flat, '-o', flat)
        docs = {}
        for path, n in files.items():
            with open(os.path.join(flat, n + '.json'), encoding='utf-8') as fh:
                docs[path] = _anim_bytes(json.load(fh))
        for e in entries:
            got = docs[e['out']]
            for c in e['copy']:
                want = docs[c.pop('_local')]
                for n in c['names']:
                    if got.get(n) != want[n]:
                        raise SystemExit('%s: %s is not byte for byte its source'
                                         % (e['out'], n))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _unbundle_sets(depots, into):
    """Extract vanilla .anims by depot path from the voice archives into
    `into`, keeping the depot path. Returns {depot: local file}."""
    want = sorted(set(depots))
    have = {d: os.path.join(into, d) for d in want}
    missing = [d for d in want if not os.path.exists(have[d])]
    if missing:
        rx = '|'.join('^%s$' % re.escape(d) for d in missing)
        for archive in [VOICE_ARCHIVE] + EXTRA_ARCHIVES:
            _run(WK, 'unbundle', archive, '-o', into, '-r', rx)
    lost = [d for d in want if not os.path.exists(have[d])]
    if lost:
        raise SystemExit('not in any voice archive: %s' % lost)
    return have


def _anim_bytes(doc):
    """{animation name: (its data chunk's bytes, its buffer's other fields)}."""
    root = doc['Data']['RootChunk']
    out = {}
    for e in root['animations']:
        a = e['Data']['animation']['Data']
        b = a['animBuffer']['Data']
        chunk = root['animationDataChunks'][b['dataAddress']['unkIndex']]
        head = {k: v for k, v in b.items()
                if k not in ('dataAddress', 'tempBuffer')}
        out[a['name']['$value']] = (chunk['buffer']['Bytes'],
                                    json.dumps(head, sort_keys=True))
    return out


def voicetag(actor_name):
    """A stable non-zero voicetag per actor name. Our sets are keyed in our
    own lipmap entries only, so the number just has to differ between the
    speakers of a scene, which distinct names guarantee."""
    h = 0xCBF29CE484222325
    for b in ('cc-voicetag:' + actor_name.lower()).encode('utf-8'):
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return (h & 0x7FFFFFFFFFFFFFFF) or 1
