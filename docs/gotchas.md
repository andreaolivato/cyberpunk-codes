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

   The anchor may be a node the mod itself ships, provided the NodeRef is
   written in the long form and the sector is declared AlwaysLoaded. See #39,
   which corrected this entry on 2026-08-18; it used to say a custom marker
   node never resolves, and that was the short-form spelling failing rather
   than the node.

   There was a fourth ingredient, patching the game's cooked mappin tables,
   until 2026-08-14. ArchiveXL does that itself, and the patched tables
   suppressed it.

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

    **CORRECTED 2026-08-23, and the correction matters more than the rule.**
    A script-issued Video call DOES NOT CRASH. Measured twice, with a body
    standing in the studio and the studio open: it draws an EMPTY FRAME. The
    missing `prefabNodeRef` is what leaves the phone with nothing to point at,
    not a fault. Whatever crashed in 2026-08-11 has not been reproduced since
    and is not this.

    The rule at the top still stands as advice, because a script-issued Video
    call is useless either way: no field, no feed, no picture.

    **A mod CAN have a real video holocall, in both directions**, by emitting
    the nodes vanilla uses into its own quest phase rather than issuing a
    request from script. Played in the gig 2026-08-23. `backlog.md` 3d,
    `scene-playbook.md`, and gotchas 55 to 58.

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

    NPCs come from COMMUNITIES, and a community is three nodes rather than a
    resource. `always_loaded_1` carries a single `worldCommunityRegistryNode`
    holding all 8540 of them: the characters, the phases, the quantities and a
    position record per spot. A `worldCompiledCommunityAreaNode` says which
    entry and phase uses which spot, and the two are joined by a 64-bit id that
    appears on both. The spots themselves are `worldAISpotNode`s in ordinary
    sectors, named, and named is how they are found:
    `worldGlobalNodeID.hash` is FNV1a64 of the NodeRef with every '#' removed,
    which is why #34 matters.

    **The `.community` file, 4033 of which ship, is an authoring artifact.**
    Nothing at runtime reads one; its contents are copied into the registry
    node at cook time. `backlog.md` 28 has the whole recipe and the
    measurements behind it.

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

50. **A redscript class in a module is registered under its FULL
    module-qualified name.** `ScriptableSystemsContainer.Get(n"MySystem")`
    returns null; `Get(n"CyberpunkCodes.Gig01.MySystem")` returns the system.
    Every class this project ships appears in the compiled bundle as
    `CyberpunkCodes.<Gig>.<Name>`, never bare.

    It bites when something OUTSIDE redscript reaches in, which in practice
    means the CET menu. It had never bitten before because the only lookups in
    the tree are for base-game systems, which carry no module.

    It also rules out reaching a mod class as a CET Lua global: a dotted name
    is not an identifier, and CET has no `_G` to index through. A
    `ScriptableSystem` is the way in.

    Pair any such lookup with a base-game CONTROL in the same press. A null
    that comes back beside a working `PhoneSystem` says the name is wrong; a
    null beside a null says the container was never reached. Those need
    opposite fixes and look identical.

51. **A quest phase's progress is SAVED, so a linear dev branch runs once per
    SAVE, not once per load.** Fire its fact a second time and nothing happens:
    the phase walked to its output and there is no longer anything listening.
    The fact sits at 1 with nothing consuming it, which looks exactly like a
    button that has stopped working.

    Vanilla's holocall phases are LOOPS: an input node, no output node, and the
    first pause node fed from more than one place. Copy that shape for anything
    meant to be run repeatedly.

    Fan-in on a pause node is ordinary (29 shipped sockets carry two sources).
    Fan-in on a SCENE node is what vanilla never does and what fails silently,
    and a second scene node inside one phase is what crashed the game on load.
    See `gen_questphase.py`.

52. **A forced, sourced gameplay restriction is released BY ITS SOURCE, not by
    its record.** A staged holocall locks the phone through
    `questSetPhoneRestriction_NodeType` with `forcedApply: 1` and a named
    source. Removing `GameplayRestriction.PhoneCall` as a status effect returns
    without error and removes nothing, through either removal API. The release
    is the same node with `applyPhoneRestriction: 0` and the SAME source
    string, which `questgraph.add_phone_restriction` emits.

    The source string is load-bearing: a wrong one releases nothing, silently.
    Read it out of the contact's own phase.

    **And the phone lock is NOT what stops a line being skipped.** Measured
    2026-08-23: both locks off for a whole call, skip still unavailable. A
    VIDEO holocall cannot be fast-forwarded, in vanilla either, and the gig
    matches that. The game's fast-forward logic has a second gate,
    `PhoneBBStateBlockingFF`, which asks the phone what kind of call is up.

53. **An empty CName is the STRING `"None"`, never a null, and a node the game
    cannot read is a QUEST PHASE THAT SILENTLY DOES NOT RUN.**

    `questkit/questgraph.py`'s `cname()` emitted `"$value": null` for an empty
    name until 2026-08-23. It never bit because every node that builder had
    ever emitted passed a real string. The first node type that needed empty
    ones, `questEntityManagerToggleComponent_NodeType`, whose
    `gameEntityReference` carries three, produced a phase that did nothing at
    all.

    **There is no error anywhere.** ArchiveXL still logs `Merged phase`,
    because the file went in; only the graph fails. The dev fact sits at 1,
    pressing the button again changes nothing, and every symptom points at the
    thing under test rather than at the file. It cost an afternoon.

    `questkit/scene.py`'s `cname()` had always been correct. The two were never
    reconciled. Both do `v if v else 'None'` now.

    Whenever a new node type is emitted, DIFF THE GENERATED JSON AGAINST
    VANILLA'S before running the game. Ten seconds, and it finds this class of
    fault without a launch.

54. **A quest phase has a POSITION, nothing reports it, and a parked phase
    looks exactly like a broken button.**

    A dev branch that stopped halfway leaves its trigger fact at 1. Pressing
    the button sets a fact that is already set, the phase is not waiting where
    you think it is, and nothing happens. No error, no log line, nothing in the
    trace, because a fact that does not CHANGE is not a change.

    Two things follow, and both are cheap:

    - **Drop a breadcrumb after every node.** `gen_questphase.nix_call()`
      writes `<prefix>_step` 1 to 9 and 20 to 21, one number per node, and it
      is the only thing that tells "the studio never arrived" apart from "the
      call was never answered". A phase that stops then says WHERE.
    - **Flush before you start.** Pulse the later waits so the token walks its
      loop home wherever it was, then start clean. It costs a second and does
      nothing when nothing was stuck.

    See also 51: a phase's progress is SAVED, so a linear dev branch is once
    per save. Loop it.

55. **A pause node that loses a race is still armed, and it fires later.**

    Two pause nodes off one source is two waits, not a choice. Whichever
    completes first carries the token on, and the other one keeps waiting: it
    completes minutes later, in the middle of whatever the winner started, and
    pushes a second token down the same chain. A scene node entered twice is
    gotcha 51.

    Vanilla never leaves that open. `qb_holocall_initializer.questphase` wires
    one `questCutControlNodeDefinition` to the `CutDestination` socket of all
    eight of its waits and fires it the moment any one of them completes,
    cutting the winner along with the losers. `permanent: 0`, so the same waits
    re-arm when the graph loops back round to them.

    Three parts, and all three are needed:

    - **Cut the losers.** The node above, wired to every arm.
    - **Do not trust the arm that won.** Which wait woke you is a different
      question from what is true now. Vanilla races "answered", "answered or
      declined" and a six second timer, and then asks the phone again with a
      `questConditionNodeDefinition` before branching
      (`nix_holocall.scene` node 444). Gotcha 10j is why: a declined call
      reports Rejected and then reports Talking a second and a half later.
    - **Close the same-frame window.** The cut lands after the winner has
      already left, so two arms completing on one frame is two tokens in
      flight. `questgraph.add_race2` has each arm check a claim fact is still 0
      before writing its own number, and the second token dies at an
      unconnected socket.

    `questConditionNodeDefinition` is the node for any branch that must be
    taken once: it reads its condition on arrival, sends the token down True or
    False, and is finished. A pause node arms. They look interchangeable in a
    graph editor and they are not.

56. **Neither phone pick-up condition reports a call that simply rang out.**

    `questPhonePickUp_ConditionType` carries `releaseOnRejection`:

        0   completes when the call is ANSWERED
        1   completes when it is answered OR declined

    A ring that nobody touches completes neither, so a wait built on these
    alone waits for ever. The phone gives up on its own after eight seconds
    (`HudPhoneGameController.m_TimeoutPeroid`) and takes the chrome down, and
    the graph is never told.

    Vanilla races them against a 6.015 second timer, which is deliberately
    SHORTER than the phone's own timeout so the graph decides rather than
    discovering the ring has already gone. Ours is longer, 10 seconds, because
    it wants the opposite: the chrome fully gone before it hangs up and rings
    again.

    `questPhone_ConditionType` is a different thing and answers a different
    question: which PHASE the call is in, not whether anyone picked up. It is
    what vanilla waits on to know the ring has registered.

    **SUPERSEDED IN PRACTICE BY 58**, which is the same subject and the harder
    finding: for a call a mod issues from a quest phase, neither pick-up
    condition reports anything at all, not even the answer. Everything above is
    still true of vanilla's own use of them and is why a race is needed either
    way; 58 is why the arm of that race has to be a fact.

57. **`deploy-dev.ps1` does not build the archive, and a stale one looks exactly
    like a change that did not work.**

    It copies whatever `build-archive.ps1` last produced. Regenerate the JSON,
    skip the build step, deploy, and the game gets THIS build's redscript with
    LAST build's quest graph, scenes, journal and localization. Nothing warns.

    2026-08-23: a whole playthrough was spent testing an archive an hour old.
    Both beats under test took their old path, which is what a change that
    silently failed looks like, and the deploy had printed
    `archive -> archive\pc\mod\...` and `Done.`

    The two halves fail differently and that is the trap. Redscript is copied
    from source on every deploy so it is never stale; everything that goes
    through WolvenKit is only as new as the last pack. A build where the script
    is current and the resources are not is the worst of the three states.

    `deploy-dev.ps1` now refuses when anything under `source\wkit\raw` is
    newer than the packed archive, and names the files. `-AllowStaleArchive`
    deploys anyway. The same guard, for the same reason, as the audio staleness
    check inside `build-archive.ps1`.

    Check the game folder rather than the console when a change appears to have
    had no effect at all: the archive's timestamp there is the answer in one
    line.

58. **`questPhonePickUp_ConditionType` reports nothing for a call a mod issues
    from a quest phase. Watch the fact instead.**

    Measured in play 2026-08-23, on a `questCallContact_NodeType` call with a
    mod's own journal contact. The player tapped to answer, PhoneSystem wrote
    `phonecall_cc_g01_nix_with_player = 2` on time, and the pause node built on
    this condition never completed. The call sat connected and silent until the
    game dropped it six seconds later.

    It is vanilla's own node, read out of vanilla's own holocall scene, with
    every field checked against the SDK header. It works there. The difference
    has not been found; the candidates are that it resolves against a scene's
    context rather than a phase's, or that it tracks the call object the
    scene's own call node created.

    **The fact is the route, and it always was.** PhoneSystem writes
    `"phonecall_" + caller + "_with_" + addressee`, both lowercased, from the
    CONTACT IDS, with `questPhoneTalkingState`: Ended 0, Initializing 1,
    Talking 2, Rejected 3. `add_pause_fact(name, 1, 'Greater')` waits for the
    player to do something and `add_condition_fact(name, 2, 'Equal')` asks
    which. Both are ordinary nodes this project has shipped for a year.

    Two things come with it:

    - **Clear the fact before every ring.** It persists, and it persists at
      Talking once a call has been answered, so a ring placed without clearing
      finds the answer already reported and connects before the phone rings.
    - **It is visible in the dev menu's fact trace**, which is how this was
      found in one playthrough. A condition node's state is visible nowhere.

    The general form: prefer the signal you can watch. A quest node that is
    supposed to fire and does not looks exactly like a phase that stopped for
    some other reason, and gotcha 54 is the only thing that tells them apart.

59. **A line that reuses a vanilla recording gets no lipsync, because the
    casting is driven by the lines you generated audio FOR.**

    Pointing a line at vanilla's own `stringId` gets the text and the voiceover
    for nothing, and it is the right thing to do when the script quotes a line
    the game already has. It also takes that line out of every list built from
    "what did we synthesise": it has no `.wav`, so no entry in the duration
    sidecar, so no entry in the lipsync casting, so
    `scnscreenplayDialogLine.maleLipsyncAnimationName` ships empty.

    **Nothing errors.** The actor is configured correctly, the animation set
    resolves, the other lines in the same scene move perfectly, and that one
    face sits completely still while its audio plays.

    Reported in play 2026-08-23, and only because the speaker had just been put
    in close-up on a phone. The same line had been mouthless behind a static
    contact portrait since 1.2.0, where there was nothing to see.

    **The duration is exact and free.** Vanilla baked a lipsync animation for
    that very line, named `f_<the stringId in 16 hex digits>`, and its length
    is the clip's length: 1533 ms against the 1537 ms this project had recorded
    by hand. Look it up in the catalogue rather than estimating.

    **It cannot simply be given its own animation**, tempting as that is, since
    one `.anims` set serves a whole scene and the set holding `f_<stringId>` is
    the contact's own, which is usually a tiny pool (backlog 2j). Cast it by
    length with everything else. If the picker does land on that set, the exact
    animation wins on merit, because its length error is zero.

    The general shape: any list built from "the things we generated" silently
    omits the things we borrowed. Check the borrowed ones separately.

60. **`ResolveNodeRef` only reaches a live entity for a node that carries
    `instanceData`. Code 3 is not evidence that a node is absent.**

    The four-code probe in `backlog.md` 11 ends at `FindEntityByID`, so a node
    with no entity payload can stream in, render in front of you, and still
    read 3, "an entity id but nothing streamed". Measured 2026-08-23 with two
    nodes in the same mod sector, four metres apart: a `worldEntityNode` with
    `instanceData: null` read 3, and one carrying a whole vanilla entity chunk
    read 4.

    This is compounded by the long-form trap in #34. An absolute `$/...` path
    is hashed rather than looked up, so a name nothing ships ALSO reads 3.
    Between them, 3 means "either not there, or there and unprobeable", and a
    bench that treats it as absence measures itself. Two rounds were spent that
    way here.

    **Only 4 carries information.** Probe with a node that has a body, and lift
    the whole node including its `instanceData` from a vanilla one rather than
    authoring the payload. Keep two controls in the same shape: a base-game
    node that must read 4, and a name nothing ships that must read 3.

61. **A mod's own AlwaysLoaded sector is resident across the whole map, and its
    nodes are live entities from anywhere in it.**

    Measured 2026-08-23. A `worldEntityNode` in a mod sector declared
    `category: AlwaysLoaded`, `level: 255`, `rldGridCell` 0 and a float-max
    streaming box probed 4, a live entity, from 2567 m away. The same node in
    the same mod's Exterior sector probed 4 beside it and 3 from that distance,
    which is the Exterior sector doing its job.

    #39 established that a map pin resolves against such a sector. This is the
    stronger statement: the node is not merely named, it is instantiated, so
    anything that needs a real entity can rely on one.

    A mod may ship several streaming blocks. ArchiveXL appends every one to the
    world's `blockRefs`, so there is no "only the first counts" rule; three
    blocks from one archive were merged and all three worked.

62. **A community's identity is the FNV1a64 of its own NodeRef, and it has to
    be registered as a name before anything can address it.**

    Three values must be the same number or a community is inert, and nothing
    reports the mismatch:

    - the community's NodeRef, listed in its sector's `nodeRefs`
    - `worldCompiledCommunityAreaNode.sourceObjectId`
    - `worldCommunityRegistryItem.communityId.entityId`

    Measured on vanilla: `always_loaded_0` registers
    `$/03_night_city/c_pacifica/coastview/#pcv_01/.../#mq025_com_fabiola` and
    the area node beside it carries `sourceObjectId` 12672209401641994660, which
    is FNV1a64 of that ref with its '#' characters removed, exactly. Same rule
    as #34 and as a spot's `worldGlobalNodeID`.

    `nodeRefs` is not parallel to anything: `always_loaded_0` registers 33506
    names against 15024 instances, so a name can be listed without being
    attached to a node. Vanilla's 2510 community area node instances carry no
    name at all and the community's name is a standalone entry.

    A quest node addresses the same string through `spawnerReference`, so a
    community named one thing and hashed from another cannot be reached from
    either direction.

63. **Vanilla drives its ambient communities from quest phases, but a MOD
    community should not need one: the wiki says `entryActiveOnStart` alone
    starts it.** (Amended 2026-08-24; the original heading overstated.)

    `base/open_world/community/city_centre/corpo_plaza/pop_cct_cpz_phase`
    `.questphase` is 2158 bytes and does exactly one thing: a
    `questSpawnManagerNodeDefinition` holding a
    `questCommunityTemplate_NodeType` with `action: Activate`, entry and phase
    `None`, and `spawnerReference: #cct_cpz_com`.

    That is an AMBIENT open-world population community, and vanilla still
    switches it on from a quest phase. 52 such phases ship under
    `base/open_world/community/`.

    **The amendment:** the REDmodding wiki states that for a World Builder
    community "Initial Phase Name and Active On Start are only of interest for
    quest modding", meaning a mod community spawns from `entryActiveOnStart`
    with no quest node at all. So vanilla's phases exist to CONTROL its
    communities (switch phases, deactivate for story beats), not because
    activation is a precondition. Keep the quest node for switching; do not
    conclude a silent community is missing one.

    The node's own keys are exactly `$type`, `actions`, `id` and `sockets`, with
    the ordinary three sockets. `action` takes Activate, Deactivate, Reactivate
    and ResetKillCount. `spawnerReference` is written long-form in 105 of 159
    sampled uses and short-form in 54; a name a MOD ships only resolves in the
    long form (#34).

64. **`GetGameObjectsFromSpawnerEntityID` returns SPAWNED objects, so 0 does
    not mean the community is unknown.**

    `GetGameObjectsFromSpawnerEntityID(entityID, entryNames, game, out objects)`
    answers "what does this community or spawner have on the ground right now",
    given its id, which is `Cast<EntityID>` of its resolved NodeRef.

    It was added here to separate "the game never read our community" from "it
    read it and nothing spawned", and **it cannot do that**: both give 0. That
    was measured on 2026-08-24, one run after #60 was written about exactly this
    shape of mistake.

    The siblings are `GetFixedEntityIdsFromSpawnerEntityID`, whose ids are
    deterministic per entry and may exist before anything spawns, and
    `CreateEntityReference(nodeRefString, entryNames)` with
    `GetFixedEntityIdsFromEntityReference` from the NodeRef side. Neither is
    measured yet.

    **Whatever you ask, calibrate it against a VANILLA community first**, with
    the player standing in its crowd. A call that returns 0 for everything looks
    exactly like a call that returns 0 for you.

65. **Do not place an NPC with a community. Use a mod-owned AI spot, a VANILLA
    spawn set, and a scene actor.**

    Nine runs on 2026-08-23 and 24 failed to get a single NPC out of a
    `worldCommunityRegistryNode` a mod ships. That covered both area-node
    shapes (`worldCompiledCommunityAreaNode` in an always-loaded sector and
    `worldCompiledCommunityAreaNode_Streamable` in a streaming one), both quest
    node types (`questCommunityTemplate_NodeType` and `questSpawnSet_NodeType`),
    the identity rule in #62, the activation in #63, our own AI spots, our own
    marker, and a vanilla workspot carrying the game's own persistent record.
    Every control was clean in every run. `backlog.md` 29.

    **What ships and works** is what Californication does, and it is three
    parts:

    - its own `worldAISpotNode` for the workspot, named long-form and nested
      under a real vanilla prefab path, in a `category: Quest` sector
    - `questSpawnSet_NodeType` against one of the GAME'S OWN spawn sets:
      `Reactivate`, entry `judy`, phase `dlc3_judy_sleep`, reference `#judy`
    - a scene actor with `acquisitionPlan: spawnDespawn`

    Three published quest mods were extracted and read node by node and NONE of
    them ships a community. The tooling route the wiki documents is World
    Builder's, and none of them uses it.

    This is a "we could not, and nobody here does" rather than "the engine
    refuses": ArchiveXL carries a hook whose only purpose is to merge a mod's
    `AISpotPersistentData` into the game's array. If it is ever retried, the one
    untried move is to make a community in World Builder itself and diff its
    files, rather than reasoning about them.

66. **A mod CAN ship a working community, and the recipe has six parts.
    Gotcha 65 is SUPERSEDED.**

    Measured 2026-08-24 after twelve bench runs: a community this mod ships
    spawned its own `Character.cc_g01_hoshino` on save load, with no quest
    node, beside a second community mod doing the same. The parts, all shipped
    together by the run that worked:

    1. ONE name for the community; `sourceObjectId` and the registry item's
       `communityId` are FNV1a64 of that name minus '#' (#62), and the name is
       registered in its sector's `nodeRefs`.
    2. A `worldCommunityRegistryNode` in an AlwaysLoaded level-1 sector with a
       +-99999 box: unnamed uint64 instance, `MaxStreamingDistance` 17.32,
       `UkFloat1` 1e8, `Uk10` 32, `Uk11` 512, holding the
       `worldCommunityRegistryItem` and one `AISpotPersistentData` per spot.
    3. The area node TOGETHER WITH its `worldAISpotNode`s in their own
       AlwaysLoaded level-1 sector, small local box, grid cell 0. The bench used
       `worldCompiledCommunityAreaNode_Streamable`; the plain
       `worldCompiledCommunityAreaNode` was later shipped at the Arasaka compound
       and spawned thirty guards, so a mod's own sector takes either. Prefer the
       streamable one, which is the value the bench established.
    4. Every NodeRef rooted **`$/mod/<sector>/#<name>`**. This project had
       only ever written `$/03_night_city/...`, and eleven runs failed with it.
    5. **`appearances` NON-EMPTY on every phase.** The wiki calls the field
       optional; every working example names one, and `default` works for a
       record that inherits an appearance. Eleven runs shipped it empty.
    6. **ONE time period per phase.** Five periods sharing one spot, this
       bench's own run-1 invention, appears in no working community anywhere.

    Which of 3 to 6 is individually load-bearing was not isolated; the stack
    matches what World Builder exports and Personal Mechanics ships, and it is
    cheap to ship whole.

    NOT needed: a quest phase (it spawns unarmed; #63's vanilla phases are
    CONTROL), the city root, Exterior spot sectors, crowd registries, or
    spawn-set tables. `questCommunityTemplate_NodeType` against the community
    works: a per-entry Activate switched the UNNAMED entries off, measured, so
    the node is live and its semantics need reading before gig use.

    A constant carried from the first bench build is invisible to every A/B
    built after it: the empty appearances and the five periods survived eleven
    rebuilds because they sat on both sides of every comparison. The fix came
    from mechanically diffing against a WORKING example, which is what
    `docs/sources.md` now says to obtain first.

67. **A position you did not measure is not ground. Survey the shipped sector's
    own nodes before placing anything.**

    Six runs of a bench put NPCs and props along a line in the North Oak estate
    garden, at the z the player stands at. The line was 48 m long. The terrace
    is 24 m long. Everything past the halfway point had been hanging in mid-air
    since the first run, and it was found on 2026-08-24 by a screenshot of the
    sky.

    **No reading in the bench could see it**, and that is the part worth
    carrying: the scan counted a body within 2 m of its slot, and a body 20 m up
    is 0 m from a slot that is also 20 m up. Every probe agreed with every other
    probe. A wrong shared assumption is invisible to any instrument built on top
    of it, which is the same shape as the constant in #66.

    The survey is cheap and it is the game's own data. Count vanilla node
    placements from the cached sectors within a few metres of each candidate
    point and take the median z:

    ```
    x        332    340    348    356    364    372    380
    y 1042  225.9  225.9  225.9  223.1  221.4  224.0      .
    y 1034  225.9  225.9  225.9      .  221.3      .      .
    y 1026  226.0  226.0  227.0  214.6      .      .      .
    ```

    `.` is no vanilla node within 4 m anywhere. Read two things off it: where
    the ground IS, and where the game itself has built nothing, which is the
    stronger signal of the two. One point being right says nothing about a point
    40 m away, however flat the ground looks from where you are standing.

    **Asking only "is there ground here" is half the question.** The corrected
    positions were on the terrace and one NPC stood inside a wall, because the
    survey counted nodes without reading them. Split them by debug name: lawn,
    sprinkler and light meshes mark open garden and give the ground height;
    hedge, pillar, wall, floor, walkway, crate, cover and planter meshes mark
    something to stand inside. Require no hard node within 3 m AND open garden
    within 4 m.

    Even then it is evidence, not proof: a node's position is its ORIGIN, so a
    6 m wall is a single point and a test on distance-to-origin can be fooled.
    The dev menu's position capture answers the same question from in game and
    is the route to prefer whenever a session is available, because it writes a
    real standing position rather than an inferred one.

68. **A quest phase's output node is `Terminating`, and reaching it kills every
    pause node the phase still has armed.**

    A bench phase set a fact, then fanned out into three
    `questPauseConditionNodeDefinition` waits, one per dev-menu button. The same
    socket also fed the `questOutputNodeDefinition`. The phase therefore ended
    on the frame the fan-out happened, and all three buttons were dead before
    anyone pressed one.

    Nothing reports this. The breadcrumb fact said the chain had completed, the
    waits looked correctly wired in the resource, and the symptom in game was
    "I pressed the button and nothing happened", which is indistinguishable from
    a button that was never pressed.

    A phase that must outlive its own main chain should not reach its output at
    all. Leave the output node in the resource, so the phase keeps its named
    output socket, and connect nothing to it.

69. **A scene CAN take an NPC a mod's own community placed, and it CAN put an
    actor into a mod's own AI spot node. Both measured 2026-08-24.**

    This is the end of the two-bodies arrangement: a mod no longer needs a
    visible NPC for the player plus an invisible scene actor for the voice.

    **Acquiring a community body.** The join is
    `worldCommunityRegistryNode.spawnSetNameToCommunityID`, a table of `CName ->
    community id` (vanilla ships 329 rows, 58 of them the holocall studios). A
    mod registers its own row against its own community, and a scene actor with

    ```
    acquisitionPlan  spawnSet
    spawnSetParams   entryName  = the community entry's name
                     reference  = the string registered in that table
    specRecordId     0, on both the actor and spawnDespawnParams
    ```

    finds that body. `specRecordId` 0 is the safety: the actor is found or the
    scene has no speaker, and nothing can ever be spawned beside the real one.

    The reference is matched as the string that was REGISTERED, not resolved as
    a world NodeRef, so `#short_name` and `$/mod/<sector>/#short_name` both work
    as long as the same string is the row's `nameReference`. That is not the
    resolution rule in #34 and does not contradict it.

    **Placing the acquired or spawned actor.** `questUseWorkspotParamsV1` with
    `workspotNode` naming a `worldAISpotNode` the mod ships works. Values copied
    from Californication: `instant`, `jumpToEntry`, `teleport`, `changeWorkspot`,
    `enableIdleMode`, `isWorkspotInfinite` all 1. `scnUseSceneWorkspotParamsV1`
    extends `questUseWorkspotParamsV1`, so it is the same field set minus
    `workspotInstanceId`, `itemOverride` and `playAtActorLocation`.

    This retires the claim, carried in `questkit/scene.py` for months, that a
    workspot node in a mod's sector is unusable because a mod's own world nodes
    do not resolve. `scnUseSceneWorkspotParamsV1` with `playAtActorLocation: 1`
    is still the right choice when the actor should stay where it spawned; it is
    no longer the ONLY choice, and it is the wrong one when the pose has to
    happen somewhere specific.

    **How to tell acquisition from a scene talking to an empty room**, because
    counting bodies cannot: write the line with `visualStyle: regular`. A regular
    line needs a speaker GameObject the subtitle system can reach, so a subtitle
    that appears at all is an actor that was acquired. See #66's write-up in
    `backlog.md` 29-ADDENDUM-7 for the bench that measured it.

70. **A world node is aimed by the quaternion on its INSTANCE, not by a yaw
    field on the data beside it.**

    A community placed an NPC at the right position facing the wrong way. The
    obvious move is to try 180 degrees, and it would have been a coin flip on
    top of a bug.

    The spot's `AISpotPersistentData.yaw` was set correctly. What was wrong was
    the `Orientation` on the node's entry in `nodeData`, which every generator
    in this project had been writing as identity because nothing shipped so far
    had needed to face anywhere in particular.

    Settled by dumping a vanilla example rather than by turning a knob:
    `generic__sit_couch__sit_around__004` in `exterior_-19_-17_0_0` carries
    `Orientation` k 0.0087 / r -0.99996, about 180 degrees, on its instance.

    ```
    half = radians(yaw) / 2
    Orientation = { i: 0, j: 0, k: sin(half), r: cos(half) }
    ```

    Set BOTH, to the same number. Which one the game reads is not established;
    agreeing costs nothing and disagreeing would be the worst of both.

    The direction of positive yaw is a convention this project has had to
    correct once already, on the script spawn route, where a captured 50.8 had
    to be turned 90 degrees anticlockwise to 140.8. If a body comes out exactly
    180 degrees wrong, flip the sign of the sine term rather than adding 180 to
    the yaw in one place and leaving the other alone.

    The general shape, and it is #67 again in a different disguise: a value that
    is written in two places and read in one is a value that will be right in
    the place nobody reads.

71. **`DynamicEntitySystem` only knows the entities IT spawned. A
    community-placed NPC is invisible to every one of its lookups.**

    Moving one NPC from a script spawn to a community broke three lookups at
    once, and not one of them errored:

    | call | what it did instead |
    |---|---|
    | `GetEntity(id)` | returned null for a body standing in plain sight, which the gig read as "streamed out" and used to skip half the mission |
    | `IsSpawned(id)` | false for the same body, so a death was never detected |
    | the same `GetEntity` inside a shared attitude helper | null every time, so the retry fired forty times over sixty seconds and the attitude was NEVER applied |

    Use `GameInstance.FindEntityByID(game, id)`, which finds either kind. Where
    both are possible, ask the dynamic system first, because it is the cheaper
    query, and
    and fall back:

    ```
    let obj = GameInstance.GetDynamicEntitySystem().GetEntity(id) as GameObject;
    if !IsDefined(obj) { obj = GameInstance.FindEntityByID(game, id) as GameObject; }
    ```

    The third one is the one to learn from. It lived in `shared/scripts`, it had
    been correct for a year, and nothing about the file changed: what changed was
    where the NPC came from. **A helper is only correct for the way its callers
    happened to work when it was written.** Any shared code that takes an
    `EntityID` and asks one system about it is worth re-reading the first time a
    caller places a body a new way.

72. **A community places the BODY at its AI spot. It does not reliably put that
    body into the spot's WORKSPOT.**

    Sixteen bench runs used a STANDING idle and every one of them looked right.
    The first pose that is not standing showed why that proved nothing: an NPC
    standing because his workspot never applied is indistinguishable from an NPC
    standing because it did.

    Given a `sit_couch` spot, the NPC was placed at the spot and stood on the
    cushion. Playtest also reported "he glitched for less than a second" as the
    player came into range, so the pose may apply and then be lost rather than
    never apply at all. Unresolved either way.

    What DOES work is driving it: `questUseWorkspotParamsV1` with a
    `workspotNode` naming a mod's own AI spot moved a scene actor into it,
    measured (#69). So treat a community spot as a POSITION, and a pose as
    something a scene or a quest node has to ask for.

73. **A generator that stops running is SILENT, because the build packs the JSON
    already on disk.**

    The generators import from each other. Renaming one constant in one of them
    breaks every importer, and nothing downstream notices: `build-archive.ps1`
    packs whatever JSON is in the raw tree, and the last good output of a
    generator that has since broken is indistinguishable from a current one.

    This shipped a hard crash on 2026-08-25. A community entry was renamed;
    the quest-phase generator had been importing the old name and had been
    failing on import ever since; the packed quest phase went on carrying three
    references to a community entry that no longer existed. **The game merged
    every file without a single warning and then died**, and the ArchiveXL log
    was clean end to end.

    `tools/gig01/run_all.py` runs every generator in dependency order and exits
    non-zero on the first failure. Run it after touching any generator, before
    building.

    `deploy-dev.ps1` already refuses to deploy when raw files are newer than the
    packed archive, and that is the other half of the same problem. It
    cannot know that a file which was never REGENERATED should have been.

    **And the rule the crash itself teaches: a quest phase switches only what it
    owns.** The gig's phase had been told to deactivate a bench entry as a
    convenience. When that entry was renamed, a shipped phase was left reaching
    for something that did not exist, on every load, for every player. The bench
    now switches its own entries off itself.

74. **A community-placed NPC arrives with no quarrel with the player, and an
    NPC with no quarrel never starts looking. The ATTITUDE is what switches
    perception on.**

    Measured 2026-08-25, three guards at one post, one at a time: two vanilla
    records at their default attitude both stood there and did nothing, and the
    same record with `CCSharedAttitude.Hostile` applied detected the player on
    the ordinary ramp, slowly at distance and faster on approach, and went to
    combat. The record decides nothing; the attitude decides everything.

    `senseComponent.ShouldStartDetectingPlayer` treats a hostile attitude as
    "start filling the meter", so with no attitude there is no meter and no
    reaction. That was written up from the game's own scripts in August and this
    is the same fact arriving from the other end.

    **Do not read "he does not react" as "community NPCs have no AI".** They have
    the base game's, at base-game rates, the moment they have a reason.

    And the thing that is genuinely NOT included: the trespass warning, "you
    shouldn't be here", the call-out, the walk over, and only then a fight. That
    happens to somebody who is NOT an enemy, which is the opposite of what makes
    the guard above work. It comes from a SECURITY AREA linked to the community
    by a `CommunityProxyPS` device connection, which the wiki documents and a mod
    can ship. `backlog.md` 31.

75. **A mod can ship MORE THAN ONE community, and two communities are two
    separate stacks rather than two items in one registry.**

    Built 2026-08-25: `cc_g01_hoshino` holds one man on a couch and
    `cc_g01_estate` holds thirty guards at thirty posts, side by side, each with
    its own pair of AlwaysLoaded sectors and its own streaming block. Both are
    registered in the same `.archive.xl` under `streaming: blocks:`, which is
    already a list.

    Vanilla does put many communities in one `worldCommunityRegistryNode`, and
    that is not the reason to avoid it. The reason is that the second community
    is the one being debugged: sharing a registry means rewriting the file that
    already works, and a change there is invisible until a save load. Two stacks
    cost one extra always-loaded sector whose entire content is one node, and
    the working community's two sectors come out BYTE-IDENTICAL, which is the
    check that says the shared recipe did not disturb it.

    It also keeps a quest phase honest. A `questCommunityTemplate_NodeType` with
    no `communityEntryName` addresses the whole community, which is what 112 of
    133 sampled vanilla uses do, so thirty guards switch in ONE node at each
    beat. Thirty entries inside one community would have meant naming them one
    at a time, or trusting `actions` to hold thirty entries, which is a shape
    nothing here has read off a working example.

    The split has a second payer. A security area is linked to NPCs by a
    `CommunityProxyPS` device connection pointing at one community's NodeRef, so
    which NPCs are in which community decides who can be alerted. An alerting
    community must not contain the man the player is there to talk to.

    The recipe itself is #66 and did not change. `questkit/community.py` is it,
    parameterised, and the per-community file states only who stands where.

76. **A restated list is a list that drifts, so make the generator READ the
    redscript and refuse to write when they disagree.**

    Thirty community entry names exist in two places: the generator that ships
    them and the `array<CName>` the encounter looks them up with. Redscript
    cannot import Python, so there is no way to have one copy.

    Nothing reports a mismatch. `GetGameObjectsFromSpawnerEntityID` given a name
    no entry carries simply returns fewer bodies, and fewer bodies is exactly
    what a post that has not streamed in yet looks like. The failure hides
    inside the normal case.

    So `gen_estate_guards.py` parses `EstateEntries()` out of
    `Gig01_Encounter.reds`, compares the two lists name for name and in order,
    and exits non-zero on any difference. It also checks the community NodeRef
    written in the redscript against the one it is about to generate. Proved to
    bite by renaming one post and watching the generator refuse.

    Same shape as the bench cross-checking its slot table against the redscript
    scan's copy, and the same lesson as #73: the dangerous version of a broken
    reference is the one that loads.

77. **A community-placed NPC arrives with his senses SWITCHED OFF as far as the
    player is concerned, so a hostile attitude on its own buys nothing.**

    #74 said the attitude is what switches perception on, measured on one guard
    at one post. Thirty guards at thirty posts said otherwise, playtest
    2026-08-25: every one of them stood at his post with the attitude applied and
    read back, and not one ever noticed the player. They fought when shot, and
    they joined in when one of the estate's OWN NPCs raised the alarm, so they
    were not inert. They never STARTED looking.

    That is the shape of a missing sense component rather than a missing
    attitude. `ShouldStartDetectingPlayer` treats a hostile attitude as "start
    filling the meter", and a meter on a component that is disabled never fills
    however hostile the NPC is.

    Hoshino's `TurnOnPlayer` has done both since August, for exactly this reason,
    and its comment says so in as many words: *"AND HIS EYES ON, which the
    attitude does not do ... an NPC who cannot perceive V cannot shoot at him
    however hostile he is."* The guards were given the attitude and not the
    eyes, and the note that would have prevented it was forty lines away in the
    same file.

    ```
    CCSharedAttitude.Hostile(game, puppet.GetEntityID());
    let senses = puppet.GetSensesComponent();
    if IsDefined(senses) { senses.Toggle(true); }
    ```

    **#74 is not wrong, it is too small.** One guard was measured and one guard
    worked, and the difference between him and these thirty is not established:
    it may be the record, or it may be that his workspot never applied and he was
    standing free. A sample of one cannot tell "this is how communities behave"
    from "this is how that guard behaved".

78. **Count what LANDED, not what you asked for.**

    `posts turned: 30 of 30` was on screen while not one guard was reacting. The
    number was true and useless: it counted the bodies the lookup found and
    called an attitude helper on, which is a statement about our own code rather
    than about the guards.

    A readback costs one pass over the same array and separates the three ways a
    guard standing at his post can still ignore the player:

    | | if it is low, or high |
    |---|---|
    | `agent.GetAttitudeTowards(player) == Hostile` | low: the attitude never reached these bodies |
    | `senses.IsEnabled()` | low: enemies who cannot see, which is #77 |
    | `GetWorkspotSystem().IsActorInWorkspot(npc)` | high: held in an idle that may suppress perception |

    Three hypotheses, one pass, one playthrough. The alternative that was very
    nearly taken instead was to change the pose and the senses together and see
    whether it got better, which would have cost a run and settled nothing.

    Same family as #17 and as the three instrument faults of 2026-08-25: the
    measurement described the intention rather than the result.

79. **A mod CAN ship a node with an embedded `entEntityInstanceData` RedPackage
    buffer, and that unblocks security areas.**

    This was called the blocker on the whole security-area feature for two days,
    because a security area's trigger polygon lives in such a buffer and nothing
    this project ships had ever contained one.

    Settled 2026-08-25 by asking the smallest version of the question rather
    than by writing a generator and hoping. The vanilla node was taken WHOLE,
    given our names and our refs, put in a sector of our own, and handed to the
    converter the build already uses:

    ```
    WolvenKit.CLI convert deserialize <our sector>.json
    WolvenKit.CLI convert serialize   <our sector>       # and read it back
    ```

    It converted, and the round trip returned the buffer intact: both chunks,
    the outline point for point, the height, `securityAreaType` and all 122
    fields of the controller state. The feature was data all along.

    **The technique generalises past security areas.** Any vanilla node type
    with an instance buffer can be copied this way, and the round trip is what
    turns "it converted" into "it converted correctly": a converter that
    silently drops a buffer would also report success.

    **TWO THINGS HAVE TO BE FIXED UP, and both refuse the WHOLE FILE rather
    than the node, with an error that points at the line where the buffer ends
    and says nothing about why.**

    - **`BufferId` must not be 0.** A sector's `nodeData` is itself a buffer and
      it is buffer 0, so an instance buffer that also claims 0 collides with it:
      `The JSON value could not be converted to RedFileDto`. Vanilla's example
      is buffer 78 in a sector with many; 1 is enough for a sector with one.
    - **A CRUID is a SIGNED 64-bit integer.** Deriving component ids from an
      FNV1a64 uses the whole unsigned range, and the first attempt produced
      10314632116389077042, which is above 2^63:
      `The JSON value could not be converted to RedPackage`. Mask to 63 bits.
      Vanilla's two are 1508365491801698304 and 1395159393761816576, both
      comfortably positive.

    Neither is discoverable by reading a vanilla node, because a vanilla node
    has the right values already. They were found by diffing a node that
    converted against one that did not, field by field, which took minutes
    where guessing had already taken longer.

80. **A SECURITY AREA DOES NOT ALERT A MOD'S OWN COMMUNITY. Built, measured,
    and taken back out on 2026-08-25.**

    READ THIS BEFORE BUILDING ONE. The shape below is correct and is copied
    from the game's own data; what it does not do is work. Every part was
    measured right in game and the guards did nothing at all:

    | | |
    |---|---|
    | the area node | found and resolved |
    | its device state | ON, attached, not disabled |
    | `securityAreaType` | RESTRICTED, the same value a vanilla area reports |
    | `CommunityProxyPS` | pointing at our community |
    | the security system node | present, linked to the area |
    | `IsPlayerInside()` | TRUE while the player stood in the compound |

    Setting the type between RESTRICTED, DANGEROUS and SAFE at runtime changed
    nothing, which is what an area with nothing on the other end of its wire
    looks like.

    **The one difference left, after eliminating the node class, the type, the
    component ids, the outline, its winding, the missing system node and
    containment:** every vanilla community a security area alerts, all 21 that
    resolve in the cached sectors, is a `worldCompiledCommunityAreaNode` in the
    GAME'S OWN `always_loaded` sectors. A mod cannot add nodes to those.
    ArchiveXL deletes and mutates what is there; it does not add.

    That is not proof, it is what survived elimination. `backlog.md` 31 has the
    whole thing.

    **What to build instead:** give the guards a hostile attitude (#74) and let
    the ordinary detection ramp do the work. That is what a mod can have, it
    runs at base-game rates, and at an Arasaka site under infiltration it is
    what the base game does anyway.

    The shape itself, for whoever gets further than this:

80a. **A security area is ONE node, and it carries both halves of the wiring.**

    Read off `{q112_infiltration_security_area_civilian_restricted}` in
    `exterior_-4_-23_0_0`, which is at the Arasaka compound this gig already
    uses:

    ```
    worldDeviceNode
      entityTemplate   base\gameplay\devices\security_systems\security_area\
                       security_area_1.ent
      deviceConnections
        CommunityProxyPS                 -> the communities it alerts  (3)
        SurveillanceCameraControllerPS   -> the cameras that feed it   (9)
      instanceData -> buffer -> Chunks
        gameStaticTriggerAreaComponent   outline points in LOCAL space + height
        SecurityAreaController
          persistentState.securityAreaType   RESTRICTED
    ```

    **On the system node:** the `CommunityProxyPS` link can live on either the
    area or the system, and vanilla has it both ways. The wiki calls the system
    MANDATORY and omitting it was one of the things tried and eliminated above,
    so ship both. And `securityAreaType` is RESTRICTED on this example rather
    than the Hostile the wiki gives as the default.

    RESTRICTED is the trespass case and is the point of the exercise: somebody
    who is not yet an enemy being told to leave. Hostile skips the warning,
    which is the half a guard's attitude already provides (#74).

    Eighteen device nodes in the cached sectors carry a `CommunityProxyPS`
    connection: 9 security systems, 4 security areas, 2 access points, 2 virtual
    access points and a wall router. Three of the eighteen have no instance
    buffer at all, so the wiring half can be shipped without one.

81. **A stim broadcast has no audience, so it is the wrong tool for a mod's own
    alarm.**

    The camera alarm was a script for one build: watch the cameras, and when one
    reports `IsDetecting`, call
    `stim.TriggerSingleBroadcast(player, gamedataStimType.Combat, 60.0)`.

    Playtest, within minutes: *"the police also marks me as enemy even if I
    haven't done anything"*. A stim broadcast announces at the player's position
    that combat is happening, to EVERY NPC in range. Police, civilians and
    anyone passing all reacted correctly to an announcement the mod had no
    business making.

    It also fed itself: the fight it started made the cameras legitimately
    detect the player, which raised the alarm again. A second report, "the
    cameras spot me when I am far away", was the same loop seen from the other
    end, and it sent one debugging session after a distance problem that did not
    exist.

    **The fault is the shape, not the radius.** Twenty metres would have been a
    smaller blast, not an aimed one. An alarm meant for one community has to be
    addressed to it, and that is exactly what a `CommunityProxyPS` connection
    does and what the stim system cannot do at all.

    The camera side of it is worth keeping: `SurveillanceCameraControllerPS.
    IsDetecting()` is the one question a camera answers about what it can see,
    and of thirty detection and alarm names probed on one, only `IsDetecting`,
    `GetTargets`, `GetSensesComponent`, `IsHostile`, `GetSecuritySystem` and
    `GetBlackboard` exist.

82. **A base-game device's runtime entity id is the FNV1a64 of its full NodeRef,
    so a mod can address one without ever touching it in game.**

    Predicted and confirmed 2026-08-25. A camera captured in game reported
    entity id `8148897925467091288`; the FNV1a64 of its NodeRef in
    `exterior_-4_-23_0_0`, with the '#' characters removed, is exactly that
    number. Same rule as a community's id (#62), applied to a shipped device.

    That turns "which cameras are at this site" from twenty-six clicks into a
    cache query, and it is what makes both the security area's camera list and
    the script that switches them on possible at all.

    ```
    let g: GlobalNodeRef = ResolveNodeRef(CreateNodeRef(<the full ref>), root);
    let obj = GameInstance.FindEntityByID(game, Cast<EntityID>(g));
    ```

    The refs are the absolute `$/03_night_city/...` form and are registered in
    their sector's `nodeRefs`, which is the form a mod resolves (#39). The short
    `#name` form vanilla writes inside its own prefabs does not.

83. **A device walks DISABLED to OFF to ON, one action per frame, and a
    destroyed one does not walk back at all.**

    #37 and `Gig01_OfficeDoors` established the ladder for doors. Probed on a
    camera 2026-08-25, the whole menu of what a `SurveillanceCameraControllerPS`
    will accept:

    | | |
    |---|---|
    | EXISTS | `ActionQuestForceON` / `OFF` / `Enabled` / `Disabled` |
    | EXISTS | `ActionSetDeviceON` / `OFF`, `ActionToggleON` |
    | EXISTS | `ActionForceIgnoreTargets`, `ActionSetDeviceAttitude` |
    | no | `ActionQuestForceUndestroy`, `ActionQuestForceDestroy` |
    | no | `ActionRepair`, `ActionQuestRepair`, `ActionRestoreDeviceState` |

    **There is no repair ACTION.** It was looked for under four names. What does
    exist is a method, `SetDurabilityState` on the state, and restoring the
    health separately does un-kill the device: measured, a shot camera went from
    health 0 / `IsDead` true / durability BROKEN to health 1 / `IsDead` false
    with durability still BROKEN, and `ActionQuestForceEnabled` then took its
    device state to ON. So repair is possible and is two steps, not one.

    A shot camera reads `EDeviceStatus 4294967294`, which is not a state. The
    same number appears in `Gig01_OfficeDoors` from racing actions, so it is
    what the field holds when it holds nothing.

    **Ask what a device can be told, do not guess.** Building an action
    (`ps:ActionQuestForceON()`) does not execute it, so constructing each one is
    a free way to enumerate the menu. That one probe replaced a queue of
    one-theory-per-playthrough.
