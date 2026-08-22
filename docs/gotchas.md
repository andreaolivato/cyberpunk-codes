# Critical gotchas

Things that cost hours. Numbered, because code comments cite them by number.
Never renumber. Append.

1. Journal LocKeys take string keys WITHOUT the `LocKey#` prefix. See
   `journal-research.md`.

2. Map pins work natively, but need all three ingredients. Read
   `map-pins-playbook.md` before touching pins.
   - pin entry authored
   - pin entry activated by the quest phase
   - a resolvable base-game NodeRef in an always-loaded sector as anchor

   Custom marker nodes in a mod streaming sector never resolve. There was a
   fourth ingredient, patching the game's cooked mappin tables, until
   2026-08-14. ArchiveXL does that itself, and the patched tables suppressed it.

3. Quest-phase realtime delays stall while menus are open. Pace phone threads
   with the journal messages' own `delay` fields, not graph timers.

4. `JournalManager.GetEntryHash` returns Int32 (signed). AXL and world hashes
   are the same values as Uint32. Hash is Murmur3-32(path, seed 0x5EEDBA5E).

5. `gameJournalQuestMapPinBase` is abstract. Use `gameJournalQuestMapPin` with a
   null NodeRef.

6. Gig quests need `"type": "StreetStory"` on the gameJournalQuest, or they
   present as main quests.

7. RED4ext occasionally fails to load at launch. Symptom: no new red4ext log,
   and a "compilation failed / install Codeware" popup listing every script mod.
   Benign, just relaunch.

   Tell-tale: established mods like They_Will_Remember fail with the same
   "GetDynamicEntitySystem not found" error. Confirm with `check-scripts.ps1`,
   which compiles offline and passes. A popup naming only ONE mod is a real
   error. Read the actual message rather than assuming the usual cause.

8. If the repo lives in a synced folder, pause sync when file locks misbehave.
   WolvenKit and a sync client fight over the same files.

9. `scc.exe` fails silently when misinvoked. `scc -compile <dir> <cache>` with a
   flat directory, or one that does not exist at all, prints "Compilation
   complete" and exits 0 having compiled nothing.

   It only works on `<root>\r6\scripts` with a sibling
   `<root>\r6\cache\final.redscripts`, because it derives the game root by
   walking up. `check-scripts.ps1` got this wrong from the start and passed
   files that were not valid redscript. That is how a guessed-method-names
   attempt shipped a broken bundle "after a clean check" (found and fixed
   2026-08-11). It now refuses to report success unless scc printed "Compiling
   files in". Re-run
   `check-scripts.ps1 -SelfTest` after touching that script.

10. A script-issued phone call must be `questPhoneCallMode.Audio`. `Video` hard
    crashes the game the moment the player answers.

    Video renders a live feed of the caller. Vanilla stages a body for it via
    `questCallContact_NodeType.prefabNodeRef = "#holocalls_studio"`, a field
    `questTriggerCallRequest` does not have. See `scene-playbook.md`.

11. On a hard crash read `%LOCALAPPDATA%\CD Projekt Red\Cyberpunk 2077\
    CrashInfo.json`. It has position, district and session length when every
    other log has nothing. CET's logs are buffered and lose the last seconds;
    the dev menu's `call_trace.log` opens, writes and closes per line, so it
    survives.

12. `check-scripts.ps1` compiles the DEPLOYED scripts, not the repo. Deploy
    first, then check.

    Run it the other way round and it faithfully compiles the previous version
    and reports success, which is a green light on untested code. It cost a
    failed launch on 2026-08-12. It now refuses to run when the repo and the
    deployed copy differ, so the mistake is no longer possible. Keep the order
    right anyway.

13. A redscript ResRef literal still processes escapes, so backslashes in a
    depot path must be doubled. Write `r"mod\\my_mod\\entity\\thing.ent"` to
    mean `mod\my_mod\entity\thing.ent`.

    A single backslash turns `\n` (as in `\negative_balance`) into a newline and
    the file will not parse. The error is a bare "syntax error, expected one of
    ..." with no mention of paths. Worked example: `PlaceSceneJohnny` in
    `Gig01_Encounter.reds`, which spawns the workspot device from
    `r"mod\\negative_balance\\entity\\cc_g01_workspot.ent"`. This entry was
    itself mangled by the bug it describes until 2026-08-12.

14. Redscript has no `continue`. The error is `unresolved reference 'continue'`,
    which reads like a missing function rather than a missing keyword. Guard the
    loop body with a `Bool` instead. `break` does exist.

15. Four ways Johnny's apparition broke, each from a "safe" change elsewhere.
    Each came from changing one thing without checking what else reads it, and
    the pattern is not specific to Johnny.

    - **A staging window bounded by someone else's fact.** His spawn window
      ended at `cc_g01_call_done`, owned by the phone state machine. Speeding
      that machine from 2 s to 0.2 s shrank the window below the 1.5 s tick and
      he stopped appearing. Bind a window to the beat's own fact. They all use
      `cc_g01_johnny_done` now.
    - **A liveness check that fires during the spawn it is checking.** "Marked
      spawned but does not resolve, so respawn" is true for the first tick or
      two of every spawn, because entities stream in asynchronously. It
      respawned him endlessly and he never rendered. Treat absence as meaningful
      only after the entity has resolved at least once.
    - **"Still there" is not "still visible".** `phantomVisibleStates` is
      `["RootMotion","Workspot"]`, so he renders only while in a workspot. The
      entity keeps resolving after he leaves one.
    - **A port that carried the code and not the comment.** Placement moved to
      `PlaceSceneJohnny` and left `dev.orientation` behind, so Johnny faced
      world-yaw-0 wherever V stood. Most beats looked right by luck, which is
      why it survived two playtests. The fix was one line, sitting in a comment
      forty lines below. When porting a routine, carry over what its comments
      record, not only the code.

16. A lipsynced NPC must be the SCENE's own actor, because lipsync lands on the
    line's speaker and only a scene can own a speaker.

    **The second half of this entry was wrong for months and is corrected
    here.** It read "and script-placed: only a script can put a body where the
    player is". A scene can, and the whole architecture built on that sentence
    is gone. See #31, `backlog.md` 9, and the recipe in `scene-playbook.md`,
    "STAGING A CHARACTER WHO SPEAKS, LIPSYNCS AND STANDS BESIDE V".

    What still holds, each of it a test session:

    - A workspot is what makes the actor exist at all.
      `gamePhantomEntityComponent.phantomVisibleStates` is
      `["RootMotion", "Workspot"]`, so without one he is invisible AND
      untargetable. Fire it at t=0 of the scene's FIRST section.
    - The SCENE must time the exit, and must play it. It is the only thing that
      knows its own length, and it deletes its actors on the frame it exits.
    - A scene actor cannot exist before its own scene starts. This decides which
      scene a line has to live in, and which characters can use any of this at
      all: one who has to be found, talked to or killed outside his scene
      cannot.
    - `Teleport` is not the way to place a puppet from script. It ignores the
      position and drops him on the player. This no longer matters here, since
      nothing places a puppet from script, but the API still reads as though it
      works.

17. An enum member is no proof the engine implements it.
    `gameEntityReferenceType.Tag` exists, is the right shape for the job, and is
    used by zero of the 7067 shipped scenes. Shipping it crash-killed the game
    three seconds into the first scene that used it.

    Before relying on a field, grep a serialized corpus for a USE of it. Zero
    uses means treat it as unimplemented until a playtest shows otherwise.

    From the same experiment: a diagnostic must not be gated on anything
    downstream of what it measures. The fact meant to explain that crash never
    got written, because it was set inside `if accepted`, and `cc_g01_accepted`
    is set by the quest phase AFTER the beat that crashed. Ask what sets the
    gate, and whether it runs before or after the thing you are watching. For a
    quest-phase fact the answer is almost always "after".

18. Native game-system methods are declared in Codeware, not in the game's
    script cache. `r6\cache\final.redscripts` does not contain the string
    "DynamicEntitySystem" at all, so grepping it proves nothing.

    The real declaration is
    `red4ext\plugins\Codeware\Scripts\Codeware.Global.reds`
    (`DynamicEntitySystem` at line 43422). Read it before guessing. The obvious
    `GetEntityIDs` does not exist; the real names are `GetTagged`,
    `GetTaggedID`, `GetTaggedIDs`, `IsPopulated`, `AssignTag`, `IsTagged`.

19. A killed `check-scripts.ps1` leaves `scc.exe` running and wedged. The script
    pipes through `Select-Object -Last 25`, which buffers the whole stream, so a
    run in progress looks identical whether it is working or hung. A clean run
    takes about 5 seconds. If one seems stuck, `Get-Process scc` and kill that
    before re-running.

20. Keep `.ps1` files pure ASCII. Windows PowerShell 5.1 reads a BOM-less script
    as Windows-1252, so a UTF-8 em dash becomes mojibake, and the stray quote
    character in it breaks string parsing with a "missing the terminator" error.

21. A fact survives a load. A script field does not.

    A plain `let` on a ScriptableSystem is gone after a reload; every `cc_g01_*`
    fact comes back exactly as it was. A state machine mixing the two comes back
    half-reset: facts saying "already happened", memory saying "not yet".

    This shipped in 1.0.0 and players found it. `Gig01_Holocall` remembered
    finished calls in `m_state`, so a reload re-rang every completed call, and
    each hung up half a second later because `<prefix>_end` was still set.
    Reported as "ghost calls that died before pickup".

    Derive the state from the persisting `<prefix>_done` rather than storing it
    in a field. `Gig01_Start.AlreadyRunning()` is the same rule applied
    correctly.

    Invisible to testing that always starts from a clean save, so reload paths
    have to be checked by reading the code.

22. Cap how long a beat may block when it gates on a signal you have not watched
    across a whole save. A gate that can latch true is a gig that never starts,
    which is the hardest report to act on.
    `CCGig01StartRules.IsFastTravelling` defers for at most a minute, then
    proceeds regardless.

    The blackboard is spelled `GetAllBlackboardDefs().FastTRavelSystem`, capital
    R, CDPR's own typo in 2.31. Spell it the game's way. A corrected name is a
    different field and reads as nothing.

23. Redscript has no `==` for Bool, and the error does not say so. It is
    `[NO_MATCHING_OVERLOAD] ... expected 'TweakDBID', given 'Bool'`, naming the
    first overload in the table and pointing you at whatever TweakDBID is
    nearest. Write `(a && b) || (!a && !b)`. Cost twenty minutes on 2026-08-15.

24. Fast travel can be blocked properly, with a shipped API:
    `FastTravelSystem.AddFastTravelLock(name, gameInstance, reason)` and
    `RemoveFastTravelLock(...)`, with `t"GameplayRestriction.BlockFastTravel"`
    as the reason record. `Gig01_Holocall` holds one while the phone rings.

    Locks are SAVED. The game's own `EvaluateFastTravelLocksOnRestore` says so,
    which means a stuck one persists for the rest of the save and reads as "this mod
    broke fast travel". Derive the lock from live state every tick, and force one
    unconditional pass per session so a lock saved by a previous run is lifted.

    **Deriving it correctly is not enough if the state means something wider
    than its name.** Reported in play on 2026-08-16: every fast travel point
    unavailable after ignoring the phone a few times. The lock was derived from
    live state exactly as written above, and it was still wrong, because it
    asked "is this call in state 1", and the comment beside it called state 1
    "ringing". State 1 is *we rang and are waiting to see if it is answered*,
    and that wait is the whole retry back-off: 24 s, 30, 30, 60, then 300 s
    from the fifth ring on. The phone itself rings for eight seconds.

    So a lock intended to cover eight seconds covered five-minute stretches
    with a single tick of daylight between them. Bound a lock to the thing it
    is named after, and check what the state actually spans rather than what it
    is called.

25. A quest map pin cannot be un-shown. Activating a `gameJournalQuestMapPin`
    registers it; setting it back to `Inactive` with `ChangeEntryState` leaves
    the marker on the map. Six waypoints were authored under one objective with
    five held Inactive and all six rendered (screenshots, 2026-08-15).

    Vanilla never tries. 288 shipped objectives carry two pins, one carries 28,
    and its own routes (`follow_tracks`, `cross_border`) show every marker at
    once.

    One marker at a time is a `MappinSystem.RegisterMappin` job, not a journal
    job. It takes a world position (no anchor, no offset), `SetMappinPosition`
    moves it, and nothing else removes it, so unregister on every exit
    path. The struct is `MappinData`, not `gamemappinsMappinData`, and it has no
    `active` field.

26. A phone-call restriction also suppresses the dialogue skip.
    `questTriggerCallRequest.isPlayerTriggered` becomes
    `PhoneManager.ApplyPhoneCallRestriction(true)` for the whole call
    (`phoneSystem.swift:109`), and the restriction takes the skip button with
    it, so the player cannot page through the conversation.

    The game's blackboard puts `FastForward` and `FastForwardHintActive` beside
    `PhoneNoTexting` and `PhoneNoCalling`. One family of restrictions, not
    separate systems. Vanilla sets it because it is staging a full holocall with
    its own pacing. A scripted Audio call carrying a `.scene` wants the player
    able to move through it, so leave it false.

    The wider point is about the unverified guess, not this flag. It was set as the cheapest
    plausible lever against an unrelated problem, marked UNVERIFIED, and never
    checked. The real fix landed elsewhere and this was never removed, so it sat
    there for three days breaking one call. A speculative fix needs an expiry:
    verify it, or remove it when the real cause is found.

27. `ExecutePSAction` is deferred, and a base-game device can need two steps to
    become usable. Reading a device's state in the frame you send it an action
    gives you the state *before* the action, every time.

    Two wrong conclusions came out of that in one evening. A fix that had worked
    was written off as dead because the state read back unchanged. A probe that
    fired five candidate actions in one frame "proved" four of them did nothing,
    when the reads were stale and the actions raced each other. The device ended
    up reporting an `EDeviceStatus` of 4294967294, which is not a state.

    Send one action, then read on a later frame.

    The doors in the Arasaka Industrial Park need
    `DISABLED --ActionQuestForceEnabled--> OFF --ActionQuestForceON--> ON`. The
    middle state is the trap: an OFF device offers the player nothing at all, no
    interaction prompt and not even a "Locked" one, so a half-applied fix is
    indistinguishable from no fix.

    Write this kind of thing as a pump. Look at the state, take one step towards
    the target, come back, and cap the passes. Then it is also correct on a save
    where an earlier build left the device half-way.

    Related: a base-game device's authored state may already have been changed
    by an earlier main quest. Testing here always starts from a late save, where
    "Gimme Danger" has long since switched those doors on, so this was invisible
    for months. When a gig reuses a base-game interior, grep the streaming
    sector for the doors' `deviceState` before assuming the room is enterable.

28. **Depot paths get eaten by string escapes in whatever you generate them
    from.** Gotcha 13 is the redscript case. This is the same trap one layer up,
    in the tooling, and it matters here because the whole approach in this repo
    is to generate resources from a script.

    Depot paths are made of backslashes, and a backslash followed by a letter is
    an escape in Python, Lua, PowerShell, YAML and most things you would write a
    generator in. The backslash AND the letter are replaced by one byte:

    | You typed | The tool stored | Ate |
    |---|---|---|
    | `r6\cache\tweakdb.bin` | `r6\cache` + TAB + `weakdb.bin` | `\t` |
    | `base\amm_workspots\...` | `base` + BEL + `mm_workspots\...` | `\a` |
    | `mod\worlds\03_night_city\...` | `mod\worlds` + ETX + `_night_city\...` | `\0` |
    | `...\heywood\glenn\sts_hey_gle_04` | `...\heywood\glennsts_hey_gle_04` | `\s`, not an escape, backslash just dropped |

    **The failure is silent and reads as a typo.** A tab looks like a space and
    a null byte looks like nothing, so a resource path that will never resolve
    looks merely misspelled. In the game you get no error naming the path: the
    entity does not spawn, the pin does not appear, the sound does not play.

    Write paths as raw strings (`r"mod\my_mod\thing.ent"` in Python,
    `'...'` in PowerShell), or build them from a variable holding one backslash.
    Never type a depot path into an ordinary quoted string.

    Check your own output for it: any control byte sitting mid-line in
    generated text is almost certainly this. Four of them shipped here before
    anyone looked.

29. **A synchronous resource reference on a dynamically spawned entity hard
    crashes the game.**

    `workWorkspotResourceComponent` offers three slots for the same animation:

    | Field | Kind |
    |---|---|
    | `workspotResource` | `raRef`, loaded asynchronously |
    | `deviceWorkspotResourceSync` | `rRef`, loaded with the entity |
    | `npcWorkspotResourceSync` | `rRef`, loaded with the entity |

    Filling either sync slot on an entity spawned through
    `DynamicEntitySystem` takes the process down on the frame the entity
    streams in. Reproduced twice on 2026-08-16, one slot each, with the crash
    landing at the test position and the log stopping at the spawn request.

    The trap is that the field names read like the fix for a loading problem.
    A body appearing before its animation has bound looks exactly like an async
    load that has not finished, so the sync slot looks like the answer. It is
    not, and the failure is not a warning or a missing animation, it is the
    game closing.

    Same shape as #17: the field exists, the name says what you want, and the
    engine does not implement it the way you assume.

30. **`DynamicEntitySpec.templatePath` is ignored when `recordID` is set.**

    Set both and the character record's own entity template wins, silently.
    Proven on 2026-08-16 by spawning two different templates and reading the
    components back: both returned an identical `phantom 1 / mesh 22`, and one
    of them is a template documented as carrying no phantom at all.

    Drop the record and the template does apply, but what comes out is not a
    puppet the workspot system will accept: `IsActorInWorkspot` never goes true
    and the actor never moves.

    So a spawned NPC is EITHER a record with its own template, OR a template
    with no record and reduced capability. There is no combining them.

    The CET dev menu's Johnny lab has offered template radio buttons since it
    was built and every one of them spawns the same entity, because it sets both
    fields. Read a component count back rather than trusting that a spec field
    took: `GetCurrentAppearanceName()` and `GetComponents()` both answer, and
    an hour of this session went on a test that had silently changed nothing.

31. **An impression is not a measurement, and a `DO NOT` written on top of one
    will outlive the evidence.**

    `scene-playbook.md` carried a rule for months: an `around_player` scene
    marker "IS NOT ON THE PLAYER, it lands a few metres to one side", and its
    rotation is "not knowable", therefore **DO NOT** offset an actor from it.
    A whole architecture was built to route around that: the speaker buried
    2.5 m under the floor for his voice, a separate script-spawned body, a
    workspot device to lift him, exit effects to cover the lift, and a 40 m
    targeting sweep six times a second to find him again.

    All of it rested on one playtest sentence about how a voice SOUNDED
    (*"still feels very far, like on the right of where I am"*), from an actor
    who was underground at the time. What that was hearing was the floor.

    Measured on 2026-08-16, in five runs: the marker sits at V's EXACT x and y,
    it carries V's rotation, +Y is forward and +X is right. The offset is
    perfectly aimable. Every workaround above was unnecessary, and the T-pose
    two Nexus reporters described was a side effect of the workaround rather
    than of anything the engine forces.

    What to take from it:

    - A claim that FORECLOSES an approach earns a measurement before it earns a
      `DO NOT`. The cost of a wrong "impossible" is unbounded, because nobody
      re-tests it.
    - Instrument the thing itself. Two facts written from script and read off
      the dev menu settled in ten minutes what three months of reasoning did
      not.
    - "Vanilla never does this" is an absence of precedent. It is worth noting
      and it is not evidence that something fails.
    - Write down which sentences are measurements and which are impressions.

32. **`CreateEntity` queues. A latch set on the REQUEST records a job that may
    never have happened.**

    Reported in play 2026-08-16, and the words name the symptom exactly:
    *"when I reached the area where the NPCs should have been, they simply
    weren't there. I checked the emails on the computer, turned around, and the
    NPCs suddenly spawned directly in front of me."*

    Two separate faults produce that one sentence, and both are worth carrying
    into gigs 02-04.

    **Asking for twenty entities in one tick.** `DynamicEntitySystem
    .CreateEntity` returns an EntityID immediately and the body arrives later:
    this project already knew that, because its own attitude code retries for
    ten seconds waiting for one to resolve. Ask at the moment the player
    arrives and the bodies land behind him while he walks on. Spread the
    request over a callback chain and trigger it from further out, so the
    approach absorbs the work.

    **Latching on intent rather than on outcome.** `m_officeSpawned = true` was
    set BEFORE the spawning, and each guard is placed only if
    `FindPointInSphereOnlyHumanNavmesh` answers OK. A navmesh that is not ready
    yet therefore binned all twenty and the gig recorded the site as populated,
    with no second chance for the rest of the save. Count what was placed, latch
    on a non-zero count, and retry otherwise. Same shape as #21, one level down.

    A HUD banner is part of the outcome, not part of the request. "Arasaka
    security on site" fired in the tick the entities were asked for, so it
    announced an empty compound.

33. **In a serialized resource, 0 usually means index zero, and "none" is
    `4294967295`.**

    `scnEffectInstanceId` reads like a handle that can be left empty, and
    leaving it at 0 does not error: it points the event at entry 0 of the
    scene's own `effectDefinitions`. In 1161 shipped scenes the value for "this
    effect is named on the performer, not owned by the scene" is 4294967295 in
    both halves of the struct, and the only `(0, 0)` in the file examined was a
    genuine reference to that scene's one declared effect.

    The same convention is everywhere in these formats and the sentinels are not
    even all the same number: `scnActorId` and `scnLipsyncAnimSetSRRefId` use
    4294967295 for none, `scnPerformerId` uses 4294967040 for "no performer, a
    world effect". A `TweakDBID` or `NodeRef` really does use 0.

    So do not reason about an empty id from its name. Dump a vanilla resource
    that uses the field and copy what it writes.

34. **A NodeRef has two spellings and only the long one is a name.**

    `$/03_night_city/#c_santo_domingo/arroyo/#my_node` registers and resolves.
    `#my_node` does not, for a node a mod ships. Every one of the 33506
    nodeRefs in the game's `always_loaded_0` is the long form; this repo wrote
    the short one everywhere, and read the resulting failure as "a node in a
    mod sector never registers its global name". That claim then shaped the map
    pin architecture for months. Measured and corrected 2026-08-17,
    `backlog.md` 11.

    **The probe for it has a trap of its own.** An absolute `$/...` path is
    HASHED rather than looked up, so `ResolveNodeRef` reports a defined
    reference for any long string, including one nothing ships. Only reaching a
    live entity is evidence. A run whose negative control is a short name
    cannot tell the two apart, and the first run here was exactly that and
    looked like a breakthrough for twenty minutes.

35. **`worldEntityNode` places props, not people.**

    Two different character entity templates were shipped in a mod sector as
    `worldEntityNode` and neither instantiated, while a prop node four metres
    away resolved to a live entity. The shipped data says the same thing: a
    real exterior sector holds 25 entity nodes, 77 static meshes and 71 smart
    objects, and no NPCs at all.

    NPCs come from COMMUNITIES. `always_loaded_0` holds exactly two node types,
    4500 `worldStaticMarkerNode` for the spots and 785
    `worldCompiledCommunityAreaNode` binding entry and phase to spot. The
    characters live in a `.community` resource, 4033 of which ship, whose
    `communitySpawnEntry.characterRecordId` is a TweakDBID and whose
    `timePeriods[].spotNodeRefs` are NodeRefs. Both are things a mod can
    author, which is why #34 matters.

    Before concluding a thing cannot be placed, check which NODE TYPE the base
    game places it with. Two failed templates say nothing if the node type was
    never the right one.

36. **A marker's height is not a floor, so burying an actor under one is a
    guess.**

    Hiding a voice-only scene actor by spawning it a couple of metres below the
    scene's marker works only if the marker stands on ground. Gig 01 buried one
    2.5 m under `#q113_dvc_arasaka_estate_camera_010`, which is a security
    camera, so its height is a mounting height. The burial landed 3.2 m below
    the terrace where the conversation happens, inside a furnished room one
    storey down, and players saw a man appear there and vanish when the
    dialogue ended.

    The height cannot be checked at the desk either. A cooked sector stores its
    node refs as hashes, and the only place a name is written out is the
    always-loaded name registry, which carries no positions. Resolving the ref
    in game is the whole measurement:

    ```
    ResolveNodeRef(CreateNodeRef(path), root) -> Cast<EntityID> -> FindEntityByID
    ent.GetWorldPosition()
    ```

    Prefer not needing the number. A line with `voExpression:
    Vo_Expression_InnerDialog` plays 2D, so its speaker can stand a kilometre
    away where nothing can see it, and no burial has to be justified. See
    `backlog.md` 10k.

37. **A base-game device can ship enabled and still be disabled on a save, so
    the sector files cannot answer "is this door open".**

    The office doors in `backlog.md` 8a ship `deviceState: DISABLED` and a main
    quest turns them on, which is readable from the streaming sector. El Coyote
    Cojo's entrance is the opposite and looks identical in game: the sector
    ships it `deviceState: ON`, `initialDoorState: CLOSED`, `isLocked: 0`, and
    on a save where the owning quest has not finished it reports DISABLED with
    no interaction prompt at all.

    So a shut door is not evidence about the shipped data, and shipped data is
    not evidence about a save. Only a runtime probe answers it. Read the door's
    `DoorControllerPS` and print `GetDeviceState`, `IsDisabled`, `IsLocked`,
    `IsSealed`, `IsOpen`: locked, sealed and disabled are three different
    states with three different causes, and a static prop door has no PS at all.

    If a gig ends somewhere the base game gates, gate the gig on the same quest
    rather than forcing the door. The NPCs in a gated location are gated with
    it, so a forced door opens onto an empty room. `backlog.md` 18 and 19.

38. **`rldGridCell` and a sector's streaming box are derivable, and copying
    another mod's values makes your sector resident for the whole session.**

    Measured across the 23,689 sector descriptors in the base game's
    `all.streamingblock`, of which 21,332 state their own grid coordinates in
    the filename. No exceptions:

    ```
    W    = 64 * 2^level                     cell size in metres
    i,j,k = floor(x/W), floor(y/W), floor(z/W)
    S    = 2^(8 - level)   Exterior
           2^(9 - level)   Interior, Navigation      (one level finer)
    rldGridCell = (i + S/2) + S*(j + S/2) + S^2*(k + S/2)
    ```

    Check it by prediction rather than by pattern: feed a known position in and
    the answer should equal the `rldGridCell` of the vanilla sector covering
    that position.

    `rldGridCell` 0 is legal. 2,354 shipped Quest sectors carry it together
    with a float-max streaming box, which is the game's shape for a sector that
    is not on the exterior grid.

    Size the streaming box from the content, not the map: the node's own
    `MaxStreamingDistance` plus a margin. A whole-map box is correct only for a
    mod that edits the whole map. `backlog.md` 14.

39. **A mod CAN ship a node that a map pin anchors to, and CAN ship an
    always-loaded sector to keep it resolvable.** Both were written down as
    impossible here for months, and both are wrong.

    A pin resolves against a node of your own if the NodeRef is written in the
    long form (gotcha 34). Written short it is not a name, and the pin is never
    even requested: no line appears in `ArchiveXL.log` at all, which is a
    different failure from the two the log does report.

    Resolution happens once, when the pin's entry is activated, and the result
    is cached. A quest activates its pins while the player is across the city,
    so a node in an ordinary Exterior sector of yours is cold at that moment
    and the pin fails with `Can't resolve ... position`. Walking there
    afterwards does not fix it, because nothing asks again.

    The answer is a sector of your own declared `category: AlwaysLoaded`,
    `level: 255`, `rldGridCell` 0 and a float-max streaming box, which is what
    the game's own three always-loaded sectors carry. Nodes in one resolve from
    anywhere on the map. Measured 2026-08-18 with an eight-slot bench: the same
    marker node failed in an Exterior sector and resolved in an always-loaded
    one, cold, from the far side of Night City.

    That removes the constraint that shaped every pin decision in this project,
    which was to find a base-game always-loaded node within ~50 m of wherever a
    pin was wanted. A sector of marker nodes and no geometry costs nothing to
    keep resident.

    Node type is not a factor: `worldStaticMarkerNode` and `worldEntityNode`
    behaved identically as anchors. `backlog.md` 11 and 20.

40. **A GPS guidance route is absolute, not relative, so keep the chain
    short.** `gameJournalQuestGuidanceMarker` works from a mod, on nodes the
    mod ships, and the game draws a real walking route through them. Two rules
    come with it and neither is optional.

    The chain always runs from its own first waypoint to its pin, and it does
    not know where the player has got to. A player standing halfway along a
    long chain is routed BACK to the start of it and then forward again, which
    on a twelve-waypoint route up a hillside drew a loop several hundred metres
    long. Near the first waypoint the two readings are close enough that the
    line flickers in and out.

    Vanilla never exposes this, and the reason is visible in the shipped data:
    all 44 guidance markers cover short discontinuities, 1 to 4 per pin, at
    places like the Dollhouse exit and the Atlantis staircase. Use them for the
    stretch the ordinary router cannot do, a climb or a staircase, and let it
    handle the approach.

    The second rule is height. A waypoint must sit above the ground, not on it.
    Points captured at the player's own position drew no route at all; the same
    points raised 1.7 m drew one. And a single unusable waypoint silences the
    WHOLE route rather than breaking one leg, so a chain whose second half
    drew on its own drew nothing once a bad first half was put in front of it.
    A route that fails does not degrade, it vanishes, so bisection is the only
    way to find the point at fault.

    All measured in game 2026-08-18. `backlog.md` 20.

41. **A voiced line can exist in four processed versions, the processing is
    baked into the asset, and a mod cannot register a variant.** Under
    `base\localization\<lang>\` the game ships `vo`, `vo_holocall`, `vo_helmet` and
    `vo_rewinded`, with a voiceover map for each. A twin shares its filename, so
    its stringId, with the `vo` original: 3,036 of the 78,026 English clips have
    a holocall twin, and all 2,981 ids in `voiceovermap_holocall.json` are in
    the main maps too.

    `volanguagedatamap.json` is what the engine loads, and its `en-us` entry
    lists all five chunks in one array. ArchiveXL appends to that array through
    `localization: vomaps:` and accepts no other localization key than
    `onscreens`, `subtitles`, `vomaps`, `lipmaps` and `extend`. So a mod gets
    one clip per RUID: whatever processing a line needs has to be baked into the
    clip the mod ships. That is only a constraint if the same RUID must be heard
    both ways, and it never is, because a RUID belongs to one line in one scene.

    `isHolocallSpeaker` routes a line into the phone UI and makes it play 2D. It
    applies no filter.

42. **The holocall treatment is a phase effect, not an EQ, and no amount of EQ
    will imitate it.** Vanilla keeps the source's short-time magnitude spectrum
    and discards its phase. Measured on a vanilla clip against its own twin,
    coherence is 0.02 above 500 Hz; a known linear filter measured the same way
    reads 0.20.

    Four properties of the shipped assets follow from that and are otherwise
    inexplicable: the stereo channels decorrelate to a sample correlation of
    0.04 while their envelopes track at 0.96, the file runs about 100 ms long,
    it starts about 9 ms late, and its crest factor drops 4 to 5 dB without a
    limiter being involved.

    The practical consequence for any mod imitating a processed vanilla voice:
    fit the magnitude curve on the stereo MID and energy-weighted, then add the
    phase treatment. Fitting one channel with a median of frame ratios reads
    about 10 dB too shallow through the low mids, and even a perfect magnitude
    match sounds, in a field report, *"just a tad different"*. `backlog.md` 15
    carries the numbers and `tools/questkit/phone.py` the implementation.

43. **Redscript has no equality operator for `Bool`, and the error names a type
    you never mentioned.** `if a == b` or `if a != b` on two Bools fails to
    compile with:

    ```
    [NO_MATCHING_OVERLOAD] arguments passed to 'OperatorNotEqual' do not match
    any of the overloads:
    1st argument: expected 'TweakDBID', given 'Bool'
    ```

    `TweakDBID` is simply the first overload in the table. If the line above
    happens to mention a TweakDBID, and in practice it often does, the message
    sends you to inspect that instead of the comparison. Write it out:

    ```swift
    let matches: Bool = (a && b) || (!a && !b);
    ```

    This has cost time twice in `Gig01_Holocall.reds`, in `ApplyLock` and again
    in `UpdateVehicleLock`, which is why it is here rather than only in a code
    comment. Both places compare "what should be true" against "what is actually
    applied", which is a shape any lock or latch reaches for, so expect it again.

44. **A `@wrapMethod` on a base-game method whose name ends in `ByTask`, or that
    has a matching `...Task` class, runs on a job worker thread. Do not read game
    state from it.** A hook on
    `VehicleComponent.DetermineInteractionState(CName)` that called
    `GetEntity()` and `GameInstance.GetQuestsSystem()` compiled cleanly and
    crashed the game on load, before the main menu, while the world streamed
    vehicles in. Its own dev switch was off; the early-out still touched both
    before deciding to do nothing.

    The tell is in the script bundle next to the method:
    `DetermineInteractionStateByTask`, `DetermineInteractionStateTask` and
    `DetermineInteractionStateTask;ScriptTaskData`. `ScriptTaskData` means the
    engine's script job system, so the method is not on the main thread.

    Grep for those siblings before wrapping anything. A method that only ever
    runs on the main thread, an `On*Event` handler for instance, is safe to hook
    the ordinary way. `backlog.md` 10i is a reminder that crashes on job-worker
    threads in the world streamer are hard to attribute afterwards, so it is
    much cheaper to avoid causing one.

45. **A `.reds` saved with CRLF line endings silently breaks the shared-module
    import, and the error names the class rather than the line endings.** Every
    script in this repo is LF. `tools/vendor-shared.ps1` rewrites each gig's
    `import CyberpunkCodes.Shared.*` to point at the per-gig module name, and it
    matches with:

    ```
    (?m)^import CyberpunkCodes\.Shared\.\*$
    ```

    In .NET regex, `(?m)$` matches immediately before `\n`. On a CRLF file the
    line ends `...\*\r\n`, so the `\r` sits between `\*` and `$` and the pattern
    does not match. The import is left pointing at a module that does not exist
    under that name, and compilation fails with:

    ```
    [UNRESOLVED_REF] unresolved reference 'CCSharedHud'
    ```

    which sends you looking at the class, the vendoring, or the shared file,
    none of which are wrong.

    It is easy to introduce without noticing. Python's `open(path, "w")` on
    Windows translates `\n` to `\r\n`, so any script that rewrites a `.reds` in
    text mode converts the whole file. Write with `newline=""` or in binary, and
    if a reference that plainly exists will not resolve, check the file with:

    ```bash
    python -c "d=open('X.reds','rb').read(); print(d.count(b'\r\n'))"
    ```

    Anything above zero is the fault. The same applies to the `module` rewrite
    on the shared files themselves, which is anchored the same way.

46. **A generator that writes through Python's text mode produces different
    bytes on Windows than anywhere else, and the output stops being
    reproducible.** `open(path, "w")` translates every newline to a carriage
    return plus newline on Windows. Git in this repo is `core.autocrlf=input`,
    so it stores and checks out LF. Every generator run therefore rewrote its
    own output, and sixteen generated files showed as modified while the content
    was identical: `lipsync_picks.json` was 3,043 bytes as committed and 3,125
    on disk, one byte per line and nothing else.

    It is worse than noise. It means a regenerated file cannot be diffed against
    the committed one to see whether a change to a generator did what you
    intended, which is the whole reason the generated output is committed at
    all. And it is intermittent: the files agree right after a regen and
    disagree after a fresh clone, so the fault looks like it comes and goes.

    Every writer under `tools/` passes an explicit newline:

    ```python
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
    ```

    Do the same in any new one. `tools/native/vendor/` is excluded, being
    somebody else's SDK.

    Gotcha 45 is the same root cause landing somewhere else entirely, on a
    `.reds` file, where it breaks an import instead.

47. **ArchiveXL's `expectedNodes` and `nodeDeletions[].index` count a sector's
    INSTANCES, not its nodes, and the two numbers are different.**

    A `.streamingsector` carries two parallel tables. `nodes` is one entry per
    distinct thing, and `nodeData` is one entry per PLACEMENT of one, pointing
    back at its node through `NodeIndex`. The two are nowhere near equal:
    `exterior_-4_-23_0_0` has 939 nodes and 1242 instances.

    Both `.archive.xl` fields want the second table. A node at index 527 in
    `nodes` is at 591 in `nodeData`, and `expectedNodes` wants 1242 despite its
    name.

    Getting it wrong is refused cleanly rather than silently, which is the one
    good thing about it. ArchiveXL logs, to
    `red4ext\plugins\ArchiveXL\ArchiveXL.log`:

    ```
    [WorldStreaming] Patching sector "base\worlds\...\exterior_-4_-23_0_0.streamingsector"...
    [WorldStreaming] <mod>.archive.xl: The target sector has 1242 node(s), but the mod expects 939.
    [WorldStreaming] No patches have been applied to "base\worlds\...".
    ```

    Read that log before concluding anything about a sector patch. The line is
    written when the sector STREAMS IN, not at startup, so it does not appear
    until the player is near the place being patched, and a grep that stops at
    the first few hundred lines will miss it.

    While you are in there, ArchiveXL 1.27 can `nodeDeletions`, `nodeMutations`
    (position, orientation, scale, mesh, material, effect, entityTemplate,
    appearance, meshAppearance, recordID), `instanceDeletions`,
    `instanceMutations`, `actorDeletions` and `actorMutations` on a shipped
    sector. There is no addition, so a mod cannot append a node to a base-game
    sector; its own sector is the only place a new one can go.

48. **A readable shard's title and text hang off `itemSecondaryAction`, not
    off any name on the item and not off `objectActions`. A `$base` clone
    inherits that property still pointing at the BASE item's inline record, so
    the clone shows the base item's shard.**

    The chain, measured 2026-08-22, because none of it is guessable from the
    field names:

    - The loot line and the scanner title are the **journal entry's title**.
      `base\journal\cooked_journal.journal` gives `generic_hanako_flowers` a
      `title` of `LocKey#7190`, and `base\localization\en-us\onscreens` resolves
      that to the exact string on screen. The vanilla ITEM's DisplayName
      accessor returns `None`: it has no name at all and still shows a title.
    - The journal path lives on an **inline ObjectAction record**,
      `Items.<shard>_inline0`, in its `journalEntry` flat.
    - The item reaches that record through **`itemSecondaryAction`**. All 335
      shards in the game are built this way.
    - **`objectActions` is not that list.** The vanilla shard's is
      `[ItemAction.Drop, ItemAction.Disassemble]`, with no read action in it.
      Overriding it does nothing useful and silently drops Disassemble.

    So:

    ```yaml
    ObjectAction.my_shard_read:
      $base: Items.generic_hanako_flowers_shard_inline0
      journalEntry: onscreens/emails/quests/.../my_shard_note

    Items.my_shard:
      $base: Items.generic_hanako_flowers_shard
      displayName: my-shard-item
      localizedDescription: my-shard-item-desc
      itemSecondaryAction: ObjectAction.my_shard_read
    ```

    **The wider rule, and the cheaper one: `$base` is not free.** A clone
    carries every inline child the base had, and those children keep pointing
    at the base's content. Cloning a shard that already has a story attached
    means inheriting that story through a property nobody thinks to look at.
    Starting from something empty avoids the whole class.

    Four wrong guesses preceded this, all of them about name fields, and each
    looked plausible because a clone that applies in full can still show the
    base's text. The reading that would have short-circuited it is the ITEM
    record's own `objectActions`, printed back: seeing `[Drop, Disassemble]`
    says immediately that the read action is somewhere else.

    Method notes worth keeping:

    - An item's flat names come out of CET's `tweakdbstr.kark` (the route in
      `gameplay-restrictions.md`). `TweakDB:GetFlat` in CET Lua prints what one
      resolved to without quitting, and `TweakDB:SetFlat` plus `TweakDB:Update`
      tests a candidate in the running session, since TweakDB is built at
      launch.
    - `SetFlat` CREATES a flat whether or not the record exists, so a flat
      reading back what you just wrote is not evidence the record is real.
      Check a second flat on the same record.
    - **CET's Lua sandbox has no `_G`.** Indexing it throws, and inside a
      `pcall` that becomes a silent failure. Three candidate fixes were
      reported as tried when they had never run.
    - A flat holding a `LocKey` accepts a plain string from `SetFlat` and then
      does nothing.
    - ArchiveXL LocKeys are FNV1a64 of the bare key, so a `LocKey(...)` printed
      by `GetFlat` can be checked against the key you meant at the desk.
    - Identify the OBJECT before reading anything off it.
      `TargetingSystem:GetLookAtObject` returns what the CROSSHAIR is on, while
      a direction finder built on `GetWorldForward` steers off the player's
      BODY; with test objects four metres apart the two disagree. Match the
      object's `GetWorldPosition()` against known positions instead.

49. **`PopupsManager.OnShardReadClosed` only fires for a shard read IN THE
    WORLD. Reading the same shard out of the backpack, or out of the Shards
    list, does not run it.**

    Measured in playtest, 2026-08-22. A quest step waiting on that callback
    sits there while the player reads the note in front of them, which is
    indistinguishable from a permanent stall.

    Ask the journal instead. It does not care where the reader was raised
    from:

    ```reds
    let entry = jm.GetEntryByString(path, "gameJournalOnscreen");
    return jm.IsEntryVisited(entry);
    ```

    Two things about that, and both bite.

    **`IsEntryVisited` goes true when the popup OPENS**, not when it closes.
    Acting on it directly resumes the quest while the shard is still on screen,
    under a modal popup that pauses the game and hides subtitles, so the next
    lines are spoken into nothing. Let TWO TICKS pass first: the popup pauses
    the game, DelaySystem ticks do not advance while it is up, so two of them
    cannot elapse until the reader has been shut. That converts the open signal
    into a close signal with no second callback.

    **Visited, not `Active`.** An entry goes `Active` when the shard is merely
    PICKED UP. A state check therefore completes the objective for a player who
    took the shard and read nothing, which is the exact case this exists to
    catch.

    Keep the close callback as well. It fires instantly for the common case,
    and the journal check is the net under everything else.

    See `shard-playbook.md`.
