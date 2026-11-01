r"""The picture Hodan sends with the gig: Ligaya at her stall, as a texture,
a one-part atlas and two icon records.

    python tools\gig04\gen_photo.py

Reads   source\gui\ligaya.png             the photo, committed like a WAV master
Writes  raw\mod\return_ticket\gui\ligaya.xbm            the texture (binary)
        raw\mod\return_ticket\gui\ligaya.inkatlas.json  the atlas, one part
        source\tweaks\photo.yaml                        the two UIIcon records

GIG 03'S TOOL with the names changed (tools/gig03/gen_photo.py): its header
carries the measurements, how a message shows a picture, the UI texture
flags and the atlas shape. The atlas shape file is read from tools/gig03.

THE PICTURE is a playtest screenshot of 2026-10-02, cropped to gig 03's
1000x563 with the conversation icon over her head painted out from the
wall beside it. The design call: "you can use the 2nd screenshot of the
sister as image".

Run by hand when the PNG changes, like gen_voice.py; the xbm it writes is
committed and ships.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gig04_config import SOURCE, RAW_MOD, DEPOT                     # noqa: E402

WK = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
B = chr(92)

PNG = os.path.join(SOURCE, 'gui', 'ligaya.png')
GUI_OUT = os.path.join(RAW_MOD, 'gui')
XBM_OUT = os.path.join(GUI_OUT, 'ligaya.xbm')
ATLAS_OUT = os.path.join(GUI_OUT, 'ligaya.inkatlas.json')
TWEAK_OUT = os.path.join(SOURCE, 'tweaks', 'photo.yaml')

XBM_DEPOT = DEPOT + B + 'gui' + B + 'ligaya.xbm'
ATLAS_DEPOT = DEPOT + B + 'gui' + B + 'ligaya.inkatlas'
PART = 'ligaya'
RECORD = 'UIJournalIcons.cc_g04_ligaya'


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('%s\n%s' % (' '.join(args), r.stdout + r.stderr))
    return r.stdout


def import_texture():
    if not os.path.exists(PNG):
        raise SystemExit('no picture at %s' % PNG)
    tmp = tempfile.mkdtemp(prefix='cc-g04-photo-')
    run([WK, 'import', PNG, '-o', tmp])
    xbm = os.path.join(tmp, 'ligaya.xbm')
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
    here = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gig03')
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
        '# THE PICTURE HODAN SENDS, Ligaya at her stall, as two icon records: the one a message names',
        '# through `imageId`, and its `_full` twin for the enlarged view. Generated',
        '# by tools/gig04/gen_photo.py, which also makes the texture and the atlas',
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
