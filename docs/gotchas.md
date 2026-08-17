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
