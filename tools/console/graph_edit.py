"""Adding nodes to a serialized quest phase, for the console build's patches.

WolvenKit reads a handle's first appearance as its definition and refuses a
reference that comes before it (found 2026-10-28 on the Hoshino bench branch).
So every node added here goes at the END of the graph, and every link runs
from an earlier node to a later one: the link is appended to the source's
output socket and defines the destination's input socket inline, and the new
node then names that socket by reference. Built that way, every reference
points backwards.
"""
import copy
import json


def cname(v):
    return {"$type": "CName", "$storage": "string", "$value": v}


class Graph:
    def __init__(self, doc, graph=None):
        self.doc = doc
        self.graph = graph or doc["Data"]["RootChunk"]["graph"]["Data"]
        self.handles = {}
        self._index(doc)
        self.next_h = max(int(h) for h in self.handles) + 1
        self.pending = {}   # new node id -> {input name: handle id}
        self.pending_out = {}   # new node id -> {output name: handle id}

    def _index(self, o):
        if isinstance(o, dict):
            if "HandleId" in o:
                self.handles[o["HandleId"]] = o
            for v in o.values():
                self._index(v)
        elif isinstance(o, list):
            for v in o:
                self._index(v)

    def h(self):
        self.next_h += 1
        return str(self.next_h)

    def deref(self, o):
        return self.handles.get(o.get("HandleRefId"), o) if "HandleRefId" in o else o

    def node(self, nid):
        for n in self.graph["nodes"]:
            if n["Data"]["id"] == nid:
                return n["Data"]
        raise KeyError(nid)

    def ids(self):
        return {n["Data"]["id"] for n in self.graph["nodes"]}

    def out_socket(self, nid, name):
        for s in self.node(nid)["sockets"]:
            s = self.deref(s)
            if s["Data"]["name"]["$value"] == name and s["Data"]["type"] == "Output":
                return s
        raise KeyError(f"node {nid} has no output {name}")

    def link(self, src, src_out, dst_id, dst_in):
        """src's output -> the input `dst_in` of a node not added yet."""
        sock = self.out_socket(src, src_out) if isinstance(src, int) else src
        c, d = self.h(), self.h()
        sock["Data"]["connections"].append({"HandleId": c, "Data": {
            "$type": "graphGraphConnectionDefinition",
            "destination": {"HandleId": d, "Data": {
                "$type": "questSocketDefinition", "connections": [{"HandleRefId": c}],
                "name": cname(dst_in), "type": "Input"}},
            "source": {"HandleRefId": sock["HandleId"]}}})
        self.handles[d] = sock["Data"]["connections"][-1]["Data"]["destination"]
        self.pending.setdefault(dst_id, {})[dst_in] = d

    def link_back(self, src_id, src_out, dst, dst_in):
        """The output `src_out` of a node not added yet -> the input `dst_in`
        of a node already in the graph: the link that closes a loop.

        Every reference still points backwards. The connection is written
        inside the input socket's own definition, which comes earlier in the
        file, and it defines the new node's output socket inline; add() then
        names that socket by reference."""
        sock = None
        for s in self.node(dst)["sockets"]:
            s = self.deref(s)
            if s["Data"]["name"]["$value"] == dst_in and s["Data"]["type"] == "Input":
                sock = s
        if sock is None:
            raise KeyError(f"node {dst} has no input {dst_in}")
        c, o = self.h(), self.h()
        sock["Data"]["connections"].append({"HandleId": c, "Data": {
            "$type": "graphGraphConnectionDefinition",
            "destination": {"HandleRefId": sock["HandleId"]},
            "source": {"HandleId": o, "Data": {
                "$type": "questSocketDefinition", "connections": [{"HandleRefId": c}],
                "name": cname(src_out), "type": "Output"}}}})
        self.handles[o] = sock["Data"]["connections"][-1]["Data"]["source"]
        self.pending_out.setdefault(src_id, {})[src_out] = o

    def loop(self, nid, src, fact, actions, src_out="Out"):
        """A request answered any number of times: wait for `fact` above 0,
        set it back to 0, run `actions` (each adds the node id it is given),
        and wait again. Fed from `src`. A quest node fires again each time it
        is reached (docs/console-research.md, the re-arming loops). Returns
        the next free node id."""
        self.link(src, src_out, nid, "In")
        self.add_pause(nid, fact, "Greater", 0)
        self.link(nid, "Out", nid + 1, "In")
        self.add_set_fact(nid + 1, fact, 0)
        last, k = nid + 1, nid + 2
        for i, add in enumerate(actions):
            self.link(last, "Out", k, "In")
            if i == len(actions) - 1:
                self.link_back(k, "Out", nid, "In")
            add(k)
            last, k = k, k + 1
        return k

    def add(self, nid, type_name, fields, outputs, extra=()):
        """Append a node. Its inputs are the ones link() made for it; `outputs`
        are socket names; `extra` is (name, type) for sockets nothing links."""
        if nid in self.ids():
            raise SystemExit(f"node {nid} already exists")
        socks = [{"HandleId": self.h(), "Data": {"$type": "questSocketDefinition", "connections": [],
                                                 "name": cname("CutDestination"), "type": "CutDestination"}}]
        socks += [{"HandleRefId": h} for h in self.pending.pop(nid, {}).values()]
        reserved = self.pending_out.pop(nid, {})
        for name in outputs:
            if name in reserved:
                socks.append({"HandleRefId": reserved[name]})
                continue
            socks.append({"HandleId": self.h(), "Data": {"$type": "questSocketDefinition",
                                                         "connections": [], "name": cname(name),
                                                         "type": "Output"}})
        for name, kind in extra:
            socks.append({"HandleId": self.h(), "Data": {"$type": "questSocketDefinition",
                                                         "connections": [], "name": cname(name),
                                                         "type": kind}})
        data = {"$type": type_name, "id": nid}
        data.update(self.fresh(fields))
        data["sockets"] = socks
        node = {"HandleId": self.h(), "Data": data}
        self.graph["nodes"].append(node)
        self._index(node)
        return data

    def fresh(self, o):
        """A copy with new handle ids, so a field copied from another node is
        not a second definition of that node's handles."""
        o = copy.deepcopy(o)
        remap = {}

        def walk(x):
            if isinstance(x, dict):
                if "HandleId" in x:
                    remap[x["HandleId"]] = self.h()
                    x["HandleId"] = remap[x["HandleId"]]
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(o)

        def refs(x):
            if isinstance(x, dict):
                if "HandleRefId" in x and x["HandleRefId"] in remap:
                    x["HandleRefId"] = remap[x["HandleRefId"]]
                for v in x.values():
                    refs(v)
            elif isinstance(x, list):
                for v in x:
                    refs(v)
        refs(o)
        return o

    # The three node shapes the console patches use, in the shape gig 01's
    # own generator writes them (questkit/questgraph.py).

    def fact_condition(self, fact, cmp="Greater", value=0):
        return {"$type": "questFactsDBCondition", "type": {"HandleId": "0", "Data": {
            "$type": "questVarComparison_ConditionType", "comparisonType": cmp,
            "factName": fact, "value": value}}}

    def add_pause(self, nid, fact, cmp="Greater", value=0):
        return self.add(nid, "questPauseConditionNodeDefinition",
                        {"condition": {"HandleId": "0", "Data": self.fact_condition(fact, cmp, value)}},
                        ["Out"])

    def add_condition(self, nid, fact, cmp="Greater", value=0):
        return self.add(nid, "questConditionNodeDefinition",
                        {"condition": {"HandleId": "0", "Data": self.fact_condition(fact, cmp, value)}},
                        ["True", "False"])

    def add_set_fact(self, nid, fact, value=1):
        return self.add(nid, "questFactsDBManagerNodeDefinition",
                        {"type": {"HandleId": "0", "Data": {"$type": "questSetVar_NodeType",
                                                            "factName": fact, "setExactValue": 1,
                                                            "value": value}}},
                        ["Out"])

    def add_scene(self, nid, scene_depot, marker_ref, exits):
        return self.add(nid, "questSceneNodeDefinition", {
            "interruptionOperations": [], "notAllowedToBeFrozen": 0,
            "reapplyInterruptionOperationsAfterGameLoad": 0,
            "sceneFile": {"DepotPath": {"$type": "ResourcePath", "$storage": "string", "$value": scene_depot},
                          "Flags": "Soft"},
            "sceneLocation": {"$type": "scnWorldMarker",
                              "nodeRef": {"$type": "NodeRef", "$storage": "string", "$value": marker_ref},
                              "tag": cname("None"), "type": "NodeRef"},
            "syncToMusic": 0}, exits,
            extra=[("Default INT", "Output"), ("Default RET", "Output"), ("Prefetch", "Input")])


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, doc):
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
