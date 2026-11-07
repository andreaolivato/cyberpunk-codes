r"""Trauma Team: the crew's vest refitted to V's female body.

    python tools\gig05\gen_vest.py

Writes vest_w.mesh and vest_w_fpp.mesh under mod\trauma_team\outfit, each the game's
own `t2_020_ma_full__armor` with new vertex positions. Nothing else in the mesh changes.

The vest's bones are male V's, position for position, so male V wears the game's mesh.
On the female body the vest stands 10 cm off the chest and 11 cm off the back.

The refit is measured against her jacket, in three steps:

1. Where the game puts the vest on her. A skinned vertex lands at
   sum(weight * her bone * inverse of the vest's bone) * vertex, which already moves
   the shoulders in by 4 cm and the torso up by 3 cm.
2. An even shrink of the plate around her torso. One scale for the whole height keeps
   the plate rigid: following her waist height by height pinches it.
3. Back through step 1, because the mesh keeps the male bones and the game applies
   step 1 again: vertex = inverse(skin matrix) * fitted position.

Materials and appearances stay, because the import writes only the geometry.

Reads vanilla meshes into `tools\_ent_cache\gig05_vest`. The result is not committed:
it is a copy of vanilla data, like the lipsync sets.
"""
import json
import os
import shutil
import struct
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gig05_config as cfg  # noqa: E402
from gen_recruiter import CLI, CACHE, B  # noqa: E402

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
CONTENT = os.path.join(GAME, 'archive', 'pc', 'content')
WORK = os.path.join(CACHE, 'gig05_vest')
OUT = os.path.join(cfg.RAW_MOD, 'outfit')

VEST = 't2_020_ma_full__armor'
VEST_FPP = 't2_020_ma_full__armor_no_shoulder_pads'
JACKET = 't2_106_pwa_jacket__trauma_small'
BODY = 't0_000_pwa_base__full'
JACKET_TORSO = 3                  # the jacket's first three parts are the torso

SHRINK_X, SHRINK_Z = 0.82, 0.76   # the even shrink, across and front to back
PIVOT_Z = 0.03                    # front to back position the shrink works around
FORWARD = -0.004                  # the plate sits this much towards her front
HOLD_BELOW = 1.16                 # below this height the flap hangs straight
PAD_FROM = 0.235                  # further out than this is shoulder pad: moved, not shrunk
PAD_BLEND = 0.03
STRAP_FROM, STRAP_RISE = 1.42, 0.04  # the back straps ease out over her collar
HEIGHTS = np.arange(0.90, 1.66, 0.02)

COMPONENT = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
TYPES = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}


def fetch():
    wanted = (VEST, VEST_FPP, JACKET, BODY)
    if all(os.path.exists(os.path.join(WORK, n + '.glb')) for n in wanted):
        return
    os.makedirs(WORK, exist_ok=True)
    rx = '(%s)\\.mesh$' % '|'.join(wanted)
    subprocess.run([CLI, 'unbundle', CONTENT, '-o', WORK, '-r', rx], capture_output=True, check=True)
    subprocess.run([CLI, 'uncook', CONTENT, '-r', rx, '-o', WORK, '-gp', GAME,
                    '--mesh-export-type', 'MeshOnly', '--mesh-export-lod-filter', '-v', 'Minimal'],
                   capture_output=True, check=True)
    for root, _, files in os.walk(WORK):
        for f in files:
            if root != WORK and f.endswith(('.glb', '.mesh')):
                os.replace(os.path.join(root, f), os.path.join(WORK, f))


class Glb:
    def __init__(self, name):
        with open(os.path.join(WORK, name + '.glb'), 'rb') as fh:
            self.raw = bytearray(fh.read())
        size = struct.unpack('<I', self.raw[12:16])[0]
        self.head = json.loads(self.raw[20:20 + size])
        self.base = 20 + size + 8

    def where(self, i):
        a = self.head['accessors'][i]
        v = self.head['bufferViews'][a['bufferView']]
        return a, self.base + v.get('byteOffset', 0) + a.get('byteOffset', 0), v.get('byteStride')

    def read(self, i):
        a, at, stride = self.where(i)
        kind, n = TYPES[a['componentType']], COMPONENT[a['type']]
        width = np.dtype(kind).itemsize * n
        if stride in (None, width):
            return np.frombuffer(self.raw, kind, a['count'] * n, at).reshape(-1, n).copy()
        return np.stack([np.frombuffer(self.raw, kind, n, at + k * stride)
                         for k in range(a['count'])])

    def write_positions(self, i, values):
        a, at, stride = self.where(i)
        values = values.astype('<f4')
        if stride in (None, 12):
            self.raw[at:at + values.size * 4] = values.tobytes()
        else:
            for k, row in enumerate(values):
                self.raw[at + k * stride:at + k * stride + 12] = row.tobytes()
        a['min'], a['max'] = values.min(0).tolist(), values.max(0).tolist()

    def primitives(self):
        for node in self.head['nodes']:
            if 'mesh' in node:
                yield from self.head['meshes'][node['mesh']]['primitives']

    def bones(self):
        out = {}
        for skin in self.head.get('skins', []):
            matrices = self.read(skin['inverseBindMatrices']).reshape(-1, 4, 4)
            for n, m in zip(skin['joints'], matrices):
                out.setdefault(self.head['nodes'][n]['name'], m.T.copy())
        return out

    def save(self, path):
        size = struct.unpack('<I', self.raw[12:16])[0]
        text = json.dumps(self.head, separators=(',', ':')).encode()
        if len(text) > size:
            raise SystemExit('glb header grew past its room')
        self.raw[20:20 + size] = text.ljust(size)
        with open(path + '.tmp', 'wb') as fh:
            fh.write(self.raw)
        os.replace(path + '.tmp', path)


def skin_matrices(glb, prim, onto):
    bones = glb.head['skins'][0]
    names = [glb.head['nodes'][n]['name'] for n in bones['joints']]
    ours = glb.read(bones['inverseBindMatrices']).reshape(-1, 4, 4)
    move = np.stack([np.linalg.inv(onto[n]) @ m.T if n in onto else np.eye(4)
                     for n, m in zip(names, ours)])
    at = prim['attributes']
    joints = np.hstack([glb.read(at['JOINTS_0']), glb.read(at['JOINTS_1'])]).astype(int)
    weights = np.hstack([glb.read(at['WEIGHTS_0']), glb.read(at['WEIGHTS_1'])]).astype(float)
    weights /= weights.sum(1, keepdims=True)
    out = np.zeros((len(joints), 4, 4))
    for k in range(joints.shape[1]):
        out += weights[:, k, None, None] * move[joints[:, k]]
    return out


def homogeneous(p):
    return np.c_[p, np.ones(len(p))]


def smooth(values, reach=10):
    kernel = np.exp(-np.arange(-2 * reach, 2 * reach + 1) ** 2 / (reach * reach / 2.0))
    kernel /= kernel.sum()
    return np.convolve(np.pad(values, 2 * reach, mode='edge'), kernel, 'valid')


def middle(points):
    out = np.full(len(HEIGHTS), np.nan)
    for i, y in enumerate(HEIGHTS):
        s = points[(abs(points[:, 1] - y) < .03) & (abs(points[:, 0]) < .26), 2]
        if len(s):
            out[i] = (s.min() + s.max()) / 2
    ok = ~np.isnan(out)
    return np.interp(HEIGHTS, HEIGHTS[ok], out[ok])


def field(vest_points, jacket_points):
    shift = middle(jacket_points) - middle(vest_points)
    held = shift[np.searchsorted(HEIGHTS, HOLD_BELOW)]
    shift = smooth(np.where(HEIGHTS < HOLD_BELOW, held, shift)) + FORWARD

    def fit(q):
        y = np.clip(q[:, 1], HEIGHTS[0], HEIGHTS[-1])
        move = np.interp(y, HEIGHTS, shift)
        wide = abs(q[:, 0])
        pad = np.clip((wide - PAD_FROM) / PAD_BLEND, 0, 1)
        pad = pad * pad * (3 - 2 * pad)
        z = (PIVOT_Z + (q[:, 2] - PIVOT_Z) * SHRINK_Z) * (1 - pad) + q[:, 2] * pad + move
        strap = np.clip((q[:, 1] - STRAP_FROM) / .1, 0, 1) * (q[:, 2] > PIVOT_Z)
        z += strap * STRAP_RISE
        x = np.where(wide <= PAD_FROM, wide * SHRINK_X, PAD_FROM * SHRINK_X + wide - PAD_FROM)
        return np.c_[np.sign(q[:, 0]) * x, q[:, 1], z]
    return fit


def refit(name, out_name, her_bones, fit):
    glb = Glb(name)
    for prim in glb.primitives():
        i = prim['attributes']['POSITION']
        now = glb.read(i).astype(float)
        skin = skin_matrices(glb, prim, her_bones)
        placed = np.einsum('nij,nj->ni', skin, homogeneous(now))[:, :3]
        target = homogeneous(fit(placed))
        glb.write_positions(i, np.linalg.solve(skin, target[:, :, None])[:, :3, 0])
    temp = os.path.join(WORK, 'build')
    os.makedirs(temp, exist_ok=True)
    glb.save(os.path.join(temp, out_name + '.glb'))
    shutil.copy(os.path.join(WORK, name + '.mesh'), os.path.join(temp, out_name + '.mesh'))
    subprocess.run([CLI, 'import', os.path.join(temp, out_name + '.glb'), '-k', '-o', temp],
                   capture_output=True, check=True)
    os.makedirs(OUT, exist_ok=True)
    shutil.copy(os.path.join(temp, out_name + '.mesh'), os.path.join(OUT, out_name + '.mesh.tmp'))
    os.replace(os.path.join(OUT, out_name + '.mesh.tmp'), os.path.join(OUT, out_name + '.mesh'))
    print('wrote %s' % os.path.join(OUT, out_name + '.mesh'))


def main():
    fetch()
    jacket, body = Glb(JACKET), Glb(BODY)
    her_bones = {**body.bones(), **jacket.bones()}
    torso = [p for k, p in enumerate(jacket.primitives()) if k < JACKET_TORSO]
    points = np.vstack([jacket.read(p['attributes']['POSITION']) for p in torso]).astype(float)
    below = np.vstack([body.read(p['attributes']['POSITION']) for p in body.primitives()]).astype(float)
    points = np.vstack([points, below[(abs(below[:, 0]) < .2) & (below[:, 1] > .9) & (below[:, 1] < 1.08)]])
    bare = Glb(VEST_FPP)
    placed = [np.einsum('nij,nj->ni', skin_matrices(bare, p, her_bones),
                        homogeneous(bare.read(p['attributes']['POSITION']).astype(float)))[:, :3]
              for p in bare.primitives()]
    fit = field(np.vstack(placed), points)
    refit(VEST, 'vest_w', her_bones, fit)
    refit(VEST_FPP, 'vest_w_fpp', her_bones, fit)


if __name__ == '__main__':
    main()
