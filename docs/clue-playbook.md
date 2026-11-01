# Clues: a scanner hunt with a counter

How to put objects in the world that the player finds with the scanner.
Each one shows your own title and your own text when scanned. The objective
counts them as "[1/3]", and your quest moves on when all are found.

This is the game's own clue hunt, the one its NCPD activities and its
tutorial use. Everything here was measured in game 2.31. The worked example
is gig 04's van: `tools/gig04/gen_clues.py`, `source/tweaks/clues.yaml` and
the clue section of `tools/gig04/gen_questphase.py`.

Read `shard-playbook.md` too if the hunt ends on a readable object. The two
work side by side.

## A clue is five separate things

| | what it is | where it lives |
|---|---|---|
| the OBJECT | an entity file with a scanning component | your `.ent` |
| the PLACE | a named node in your own streaming sector | your `.streamingsector` |
| the RECORD | the title and text the scanner shows | your `.yaml` |
| the SIGNAL | a fact the scan sets when it finishes | the `.ent` |
| the COUNT | a counted objective and one node per clue | your `.journal` and quest phase |

Each one fails without a visible error. A clue that glows but never counts is
the SIGNAL half done. A clue that counts but shows a raw key is the RECORD
half done.

## 1. The object: copy a shipped clue

Do not build the entity from nothing. Lift a vanilla clue file whole and
change four things.

The NCPD activity `ma_bls_ina_se1_07` has two clues and both shapes:

| file | what it draws |
|---|---|
| `ma_bls_ina_se1_07_trail.ent` | a blood decal on the ground |
| `ma_bls_ina_07_case.ent` | a mesh |

Each is a `gameObject` with a `gameScanningComponent`. Its `clues` array holds
one `FocusClueDefinition`. That definition names the record and the fact.

Change only these:

1. The decal material, or the mesh and its appearance.
2. `clueRecord`: your own record (section 3).
3. `clueGroupID`: a name of your own, one per clue.
4. `facts`: your own fact (section 4).

Keep the components from `compiledData`, where the handles are defined
inline. That is the shape WolvenKit writes back. The `components` list holds
the same components by reference.

Commit the lifted JSON beside the generator. An ordinary build then needs
neither the game nor WolvenKit.

## 2. The place: a named entity node

Put each clue in your own sector as a `worldEntityNode` pointing at your
`.ent`. Copy the vanilla clue's node: no instance data, the entity node
flags. Name it in the long form, `$/03_night_city/<district>/#<name>`. An
unnamed node in a mod sector does not load.

**Read the mesh's bounding box before you set the height.** A mesh's origin
is not always at its base. The game's duffel bag
(`int_accessories_001__duffel_bag.mesh`) runs from 0.467 m below its origin to
0.015 m above it. Placed at ground height, it sat almost half a metre in the
ground. Its box is in the `.mesh` file's `boundingBox`.

## 3. The record: the scanner's title and text

The text the scanner shows is a TweakDB record in the `scanning.` namespace.
Copy a vanilla one with TweakXL and change the text keys:

```yaml
scanning.my_clue_blood:
  $base: scanning.ma_bls_ina_07_blood_trail_conclusion
  localizedName: my-clue-blood-name
  localizedDescription: my-clue-blood-desc
```

Put the two keys and their text in your `onscreens` localization file.

**The entity's own name needs the hash form.** The scanner's header comes from
the entity's `displayName`, not from the record. A bare key there shows as the
raw key in capitals. Write `LocKey#` followed by the FNV-1a 64 hash of the
bare key, in decimal:

```
displayName: { unk1: "0", value: "LocKey#<fnv1a64('my-clue-blood-name')>" }
```

This is the same hash ArchiveXL files your text under. `questkit.community.fnv1a64`
computes it.

## 4. The signal: a fact when the scan finishes

`FocusClueDefinition.facts` is a list of fact operations. The game runs them
when the scan of that clue completes:

```json
"facts": [{ "$type": "SFactOperationData",
            "factName": "my_clue_blood", "factValue": 1,
            "operationType": "Set" }]
```

Your quest waits on that fact. That is how the vanilla activity hears its own
clue (`ma_bls_ina_se1_07_blood_found`).

**The facts fire only if the clue has at least one step.** A step is an entry
in `extendedClueRecords`. The scripts decide this in two places:

- `scanningComponent.swift` gives the clue's conclusion a time of 1.0 when
  `extendedClueRecords` has entries, and 0.0 when it is empty.
- `gameObject.swift`, `ResolveFocusClueConclusion`, runs the facts only when
  that time is at least the scan's progress. At 0.0 it never is.

So an empty list scans, shows the text and sets nothing. The counter stays at
zero.

**A step with the same record as the conclusion lists the clue twice.** The
vanilla blood trail has a step record of its own beside its conclusion. Give
your clue one step with no record:

```json
"extendedClueRecords": [{ "$type": "ClueRecordData",
    "clueRecord": { "$type": "TweakDBID", "$storage": "uint64", "$value": "0" },
    "facts": [], "percentage": 0.0, "wasInspected": 0 }]
```

The conclusion keeps its 1.0. The scanner skips a step whose record is not
valid, so nothing extra is listed.

## 5. The count: "[0/3]" on the objective

The tracker's counter belongs to the objective. Set its total in the journal:
`gameJournalQuestObjective.counter`, here 3. The tracker then shows "[0/3]"
after the objective's text.

Add one with a quest node per clue. The shape is the game's tutorial counter,
node 308 of `q000`:

```
questJournalNodeDefinition
  type: questJournalQuestObjectiveCounter_NodeType
        path: <the objective's journal path>
```

Its input socket is `Increment`, not `In`.

Wire one branch per clue off the point where the objective opens:

1. A fact pause on that clue's fact.
2. Its output into a counter node's `Increment`.

A clue scanned before the objective opened counts at once, because the pause
finds the fact already set.

## 6. The end of the hunt

Close the objective with one more pause, on all the clue facts at once (a
`questLogicalCondition`, operation AND). Wait a second before closing, so the
last count is on screen before the objective goes.

**Let the reward end the hunt too.** A player who finds what the clues point
to before scanning them should not be stuck. Gig 04 ends its hunt on either of
two facts:

1. A side branch waits on all three clue facts and sets `clues_all`.
2. The main chain waits on `clues_all` OR the shard taken, with one pause.

One pause on two facts, rather than two branches into the next node, keeps
the rest of the chain from running twice.

## 7. Showing where to look

A clue hunt wants an area, not a point. Draw it on the minimap with a trigger
area node and anchor the objective on it. `map-pins-playbook.md`, "A quest
area drawn on the minimap", is the recipe.

The outline can be any polygon. Capture its corners in game, walking the edge
you want, and use them in order. Check every clue is inside it, and put the
objective's anchor at the middle of the corners.

## Checks before a playtest

- Scan each clue. The header and text are yours, not a raw key.
- The counter goes up by one on each scan, never two.
- Each clue is listed once on the scanner.
- Each object sits on the ground, not in it and not above it.
- Take the reward first on a second run. The hunt ends.
