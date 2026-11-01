r"""Fixer 01: her body. An entity and an appearance file built from the preset
saved at the mirror, on the NPV recipe.

    python tools\fixer01\gen_npv.py

Writes, under source\wkit\raw:

  mod\fixer01\npv\fixer01.ent.json
  mod\fixer01\npv\fixer01.app.json

WHAT AN NPV IS. "Non-Player V": a face made in the game's own character
creator, turned into an ordinary NPC the game can place and talk through. The
REDmodding wiki's recipe ("NPV - V as custom NPC") starts from an example
WolvenKit project whose two files are V's body assembled as an NPC: an entity
(`.ent`, the ninety-odd gameplay components an NPC needs, none of them
visual) and an appearance file (`.app`, the meshes). Those two files, from
the example project on Nexus (mod 8328, downloaded 2026-09-18), are the seeds
in `npv_seed/`. This generator rewrites the appearance from the preset and
points the entity at it. Nothing else of the example is used.

WHY NO BLENDER, AND WHAT THAT COSTS. The creator's six face-shape sliders
(eyes, eyebrows, nose, mouth, jaw, ears) bend V's head mesh at runtime. An
NPC head does not bend, so the recipe bakes those sliders into a new head
mesh in Blender. The design call (2026-09-18) skips that: she has the base
head's shape, and every other choice, which is a part name rather than a
shape, is honoured. The preset's nose was on its second setting; the design
accepted the default.

WHY THE MESHES ARE THE GAME'S OWN AND NOTHING SHIPS BUT TWO FILES. The
example copies V's meshes into the project so Blender can replace the head.
Compared byte for byte on 2026-09-18, those copies are an older cut of the
same files (the eyebrow mesh carries 369 colour appearances against the
game's 657), so every component below points at the game's current mesh
instead, by its real path. The mod carries her entity and her appearance,
40 KB together, and no mesh.

HOW EACH CHOICE BECAME A COMPONENT. The preset is `LocKey#<hash>:<index>`
lines, the hash being FNV1a64 of a creator option's name. The creator's own
definition (`base\gameplay\gui\fullscreen\main_menu\female_cco.
inkcharcustomization`) turns the index into an appearance definition, and
that definition names a small `.app` under `base\characters\head\
player_base_heads\appearances\` whose one appearance holds the component V
gets for that choice: its morph target (a wrapper naming a base mesh), its
mesh appearance and its chunk mask. The base mesh, the appearance name and
the mask below were read off those files, one per choice, and are written
as plain skinned-mesh components the way the example does (the morph
wrapper exists for the sliders, and there are none).

THE COMPILED BUFFER. Each appearance in the seed carries `compiledData`, a
package mirroring its components. `components` is the master and WolvenKit
regenerates the buffer on write (backlog 10, measured on an entity); the
buffer is dropped here so the converter cannot keep a stale copy of the
example's clothes beside the new list. Unverified for an appearance file
until the first build: the check is to serialise the built `.app` back and
grep its buffer for `t2_041` (ours) and `l1_066` (the example's).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixer01_config import RAW_MOD, DEPOT, FIXER_ID  # noqa: E402

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, 'npv_seed')
OUT = os.path.join(RAW_MOD, 'npv')

B = chr(92)


def depot(*parts):
    r"""A depot path is BUILT, never typed (gotcha 28)."""
    return B.join(parts)


# THE NAMES. `APPEARANCE` is what the character record and the community entry
# ask for (`appearanceName`); `ENTITY_APPEARANCE` is the entry's own name in
# the entity, which is what `defaultAppearance` points at.
APPEARANCE = 'fixer01'
ENTITY_APPEARANCE = FIXER_ID
APP_DEPOT = depot(DEPOT, 'npv', 'fixer01.app')
ENT_DEPOT = depot(DEPOT, 'npv', 'fixer01.ent')

FULL = '9223372036854775807'

HEAD = depot('base', 'characters', 'head', 'player_base_heads',
             'player_female_average', 'h0_000_pwa_c__basehead')
BODY = depot('base', 'characters', 'common', 'player_base_bodies',
             'player_female_average')
GARM = depot('base', 'characters', 'garment', 'player_equipment')


def head(f):
    return depot(HEAD, f)


def body(*p):
    return depot(BODY, *p)


# ---------------------------------------------------------------- the preset
#
# Every entry: the seed component to rewrite (by name), the mesh, the mesh
# appearance and the chunk mask. `None` for a mask keeps the seed's. Read off
# the option appearance files named in the header on 2026-09-18.
SKIN = '06_bl_dark'                      # skin colour 12 of 12
EDIT = {
    # head
    'h0_head': (head('h0_000_pwa_c__basehead.mesh'), SKIN + '_d02', FULL),   # skin type 02
    'he_eyes': (head('he_000_pwa_c__basehead.mesh'), 'gradient_black',
                '18446744073709551614'),
    'ht_teeth': (head('ht_000_pwa_c__basehead.mesh'), 'teeth_001', FULL),
    'heb_eyebrows': (head('heb_000_pwa_c__basehead.mesh'), 'blue_sky__07', FULL),
    # body
    't0_body': (body('t0_000_pwa_base__full.mesh'), SKIN, None),
    'an0__arm_right': (body('arms_hq', 'a0_000_pwa_base_hq__r.mesh'), SKIN, FULL),
    'an0__arm_left': (body('arms_hq', 'a0_000_pwa_base_hq__l.mesh'), SKIN, FULL),
    'an0_nails_right': (body('arms_hq', 'nails', 'a0_000_pwa_base__nails_r.mesh'),
                        'dots_01', FULL),
    'an0_nails_left': (body('arms_hq', 'nails', 'a0_000_pwa_base__nails_l.mesh'),
                       'dots_01', FULL),
    's0_flat_feet': (body('l0_000_pwa_base__cs_flat.mesh'), SKIN, '0'),     # boots
    # make-up, piercings, cyberware
    'hx_makeup_eyes': (head('hx_000_pwa_c__basehead_makeup_eyes_01.mesh'), 'pink_19', FULL),
    'hx_makeup_freckles': (head('hx_000_pwa_c__basehead_makeup_freckles_01.mesh'),
                           'frecles_black_01', FULL),
    'hx_makeup_lips_01': (head('hx_000_pwa_c__basehead_makeup_lips_01.mesh'),
                          'red_03_02', FULL),
    'i1_earring': (head('i1_000_pwa_c__basehead_earring_01.mesh'), 'plastic_pink',
                   '18446744073709549583'),
    # CYBERWARE 11 is the second face-tattoo mesh in its `cyberware_10_dark`
    # appearance; that is what the creator's own definition names.
    'h0_tattoo': (head('hx_000_pwa_c__basehead_tattoo_02.mesh'), 'cyberware_10_dark', FULL),
    'h0x001__personal_slot_decal': (head('hx_000_pwa_c__basehead_personal_slot_dec.mesh'),
                                    'personal_link', FULL),
    # hair: style 14 is a buzz cut
    'hh_hair': (depot('base', 'characters', 'common', 'hair', 'hh_999_ma__buzz_cap',
                      'hh_999_wa__buzz_cap.mesh'), 'blue_sky', FULL),
    # clothes (the design call: edgy, leather, spikes, not Maelstrom)
    'l1_pants': (depot(GARM, 'legs', 'l1_063_pants__leather', 'l1_063_pwa_pants__leather.mesh'),
                 'default', FULL),
    's1_boot': (depot(GARM, 'feet', 's1_056_boot__biker', 's1_056_pwa_boot__biker.mesh'),
                'black_glossy', FULL),
    't1_shirt': (depot(GARM, 'torso', 't1_089_tank__short_torn', 't1_089_pwa_tank__short_torn.mesh'),
                 'black', FULL),
}

# Seed components that become something else: (new name, mesh, appearance, mask).
RENAME = {
    't2_117_wa_vest__ninja_harness': ('t2_jacket', depot(GARM, 'torso', 't2_041_jacket__spiked',
                                                         't2_041_pwa_jacket__spiked.mesh'),
                                      'black', FULL),
}

# The seed's gloves and gun harness go. A spiked choker and gold aviators
# stood in the harness's two slots on the first build and came out on the
# design call (2026-09-18, after the first look at her): no collar, no
# glasses. The aviators' mesh has an appearance the game calls `fixer`, for
# whoever wants it back.
DELETE = {'s0_heeled_feet', 'h0_cyberware_face', 'hh_hair_shadow',
          'g1_014_wa_gloves__ninja_gloves6458',
          'i1_088_wa_full__gun_harness0222', 'i1_088_wa_full__gun_harness_pistol'}

# Components the seed has no slot for: (new name, copy of, mesh, appearance, mask).
ADD = [
    ('he_lashes', 'he_eyes', head('he_000_pwa_c__basehead.mesh'), 'eyelashes__blue_sky',
     '18446744073709551609'),
    ('i1_earring_02', 'i1_earring', head('i1_000_pwa_c__basehead_earring_02.mesh'),
     'plastic_pink', '18446744073709545472'),
    ('i1_earring_03', 'i1_earring', head('i1_000_pwa_c__basehead_earring_03.mesh'),
     'plastic_pink', '18446744073709551612'),
    ('t0_tattoo', 't0_body', body('tattoos', 'tx_000_pwa_base__full_tattoo_04.mesh'), SKIN, FULL),
    ('t0_scars', 't0_body', body('scars', 't0_000_pwa_base__scars.mesh'), 'scar__06_bl_black',
     '18446744073709551601'),
    ('t2_jacket_shadow', 'hh_hair_shadow', depot(GARM, 'torso', 'shadow_meshes',
                                                 't2_pwa_jacket__spiked_shadow.mesh'), 'default', FULL),
    ('s1_boot_shadow', 'hh_hair_shadow', depot(GARM, 'feet', 'shadow_meshes',
                                               's1_pwa_boot__biker_shadow.mesh'), 'default', FULL),
    ('l1_pants_shadow', 'hh_hair_shadow', depot(GARM, 'legs', 'shadow_meshes',
                                                'l1_pwa_pants__basic_shadow.mesh'), 'default', FULL),
]


# A SMALL TOP UNDER THE JACKET (the design call, 2026-09-28): the torn tank
# left her chest bare, so the game's own tank bra goes on under it, in the
# same black, copied from the tank's component. It sits below the chest
# tattoo. `WITH_BRA = False` is the look before this change, kept so it can
# be gone back to; nothing else differs between the two.
WITH_BRA = True
if WITH_BRA:
    ADD.append(('t1_bra', 't1_shirt',
                depot(GARM, 'torso', 't1_057_tank__bra', 't1_057_pwa_tank__bra.mesh'),
                'black', FULL))


def serialize(name):
    """The seed as JSON, through the CLI, cached beside it."""
    src = os.path.join(SEED, name)
    out = src + '.json'
    if not os.path.exists(out):
        if not os.path.exists(CLI):
            raise SystemExit('WolvenKit CLI not found and %s has no JSON beside it' % name)
        subprocess.run([CLI, 'convert', 'serialize', src, '-v', 'Quiet'],
                       capture_output=True, check=True)
    with open(out, encoding='utf-8-sig') as fh:
        return json.load(fh)


def strpath(v):
    return {'$type': 'ResourcePath', '$storage': 'string', '$value': v}


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def set_mesh(comp, mesh, appearance, mask):
    comp['mesh']['DepotPath'] = strpath(mesh)
    comp['meshAppearance'] = cname(appearance)
    if mask is not None:
        comp['chunkMask'] = mask


def collect_handles(obj, out):
    """Every `{HandleId, Data}` definition in a document, by id."""
    if isinstance(obj, dict):
        if 'HandleId' in obj and 'Data' in obj:
            out[str(obj['HandleId'])] = obj['Data']
        for v in obj.values():
            collect_handles(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_handles(v, out)


def inline_missing_handles(obj, defs, defined):
    """Handles are file-wide: the first appearance in the seed DEFINES the
    shared skinning and transform bindings and the later ones only refer to
    them by `HandleRefId`. Keeping one appearance and dropping the others
    leaves references to nothing, which the converter refuses with a bare
    line number. Walk the kept appearance in document order and turn the
    first reference to any dropped definition back into the definition."""
    if isinstance(obj, dict):
        if 'HandleId' in obj:
            defined.add(str(obj['HandleId']))
        if 'HandleRefId' in obj and str(obj['HandleRefId']) not in defined:
            hid = str(obj['HandleRefId'])
            defined.add(hid)
            obj.clear()
            obj['HandleId'] = hid
            obj['Data'] = json.loads(json.dumps(defs[hid]))
            inline_missing_handles(obj['Data'], defs, defined)
            return
        for v in obj.values():
            inline_missing_handles(v, defs, defined)
    elif isinstance(obj, list):
        for v in obj:
            inline_missing_handles(v, defs, defined)


def build_app():
    doc = serialize('female.app')
    rc = doc['Data']['RootChunk']
    defs = {}
    collect_handles(doc, defs)
    seed = None
    for a in rc['appearances']:
        a = a.get('Data', a)
        if a['name']['$value'] == 'business':
            seed = a
    assert seed, 'the seed has no "business" appearance'
    comps = [c.get('Data', c) for c in seed['components']]
    by_name = {c['name']['$value']: c for c in comps}
    for name in list(EDIT) + list(RENAME) + list(DELETE):
        assert name in by_name, 'seed lacks component %s' % name
    for _new, copy_of, *_ in ADD:
        assert copy_of in by_name, 'seed lacks component %s' % copy_of

    out = []
    for c in comps:
        name = c['name']['$value']
        if name in DELETE:
            continue
        if name in EDIT:
            set_mesh(c, *EDIT[name])
        elif name in RENAME:
            new, mesh, app, mask = RENAME[name]
            c['name'] = cname(new)
            set_mesh(c, mesh, app, mask)
        out.append(c)
    for new, copy_of, mesh, app, mask in ADD:
        c = json.loads(json.dumps(by_name[copy_of]))
        c['name'] = cname(new)
        set_mesh(c, mesh, app, mask)
        out.append(c)

    # A COMPONENT LIST ENTRY IS AN INLINE OBJECT, not a {HandleId, Data} handle
    # (scene-playbook, the three traps). The seed wrote them inline already;
    # keep whichever shape it used.
    inline = not isinstance(seed['components'][0].get('Data'), dict)
    seed['components'] = out if inline else [{'HandleId': str(1000 + i), 'Data': c}
                                              for i, c in enumerate(out)]
    seed['name'] = cname(APPEARANCE)
    # THE DEPENDENCY LIST names the meshes so the loader can fetch them ahead:
    # rebuilt from what the components use, so no example mesh is asked for.
    seen, deps = set(), []
    for c in out:
        m = c.get('mesh', {}).get('DepotPath', {}).get('$value')
        if isinstance(m, str) and m and m not in seen:
            seen.add(m)
            deps.append({'DepotPath': strpath(m), 'Flags': 'Soft'})
    seed['resolvedDependencies'] = deps
    seed.pop('compiledData', None)
    rc['appearances'] = [{'HandleId': '1', 'Data': seed}]
    defined = set()
    # Everything above the appearance list is walked first, so a definition
    # that lives there still counts as seen.
    for k, v in rc.items():
        if k != 'appearances':
            inline_missing_handles(v, defs, defined)
    inline_missing_handles(rc['appearances'], defs, defined)
    return doc, len(out)


def build_ent():
    doc = serialize('female.ent')
    rc = doc['Data']['RootChunk']
    rc['appearances'] = [{
        '$type': 'entTemplateAppearance',
        'appearanceName': cname(APPEARANCE),
        'appearanceResource': {'DepotPath': strpath(APP_DEPOT), 'Flags': 'Soft'},
        'name': cname(ENTITY_APPEARANCE),
    }]
    rc['defaultAppearance'] = cname(ENTITY_APPEARANCE)
    # The example's appearance file is named once more, in the dependency
    # list; ours takes its place.
    text = json.dumps(doc)
    old = 'tutorial' + B * 2 + 'npv' + B * 2 + 'your_female_character' + B * 2 + '_your_female_character.app'
    text = text.replace(old, APP_DEPOT.replace(B, B * 2))
    assert 'tutorial' not in text, 'the entity still names the example'
    return json.loads(text)


if __name__ == '__main__':
    # THE SEEDS ARE NOT IN THE REPOSITORY: they are the example project's
    # files (Nexus mod 8328), not ours to publish. Without them the two
    # committed files stand as they are, and the other generators run on.
    if not os.path.isdir(SEED) or not os.listdir(SEED):
        print('npv: no seeds in %s; the committed fixer01.app.json and '
              'fixer01.ent.json are kept. Put the two files of Nexus mod 8328 '
              'and fixer01.preset there to rebuild them.' % SEED)
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    app, n = build_app()
    # THE HEADER NAMES THE FILE ITSELF, not the seed it was read from: the
    # CLI writes the seed's full path on this machine there, and the file
    # ships (the export gate found it, 2026-11-01). The field is a label.
    app['Header']['ArchiveFileName'] = 'fixer01.app'
    with open(os.path.join(OUT, 'fixer01.app.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(app, fh, indent=2)
    ent = build_ent()
    ent['Header']['ArchiveFileName'] = 'fixer01.ent'
    with open(os.path.join(OUT, 'fixer01.ent.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(ent, fh, indent=2)
    print('npv: %s (%d components) and %s' % (APP_DEPOT, n, ENT_DEPOT))
