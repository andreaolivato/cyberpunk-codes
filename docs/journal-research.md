# Journal system research (2026-08-10)

How Cyberpunk 2077 stores phone contacts/messages/gigs, and how mods extend them.

## Base game structure

- The entire journal is one cooked resource: `base\journal\cooked_journal.journal`
  (4.5 MB, ~68 MB as JSON; extract and serialize it with WolvenKit if you need
  to grep it).
- Contact anatomy (see JSON around the `teddy` / `zane` entries):
  - `gameJournalContact`: fields: `id` (string), `name` (LocKey), `avatarID`
    (TweakDBID like `PhoneAvatars.Avatar_Teddy`), `isCallableDefault`,
    `useFlatMessageLayout`, `type: "Caller"`, `entries: [...]`
  - inside `entries`: `gameJournalPhoneConversation` → `entries` of
    `gameJournalPhoneMessage` (fields: `id`, `delay`, `sender`, `text` LocKey,
    `attachment`, `isQuestImportant`)
  - player replies: `gameJournalPhoneChoiceGroup` / `gameJournalPhoneChoiceEntry`
    (verify exact names in JSON when authoring)
- Quests/gigs live in the same tree under their own containers; codex links use
  `gameJournalPath` with `realPath` like `contacts/judy`.

## How mods add entries: ArchiveXL journal extension

- Ship our own `.journal` resource in our `.archive`, then declare it in the
  mod's `.archive.xl`:

  ```yaml
  journal:
    - mod\negative_balance\journal\gig01.journal
  ```

- Merge semantics (from ArchiveXL source, `src/App/Extensions/Journal/Extension.cpp`):
  entries are matched by id-path against the base tree; existing containers are
  descended into, missing entries are appended (`EmplaceBack`) to the matched
  parent. So our file mirrors the tree down to the parent container
  (e.g. root → contacts) and contains only our additions (contact `elena_ortega`).
- ArchiveXL also processes journal map pins (world node refs) from merged entries.

## Gotchas learned the hard way

- **Custom string LocKeys in journal files must be written WITHOUT the `LocKey#` prefix**
  (`"value": "cc-g01-msg-01"`). ArchiveXL converts any non-prefixed value to
  `LocKey#<FNV1a64>`; prefixed values are assumed numeric and left alone (shown raw in UI).
  The localization side registers `secondaryKey` under the same FNV1a64, keys match only
  via this convention. (AXL `Journal/Extension.cpp: ConvertLocKeys`).
- `gameJournalQuestMapPinBase` is abstract. Use `gameJournalQuestMapPin` with a null
  NodeRef reference; AXL then uses `offset` as an absolute world position.
- JournalManager scripted API: `GetEntryByString(path, className)`,
  `ChangeEntryState(path, className, state, notifyOption)`: className required;
  in CET, enum args accept strings ("Active", "Notify").
- `unk1` on LocalizationString is an editor CRUID, not a hash, 0 is fine for mods.
- Deceptious's mods are working references: numeric-LocKey style
  journal + localization, plus `.questphase`/`.scene` examples (extract them
  from `archive\pc\mod\*.archive` with WolvenKit).

## Map pins: SOLVED. See `docs/map-pins-playbook.md`

Native map pins, journal distance, tracking and GPS routing all work for
mod-added quests. The playbook is the authority; this file no longer describes
pin mechanics.

Two earlier conclusions recorded here were WRONG and have been deleted, because
both were measured while the pin journal entries were never activated:

- *"journal-merged quest map pins are systemically broken"*. They are not. The
  engine simply never queries a pin entry whose state is Inactive, which made
  every downstream layer look dead (including the reference mods, when their
  objectives were force-activated out of context).
- *"ship a streaming sector with marker nodes and reference those"*, custom
  marker nodes shipped in a mod sector do NOT resolve, with either
  `worldStaticMarkerNode` or `worldTriggerAreaNode`. **This is TRUE, was briefly
  overturned on 2026-08-14 and re-confirmed the same evening**: Californication
  and OneMoreLight both do it, and playtesting confirmed their pins are broken in
  game too. The log says `Can't resolve mappin ... reference`: the name never
  registers.

**Anchor to a base-game node in an ALWAYS-LOADED sector**, and put the exact
vector from it to the target in the pin's `offset`
(`python tools/find_pin_anchors.py <x> <y> <z>`). An ordinary base-game node is
not enough: since the position now comes from the node rather than from a
patched cooked table, the node must be STREAMED IN when the quest activates the
pin, and a quest does that while V is across the city. Full recipe and the three
failure modes: `docs/map-pins-playbook.md`.

The mod's own marker sector and its streaming block were deleted on 2026-08-14
along with `tools/patch_cooked_mappins.py`; the mod ships no base-game files.

## Phone messages and reply choices

An SMS thread is a cheaper conversation than a holocall: no scene, no audio, no
actor. This gig shipped one in v0.2.0, then replaced both its conversations with
holocalls and removed the thread on 2026-08-15. The recipe is kept here because
it works, it is verified in game, and it is the right tool when a beat needs a
back-and-forth that nobody has to voice.

Three entry types nest inside a contact:

```
gameJournalContact
  gameJournalPhoneConversation        id, title (a LocKey)
    gameJournalPhoneMessage           one NPC message
    gameJournalPhoneChoiceGroup       a set of player replies
      gameJournalPhoneChoiceEntry     one reply
```

The message and the choice entry, with the fields that matter:

```python
{'$type': 'gameJournalPhoneMessage',
 'attachment': None,
 'delay': 3,                 # SECONDS BEFORE THIS MESSAGE ARRIVES
 'id': 'cc_g01_msg_01',
 'imageId': tweak(None),
 'isQuestImportant': 0,
 'journalEntryOverrideDataList': [],
 'sender': 'NPC',            # or 'Player' for a sent message
 'text': lockey('msg-01')}

{'$type': 'gameJournalPhoneChoiceGroup',
 'entries': [{'$type': 'gameJournalPhoneChoiceEntry',
              'id': 'cc_g01_ch_01a',
              'isQuestImportant': 1,
              'journalEntryOverrideDataList': [],
              'questCondition': None,
              'text': lockey('ch-01a')}],
 'id': 'cc_g01_ch_01',
 'journalEntryOverrideDataList': []}
```

The quest phase drives it by activating each entry in order, and waits for the
player on a choice by pausing on the choice ENTRY rather than the group:

```python
step(add_journal('gameJournalPhoneConversation', CONV, notify=0), in_sock='Active')
step(add_journal('gameJournalPhoneMessage', CONV + '/cc_g01_msg_01'), in_sock='Active')
step(add_journal('gameJournalPhoneChoiceGroup', CONV + '/cc_g01_ch_01', notify=0),
     in_sock='Active')
step(add_pause_journal('gameJournalPhoneChoiceEntry',
                       CONV + '/cc_g01_ch_01/cc_g01_ch_01a'))
step(add_journal('gameJournalPhoneMessage', CONV + '/cc_g01_msg_04'), in_sock='Active')
```

Two things that are easy to get wrong:

- **Pace the thread with each message's own `delay`, never with graph timers.**
  A `questRealtimeDelay` stalls while a menu is open, and the phone IS a menu, so
  a graph-timed thread stops advancing exactly when the player is reading it.
  See `docs/gotchas.md` #3.
- **A contact must exist before it can be addressed**, by a message or by a call.
  `HudPhoneGameController` resolves a caller by walking
  `JournalManager.GetContacts`, so activate the `gameJournalContact` first.

Answered while authoring: the choice-group shape is above; the onscreens
LocKey strings are registered through the `localization:` block of the `.xl` and
must list every locale (see `docs/gotchas.md` and the archive extension file);
`PhoneAvatars.Avatar_Unknown` works as-is for an unknown caller and needs no
TweakXL record; and the top-level container does not need base metadata cloned
into it.
