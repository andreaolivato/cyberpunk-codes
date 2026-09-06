r"""The outline every area node and trigger component carries.

ONE WRITER, 2026-09-06. The polygon was being packed in three places that had
each worked it out separately: `community.crowd_null_area_node`, gig 02's
`gen_community.hit_area_node`, and gig 01's retired `gen_security.trigger_area`.
The first two now call this; the third is research that nothing runs and it
keeps its own copy on purpose, because it is the record of a shape that was
built and taken back out (its header says so).

WHAT THE GAME ACTUALLY READS IS THE BUFFER, not the `points` list beside it.
Read off `{cs_crowd_null}` in exterior_-24_16_0_0 and `{cs_tr_vo}` in
exterior_-10_18_0_0 (2026-09-04 and 2026-09-06): a uint32 corner count, then
one Vector4 (x, y, z, 1) per corner in the NODE'S OWN local space, then the
height, all little-endian float32. Four corners come to 72 bytes, which is what
every vanilla one measured.

The `points` list is a class default on some vanilla nodes and the real corners
on others, and changing it changed nothing in play. Pass the real corners
unless copying a node that ships something else.
"""
import base64
import struct

# What `{cs_crowd_null}` ships in its `points` list: a unit square that has
# nothing to do with its actual outline.
UNIT_SQUARE = [(-1, -1), (1, -1), (1, 1), (-1, 1)]


def outline(local, height, handle_id='1', points=None):
    """The `outline` handle, from corners in the node's own local space.

    `local` is [(x, y)] around the node's position. `points` overrides what
    goes in the `points` list when a vanilla node being copied ships something
    other than its own corners there.
    """
    raw = struct.pack('<I', len(local))
    for x, y in local:
        raw += struct.pack('<4f', float(x), float(y), 0.0, 1.0)
    raw += struct.pack('<f', float(height))
    if points is None:
        points = local
    return {'HandleId': handle_id, 'Data': {
        '$type': 'AreaShapeOutline',
        'buffer': base64.b64encode(raw).decode('ascii'),
        'height': float(height),
        'points': [{'$type': 'Vector3', 'X': x, 'Y': y, 'Z': 0}
                   for x, y in points],
    }}
