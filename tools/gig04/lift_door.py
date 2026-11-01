r"""Lift a working door out of a shipped sector, for the room.

    python tools\gig04\lift_door.py

Writes tools/gig04/door_single.json: the game's own single door
(`single_door.ent`, appearance `doors_single_entropy_c_baremetal`, a plain
interactive door that ships CLOSED), lifted whole from
`exterior_-20_-16_0_0` node 975 with its DoorController state and the
instance flags it was placed with, in the shape of door_node.json (the
double door at the front, lifted the same way on 2026-09-30). gen_room.py
places the copy in the cell's wall. The file is committed so a fresh clone
regenerates the room with nothing installed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), '_anchor_cache', 'base', 'worlds',
                     '03_night_city', '_compiled', 'default')
SECTOR = 'exterior_-20_-16_0_0'
NODE = 975
OUT = os.path.join(HERE, 'door_single.json')


def main():
    p = os.path.join(CACHE, SECTOR + '.streamingsector.json')
    if not os.path.exists(p):
        raise SystemExit('%s is not in the anchor cache' % SECTOR)
    with open(p, encoding='utf-8') as fh:
        rc = json.load(fh)['Data']['RootChunk']
    data = rc['nodes'][NODE]['Data']
    inst = next(i for i in rc['nodeData']['Data'] if i['NodeIndex'] == NODE)
    tmpl = data['entityTemplate']['DepotPath']['$value'].split(chr(92))[-1]
    chunks = [c.get('$type') for c in data['instanceData']['Data']['buffer']['Data']['Chunks']]
    if tmpl != 'single_door.ent' or 'DoorController' not in chunks:
        raise SystemExit('node %d of %s is %s with %s, not the door expected' % (NODE, SECTOR, tmpl, chunks))
    out = {'sector': SECTOR, 'node': NODE, 'instance': inst['NodeIndex'],
           'expectedNodes': len(rc['nodeData']['Data']), 'instanceRecord': inst,
           'data': data}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, indent=1)
    print('wrote %s: %s %s, chunks %s' % (OUT, tmpl, data['appearanceName']['$value'], chunks))


if __name__ == '__main__':
    sys.exit(main())
