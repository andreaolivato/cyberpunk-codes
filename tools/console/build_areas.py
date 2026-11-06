r"""Build NCR Map Areas for console: one package that draws quest mods' areas
on the minimap and the world map.

    python tools/console/build_areas.py [--c77]

On PC ArchiveXL draws a quest pin's area from the trigger area the pin points
at (backlog 39). The game's own loader has nothing that does: the minimap
reads area outlines only from the game's map pin table,
`base\worlds\03_night_city\_compiled\default\03_night_city.mappins`, an
entry per pin keyed by the hash of the pin's journal path, with the pin's
position and the outline in it (playtest, 2026-10-29: the pin and no area;
2026-10-30: the area drawn from a copy of the table). Security zones are
the same, from `03_night_city.areas`, so there is no route around it.

A mod can only replace that file, and two mods replacing it knock each other
out. This is the one package that replaces it: a copy of the player's table
(Phantom Liberty's, which lists every pin of the base game's too) with every
area in `map_areas.json` appended. The table holds each outline itself, not a
path to one, so an area cannot be reserved and filled in later the way a slot
of NCR Quest & Voice Slots is: a mod's area is in the package from the
release that adds it.

The table changes when a game patch adds or moves the game's own pins, and a
player on a stale copy loses those positions, so the package is rebuilt for
every game patch that changes the file. The build compares the game's table
with the pin count it was last checked against (VANILLA_PINS) and says when
it moved.
"""
import argparse
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import console_archive  # noqa: E402

SHIP = "NCRMapAreas"
ARCHIVE = "ncr_map_areas"
MAPPINS = "\\".join(["base", "worlds", "03_night_city", "_compiled", "default", "03_night_city.mappins"])
EP1 = console_archive.GAME / "archive" / "pc" / "ep1" / "ep1_1_nightcity.archive"
REGISTRY = HERE / "map_areas.json"
# The vanilla table this build was last checked against (2.5, Phantom Liberty).
VANILLA_PINS = 4465


def gig_area(gig):
    """An area of one of this repo's gigs, read from its own generator: the
    journal paths of the pins on its area node, the node's position, the
    height and the outline relative to the position."""
    tools = REPO / "tools"
    for p in (tools, tools / gig):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    if gig == "gig01":
        import compound_area as a
        journal = REPO / "mods/gig-01-negative-balance/source/wkit/raw/mod/negative_balance/journal/gig01.journal.json"
    elif gig == "gig02":
        import hit_area as a
        journal = REPO / "mods/gig-02-dead-ringer/source/wkit/raw/mod/dead_ringer/journal/gig02.journal.json"
    else:
        raise SystemExit(f"map_areas.json: no generator known for {gig}")
    x, y, z = a.position()
    pins = pins_on(json.loads(journal.read_text(encoding="utf-8")), a.AREA_REF)
    if not pins:
        raise SystemExit(f"{gig}: no journal pin points at {a.AREA_REF}")
    return {"pins": pins, "position": [x, y, z], "height": a.AREA_HEIGHT,
            "outline": [[cx - x, cy - y] for cx, cy in a.corners()]}


def pins_on(jd, ref):
    """The journal path of every quest map pin whose node is `ref`."""
    out = []

    def walk(o, path):
        if isinstance(o, dict):
            e = o.get("Data")
            if isinstance(e, dict) and "id" in e:
                p = path + [e["id"]] if e["id"] else path
                if (e["$type"] == "gameJournalQuestMapPin"
                        and e["reference"]["reference"]["$value"] == ref):
                    out.append("/".join(p))
                for v in e.values():
                    walk(v, p)
                return
            for v in o.values():
                walk(v, path)
        elif isinstance(o, list):
            for v in o:
                walk(v, path)
    walk(jd["Data"]["RootChunk"], [])
    return out


def areas():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    out = []
    for e in reg["areas"]:
        a = gig_area(e["from"]) if "from" in e else {k: e[k] for k in ("pins", "position", "height", "outline")}
        if len(a["outline"]) < 3:
            raise SystemExit(f"{e['mod']}: an outline needs three corners at least")
        out.append((e["mod"], a))
    return out


def table(work):
    d = console_archive.vanilla_json(MAPPINS, work, first=[EP1])
    cooked = d["Data"]["RootChunk"]["cookedData"]
    if len(cooked) != VANILLA_PINS:
        print(f"  NOTE: the game's table has {len(cooked)} pins, {VANILLA_PINS} when this was last checked."
              " A game patch changed it: rebuild and release, then update VANILLA_PINS.")
    have = {e["journalPathHash"] for e in cooked}
    handle = sum(1 for e in cooked if e.get("volume"))
    n = 0
    for mod, a in areas():
        x, y, z = a["position"]
        for path in a["pins"]:
            h = console_archive.murmur3_32(path)
            if h in have:
                raise SystemExit(f"{mod}: {path} hashes to {h}, already in the table")
            have.add(h)
            cooked.append({"$type": "gameCookedMappinData", "journalPathHash": h,
                           "position": {"$type": "Vector3", "X": x, "Y": y, "Z": z},
                           "volume": {"HandleId": str(handle), "Data": {
                               "$type": "gamemappinsOutlineMappinVolume", "height": a["height"],
                               "outlinePoints": [{"$type": "Vector2", "X": px, "Y": py}
                                                 for px, py in a["outline"]]}}})
            handle += 1
            n += 1
        print(f"  {mod}: {len(a['pins'])} pin(s), {len(a['outline'])} corners")
    return d, n


def build():
    root = REPO / "dist" / "console" / "map-areas"
    work = root / "work"
    raw = work / "raw"
    if raw.exists():
        shutil.rmtree(raw)
    doc, n = table(work)
    f = raw / (MAPPINS.replace("\\", "/") + ".json")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    console_archive.cli("convert", "deserialize", raw, "-w", "*.json")
    stage = work / "pack" / ARCHIVE
    if stage.parent.exists():
        shutil.rmtree(stage.parent)
    dst = stage / MAPPINS.replace("\\", "/")
    dst.parent.mkdir(parents=True)
    shutil.move(str(raw / MAPPINS.replace("\\", "/")), dst)
    pkg = root / SHIP
    if pkg.exists():
        shutil.rmtree(pkg)
    out = pkg / "archive" / "pc" / "mod"
    out.mkdir(parents=True)
    console_archive.cli("pack", stage, "-o", out)
    if not (out / f"{ARCHIVE}.archive").exists():
        raise SystemExit(f"WolvenKit packed nothing into {out}")
    (pkg / "about.json").write_text(json.dumps({"ModInfo": {"ModName": SHIP, "ModID": -1}}, indent="\t"),
                                    encoding="utf-8")
    print(f"staged {pkg}: {n} area pins added to the game's table")
    return pkg


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--c77", action="store_true", help="also lay it out for <game>/r6/c77 and zip it")
    a = ap.parse_args()
    pkg = build()
    if a.c77:
        console_archive.core_c77(pkg, SHIP, True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
