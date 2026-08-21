# Gig 01: Negative Balance

## Premise

When a debtor can't pay Arasaka, Arasaka takes out a life-insurance policy on them,
then quietly contracts the kill and collects the payout. The debt ledger literally
turns people into revenue when it goes negative, hence the title.

Elena Ortega (Heywood; Jackie Welles used to help her family) is an accounts clerk
who handles reconciliations. She noticed dead debtors' accounts *clearing* instead
of freezing. Immediately, no disputes, no appeals, too many times. Her access was
revoked after she saw it. She lost no one: **she is the witness, and possibly the
next name on the list.** V hides her at El Coyote Cojo with Mama Welles, then
dismantles the scheme at its point of execution: the Arasaka office where she
worked, run by an exec named Hoshino who signs the contracts.

Timeline: during the main game, post-relic (Johnny present throughout).
Source material: the Negative Balance comic (63 pages, not part of this repo),
which doubles as the visual/staging reference for every beat.

## Quest flow

| # | Beat | Mechanic | Facts |
|---|------|----------|-------|
| 1 | Night holocall from UNKNOWN CALLER → Elena | Phone call scene (Elena AI-voiced). She reports the pattern; V sends her to El Coyote Cojo ("Stay with Mama Welles") and asks where she works | `cc_g01_started` |
| 2 | Location received | Elena sends workplace location; journal gig "Negative Balance" + map pin; V/Johnny recognize it as Arasaka-run | `cc_g01_accepted` |
| 2b | Daytime recon (optional beat) | Approach by day: goons + mech out front make the front door a non-option; establishes night entry | `cc_g01_recon_done` |
| 3 | Infiltration, LOCATION 1 | Arasaka Industrial Park, Arroyo/Santo Domingo. Street approach x=-177.761, y=-1472.829, z=7.477 (pin anchor `#std_arr_parking_spwn_179`). Guards inside (stealth-viable), hackable cameras | `cc_g01_office_reached` |
| 4 | The terminal | Interactable terminal inside the office → connect/upload sequence. This is where V learns the scheme AND that Hoshino is at the estate | `cc_g01_malware_done` |
| 4b | **Nix holocall** | V sends the terminal data to Nix (existing game netrunner, contact `contacts/nix`, merge a new conversation into his contact like Elena's). He decrypts it, names Hoshino and sends the estate location | `cc_g01_nix_done` |
| 5 | Travel, LOCATION 2 | **Arasaka residence on the hill (North Oak estate)**, objective + map pin appear only after Nix's call | `cc_g01_estate_reached` |
| 6 | Hoshino | At the estate: short exchange, combat-or-execute branch (both → dead) | `cc_g01_hoshino_dead` |
| 7 | Escape | Security responds; clear the way and leave | `cc_g01_escaped` |
| 8 | Epilogue, LOCATION 3 | El Coyote Cojo (pin anchor `#loc_sq022_el_coyote_cojo_bar_marker`): Mama Welles line, drink with Pepe, closing V/Johnny beat | `cc_g01_done` |

**Three-location structure (corrected 2026-08-11 in playtest):** the comic's
office and Hoshino scenes are different places. The office (industrial park) is
the intel; Hoshino lives at the **Arasaka estate on the hill in North Oak** - 
the luxury interior seen in the comic panels. The estate pin must appear only
after Nix's call, so the reveal drives the travel.

**Nix as the bridge:** V can't read what the terminal gives up, so the data goes
to Nix (Afterlife's netrunner). He's an existing character with an existing
journal contact, so his conversation merges into `contacts/nix`: no new contact
needed, and it grounds the gig in the game's world. His holocall is what turns
"something is wrong at Arasaka" into "Hoshino, at the estate on the hill".

Reward: **revised 2026-08-11 in playtest. The gig now pays.** It is still not
Elena's money (she never learns it was V); it is framed as what V skims on the
way through Hoshino's payment network, so the ending's silence is intact.
2500 eddies + 300 Street Cred, granted by `NegativeBalanceEncounter.GiveReward`
when `cc_g01_done` flips, guarded by the `cc_g01_rewarded` FACT, a script field
would reset on load and re-pay every time the save is loaded.

Previous decision, kept for context: no eddies at all, quest XP and in-building
loot only, on the grounds that the point of the ending is the silence.

## Dialogue script

**The lines that ship are `docs/dialogue.txt`.** It is generated from the scenes
themselves by `tools/gig01/dump_dialogue.py`, so it cannot disagree with what
plays. Fourteen scenes, 60 spoken lines. The reasoning behind each one, the comic
page it came from and any departure from it are in `tools/gig01/gen_scenes.py`,
one `build_*()` per scene.

A first draft of the script sat here until 2026-08-19, annotated for two
questions that are both settled now. It was removed because a second copy of the
dialogue is a copy that eventually disagrees with the first, and three of the
four conversations had already drifted from it. What its annotations were
asking:

- `[VDB: check]` asked whether a vanilla take could be reused for the line.
  Measured against all 62,992 vanilla lines: 3 of 59 had a verbatim match from
  the right speaker, which is too few to build a gig on.
  Exactly one vanilla take ships, Nix's "How's things, V?", and every other line
  is generated.
- `[REWRITE]` marked a placeholder waiting for a better line. Those rewrites
  happened in the generator, which is where the dialogue has lived since.

## Open design questions
- ~~Which existing interior plays the office~~, DECIDED: Arasaka location at
  x=-214.937, y=-1426.393, z=14.604 (captured in-game 2026-08-10; El Coyote Cojo
  bar at x=-1259.598, y=-989.166, z=12.037).
- Recon beat (comic p.12, daytime, goons + mech): full quest stage or just ambient staging on first approach?
- Female-V comic staging ("mija"). Write epilogue so it works for both voice types (Mama Welles says "mijo" variants exist in her recorded lines - verify).
- Does Elena get any final text after the gig (risk: undermines "she'll never know", current call: no).

## DONE: the ledger renders on the terminal screen (2026-08-11)

`source/scripts/Gig01_OfficeComputer.reds`. The ledger is now a file inside the
real narrative computer's Files menu instead of on-screen messages, and opening
it is the trigger. Full API notes: `docs/computer-ui-playbook.md`.

- Device: `q112_dvc_narrative_computer`, matched by owner position within 6 m of
  the captured desk spot (-251.915, -1456.364, 14.600); the device itself sits
  ~1.6 m away.
- Three `@wrapMethod`s on `ComputerControllerPS` - 
  `RequestFileThumbnailWidgetsUpdate`, `RequestMenuButtonWidgetsUpdate`,
  `RequestMainMenuButtonWidgetsUpdate` (all non-final, and the only route from
  the UI to `m_computerSetup`). Call one `@addMethod` helper that pushes a
  RECONCILIATION folder + `DataElement` into `m_filesStructure` and sets
  `m_filesMenu = true`. Gated on `cc_g01_accepted > 0`.
- Text: `cc-g01-file-title` / `-body` / `-owner` / `-date` / `-folder`, resolved
  at runtime with `GetLocalizedTextByKey` (the widget uses plain
  `inkTextRef.SetText`, so it needs finished strings, and real newlines).
- **No trigger hook.** `DataElement.questInfo.factName = cc_g01_terminal_done`;
  the engine's `OpenDocument` → `ResolveQuestInfo` → `AddFact` does the rest.
  Because `AddFact` increments, `Gig01_Encounter.reds` now compares that fact
  with `> 0`; the quest phase already used Greater-than-0.
- The old proximity trigger (1.5 m) and the office branch of `TerminalStep` are
  gone; the estate malware upload keeps its on-screen sequence (`UploadStep`).

Confirmed in playtest, 2026-08-11: the device is NOT password-locked, so no
`TurnAuthorizationModuleOFF()` call is needed. Don't add one. The file lists and
reads correctly in the computer UI.

**Read -> download -> objective (revised after the first playtest).** The
document must contain only the document; what V *does* with it plays as HUD
banners, and the "get clear of the compound" objective comes last. The chain is
now three facts:

1. `cc_g01_ledger_read`: set by the ENGINE when V opens the file
   (`DataElement.questInfo.factName`). Increments, so test `> 0`.
2. `DownloadStep` starts on the next tick after the read, the design call
   (2026-08-11): trigger on opening the file, do not wait for V to walk away.
   Tradeoff: the device zoom hides the HUD, so beats landing while V is still
   reading are not seen. Steps are 1.6 s apart (~6.4 s total) so most of it is
   caught on the way out. If none of it turns out to be visible, gate ONLY the
   banners. Never the fact - on `PlayerStateMachine.IsUIZoomDevice` going false.
3. `cc_g01_terminal_done`: set by the LAST step of `DownloadStep` in
   `Gig01_Encounter.reds`, which is what the quest phase waits on.

**Leaving the compound** (`cc_g01_left_compound`, gates Nix's call) is measured
from the TERMINAL at >110 m, not from the compound entry. The terminal sits
~63.5 m inside the entry, so an entry-anchored radius must exceed that before it
means anything: that is why it was 150 m and felt like a hike. 110 m from the
terminal is ~46 m past the entry and still cannot fire inside the building.
Lower it further only with that 63.5 m figure in mind.

**Two bugs found in the first pass of this, both fixed, do not reintroduce:**

- `@wrapMethod OnToggleZoomInteraction` does NOT fire when a computer screen is
  closed (exiting takes another route). The download then sat on the 5 m
  distance fallback, so the objective only completed once V wandered away from
  the desk. It looked like a dead trigger. Detection is now
  `PlayerStateMachine.IsUIZoomDevice`, which `deviceBase.SetZoomBlackboardValues`
  drives for every device zoom. There has never been any enemy/combat condition
  on this chain.
- `questInfo` is not persistent, so a reloaded element can come back with no
  `factName` and opening the file then fires nothing at all.
  `CCG01PromoteRead` covers that: `wasRead` IS persistent, vanilla sets it on
  open and then calls `RequestMenuButtonWidgetsUpdate` (which we wrap), so the
  read is recovered on the spot and on any later visit.

`DownloadStep` uses `SimpleScreenMessage.type` for the coloured banners
(`Neutral` for the download %, `Connection` for the Nix send). The encounter
tick has a distance fallback (>5 m from the terminal) so an exit path that never
fires the zoom action cannot strand the objective.

Still to confirm in the playtest:
1. The banners are actually visible, and in order: download % -> complete ->
   sending to Nix -> sent -> only THEN the new objective.
2. Save/reload standing at the terminal, reopen: exactly ONE ledger file (see
   the persistence trap in the playbook).

## Dialogue now uses real subtitles (2026-08-11, VERIFIED)

Hoshino's scene and the El Coyote epilogue were playing as red warning banners.
They now go through the game's subtitle panel via the UIGameData blackboard - 
see `docs/architecture.md` "Spoken lines without a .scene". Warning banners are
kept only for system feedback (the ledger download beats).

Consequence for the text: `scnDialogLineData` has a separate `speakerName`, so
the line strings no longer carry a "Hoshino: " / "V: " prefix. Speaker labels
are their own LocKeys (`cc-g01-spk-v`, `-spk-johnny`, `-spk-mama`, and the
existing `cc-g01-hoshino-name`). Keep it that way when adding lines.

V's "Ledger's closed." after the kill is now line index 3 rather than a
hardcoded English `Notify`, and lives in localization as `cc-g01-hoshino-04`.

Note: subtitles respect the player's subtitle setting. If they are off in the
game options these lines will not show. That is correct behaviour, not a bug.

## Ending rewritten + payout (2026-08-11, VERIFIED)

**The gig used to complete itself from the street.** `Gig01_NegativeBalance.reds`
still carried a pre-encounter-layer shortcut that set `cc_g01_at_coyote` on a
15 m proximity to the bar. Wide enough to fire outside, before V went in, and
racing the encounter layer's own 6 m epilogue. Removed. The ending belongs to
`NegativeBalanceEncounter` only; do not add a second trigger for it.

The epilogue is now two objectives:

- `obj_epilogue` "Stop by El Coyote Cojo" -> completed by stepping inside
  (6 m of the bar marker), which sets `cc_g01_at_coyote` and starts the
  conversation.
- `obj_mama` "Talk to Mama Welles" (no pin, V is already there) -> completed by
  the LAST epilogue line, which sets `cc_g01_mama_talked`. Only then does the
  quest phase close the gig and the payout fire.

**Prefer the real Mama Welles, spawn a stand-in only if absent** (playtest,
2026-08-11). She usually IS in El Coyote Cojo but not dependably (time of day +
quest state), so:

- `FindMamaWelles` runs a `TSQ_NPC` targeting query (`TargetingSet.Complete`, so
  it sees her through the bar walls) and matches on `GetRecordID()`. One query
  finds either her or our stand-in, since both carry the same record.
- Found -> trigger on HER live world position within 3.5 m. Cannot fire from the
  street, and does not care if she wanders off her mark.
- Not found, V within 15 m, for 4 consecutive ticks -> spawn the stand-in. The
  tick delay matters: interior NPCs may not have streamed in the instant V walks
  in, and spawning on the first miss would double her up.
- `DespawnMamaWelles` only ever removes OUR stand-in (`m_mamaSpawned` is false
  when the real one was found), so the base-game NPC is never deleted.

**Her record is `Character.Mama_Welles`: capital M and W.** Confirmed
2026-08-11 by inspecting the live NPC with the dev menu's look-at dump. Every
lowercase spelling returns false from TweakDB; TweakDBIDs are case-sensitive, so
do not "tidy" this. Nothing in the TweakDB files revealed it: `mama_welles`
appears in the string pool only as a bare name with no group, and neither the
sector cache nor CET's tweakdbstr gave up the full ID. Runtime inspection was
the only route. The two dump buttons in the CET dev menu exist for this.

Other useful ids found the same way: `Character.Elcoyote_Barman`,
`Character.q000_kid_coyote_staffer`.

The stand-in's spawn point is MEASURED, not guessed: `-1262.178, -998.805,
12.057`, yaw `-80.3`, captured off the live NPC with the dev menu's
[CAPTURE THE NPC I'M LOOKING AT] (the capture log records the record id
alongside, confirming it was Mama Welles and not the barman).

**She stands ~10 m from `CCGig01Places.Coyote()`**: the bar
marker is the spot V walks to, not where she is. The earlier guessed offset was
~14 m out, in the wrong direction. Anything about her should be measured against
`CCGig01Places.MamaWelles()`, which is why the spawn decision uses that and not
the bar marker. Both are teleport presets in the dev menu.

The epilogue cannot strand: if she is neither found nor spawnable after ~30
ticks within 15 m of her spot, the conversation plays anyway. An ending that
cannot be finished is worse than one without her on screen.

LIMITATION: still proximity + a scripted line sequence, not real dialogue
choices, see below.

## Batch C: the three conversations are real scenes now (2026-08-11, UNTESTED)

Built, not yet playtested. Method notes live in `docs/scene-playbook.md`; the
decisions and their reasoning are in `docs/architecture.md`. What changed here:

- **Elena's opening is a holocall.** She rings, V answers, they talk, and V's
  three replies are dialogue choices instead of journal reply entries. Same
  beats and same text as the SMS thread it replaces, so the story is untouched.
  `Gig01_Holocall.reds` drives the chrome; `gig01_elena_call.scene` has the
  words. She keeps `PhoneAvatars.Avatar_Unknown`: the comic's UNKNOWN CALLER.
- **Hoshino** (`gig01_hoshino.scene`) opens with a real choice: name what he
  signed, or say nothing.
- **The epilogue** (`gig01_epilogue.scene`) has two choice hubs. Johnny's
  closing line is NOT in it. His record id is not discoverable offline, so it
  still plays as a subtitle, fired when the scene exits, and it is still the
  thing that ends the gig.
- Elena needed a Character record (`source/tweaks/elena.yaml`) purely so her
  name appears over her subtitles. She is a voice, never a body: the scene
  spawns her a kilometre away and a hundred metres down. Same for the Hoshino
  and Mama Welles scene actors. The bodies the player sees are still the ones
  `Gig01_Encounter.reds` spawns or finds.
- The SMS thread is intact behind `USE_SMS_THREAD` in `tools/gig01/gen_questphase.py`.
  Flip it, regenerate, rebuild: that is exactly v0.2.0's opening.

The section below is what led here, kept because the reasoning still holds.

## Dialogue choices: needs a .scene (researched 2026-08-11)

Asked whether the epilogue could show pick-a-line choices like real missions.
Findings from the decompiled UI:

- The choice UI is driven by `UIInteractions.DialogChoiceHubs`, a Variant
  holding `DialogChoiceHubs { choiceHubs: [InteractionChoiceHubData] }`, with
  `ActiveChoiceHubID` and `SelectedIndex` alongside it.
- **Nothing in script ever writes those hubs.** The only script access is
  `player.swift` CLEARING them. Hubs are produced by the native
  interaction/scene system, and a selection is dispatched back to the scene that
  owns it. `SelectedIndex` is the highlighted row, not a commit.

So a script-injected hub could plausibly DISPLAY choices, but there is no
owner to route the confirm press to. Capturing it would mean hooking input and
the dialog controller, which is the kind of guesswork that has bitten
this project before. The supported route is a `.scene`, which is already the
plan for Batch C (reference `californication.scene`). Recommendation: keep the
scripted subtitle exchange until the epilogue is built as a real scene, then get
choices for free.

## Radius audit (2026-08-11)

There are NO combat, enemy-count or "area clear" conditions on any of these - 
they are pure distance, and always have been. Current values:

| Fact | Anchor | Radius | Why |
|---|---|---|---|
| `cc_g01_office_reached` | compound entry | 60 m | unchanged |
| `cc_g01_left_compound` | office terminal | 110 m | terminal is ~63.5 m inside the entry, so this is ~46 m past it |
| `cc_g01_escaped` | Hoshino | 160 m | gate is ~139 m from him, so this is ~21 m past the gate (was 250 m) |
| `cc_g01_at_coyote` | bar marker | 6 m | must be inside |

When shrinking any of these, check it against the distance from the anchor to
the furthest point the player can legitimately still be "inside": that is what
makes the numbers look arbitrarily large.

## Estate arrival: tunnel false-positive (fixed 2026-08-11, VERIFIED)

The road to the North Oak estate runs through a tunnel UNDER the house. Arrival
used a 90 m `Vector4.Distance` sphere around the gate/house, and although that
distance is 3D the radius was big enough to swallow the tunnel, so driving past
underneath set `cc_g01_estate_reached` AND spawned all the estate security.

Fixed with `CCGig01Places.Near(pos, anchor, radiusXY, below, above)`:
horizontal distance (`Vector4.Distance2D`) plus an asymmetric altitude band,
since the failure mode is always being *below* the anchor. Now gate = 45 m XY /
-12..+25 m, house = 70 m XY / -12..+25 m, checked separately (they are ~139 m
apart horizontally and ~9 m apart vertically).

TUNING NOTE: the -12 m floor is a judgement call, not a measurement, the
tunnel's real depth was never captured. If a drive-through still triggers it,
capture the tunnel position with the CET dev menu's [Save current position] and
set the floor from the actual gap.

## Build status: TAG `gig-01/v0.2.0` (2026-08-11, VERIFIED IN-GAME)

playtesting covered the whole chain and confirmed "everything works well". This is
the known-good point to return to; the sections above explain each mechanism and
every trap found getting there.

Verified end to end:
- Elena's holocall thread, quest-driven, natural pacing, working replies
- Gig presents as a Street Story with native map pins, distance and tracking
- Arasaka security spawns at the office and the estate
- **Office ledger renders inside the real narrative computer's UI**; opening the
  file is the trigger, then the download/send banners, then the objective
- Nix hand-off, estate travel, Hoshino, malware upload
- **Hoshino and the epilogue play as real subtitles**, not warning banners
- **Ending requires being inside El Coyote Cojo and talking to Mama Welles** - 
  the real one when she is there, a spawned stand-in when she is not
- Payout on completion (2500 eddies + 300 Street Cred), granted once

Fixed this round, each with a "do not reintroduce" note in the sections above:
1. `tools/check-scripts.ps1` never compiled anything and reported success on
   files that were not valid redscript. Every green result before 2026-08-11 was
   meaningless. Rewritten + `-SelfTest`. See architecture.md "Toolchain
   reliability" and the `scc.exe` / pure-ASCII gotchas in docs/gotchas.md.
2. The ending completed from the street (15 m proximity leftover).
3. Estate arrival fired from the tunnel UNDER the house (90 m sphere).
4. `@wrapMethod OnToggleZoomInteraction` never fires for computers, which
   stalled the terminal objective until V wandered 5 m away.
5. `questInfo` is not persistent, so a reloaded document could open and fire
   nothing, now backstopped by `wasRead`.
6. `Character.Mama_Welles` is case-sensitive; every lowercase spelling fails.

Known-good environment: game 2.31, WolvenKit 8.20.0, RED4ext 1.30.0,
ArchiveXL 1.27.1, TweakXL 1.11.4, Codeware 1.20.3, CET 1.37.1.

**ALL THREE OF THOSE ARE DONE.** The line that stood here, "NEXT: Batch C - 
build the epilogue as a real `.scene`; Elena and Hoshino AI voices via
Audioware; V/Johnny existing-line audit", is closed on every clause:
the epilogue is `gig01_epilogue`, one of fourteen scenes; the voices are
ElevenLabs for all six speakers, not Audioware for two; and the existing-line
audit was run against the whole 62,992-line corpus and killed the reuse premise
(3 matches out of 59).

**Build status: released at 1.2.3 (2026-08-21).** The gig plays end to end,
fully voiced and lipsynced. Playtest, 2026-08-14, on the last three builds:
*"Everything is perfect"*, *"It all works perfectly"*. Everything from 1.1.x
onward is field bug fixes on top of that, and `CHANGELOG.md` is the
release-by-release account.

One of those fixes changed how a beat is allowed to start rather than what it
contains: Johnny's three free-roaming beats stage him where V is standing, so
the gig now keeps V on foot for them instead of letting a call be answered at
speed. `backlog.md` 16 has the reasoning, including why moving him or delaying
him were both wrong.
What is still open is in `docs/backlog.md`; it is short, and none of it blocks a
release.

## History

See `docs/architecture.md` for how each subsystem works and why, and
`docs/backlog.md` for the questions that were asked and how they closed. The
per-mechanism sections above hold this gig's own reasoning and traps.
