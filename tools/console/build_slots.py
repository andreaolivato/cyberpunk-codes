r"""Build NCR Quest & Voice Slots for console: one package that starts quest
mods anywhere and gives them voices, through slots they claim by name.

    python tools/console/build_slots.py [--c77] [--diag]

On console a mod cannot add to a base-game file, only replace it, and two
mods replacing the same file knock each other out. This is the one
package that replaces the two files a quest mod needs, and every quest mod
plugs into it by shipping files under a slot's name:

  the start   `base\quest\bugfixing\additional_content_bugfixing.questphase`,
              the base game's own patch-content quest, which runs in every
              save. Every save ends that quest parked on its last wait,
              node 46. The wait keeps its number and now waits for
              `ncr_slots_installed` to be 0: on the first load it sets the
              fact, fans out to one wait per slot, and goes back to wait on
              46. A save remembers a quest by node number, so after an
              uninstall the save is parked on the game's own 46 again, where
              the game's next patch expects it. Slot NNN waits until the world object
              `$/03_night_city/#ncr_slots/#ncr_slot_NNN` is loaded, or the
              fact `ncr_slot_NNN` is set, and then plays
              `mod\ncr_slots\quest\slot_NNN.questphase`. A mod ships that
              object in an always-loaded sector of its own (no script), or
              sets the fact from its script; either way a mod installed
              later starts on the next load, wherever V is. The object check
              is the game's own `questNodeLoadingCondition`, the one sq028
              uses to wait for Kerry's laptop. Nothing plays a slot nobody
              claimed, so an empty slot never asks for a file that is not
              there.

  the voices  `base\localization\volanguagedatamap.json`, the game's index
              of voice maps. Every dubbed language gets one chunk per slot,
              `mod\ncr_slots\vo\slot_NNN_<lang>.json`, as a soft reference.
              A mod ships its voice map for each language under its slot's
              name.

  the shard  a script, the one wrap the package ships. With the game's own
              loader only one mod's wrap of a method runs (docs/console-
              research.md, "Two gigs together"), so no quest mod may wrap the
              shard popup itself. This one does, for all of them: every shard
              read sets the fact `ncr_shard_read:<title>`, the title exactly as
              the popup receives it, which is the shard entry's own GetTitle().
              A read from a loot list leaves the journal's visited flag unset,
              so this is the only way a mod sees it.

Node ids, names and paths here are frozen once a build is released: a save
resumes a quest by node id, and a mod finds its slot by name.
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
import graph_edit  # noqa: E402

SHIP = "NCRQuestVoiceSlots"
ARCHIVE = "ncr_slots"
DEPOT = "mod\\ncr_slots\\"
START = "base\\quest\\bugfixing\\additional_content_bugfixing.questphase"
SINK = 46                    # the 2.5 file's last wait
INSTALLED = 60001            # sets ncr_slots_installed
SLOT_NODES = 60100           # slot k: wait SLOT_NODES+2k, phase SLOT_NODES+2k+1
DIAG_NODES = 65000           # test builds only: a fact node after slot k's wait (ids are 16-bit)
SLOTS = 200
SHARDS_SCRIPT = """// NCR Quest & Voice Slots: every shard read, as a fact a quest mod can read.
// See tools/console/build_slots.py.
@wrapMethod(PopupsManager)
event OnShardRead(evt: NotifyShardRead) -> Bool {
    var result: Bool = OnShardRead(evt);
    var player: GameObject = this.GetPlayerControlledObject();
    if( ( ( player ) != NULL ) ) {
        GameInstance.GetQuestsSystem(player.GetGame()).SetFactStr("ncr_shard_read:" + evt.title, 1);
    }
    return result;
}
"""
# The dubbed languages in the 2.5 index, the ones a slot has a voice map for.
LANGS = ["de-de", "en-us", "es-es", "fr-fr", "it-it", "jp-jp", "kr-kr", "pl-pl", "pt-br", "ru-ru", "zh-cn"]


def slot(k):
    return f"slot_{k:03d}"


def slot_object(k):
    """The object a mod ships to claim slot k, as the NodeRef its sector
    lists in nodeRefs. Long form: a short name does not register for a
    mod's node (gotcha 34)."""
    return f"$/03_night_city/#ncr_slots/#ncr_{slot(k)}"


def slot_fact(k):
    return f"ncr_{slot(k)}"


def slot_phase(k):
    return f"{DEPOT}quest\\{slot(k)}.questphase"


def slot_vomap(k, lang):
    return f"{DEPOT}vo\\{slot(k)}_{lang}.json"


def start_file(work, slots, diag=False):
    d = console_archive.vanilla_json(START, work)
    g = graph_edit.Graph(d)
    sink = g.node(SINK)
    if sink["$type"] != "questPauseConditionNodeDefinition" or "travelling_merchant_lives" not in json.dumps(sink):
        raise SystemExit(f"{START} node {SINK} is not the sink; the game file changed, see the header")
    for nid in [INSTALLED] + [SLOT_NODES + n for n in range(2, 2 * slots + 2)]:
        if nid in g.ids():
            raise SystemExit(f"{START} already has a node {nid}")
    sink["condition"] = {"HandleId": g.h(), "Data": g.fresh(g.fact_condition("ncr_slots_installed", "Less", 1))}
    g.link(SINK, "Out", INSTALLED, "In")
    g.link_back(INSTALLED, "Out", SINK, "In")
    g.add_set_fact(INSTALLED, "ncr_slots_installed")
    for k in range(1, slots + 1):
        wait, phase = SLOT_NODES + 2 * k, SLOT_NODES + 2 * k + 1
        g.link(INSTALLED, "Out", wait, "In")
        g.add(wait, "questPauseConditionNodeDefinition", {"condition": {"HandleId": "0", "Data": {
            "$type": "questLogicalCondition", "operation": "OR", "conditions": [
                {"HandleId": "0", "Data": {"$type": "questNodeLoadingCondition", "inverted": 0,
                                           "objectRef": {"$type": "NodeRef", "$storage": "string",
                                                         "$value": slot_object(k)}}},
                {"HandleId": "0", "Data": g.fact_condition(slot_fact(k))},
            ]}}}, ["Out"])
        if diag and k <= 3:
            g.link(wait, "Out", DIAG_NODES + k, "In")
            g.add_set_fact(DIAG_NODES + k, f"ncr_dbg_{slot(k)}")
        g.link(wait, "Out", phase, "In1")
        g.add(phase, "questPhaseNodeDefinition", {
            "phaseGraph": None,
            "phaseInstancePrefabs": [],
            "phaseResource": {"DepotPath": {"$type": "ResourcePath", "$storage": "string",
                                            "$value": slot_phase(k)}, "Flags": "Soft"},
            "saveLock": 0,
            "unfreezingTriggerNodeRef": {"$type": "NodeRef", "$storage": "uint64", "$value": "0"},
        }, ["Out1"])
    return d


def voice_index(work, slots):
    d = console_archive.vanilla_json(console_archive.VO_INDEX, work)
    langs = []
    for e in d["Data"]["RootChunk"]["root"]["Data"]["entries"]:
        lang = e["languageCode"]["$value"]
        if lang == "common":
            continue
        for k in range(1, slots + 1):
            e["voMapChunks"].append({"DepotPath": {"$type": "ResourcePath", "$storage": "string",
                                                   "$value": slot_vomap(k, lang)}, "Flags": "Soft"})
        langs.append(lang)
    if sorted(langs) != sorted(LANGS):
        raise SystemExit(f"the game's voice index lists {langs}, LANGS says {LANGS}: update LANGS and the slot docs")
    return d, langs


def build(slots, diag=False):
    root = REPO / "dist" / "console" / "slots"
    work = root / "work"
    raw = work / "raw"
    if raw.exists():
        shutil.rmtree(raw)
    files = {START: start_file(work, slots, diag)}
    files[console_archive.VO_INDEX], langs = voice_index(work, slots)
    for depot, doc in files.items():
        f = raw / (depot.replace("\\", "/") + ".json")
        f.parent.mkdir(parents=True, exist_ok=True)
        graph_edit.save(f, doc)
    console_archive.cli("convert", "deserialize", raw, "-w", "*.json")
    stage = work / "pack" / ARCHIVE
    if stage.parent.exists():
        shutil.rmtree(stage.parent)
    for depot in files:
        res = raw / depot.replace("\\", "/")
        dst = stage / depot.replace("\\", "/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(res), dst)
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
    scripts = pkg / "r6" / "scripts" / SHIP
    scripts.mkdir(parents=True)
    (scripts / "ncr_shards.script").write_text(SHARDS_SCRIPT, encoding="utf-8", newline="\n")
    import build_console
    log = build_console.compile_one(None, pkg)
    if not (pkg / "r6" / "cache" / "final.redscripts").exists() or "failed" in log.lower():
        raise SystemExit("the shard script did not compile:\n" + log[-1500:])
    print(f"staged {pkg}: {slots} quest slots, {slots} voice slots in {len(langs)} languages"
          + ("  (TEST BUILD)" if diag else ""))
    return pkg


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--c77", action="store_true", help="also lay it out for <game>/r6/c77 and zip it")
    ap.add_argument("--diag", action="store_true",
                    help="test build: slots 1 to 3 set ncr_dbg_slot_00N when they open")
    a = ap.parse_args()
    pkg = build(SLOTS, a.diag)
    if a.c77:
        console_archive.core_c77(pkg, SHIP, not a.diag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
