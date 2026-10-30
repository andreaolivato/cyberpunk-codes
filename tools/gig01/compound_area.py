"""The industrial compound as a drawn area: what "Get clear of the compound"
shades on the minimap, and what the script tests for leaving.

One shape, two consumers, the arrangement gig 02's hit_area.py has. The
corners are read out of `CCGig01Places.InsideCompound` in Gig01_Encounter.reds,
the four walked in playtest on 2026-08-17, so the drawn area and the leaving
test are the same polygon and cannot drift apart. The prism runs from the
script's floor (2.0) to its ceiling (45.0).

`gen_community.py` writes the area as a `worldTriggerAreaNode` in Hoshino's
always-loaded sector, which is what ArchiveXL draws a quest area from on PC
(backlog 39). On console NCR Map Areas carries the same outline
(tools/console/map_areas.json).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REDS = os.path.join(HERE, '..', '..', 'mods', 'gig-01-negative-balance', 'source',
                    'scripts', 'Gig01_Encounter.reds')

AREA_NAME = 'cc_g01_compound_area'
AREA_REF = '$/mod/cc_g01_hoshino/#' + AREA_NAME
FLOOR = 2.0
AREA_HEIGHT = 43.0


def corners():
    """The compound's corners in world X and Y, in the script's order."""
    src = open(REDS, encoding='utf-8').read()
    body = src[src.index('func InsideCompound('):]
    body = body[:body.index('return inside;')]
    xs = [float(v) for v in re.search(r'let xs: array<Float> = \[([^\]]*)\]', body).group(1).split(',')]
    ys = [float(v) for v in re.search(r'let ys: array<Float> = \[([^\]]*)\]', body).group(1).split(',')]
    if len(xs) != len(ys) or len(xs) < 3:
        raise SystemExit('compound_area: InsideCompound no longer has matching corner lists')
    return list(zip(xs, ys))


def position():
    """Where the node sits: the corners' centroid, at the script's floor."""
    cs = corners()
    return (round(sum(x for x, _ in cs) / len(cs), 3),
            round(sum(y for _, y in cs) / len(cs), 3), FLOOR)


if __name__ == '__main__':
    print(position(), corners())
