r"""Write each gig's translation kit: a ready WolvenKit project that a
translator unzips, edits and packs, generated from the build so it never
drifts from what the gig registers.

    python tools\make_translation_kit.py            # all three gigs
    python tools\make_translation_kit.py gig02

Writes `mods/<gig>/translation-kit/`:

    README.md                              the steps, for this gig
    <archive>.zip                          the project below, zipped
    <archive>/<archive>.cpmodproj          the WolvenKit project file
    <archive>/source/raw/mod/<folder>_translation/
        strings.json.json                  every UI string, in English
        lines.json.json                    the invented characters' subtitles,
                                           pre-written as the game's translation
                                           tag with the slot to fill
        subtitles.json.json                the map that names lines.json
    <archive>/source/archive/mod/<folder>_translation/
        strings.json, lines.json, ...     the same, converted to the game's format
                                           with the WolvenKit CLI, so the translator
                                           edits in WolvenKit's own editor and packs
    <archive>/source/resources/<archive>.archive.xl
                                           the manifest, with <lang> to fill in
    optional-voice/vomap.json.json         a voice map for anyone re-recording
                                           the invented characters; apart on
                                           purpose, see its README

`<archive>` is `0_<folder>_translation`: the leading digit makes it sort
before the gig's own archive in the game's mod folder, which is what lets
the translation's subtitles and clips win (gotcha 121). The zip is written
with fixed timestamps, so an unchanged kit is a byte-identical zip and the
repository does not churn.

WHY A KIT. The game's own characters are dubbed by the game in every
language, and their lines need nothing from a translator. What is left is
the text the gig wrote itself (the journal, the messages, the shard, the
terminal) and the invented characters' subtitles, and both resolve through
keys that a second mod can define for another language: ArchiveXL
overwrites a string another mod defined and appends a second subtitle, and
the game takes the first subtitle it meets, so a translation archive named
to load before the gig's wins on all counts (measured 2026-09-19;
docs/scene-playbook.md, "Other languages"). The game reads only its own
binary format from inside an archive, so WolvenKit has to run once per
translation; the kit is the project already laid out for it, files already
converted, with the English text in place, so the translator opens it,
edits and packs and nothing else. The README is the whole guide for that gig.

Run after gen_localization.py and gen_scenes.py of the gig, or through
run_all.py, which calls it last.
"""
import copy
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from questkit.scene import locstring_ruid                             # noqa: E402
from questkit.packs import CLI                                        # noqa: E402
import subprocess

GIGS = {
    'gig01': ('gig-01-negative-balance', 'negative_balance', 'Negative Balance', 'gig01_lines.json',
              'Elena and Hoshino', 'V, Johnny, Mama Welles and Nix',
              ['the journal entry and briefing', "Nix's messages and V's replies",
               'the objectives and map captions', 'the shard', 'the terminal documents',
               'the notices and alerts on screen']),
    'gig02': ('gig-02-dead-ringer', 'dead_ringer', 'Dead Ringer', 'gig02_lines.json',
              'Char and the merc', 'Wakako, V, Johnny and Yoko',
              ['the journal entry and briefing', "Wakako's and Char's messages and V's replies",
               'the objectives and map captions', 'the shard', 'the breach on the relay',
               'the notices and alerts on screen']),
    'gig03': ('gig-03-acceptable-loss', 'acceptable_loss', 'Acceptable Loss', 'gig03_lines.json',
              None, 'Dino, V and Johnny',
              ['the journal entry and briefing', "Dino's messages and V's replies",
               'the objectives and map captions', 'the shard', 'the terminal documents',
               'the notices and alerts on screen']),
}
LANGS = ('it-it, de-de, fr-fr, es-es, es-mx, pl-pl, ru-ru, pt-br, jp-jp, kr-kr, zh-cn, '
         'zh-tw, cz-cz, hu-hu, ar-ar, th-th, tr-tr, ua-ua')
B = chr(92)
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def entries(doc):
    root = doc['Data']['RootChunk']
    return root['root']['Data']['entries'] if 'root' in root else root['entries']


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    os.replace(tmp, path)


def save(doc, path, archive_file):
    doc = copy.deepcopy(doc)
    doc['Header']['ArchiveFileName'] = archive_file
    write_text(path, json.dumps(doc, indent=2, ensure_ascii=False) + '\n')


def kiroshi(english):
    esc = (english.replace('&', '&amp;').replace('"', '&quot;')
                  .replace('<', '&lt;').replace('>', '&gt;'))
    return '<kiroshi l="eng" o="%s" t="%s" b="" a=""/>' % (esc, esc)


def zip_dir(folder, out_zip):
    """Zip a folder with fixed timestamps, sorted, so the same content gives
    the same bytes."""
    tmp = out_zip + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            dirs.sort()
            for d in dirs:
                # keep the empty folders WolvenKit expects (source/archive)
                if not os.listdir(os.path.join(root, d)):
                    rel = os.path.relpath(os.path.join(root, d), os.path.dirname(folder)).replace(os.sep, '/') + '/'
                    info = zipfile.ZipInfo(rel, date_time=ZIP_TIME)
                    info.external_attr = 0o40755 << 16
                    z.writestr(info, b'')
            for name in sorted(files):
                full = os.path.join(root, name)
                rel = os.path.relpath(full, os.path.dirname(folder)).replace(os.sep, '/')
                info = zipfile.ZipInfo(rel, date_time=ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                with open(full, 'rb') as fh:
                    z.writestr(info, fh.read())
    os.replace(tmp, out_zip)


def build(gig):
    mod, folder, title, lines_name, invented, cast, content = GIGS[gig]
    loc = os.path.join(REPO, 'mods', mod, 'source', 'wkit', 'raw', 'mod', folder, 'localization')
    kit = os.path.join(REPO, 'mods', mod, 'translation-kit')
    archive = '0_%s_translation' % folder
    project = os.path.join(kit, archive)
    yours = 'mod' + B + folder + '_translation' + B      # the path inside the translator's archive
    raw = os.path.join(project, 'source', 'raw', 'mod', folder + '_translation')
    if os.path.isdir(kit):
        shutil.rmtree(kit)
    os.makedirs(raw)
    os.makedirs(os.path.join(project, 'source', 'archive'))
    os.makedirs(os.path.join(project, 'source', 'resources'))

    # the project file. WolvenKit names the PACKED ARCHIVE after ModName, not
    # Name (measured 2026-09-19: a ModName of "Negative Balance translation"
    # packed "Negative Balance translation.archive", which sorts after the
    # gig's own), so both carry the archive name.
    write_text(os.path.join(project, archive + '.cpmodproj'),
               '<?xml version="1.0" encoding="utf-8"?>\n'
               '<CP77Mod xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
               'xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
               '  <Name>%s</Name>\n'
               '  <ModName>%s</ModName>\n'
               '  <Author></Author>\n'
               '  <Email></Email>\n'
               '  <Version>1.0.0</Version>\n'
               '</CP77Mod>\n' % (archive, archive))

    # 1. strings: the English file as it is, under the kit's name
    strings = load(os.path.join(loc, 'en-us.json.json'))
    n_strings = len(entries(strings))
    save(strings, os.path.join(raw, 'strings.json.json'), 'strings.json')

    # 2. the invented characters' lines, as the translation tag with English in
    #    both slots: the translator replaces the second (`t`), and keeps the
    #    first, which is what Elena or Char actually says.
    actors = load(os.path.join(HERE, gig, 'translations', '_actors.json'))['lines']
    en_lines = load(os.path.join(loc, lines_name + '.json'))
    by_id = {e['stringId']: e for e in entries(en_lines)}
    kept = []
    for line in actors:
        scene, key = line.split('/')
        e = copy.deepcopy(by_id[str(locstring_ruid(scene, key))])
        e['femaleVariant'] = kiroshi(e['femaleVariant'])
        e['maleVariant'] = kiroshi(e['maleVariant'])
        kept.append(e)
    if kept:
        lines_doc = copy.deepcopy(en_lines)
        entries(lines_doc)[:] = kept
        save(lines_doc, os.path.join(raw, 'lines.json.json'), 'lines.json')
        smap = load(os.path.join(loc, 'subtitles.json.json'))
        for e in entries(smap):
            e['subtitleFile']['DepotPath']['$value'] = yours + 'lines.json'
        save(smap, os.path.join(raw, 'subtitles.json.json'), 'subtitles.json')

    # 3. the manifest, in resources so WolvenKit packs it beside the archive
    xl = ('# Translation of %s. Replace <lang> below with your language\'s code, in\n'
          '# every line it appears on. The codes are: %s.\n'
          'localization:\n'
          '  onscreens:\n'
          '    <lang>:\n'
          '      - %sstrings.json\n') % (title, LANGS, yours)
    if kept:
        xl += ('  subtitles:\n'
               '    <lang>: %ssubtitles.json\n'
               '  # Only if you recorded %s in your language, and only once every\n'
               '  # clip is in place (optional-voice/README.md):\n'
               '  # vomaps:\n'
               '  #   <lang>: %svomap.json\n') % (yours, invented, yours)
    write_text(os.path.join(project, 'source', 'resources', archive + '.archive.xl'), xl)

    # 4. the voice map, apart from the project: registered without its clips
    #    it silences those lines (the translation loads first, and the game
    #    takes the first clip entry it meets)
    if kept:
        vomap = load(os.path.join(loc, 'vomap.json.json'))
        want = {str(locstring_ruid(*line.split('/'))): line for line in actors}
        vo_entries = []
        for e in entries(vomap):
            if e['stringId'] in want:
                e = copy.deepcopy(e)
                stem = want[e['stringId']].replace('/', '__')
                for k in ('femaleResPath', 'maleResPath'):
                    e[k]['DepotPath']['$value'] = yours + 'vo' + B + stem + '.wem'
                vo_entries.append(e)
        vomap_doc = copy.deepcopy(vomap)
        entries(vomap_doc)[:] = vo_entries
        save(vomap_doc, os.path.join(kit, 'optional-voice', 'vomap.json.json'), 'vomap.json')
        write_text(os.path.join(kit, 'optional-voice', 'README.md'),
                   '# Only if you record %s in your language\n\n'
                   'This voice map points each of their lines at a clip you supply. Put the\n'
                   'clips (`.wem`) under `source\\archive\\mod\\%s_translation\\vo\\` in\n'
                   'the project, named as the map says (`%s.wem` and so on). Copy this\n'
                   '`vomap.json.json` next to `strings.json.json` under `raw`, right-click\n'
                   '`raw` and "Convert from JSON", and uncomment the `vomaps:` lines in the\n'
                   'manifest. Do that last, once every clip is in place: a voice map\n'
                   'registered without its clips leaves those lines silent in your\n'
                   'language. Left out, the English recordings play under your subtitles.\n'
                   % (invented, folder, actors[0].replace('/', '__')))

    # 5. the steps, for this gig
    steps = [
        '# Translating %s\n' % title,
        'This guide shows step-by-step instructions on how to translate %s into' % title,
        'one of the officially supported languages of CP2077.',
        '',
        '## What is already translated',
        '',
        'For known characters (%s), we are using the game\'s original' % cast,
        'lines either fully or split. So we also already have all the translations',
        'available.',
        '',
        'All their voices (audio) and subtitles are already translated and shipped',
        'with the mod.',
        '',
        '## What needs to be translated',
        '',
        'Everything that is original to the gig needs to be translated:',
    ] + ['- ' + c for c in content] + ([
        '- the subtitles for the NPCs invented for this gig: %s.' % invented,
        '- (optional) the voice of %s.' % invented,
    ] if kept else []) + [
        '',
        'All these texts require a translation and this guide shows how to create',
        'one, use it for yourself and publish it for other players to use.',
        '',
        'A translation is a mod of its own, which overwrites some files shipped with',
        'the original mod. It contains all the translated texts and subtitles, and',
        'optionally also the voiceovers for the new NPCs.',
        '',
        '## What you need',
        '',
        '- [WolvenKit](https://wiki.redmodding.org/wolvenkit), the modding tool the',
        '  whole community uses. Install it and open it once so it finds the game.',
        '- A copy of the original gig mod installed to test.',
        '',
        'Nothing else.',
        '',
        '## Making the mod',
        '',
        '1. Download [%s.zip](https://github.com/andreaolivato/cyberpunk-codes/raw/main/mods/%s/translation-kit/%s.zip),' % (archive, mod, archive),
        '   unzip it, and double-click the `.cpmodproj` to open the project in',
        '   WolvenKit.',
        '2. In the project explorer, under `archive`, open',
        '   `mod\\%s_translation\\strings.json`. It lists every string. Open an' % folder,
        '   entry and type your translation into `femaleVariant` over the English.',
        '   If `maleVariant` is not empty, translate it too. Never ever change',
        '   `secondaryKey`. It must always stay the same. Save.',
    ]
    if kept:
        steps += [
            '3. Open `lines.json` in the same folder: the subtitles of %s:' % invented,
            '',
            '   ```',
            '   ' + kept[0]['femaleVariant'],
            '   ```',
            '',
            '   Replace ONLY the text inside `t="..."` with your translation and leave',
            '   `o="..."` alone. To show your language only, replace the whole tag with',
            '   plain text. Save.',
            '4. Under `resources`, open `%s.archive.xl` and replace' % archive,
            '   `<lang>` with your language\'s code, on every line it appears on:',
            '   `it-it`, `de-de`, `fr-fr`, `es-es`, `es-mx`, `pl-pl`, `ru-ru`, `pt-br`,',
            '   `jp-jp`, `kr-kr`, `zh-cn`, `zh-tw`, `cz-cz`, `hu-hu`, `ar-ar`, `th-th`,',
            '   `tr-tr`, `ua-ua`. Save.',
            '5. When you\'re all done, click "Install mod" to send it to your game. Then',
            '   start the game and test that your translations are correctly shown.',
            '6. When the test is successful, click "Create zip" to produce the archive',
            '   you\'ll upload on Nexus Mods, as a translation of the gig.',
        ]
    else:
        steps += [
            '3. Under `resources`, open `%s.archive.xl` and replace' % archive,
            '   `<lang>` with your language\'s code, on every line it appears on:',
            '   `it-it`, `de-de`, `fr-fr`, `es-es`, `es-mx`, `pl-pl`, `ru-ru`, `pt-br`,',
            '   `jp-jp`, `kr-kr`, `zh-cn`, `zh-tw`, `cz-cz`, `hu-hu`, `ar-ar`, `th-th`,',
            '   `tr-tr`, `ua-ua`. Save.',
            '4. When you\'re all done, click "Install mod" to send it to your game. Then',
            '   start the game and test that your translations are correctly shown.',
            '5. When the test is successful, click "Create zip" to produce the archive',
            '   you\'ll upload on Nexus Mods, as a translation of the gig.',
        ]
    steps += [
        '',
        'Keep the archive name and folder structure as they are. Don\'t change',
        'anything apart from what you see above.',
        '',
    ]
    if kept:
        steps += [
            '## Recording %s' % invented,
            '',
            'If you are a voice actor, %s can also be voiced in your' % invented,
            'language. Record each line in `lines.json` and convert the takes to the',
            '`.wem` format (read `BUILDING.md` or "Audio toolchain" to learn how).',
            '',
            'Once you have all your .wem files, copy them under',
            '`source\\archive\\mod\\%s_translation\\vo\\` with the names defined in' % folder,
            '`vomap.json` (e.g. `%s.wem`). Then copy' % actors[0].replace('/', '__'),
            '`optional-voice/vomap.json.json` from the kit into the matching folder under',
            '`raw`, right-click `raw` and "Convert from JSON", and uncomment the',
            '`vomaps:` lines in the manifest.',
            '',
        ]
    steps += [
        '## Publishing',
        '',
        'Publish it on Nexus Mods as a translation of the gig. When you upload the',
        '.zip it asks if your mod is a translation of another mod. Just select that',
        'and then your language.',
        '',
        'Say in your description which gig version you translated.',
        '',
        '## When the gig updates',
        '',
        'I try not to change texts when I release a new version, but in case I do,',
        'the translation kit is regenerated with every build, so diff the new',
        '`strings.json.json` against the one you translated from.',
        '',
    ]
    write_text(os.path.join(kit, 'README.md'), '\n'.join(steps))

    # 6. the game files themselves, converted from the text files, so that a
    #    translator can edit in WolvenKit's own editor and never convert.
    #    The text files stay for anyone who prefers a text editor.
    if os.path.exists(CLI):
        r = subprocess.run([CLI, 'convert', 'deserialize', raw, '-w', '*.json'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit('WolvenKit CLI failed to convert the kit: ' + (r.stderr or r.stdout)[-800:])
        adir = os.path.join(project, 'source', 'archive', 'mod', folder + '_translation')
        os.makedirs(adir, exist_ok=True)
        for name in os.listdir(raw):
            if name.endswith('.json.json'):
                built = os.path.join(raw, name[:-5])
                if not os.path.exists(built):
                    raise SystemExit('conversion produced nothing for ' + name)
                os.replace(built, os.path.join(adir, name[:-5]))
    else:
        print('  WolvenKit CLI not found; the kit ships the text files only')

    zip_dir(project, os.path.join(kit, archive + '.zip'))
    print('%s: kit written to %s (%d strings, %d invented-character lines)'
          % (gig, kit, n_strings, len(kept)))


if __name__ == '__main__':
    for gig in (sys.argv[1:] or sorted(GIGS)):
        build(gig)
