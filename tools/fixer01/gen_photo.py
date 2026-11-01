r"""The fixer's portrait: a texture, a one-part atlas and two icon records.

    python tools\fixer01\gen_photo.py

Reads   source\gui\portrait.png        her portrait, committed like a WAV master
Writes  raw\mod\fixer01\gui\portrait.xbm            the texture (binary)
        raw\mod\fixer01\gui\portrait.inkatlas.json  the atlas, one part
        source\tweaks\portrait.yaml                    the three UIIcon records

A copy of tools/gig03/gen_photo.py (the picture on Dino's brief), re-pointed;
that file carries the account of the texture flags and the atlas shape. What
is different here is where the picture is DRAWN.

WHERE A FIXER'S FACE IS DRAWN, AND WHY THIS NEEDS A SCRIPT. Three places show
it: the map tooltip on the hands icon, the map tooltip on one of her gigs'
pins, and the gig card in the journal. All three set only a texture PART on
an image widget whose atlas is fixed in the widget file:
`base\gameplay\gui\common\icons\avatars\avatars_tooltips.inkatlas`, a
sheet of 26 faces (the eight fixers and the ripperdocs, 94 by 95 pixels
each on the 1080p sheet, head and shoulders on a light grey ground with a
cyan edge). A part name that is not on that sheet draws nothing, which is
what the first playtest showed with Johnny's journal picture. ArchiveXL
patches `.ent`, `.app` and `.mesh`, not an atlas, so the part cannot be added
to the sheet. Instead the records below name OUR atlas, and
source/scripts/Fixer01_Portrait.reds swaps the widget's atlas to ours when
the part it was just given is hers, and back to the game's sheet otherwise.

THE PICTURE IS A PLACEHOLDER (2026-09-18): a drawn silhouette with her
initials, in the sheet's framing. The real one is a photo-mode shot of her,
cropped to the same framing, saved over source\gui\portrait.png; this
generator does the rest.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fixer01_config import SOURCE, RAW_MOD, DEPOT, FIXER_ID                     # noqa: E402

WK = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
B = chr(92)

PNG = os.path.join(SOURCE, 'gui', 'portrait.png')
GUI_OUT = os.path.join(RAW_MOD, 'gui')
XBM_OUT = os.path.join(GUI_OUT, 'portrait.xbm')
ATLAS_OUT = os.path.join(GUI_OUT, 'portrait.inkatlas.json')
TWEAK_OUT = os.path.join(SOURCE, 'tweaks', 'portrait.yaml')

XBM_DEPOT = DEPOT + B + 'gui' + B + 'portrait.xbm'
ATLAS_DEPOT = DEPOT + B + 'gui' + B + 'portrait.inkatlas'
PART = FIXER_ID
RECORD = 'UIJournalIcons.' + FIXER_ID
# HER FACE IN THE PHONE: the contact list, the message thread and the call
# banner all draw `avatarID` off a `PhoneAvatars.*` UIIcon record through
# `InkImageUtils.RequestSetImage` (`messengerContacts.swift` 59), which
# resolves the record's own atlas, so the same picture serves with no atlas
# swap. The game's own fixers each have one (`PhoneAvatars.Avatar_Dino`,
# two flats: atlasResourcePath, atlasPartName). gen_journal names this.
AVATAR_RECORD = 'PhoneAvatars.Avatar_' + FIXER_ID


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
    xbm = os.path.join(tmp, 'portrait.xbm')
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
        "# THE FIXER'S PORTRAIT, as three icon records: the one her character",
        '# record names as `tooltipAvatar` and her codex entry as `linkImageId`,',
        '# its `_full` twin for the codex page, and her phone avatar, which the',
        '# contact list and the call banner draw. Generated by',
        '# tools/fixer01/gen_photo.py, which also makes the texture and the atlas',
        '# they point at, and whose header says why a script has to point the',
        '# map and gig-card widgets at that atlas (the phone needs no such help).',
        '',
        RECORD + ':',
        '  $type: UIIcon',
        '  atlasResourcePath: ' + ATLAS_DEPOT,
        '  atlasPartName: ' + PART,
        RECORD + '_full:',
        '  $type: UIIcon',
        '  atlasResourcePath: ' + ATLAS_DEPOT,
        '  atlasPartName: ' + PART,
        AVATAR_RECORD + ':',
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
