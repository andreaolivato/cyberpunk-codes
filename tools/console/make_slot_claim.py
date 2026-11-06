"""Write the two files that claim a slot of NCR Quest & Voice Slots, as
WolvenKit JSON, for a quest mod without scripts.

    python tools/console/make_slot_claim.py 17 [-o <folder>]

Writes, under <folder> (default: the current folder), in depot layout:

    mod/ncr_slots/claims/slot_017.streamingsector.json
    mod/ncr_slots/claims/slot_017.streamingblock.json

The sector holds one marker node whose NodeRef is the slot's object,
`$/03_night_city/#ncr_slots/#ncr_slot_017`, which is what the slot waits for
(build_slots.py). The block loads that sector everywhere: category
AlwaysLoaded and a streaming box with no bounds. Convert both with
`WolvenKit.CLI convert deserialize`, pack them with the mod, and name the
block under `streaming: blocks:` in the mod's `.archive.xl`. A mod that
already ships a block can add the descriptor to its own block instead:
several blocks in one mod crashed the game's own loader on PC 2.5
(docs/console-research.md).
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_slots  # noqa: E402

BIG = 3.40282347e+38


def header(name):
    return {"WolvenKitVersion": "8.20.0", "WKitJsonVersion": "0.0.9", "GameVersion": 2500,
            "DataType": "CR2W", "ArchiveFileName": name}


def vec4(x, y, z, w=0):
    return {"$type": "Vector4", "W": w, "X": x, "Y": y, "Z": z}


def sector(k):
    return marker_sector(f"{build_slots.slot(k)}.streamingsector",
                         [(build_slots.slot_object(k), f"ncr_{build_slots.slot(k)}", (0, 0, 0))])


def marker_sector(file_name, items):
    """An always-loaded sector of unrotated marker nodes, one per
    (NodeRef, debug name, position). Also what a gig's console build uses
    for its own markers (a scene's location, a map pin's anchor)."""
    nodes, refs, data = [], [], []
    for i, (ref_value, debug, (x, y, z)) in enumerate(items):
        ref = {"$type": "NodeRef", "$storage": "string", "$value": ref_value}
        nodes.append({"HandleId": str(2 * i), "Data": {
            "$type": "worldStaticMarkerNode",
            "data": {"HandleId": str(2 * i + 1), "Data": {"$type": "scnSceneMarker", "markers": [],
                                                          "workspotMarkers": []}},
            "debugName": {"$type": "CName", "$storage": "string", "$value": debug},
            "isEnabled": 1, "isHostOnly": 0, "isVisibleInGame": 1, "proxyScale": None,
            "sourcePrefabHash": "0", "tag": "None", "tagExt": "None",
            "tags": {"$type": "redTagList", "tags": []}}})
        refs.append(ref)
        data.append(node_data(i, ref, x, y, z))
    return {"Header": header(file_name), "Data": {"Version": 195, "BuildVersion": 0,
        "RootChunk": {
            "$type": "worldStreamingSector", "category": "AlwaysLoaded", "cookingPlatform": "PLATFORM_PC",
            "externInplaceResource": {"DepotPath": {"$type": "ResourcePath", "$storage": "uint64", "$value": "0"},
                                      "Flags": "Soft"},
            "level": 1, "localInplaceResource": [],
            # WolvenKit reads "Type" before "Data", so the key order matters.
            "nodeData": {"BufferId": "0", "Flags": 4063232,
                         "Type": "WolvenKit.RED4.Archive.Buffer.worldNodeDataBuffer, WolvenKit.RED4, "
                                 "Version=8.20.0.0, Culture=neutral, PublicKeyToken=null",
                         "Data": data},
            "nodeRefs": refs, "nodes": nodes,
            "persistentNodeIndex": 0, "persistentNodes": [], "variantIndices": [0], "variantNodes": [],
            "version": 62},
        "EmbeddedFiles": []}}


def node_data(i, ref, x, y, z):
    return {"Id": str(i), "NodeIndex": i, "Position": vec4(x, y, z),
            "Orientation": {"$type": "Quaternion", "i": 0, "j": 0, "k": 0, "r": 1},
            "Scale": {"$type": "Vector3", "X": 1, "Y": 1, "Z": 1},
            "Pivot": {"$type": "Vector3", "X": x, "Y": y, "Z": z},
            "Bounds": {"$type": "Box", "Max": vec4(x, y, z), "Min": vec4(x, y, z)},
            "QuestPrefabRefHash": ref,
            "UkHash1": {"$type": "NodeRef", "$storage": "uint64", "$value": "0"},
            "CookedPrefabData": {"DepotPath": {"$type": "ResourcePath", "$storage": "uint64", "$value": "0"},
                                 "Flags": "Default"},
            "MaxStreamingDistance": 120, "UkFloat1": 100, "Uk10": 1056, "Uk11": 512, "Uk12": 0,
            "Uk13": "0", "Uk14": "0"}


def block(k, sector_depot):
    return {"Header": header(f"{build_slots.slot(k)}.streamingblock"), "Data": {"Version": 195, "BuildVersion": 0,
        "RootChunk": {
            "$type": "worldStreamingBlock", "cookingPlatform": "PLATFORM_PC",
            "index": {"$type": "worldStreamingBlockIndex", "oup": "Base", "rldGridCell": 0},
            "descriptors": [descriptor(sector_depot)]},
        "EmbeddedFiles": []}}


def descriptor(sector_depot):
    """A block entry that loads the sector everywhere."""
    return {
                "$type": "worldStreamingSectorDescriptor",
                "blockIndex": {"$type": "worldStreamingBlockIndex", "oup": "Base", "rldGridCell": 0},
                "category": "AlwaysLoaded",
                "data": {"DepotPath": {"$type": "ResourcePath", "$storage": "string", "$value": sector_depot},
                         "Flags": "Soft"},
                "level": 1, "numNodeRanges": 1,
                "questPrefabNodeRef": {"$type": "NodeRef", "$storage": "uint64", "$value": "0"},
                "streamingBox": {"$type": "Box", "Max": vec4(BIG, BIG, BIG, BIG),
                                 "Min": vec4(-BIG, -BIG, -BIG, -BIG)},
                "variants": []}


def write(k, out):
    base = f"mod\\ncr_slots\\claims\\{build_slots.slot(k)}"
    files = {base + ".streamingsector": sector(k)}
    files[base + ".streamingblock"] = block(k, base + ".streamingsector")
    paths = []
    for depot, doc in files.items():
        f = out / (depot.replace("\\", "/") + ".json")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        paths.append(f)
    return base + ".streamingblock", paths


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slot", type=int, help=f"the slot number, 1 to {build_slots.SLOTS}")
    ap.add_argument("-o", "--out", default=".", help="folder to write the depot tree into")
    a = ap.parse_args()
    if not 1 <= a.slot <= build_slots.SLOTS:
        sys.exit(f"a slot is 1 to {build_slots.SLOTS}")
    blk, paths = write(a.slot, pathlib.Path(a.out))
    for p in paths:
        print(f"wrote {p}")
    print(f"name it in the mod's .archive.xl:\n\nstreaming:\n  blocks:\n    - {blk}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
