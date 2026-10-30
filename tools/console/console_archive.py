"""The mod.io copy of a gig's archive and manifest.

build_console.py calls this. The Nexus archive is built by build-archive.ps1
from `source/wkit/raw`; this builds the mod.io one from the same raw tree,
with these changes, each because the game's own loader refuses or ignores
what ArchiveXL does:

1. TEXT BY NUMBER. The loader does not read an onscreen entry by its
   secondary key ("cc-g01-..."), only as `LocKey#<number>` (wiki page
   "What can I upload on mod.io?", the `.journal` row; unmeasured here). The
   number is FNV1a64 of the key, which PC already resolves too:
   `elena.yaml` has used `LocKey#<FNV1a64("cc-g01-elena-short")>` since
   2026-08. So each entry gets that number as its primaryKey, the journal and
   the tweaks name it as `LocKey#<number>`, and the scripts go through the
   table loc_script() writes.
2. NO QUEST HOOK IN THE MANIFEST. REDmod's converter refuses the `quest:` key
   ("Unsupported ArchiveXL feature quest.", measured 2026-10-28). The gig's
   phase ships under its slot of NCR Quest & Voice Slots instead, with its
   voice maps (core_slot(), slot named in `modio/hook.json`).
3. NO MOD ENTITY TEMPLATE. mod.io lists `.ent` as PC only. The one `.ent` in
   gig 01 (the old shard) is no longer placed by anything, so it is left out.
4. NO COMMUNITY REGISTRIES and NO SECTOR EDITS in the manifest
   (merge_blocks, console_manifest).
5. Everything else is the Nexus raw tree, converted and packed the way
   build-archive.ps1 does it.
"""

import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess

GAME = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077")
CLI = pathlib.Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe"))
CONTENT = [GAME / "archive" / "pc" / "content" / "basegame_4_gamedata.archive",
           GAME / "archive" / "pc" / "ep1" / "ep1_2_gamedata.archive"]
BINARIES = (".wem", ".xbm", ".anims")


def fnv1a64(text):
    h = 0xcbf29ce484222325
    for b in text.encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


def murmur3_32(data, seed=0x5EEDBA5E):
    """A journal path's hash: the key the game's map pin table files an entry
    under. Checked against two of ArchiveXL's logged keys for gig 02's pins
    (2026-10-29)."""
    key = data.encode()
    n = len(key)
    h = seed
    c1, c2 = 0xCC9E2D51, 0x1B873593
    for i in range(n // 4):
        k = int.from_bytes(key[i * 4:i * 4 + 4], "little")
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = key[(n // 4) * 4:]
    k = 0
    if len(tail) >= 3:
        k ^= tail[2] << 16
    if len(tail) >= 2:
        k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= n
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def cli(*args):
    p = subprocess.run([str(CLI), *map(str, args)], capture_output=True, text=True, errors="replace")
    if p.returncode != 0:
        raise SystemExit(f"WolvenKit {args[0]} failed:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
    return p.stdout


# ------------------------------------------------------------- 1. text

def onscreen_files(raw):
    return [p for p in raw.rglob("*.json.json")
            if '"localizationPersistenceOnScreenEntries"' in p.read_text(encoding="utf-8")]


def loc_keys(raw):
    """Every secondary key the gig's onscreen files define."""
    keys = set()
    for p in onscreen_files(raw):
        d = json.loads(p.read_text(encoding="utf-8"))
        for e in d["Data"]["RootChunk"]["root"]["Data"]["entries"]:
            if e.get("secondaryKey"):
                keys.add(e["secondaryKey"])
    return sorted(keys)


def number_text(raw, keys):
    """Give each entry its number and name it by number in the journal."""
    for p in onscreen_files(raw):
        d = json.loads(p.read_text(encoding="utf-8"))
        for e in d["Data"]["RootChunk"]["root"]["Data"]["entries"]:
            if e.get("secondaryKey") and str(e.get("primaryKey", "0")) == "0":
                e["primaryKey"] = str(fnv1a64(e["secondaryKey"]))
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    wanted = set(keys)
    changed = 0
    for p in raw.rglob("*.journal.json"):
        d = json.loads(p.read_text(encoding="utf-8"))

        def walk(o):
            nonlocal changed
            if isinstance(o, dict):
                if set(o) >= {"unk1", "value"} and o["value"] in wanted:
                    o["value"] = f"LocKey#{fnv1a64(o['value'])}"
                    changed += 1
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(d)
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    return changed


def number_tweak(text, keys):
    """`displayName: cc-g01-x` -> `displayName: LocKey#<n>`, for our keys only."""
    wanted = set(keys)

    def sub(m):
        return m.group(1) + (f"LocKey#{fnv1a64(m.group(2))}" if m.group(2) in wanted else m.group(2))
    return re.sub(r"^(\s*[A-Za-z_]\w*:\s*)([A-Za-z0-9_-]+)\s*$", sub, text, flags=re.M)


# Fields a record does not declare, which the base game adds as extra flats on
# its own records. Measured 2026-10-29 with a test mod on the game's own
# loader: written inside a cloned record the value is dropped (a shard's read
# action then has no journal path, and its popup comes up empty); written as
# its own line, `Record.field: value`, it is there.
EXTRA_FLATS = ("journalEntry",)


def extra_flats(text):
    """Move every EXTRA_FLATS field out of its record and under the record's
    name, so the console's tweak loader keeps it."""
    out, moved, record = [], [], None
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z_][\w.]*):\s*$", line)
        if m:
            record = m.group(1)
        f = re.match(r"^\s+(\w+):\s*(\S.*)$", line)
        if record and f and f.group(1) in EXTRA_FLATS:
            moved.append(f"{record}.{f.group(1)}: {f.group(2)}")
            continue
        out.append(line)
    return "\n".join(out + moved) + "\n"


def loc_script(gig, keys):
    """The function the converter sends every GetLocalizedTextByKey through."""
    lines = [
        "// Written by tools/console/console_archive.py. The console reads a mod's",
        "// text by number only, so the gig's own keys are looked up as",
        "// LocKey#<FNV1a64(key)>; any other key goes to the game as before.",
        f"function CC{gig}LocText( key : CName ) : String",
        "{",
    ]
    for k in keys:
        lines.append(f'\tif( key == n"{k}" ) {{ return GetLocalizedText( "LocKey#{fnv1a64(k)}" ); }}')
    lines += ["\treturn GetLocalizedTextByKey( key );", "}", ""]
    return "\n".join(lines)


# ------------------------------------------------------------- 2. the hook

def vanilla_json(depot, work, first=()):
    """Serialize one vanilla file from the player's game into `work`. The
    archives in `first` are searched before the usual ones, for a file
    Phantom Liberty ships its own copy of."""
    out = work / "vanilla"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    pattern = re.escape(depot.replace("\\", "/")).replace("/", ".")
    others = sorted((GAME / "archive" / "pc" / "content").glob("*.archive"))
    for archive in list(first) + CONTENT + [a for a in others if a not in CONTENT]:
        cli("unbundle", "-p", archive, "-o", out, "-r", pattern + "$")
        f = out / depot
        if f.exists():
            cli("convert", "serialize", f, "-o", f.parent)
            return json.loads((f.parent / (f.name + ".json")).read_text(encoding="utf-8"))
    raise SystemExit(f"{depot} is not in the game's archives")


def drop_top_key(xl, key):
    """Remove one top-level key of the .xl with its block and the comments above it."""
    lines = xl.splitlines(keepends=True)
    out, skip = [], False
    for line in lines:
        top = re.match(r"^([A-Za-z_]+):", line)
        if top:
            skip = top.group(1) == key
        if not skip:
            out.append(line)
    return "".join(out)


def console_manifest(xl):
    """The two changes the game's own loader needs, measured on PC 2.5 with
    `r6/c77` (docs/console-research.md):

    - `streaming: sectors:` goes. The loader accepts a `nodeDeletions` entry
      and does not apply it (gig 02, 2026-10-30: the AI spot it removes on PC
      still took a sitter), so shipping it only adds a file entry that does
      nothing.
    - Each `onscreens` locale names one file, not a list of one: the shape
      every working mod.io install has (ArchiveXL on PC takes a list)."""
    lines = xl.splitlines(keepends=True)
    out, skip = [], False
    for line in lines:
        if re.match(r"^\S", line) or re.match(r"^  [A-Za-z_]+:", line):
            skip = line.rstrip() == "  sectors:"
        if not skip:
            out.append(line)
    text = "".join(out)
    return re.sub(r"^(    [a-z]{2}-[a-z]{2}):[ \t]*\r?\n[ \t]+-[ \t]+(\S+)", r"\1: \2", text, flags=re.M)


def merge_registries(raw, descriptors):
    """Every community registry sector merged into the first one, in place.

    Measured on PC 2.5 with the game's own loader, 2026-10-28: any one or two
    of gig 01's three registry sectors load, all three crash the game while
    it loads the main menu, twice out of two. Each sector has one
    `worldCommunityRegistryNode`; its `communitiesData` items move into the
    first sector's node, their HandleIds shifted past the ones already there.
    The other sectors and their descriptors are removed."""
    def path(x):
        return x["data"]["DepotPath"]["$value"]
    regs = []
    for x in descriptors:
        f = raw / (path(x).replace("\\", "/") + ".json")
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            nodes = d["Data"]["RootChunk"]["nodes"]
            if len(nodes) == 1 and nodes[0]["Data"]["$type"] == "worldCommunityRegistryNode":
                regs.append((x, f, d))
    if len(regs) < 2:
        return

    def handles(o, out):
        if isinstance(o, dict):
            for k in ("HandleId", "HandleRefId"):
                if k in o:
                    out.append(int(o[k]))
            for v in o.values():
                handles(v, out)
        elif isinstance(o, list):
            for v in o:
                handles(v, out)
        return out

    def shift(o, by):
        if isinstance(o, dict):
            for k in ("HandleId", "HandleRefId"):
                if k in o:
                    o[k] = str(int(o[k]) + by)
            for v in o.values():
                shift(v, by)
        elif isinstance(o, list):
            for v in o:
                shift(v, by)

    _, f0, d0 = regs[0]
    reg0 = d0["Data"]["RootChunk"]["nodes"][0]["Data"]
    for x, f, d in regs[1:]:
        reg = d["Data"]["RootChunk"]["nodes"][0]["Data"]
        more = reg["communitiesData"]
        shift(more, max(handles(d0, [])) + 1)
        reg0["communitiesData"] += more
        # The posts the guards stand at, and the name map, belong to the same
        # communities. Merging only communitiesData left the compound and
        # estate guards with no posts: the quest's Activate on them never
        # finished, and the gig stopped at "get inside the compound".
        reg0["workspotsPersistentData"] += reg["workspotsPersistentData"]
        reg0["spawnSetNameToCommunityID"]["entries"] += reg["spawnSetNameToCommunityID"]["entries"]
        f.unlink()
        descriptors.remove(x)
    # NO POST RECORDS ON CONSOLE. The game's AIWorkspotManager::RegisterSpots
    # REPLACES its array of spot records with a registry's own; ArchiveXL's
    # OnRegisterSpots hook is what makes it merge on PC (docs/backlog.md 29).
    # With the game's own loader, a mod registry that ships records either
    # wipes every vanilla post in the city or is wiped by them.
    reg0["workspotsPersistentData"] = []
    f0.write_text(json.dumps(d0, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  merged {len(regs)} community registries into {f0.name}")


def merge_blocks(raw, xl):
    """Every `streaming: blocks:` entry merged into the first one.

    On PC 2.5 with the game's own loader, gig 01's four blocks crashed the
    game while it loaded the main menu, where one or two did not
    (docs/console-research.md). Every mod.io install seen ships one block.
    A block's descriptors carry no handles, so they move as they are."""
    paths = re.findall(r"^    - (\S+\.streamingblock)\s*$", xl, re.M)
    if len(paths) < 2:
        return xl
    files = [raw / (p.replace("\\", "/") + ".json") for p in paths]
    first = json.loads(files[0].read_text(encoding="utf-8"))
    for f in files[1:]:
        more = json.loads(f.read_text(encoding="utf-8"))
        first["Data"]["RootChunk"]["descriptors"] += more["Data"]["RootChunk"]["descriptors"]
        f.unlink()
    merge_registries(raw, first["Data"]["RootChunk"]["descriptors"])
    # NO COMMUNITY REGISTRY ON CONSOLE, measured on PC 2.5 with the game's own
    # loader, 2026-10-28. With the merged registry, the quest's Activate on the
    # compound guards never finished (the gig stopped at "get inside the
    # compound") and loading a save from inside the game crashed at
    # +0x270242. Without it, Activate completes, the gig moves on, and three
    # loads in a row from the pause menu held. The registries' sectors go;
    # the communities' own area sectors stay, harmless without them.
    regs = [x for x in first["Data"]["RootChunk"]["descriptors"]
            if x["data"]["DepotPath"]["$value"].endswith("_reg.streamingsector")]
    for x in regs:
        first["Data"]["RootChunk"]["descriptors"].remove(x)
        f = raw / (x["data"]["DepotPath"]["$value"].replace("\\", "/") + ".json")
        if f.exists():
            f.unlink()
    if regs:
        print(f"  dropped {len(regs)} community registry sector(s): console has no ArchiveXL to merge them")
    files[0].write_text(json.dumps(first, indent=2, ensure_ascii=False), encoding="utf-8")
    for p in paths[1:]:
        xl = re.sub(r"^    - " + re.escape(p) + r"\s*\r?\n", "", xl, flags=re.M)
    return xl


# ------------------------------------------------------------- 4. build

VO_INDEX = "base\\localization\\volanguagedatamap.json"


def core_slot(raw, k, phase_depot, xl_path, claim_file=False, claim=True):
    """THE GIG IN A SLOT OF THE CONSOLE CORE (tools/console/build_slots.py).

    The gig's phase moves to the slot's path, and the slot's object goes
    into the gig's always-loaded sector, so the slots package's start quest plays the
    phase on the first load with the gig installed. Each voice map the
    manifest names is copied to the slot's path for its language; a
    language the package voices and the gig does not gets the gig's en-us map,
    so a player there hears the recordings instead of nothing. The gig then
    replaces no base-game file."""
    import build_slots
    src = raw / (phase_depot.replace("\\", "/") + ".json")
    dst = raw / (build_slots.slot_phase(k).replace("\\", "/") + ".json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), dst)
    if claim:
        slot_object(raw, build_slots.slot_object(k), build_slots.slot(k), k, xl_path, claim_file)
    xl = xl_path.read_text(encoding="utf-8")
    block = re.search(r"^  vomaps:\s*\n((?:    .+\n|\s*#.*\n)+)", xl, re.M)
    maps = dict(re.findall(r"^    ([a-z]{2}-[a-z]{2}):\s*(\S+)\s*$", block.group(1), re.M)) if block else {}
    if maps and "en-us" not in maps:
        raise SystemExit("core_slot: the manifest's vomaps have no en-us map to fall back on")
    for lang in build_slots.LANGS if maps else []:
        f = raw / (maps.get(lang, maps["en-us"]).replace("\\", "/") + ".json")
        out = raw / (build_slots.slot_vomap(k, lang).replace("\\", "/") + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
    print(f"  slots: the gig's phase in {build_slots.slot(k)}, voice maps for {len(build_slots.LANGS) if maps else 0} languages")
    return dst


def slot_object(raw, ref, name, k=None, xl_path=None, claim_file=False):
    """One marker node named `ref` in the gig's always-loaded sector: what
    the slots package's questNodeLoadingCondition waits for. Same node shape as the
    sector's own markers; its position does not matter, the sector is
    loaded wherever V is. A gig with no such sector gets the claim files a
    modder would ship (make_slot_claim.py), named in its manifest's blocks;
    merge_blocks then folds them into the gig's first block."""
    # "Always loaded" in a sector's own category still streams by its block's
    # box; the one loaded everywhere is the sector whose box has no bounds.
    secs = []
    for b in raw.rglob("*.streamingblock.json"):
        for x in json.loads(b.read_text(encoding="utf-8"))["Data"]["RootChunk"]["descriptors"]:
            if x["category"] == "AlwaysLoaded" and x["streamingBox"]["Max"]["X"] > 1e30:
                f = raw / (x["data"]["DepotPath"]["$value"].replace("\\", "/") + ".json")
                if f.exists():
                    secs.append(f)
    if (claim_file or not secs) and xl_path is not None:
        import make_slot_claim
        blk, _ = make_slot_claim.write(k, raw)
        xl = xl_path.read_text(encoding="utf-8")
        m = re.search(r"^  blocks:\s*\n", xl, re.M)
        if not m:
            raise SystemExit("core_slot: the manifest has no streaming: blocks: list to name the claim in")
        xl_path.write_text(xl[:m.end()] + f"    - {blk}\n" + xl[m.end():], encoding="utf-8")
        print(f"  slots: claim sector for {name}, from make_slot_claim.py")
        return
    if len(secs) != 1:
        raise SystemExit(f"core_slot: needs exactly one sector loaded everywhere to carry {ref}, found {len(secs)}")
    sec = json.loads(secs[0].read_text(encoding="utf-8"))
    rc = sec["Data"]["RootChunk"]
    marker = next(n for n in rc["nodes"] if n["Data"]["$type"] == "worldStaticMarkerNode")
    h = max(int(x) for x in re.findall(r'"HandleId": "(\d+)"', json.dumps(rc))) + 1
    node = json.loads(json.dumps(marker))
    node["HandleId"], node["Data"]["data"]["HandleId"] = str(h), str(h + 1)
    node["Data"]["debugName"] = {"$type": "CName", "$storage": "string", "$value": "ncr_" + name}
    i = len(rc["nodes"])
    rc["nodes"].append(node)
    nref = {"$type": "NodeRef", "$storage": "string", "$value": ref}
    rc["nodeRefs"].append(nref)
    nd = json.loads(json.dumps(rc["nodeData"]["Data"][0]))
    nd.update({"Id": str(i), "NodeIndex": i, "QuestPrefabRefHash": nref})
    rc["nodeData"]["Data"].append(nd)
    secs[0].write_text(json.dumps(sec, indent=2, ensure_ascii=False), encoding="utf-8")


def core_c77(pkg, ship, upload):
    """A core package's local test (`<game>/r6/c77/<ship>`) and, when
    `upload`, its upload zip: the same shapes build_console.py writes for a
    gig. Compiled scripts are copied only if the package has any."""
    import zipfile
    root = pkg.parent
    out = root / "c77"
    if out.exists():
        shutil.rmtree(out)
    mod = out / ship
    (mod / "archive").mkdir(parents=True)
    shutil.copy2(pkg / "about.json", mod / "about.json")
    for f in (pkg / "archive" / "pc" / "mod").iterdir():
        shutil.copy2(f, mod / "archive" / f.name)
    cache = pkg / "r6" / "cache"
    if cache.exists():
        for f in cache.iterdir():
            shutil.copy2(f, mod / f.name)
    upath = root / f"{ship}-modio.zip"
    upath.unlink(missing_ok=True)
    print(f"c77 layout in {out}")
    if not upload:
        return
    with zipfile.ZipFile(upath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pkg.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(pkg).as_posix())
    print(f"upload: {upath}")


def raw_digest(raw):
    """The same digest build-archive.ps1 writes to raw.sha256."""
    files = sorted((p for p in raw.rglob("*") if p.is_file()), key=lambda p: str(p).lower())
    lines = [f"{str(p.relative_to(raw))} {hashlib.sha256(p.read_bytes()).hexdigest().upper()}" for p in files]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def build(mod_dir, gig, out_dir, work, hook_cfg, phase_depot, diag_fact=None):
    """Stage, change, convert and pack. Returns (archive, xl, keys)."""
    src = mod_dir / "source" / "wkit" / "raw"
    packed = mod_dir / "source" / "wkit" / "packed"
    recorded = (packed / "raw.sha256").read_text().strip() if (packed / "raw.sha256").exists() else None
    stale = recorded is not None and recorded != raw_digest(src)

    raw = work / "raw"
    if raw.exists():
        shutil.rmtree(raw)
    shutil.copytree(src, raw)
    xl_name = next(raw.glob("*.archive.xl")).name
    name = xl_name[: -len(".archive.xl")]

    for p in list(raw.rglob("*.ent.json")):
        p.unlink()
    keys = loc_keys(raw)
    number_text(raw, keys)
    core = (hook_cfg or {}).get("core_slot")
    if not core:
        raise SystemExit(f"{gig}: modio/hook.json names no core_slot. Every gig starts through "
                         "NCR Quest & Voice Slots (tools/console/build_slots.py).")

    # A gig's own console changes to its generated files, if it has any.
    patch_py = mod_dir / "modio" / "patch.py"
    if patch_py.exists():
        spec = importlib.util.spec_from_file_location(f"{gig}_console_patch", patch_py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.patch(raw)

    # A test build claims the slot by its fact, from the test script, once
    # the facts it resets are clear; so it ships no claim object.
    hooked = core_slot(raw, core, phase_depot, raw / xl_name, hook_cfg.get("claim_file", False),
                       claim=not diag_fact)
    xl = console_manifest(drop_top_key((raw / xl_name).read_text(encoding="utf-8"), "quest"))
    xl = merge_blocks(raw, xl)
    (raw / xl_name).unlink()

    cli("convert", "deserialize", raw, "-w", "*.json")
    stage = work / "pack" / name
    if stage.parent.exists():
        shutil.rmtree(stage.parent)
    for j in raw.rglob("*.json"):
        if not re.search(r"\.[a-z0-9]+\.json$", j.name):
            continue
        res = j.with_name(j.name[: -len(".json")])
        if not res.exists():
            raise SystemExit(f"WolvenKit made nothing from {j.relative_to(raw)}")
        dst = stage / res.relative_to(raw)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(res), dst)
    for b in raw.rglob("*"):
        if b.is_file() and b.suffix.lower() in BINARIES:
            dst = stage / b.relative_to(raw)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(b, dst)
    out_dir.mkdir(parents=True, exist_ok=True)
    cli("pack", stage, "-o", out_dir)
    archive = out_dir / (name + ".archive")
    if not archive.exists():
        raise SystemExit(f"WolvenKit packed nothing into {out_dir}")
    (out_dir / xl_name).write_text(xl, encoding="utf-8", newline="\n")
    return archive, out_dir / xl_name, keys, stale, hooked
