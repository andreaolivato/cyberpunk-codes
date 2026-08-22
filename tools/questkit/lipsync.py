r"""Lipsync: the vanilla-animation catalogue, and casting lines into it.

The reusable half of the lipsync pipeline. THE MOD SHIPS NO ANIMATION DATA: the
animation NAME a scene line carries is free-form, so a line simply points at an
animation the game already owns, chosen for having about the right length.

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
LIPMAP_DEPOT = r'base\localization\en-us.lipmap'


def configure(cache, catalogue, wolvenkit, voice_archive, characters,
              lipmap_depot=None):
    """cache/catalogue are extraction scratch, so they are gitignored and cheap
    to rebuild. wolvenkit is the CLI, voice_archive the game's lang_*_voice
    archive: both are read, never written.

    characters is the gig's cast, {name: {'actor':..., 'regex':...}}.
    rebuild_cache needs it to know which .anims to pull out of the archive, and
    it is REQUIRED even though only that one path uses it: a machine with a warm
    cache never calls rebuild_cache, so a missing cast is invisible until
    somebody clones the repo."""
    global CACHE, CATALOGUE, WK, VOICE_ARCHIVE, LIPMAP_DEPOT, CHARACTERS
    CACHE, CATALOGUE, WK, VOICE_ARCHIVE = cache, catalogue, wolvenkit, voice_archive
    CHARACTERS = characters
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
        _run(WK, 'unbundle', VOICE_ARCHIVE, '-o', raw, '-r', rx)
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



def _score(anims, wanted_ms):
    """Assign each wanted line a DISTINCT animation from one set, greedily,
    longest line first; return (total error in ms, [names]) or None.

    Longest first because the long lines are the ones with few candidates - a
    set full of short animations has plenty to spare for a short line, and
    picking for those first strands the long one on whatever is left over.

    Overshoot is penalised 1.5x. A lipsync animation that outlasts its clip
    leaves the mouth moving in silence, which reads as broken; one that runs
    short just stops, which reads as the speaker finishing a sentence.
    """
    pool = sorted(anims, key=lambda a: -a[1])
    if len(pool) < len(wanted_ms):
        return None
    used, names, err = set(), {}, 0
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
    return err, names



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


def pick(catalogue, wanted_lines, verbose=False):
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
        best = None
        for depot, entry in catalogue.items():
            if not rx.search(depot):
                continue
            scored = _score(entry['anims'], wanted)
            if scored is None:
                continue
            err, names = scored
            if best is None or err < best[0]:
                best = (err, depot, names, entry)
        if best is None:
            raise SystemExit(
                'no lipsync set found for %s in %s - is the catalogue built? '
                '(%d candidates matched %r)'
                % (char, scene, sum(1 for d in catalogue if rx.search(d)),
                   CHARACTERS[char]['regex']))
        err, depot, names, entry = best
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
