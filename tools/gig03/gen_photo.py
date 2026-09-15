r"""The picture Dino sends: a texture, a one-part atlas and two icon records.

    python tools\gig03\gen_photo.py

Reads   source\gui\site.png            the photo, committed like a WAV master
Writes  raw\mod\acceptable_loss\gui\site.xbm            the texture (binary)
        raw\mod\acceptable_loss\gui\site.inkatlas.json  the atlas, one part
        source\tweaks\photo.yaml                        the two UIIcon records

HOW A MESSAGE SHOWS A PICTURE. `gameJournalPhoneMessage.imageId` names a
`UIIcon` record, and a UIIcon is an atlas path plus a part name. The shipped
journal uses it two ways, read off `cooked_journal.journal` on 2026-09-11:

  * a message with `imageId` and no attachment shows the picture in the thread
    (Takemura's six photos in q112, 126 messages in all);
  * a fixer's brief with an attachment AND an `imageId` shows the picture as
    the thumbnail on the gig card (`UIJournalIcons.STS_Lucy_thackery` on
    Regina's own sts_wat_kab_02 brief, and Dino's carry one the same way).

Every one of them comes as a pair, `<name>` and `<name>_full`, the second for
the enlarged view when the picture is tapped. Both are written here and both
point at the same part; vanilla's `_full` points at a bigger crop of the same
atlas, which one photo does not need.

THE TEXTURE. `WolvenKit.CLI import` turns a PNG into an xbm with the settings
of a world texture: `TEXG_Generic_Color`, gamma off, streamable. The game's own
icon textures (`sts_assets0.xbm`, read on 2026-09-11) are `TEXG_Generic_UI`,
gamma ON, not streamable. Gamma is the one that shows: a UI texture read as
linear is dark and flat. So the import is serialized, those flags are set, and
it is deserialized again. The pixel data is untouched.

THE ATLAS. Copied in shape from `sts_assets0.inkatlas`: three texture slots,
of which only the first is used, one `inkTextureAtlasMapper` part covering the
whole texture in UV space (0,0 to 1,1), `isSingleTextureMode` on. Slot 1 in
vanilla carries a 1080p twin; ours leaves it empty, as the wiki says a mod may.

THE PNG IS THE SOURCE and is committed. The xbm is a build product but ships
in the archive, so it is committed too, the same rule as the .wem files.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gig03_config import SOURCE, RAW_MOD, DEPOT                     # noqa: E402

WK = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
B = chr(92)

PNG = os.path.join(SOURCE, 'gui', 'site.png')
GUI_OUT = os.path.join(RAW_MOD, 'gui')
XBM_OUT = os.path.join(GUI_OUT, 'site.xbm')
ATLAS_OUT = os.path.join(GUI_OUT, 'site.inkatlas.json')
TWEAK_OUT = os.path.join(SOURCE, 'tweaks', 'photo.yaml')

XBM_DEPOT = DEPOT + B + 'gui' + B + 'site.xbm'
ATLAS_DEPOT = DEPOT + B + 'gui' + B + 'site.inkatlas'
PART = 'site'
RECORD = 'UIJournalIcons.cc_g03_site'


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('%s\n%s' % (' '.join(args), r.stdout + r.stderr))
    return r.stdout


def import_texture():
    if not os.path.exists(PNG):
        raise SystemExit('no picture at %s' % PNG)
    tmp = tempfile.mkdtemp(prefix='cc-photo-')
    run([WK, 'import', PNG, '-o', tmp])
    xbm = os.path.join(tmp, 'site.xbm')
    # Serialize, set the UI flags, deserialize.
    run([WK, 'convert', 'serialize', xbm, '-o', tmp])
    jpath = xbm + '.json'
    with open(jpath, encoding='utf-8') as fh:
        doc = json.load(fh)
    setup = doc['Data']['RootChunk']['setup']
    setup['group'] = 'TEXG_Generic_UI'
    setup['isGamma'] = 1
    setup['isStreamable'] = 0
    setup['allowTextureDowngrade'] = 1
    with open(jpath, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=1)
    os.remove(xbm)
    run([WK, 'convert', 'deserialize', jpath, '-o', tmp])
    if not os.path.exists(xbm):
        raise SystemExit('deserialize produced no xbm in %s' % tmp)
    os.makedirs(GUI_OUT, exist_ok=True)
    shutil.copyfile(xbm, XBM_OUT)
    w, h = doc['Data']['RootChunk']['width'], doc['Data']['RootChunk']['height']
    shutil.rmtree(tmp, ignore_errors=True)
    print('wrote %s (%dx%d)' % (XBM_OUT, w, h))


def resref(path):
    return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                          '$value': path}, 'Flags': 'Soft'}


def part(name):
    return {'$type': 'inkTextureAtlasMapper',
            'clippingRectInPixels': {'$type': 'Rect', 'bottom': 0, 'left': 0,
                                     'right': 0, 'top': 0},
            'clippingRectInUVCoords': {'$type': 'RectF', 'Bottom': 1.0,
                                       'Left': 0.0, 'Right': 1.0, 'Top': 0.0},
            'partName': {'$type': 'CName', '$storage': 'string',
                         '$value': name}}


def write_atlas():
    """Built from `vanilla_inkatlas_shape.json`, which is `sts_assets0.inkatlas`
    with its parts and paths stripped: the SHAPE of a game atlas and nothing of
    the game's in it. A hand-built one failed to deserialize on the dynamic
    slot, which is `inkDynamicTextureSlot` and not a third `inkTextureSlot`."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'vanilla_inkatlas_shape.json'),
              encoding='utf-8') as fh:
        doc = json.load(fh)
    root = doc['Data']['RootChunk']
    # `slots` is a fixed array of three, serialized as {"Elements": [...]}.
    first = root['slots']['Elements'][0]
    first['texture'] = resref(XBM_DEPOT)
    first['parts'] = [part(PART)]
    with open(ATLAS_OUT, 'w', encoding='utf-8', newline=chr(10)) as fh:
        json.dump(doc, fh, indent=2)
    print('wrote', ATLAS_OUT)


def write_tweak():
    lines = [
        '# THE PICTURE DINO SENDS, as two icon records: the one a message names',
        '# through `imageId`, and its `_full` twin for the enlarged view. Generated',
        '# by tools/gig03/gen_photo.py, which also makes the texture and the atlas',
        '# they point at.',
        '',
        RECORD + ':',
        '  $type: UIIcon',
        '  atlasResourcePath: ' + ATLAS_DEPOT,
        '  atlasPartName: ' + PART,
        RECORD + '_full:',
        '  $type: UIIcon',
        '  atlasResourcePath: ' + ATLAS_DEPOT,
        '  atlasPartName: ' + PART,
        '',
    ]
    with open(TWEAK_OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(chr(10).join(lines))
    print('wrote', TWEAK_OUT)


if __name__ == '__main__':
    import_texture()
    write_atlas()
    write_tweak()
