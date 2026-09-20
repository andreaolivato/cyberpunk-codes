# Gig 02: Dead Ringer

## Premise


Wakako Okada sells one thing, and it is not muscle. It is her word. A fixer's
approval is what lets a client believe a job was sanctioned and lets a merc
believe he will be paid, and both of those beliefs are worth more than any
single contract.

Someone has been issuing kill orders in her name. The orders carry her tag and
her phrasing, the authorization survives inspection, and the money really does
clear. People under her protection are dying on contracts she never approved.
The bodies are not her problem. The doubt is.

V is hired to find out who is speaking as her and to stop it. The trail runs
through a merc outside Afterlife, a netrunner in Japantown, and a relay hidden
inside Wakako's own pachinko parlor. The impersonator is one of her own, working
from inside the building she sits above.

Timeline: during the main game, post-relic (Johnny present throughout).
Source material: the Dead Ringer comic (92 pages, not part of this repo), which
doubles as the visual and staging reference for every beat.

## Quest flow


| # | Beat | Mechanic | Facts |
|---|------|----------|-------|
| 1 | An SMS from Wakako: a job that will not keep, call me | Phone message thread, and NOTHING ELSE: the quest does not appear until the call is over | `cc_g02_started` |
| 2 | V calls her back | The player picks the reply in the thread, and that choice issues the call. The conversation is the comic's opening call | `cc_g02_called` |
| 3 | Travel, LOCATION 1: Afterlife | Objective and map pin. The queue outside is where the lead is | `cc_g02_afterlife_reached` |
| 4 | The talk outside | A short scene carries the Jig-Jig Street lines, which are the actual lead. The Rogue and Claire chatter around it is ambient | `cc_g02_lead_heard` |
| 5 | The merc | A kill order. The brief names Jig-Jig Street, his boast outside Afterlife names it too, and the objective is to take him out. He cannot die in the fight: at a third of his health he stops, goes down on one knee and begs. He hears who sent V, says Wakako hired him, and hands over the proof. Then the player chooses: finish it, or let him go and watch him run | `cc_g02_merc_armed`, `cc_g02_merc_down`, `cc_g02_merc_fate` |
| 6 | The proof | His messages: the approval, the instruction to keep collateral minimal, the payment confirmation. Wakako's tag, her wording, and the eddies really cleared | `cc_g02_proof_read` |
| 7 | Reporting in | V tells Wakako what the shard says by picking a reply in her thread. She answers by message: bring it to her netrunner, location attached | `cc_g02_reported`, `cc_g02_wakako_2` |
| 8 | Travel, LOCATION 2: the Dewdrop Inn | Objective and map pin appear only after that call | `cc_g02_inn_reached` |
| 9 | The trace | Yoko checks who sent V, Char takes the shard, and half an in-game hour later Char's message carries the verdict: not a street spoof, the authorization checks out, and the origin is local. A pachinko parlor. Wakako's | `cc_g02_char_near`, `cc_g02_trace_done` |
| 10 | Travel, LOCATION 3: the pachinko parlor | Objective and map pin. The pin is on the parlor and never on a machine | `cc_g02_parlor_reached` |
| 11 | The breach | Char's call names a hardline access point on the parlor wall. V jacks in and plays the game's own code grid; the breach is the objective. The dump goes to Char, and her text twenty minutes later names the man | `cc_g02_ap_breached`, `cc_g02_char_named` |
| 12 | The face | Char's message off the dump: five after-hours sessions from one handset, registered to the parlor's night security. She has his face and not his name | `cc_g02_char_named` |
| 13 | Wakako in person, LOCATION 4: her office, upstairs from the parlor | The first time she is in the room rather than on the phone. She recognises him and orders a killing nobody is ever to hear about; her text after the conversation carries the target's name, the place and the rule that it stays quiet. The player may ask why she does not make an example of him, and she answers | `cc_g02_wakako_met` |
| 14 | The approach, LOCATION 5: a Japantown staircase | Toji is holed up with Tyger Claw company. **The gig requires that V is not spotted before he dies** | `cc_g02_hit_reached` |
| 15 | The kill | Toji is the only person who has to die. Nobody speaks: V reaches him and kills him, and the beat is the silence | `cc_g02_toji_dead` |
| 16 | Out again | Leaving unseen is its own objective, and the area to get out of is drawn on the minimap. Being seen, at any point, is the other ending: a firefight, and a colder call from Wakako | `cc_g02_exfil_done` |
| 17 | The two calls home | "Call Wakako" is up while her closing call dials itself; she pays either way and the words are different. Then "Listen to Johnny" until his last line, which also forks on whether V was seen | `cc_g02_closed`, `cc_g02_done` |

**Five locations, and four of them are base-game places the player can already
stand in.** The parlor and the office are one building, which is what makes the
trace coming home look damning before it turns out to be someone working from
inside Wakako's own floor. The gig is a Westbrook story with one trip out to
Watson.

## How the gig starts, and why it is not a call


**The design call: an SMS, then a call the player places from the thread.**

The obvious opening is an incoming holocall, because that is how the previous
gig starts. It is the wrong choice here, for two reasons.

A call takes the moment away from the player. If the phone rings mid-firefight,
the gig has started badly and nothing can undo that. A message waits.

More importantly, a call cannot share the player's phone with anything else. Two
mods that both ring collide, and whichever loses is answered into silence or
missed outright. Two messages simply sit in the list. A gig that expects to be
installed alongside others should open on something that can queue.

The medium is in character rather than a compromise. Wakako's canonical way of
giving a gig IS a message with a brief attached: "I am attaching more
information. Read it. Carefully." She does it in every street story she offers,
and she does it here too: the first text asks for the call, the call is her own
lines, and the brief arrives as her next message and as the journal's briefing
paragraph. The order matters, because she can only speak in her own recordings:
a call cannot carry the premise, so the text does.

**The message text:**

> V, my dear. I have a job for you, and it is one that will not keep. Call me
> the moment you read this.

It used to hint at the plot ("Something has been done in my name. I will not
put the rest in writing."), which stopped making sense once the call became
five of her own lines and the details arrived as a message afterwards. The
premise now lives in that second message and in the journal brief, in the
game's own gig layout.

**The player calls her back, and the reply in the thread is what does it.**
`docs/scene-playbook.md` is explicit that a mod cannot make V call a base-game
contact: the contact's own default conversation owns that direction, and a mod
cannot branch a base-game scene. The mod-owned route rings a contact the mod
ships, carrying the same display name and avatar, and the quest phase is what
issues the call. So the player cannot start it by opening the phone and dialling.

What the player CAN do is answer a message. The thread carries a reply, the quest
phase pauses on that choice entry, and picking it issues the call. The player
still chooses the moment, and every piece is already proven: the message thread
with replies in `docs/journal-research.md`, and the mod-owned outgoing call in
`docs/scene-playbook.md`.

**No location gate.** The message arrives shortly after the save loads, wherever
the player is. Gating it on entering a district was considered and dropped: a
player who never goes there never gets the gig, and nothing about the opening
should depend on the player working something out.

**V speaks first on that call.** The comic opens on Wakako saying "V." and V
answering "Wakako.". The player is the one dialling here, so the two lines swap.

## Voice: follow canon, for every character

The rule the whole script is written to: **a character the base game voices
speaks only in the game's own recordings**, whole or cut short at a pause, and
**a character this gig invents is recorded by a person**.

That decides the writing before it decides anything technical. If no recording
of V explains a forged authorization, V cannot explain it, so the plot moved
into what the player reads: the fixer's messages, the objective's details text,
and the shard. Which is where the base game puts its own exposition anyway.

Subtitles always, on every line, in every language the mod registers.

### Follow canon


**The rule for this gig: every character who exists in the base game is written
in their own canonical voice, and that voice is looked up rather than
remembered.** `tools/vo_corpus.py` holds every spoken line in the game joined to
its speaker, so "how does this person actually talk" is a query, not a memory.
Read a character's real lines before writing any of theirs.

That applies to Wakako, Yoko and Johnny here, and to anyone added later.

### Wakako specifically

She has two registers, and the difference is content rather than mood.

In the main story she is clipped and transactional. In her street-story gig
briefings, which is what this gig is, she is ornate and courteous, uses almost no
contractions, and calls V "my dear" or "child". She wraps a threat in politeness
and closes every contract with the same phrase.

Her own lines, for reference:

> "V, my dear, I need you to pay a visit to a Tyger Claw den and retrieve
> something for me. I know you are up to the task."

> "Next time, think before you act ... otherwise you gamble with my temper. It
> is a losing game."

> "V, I need you to acquire something. Only me, no client ... so I expect quick
> and clean results."

> "I am closing the contract and transferring your fee."

The ellipses stand in for a dash the extracted corpus does not preserve, so they
mark an elision rather than a pause she actually takes.

That third line is this gig in her own words, since here the client is her
reputation. Write her formal, unhurried and without contractions, and let the
courtesy carry the threat.

**The comic's Wakako is colder and flatter than the real one**, so her comic
lines are a starting point rather than final text. Where the comic and the canon
voice disagree, canon wins.

## Languages

The gig follows the player's voice-over language. A line spoken in the
game's own recordings comes with its own dub, so Wakako, V, Johnny and Yoko
speak whatever the voice pack speaks, and the seven cut lines are cut again
in each dub with the dub's own words as subtitles. Char and the merc are
English only. The gig's own text is English until a translation exists; a
translation is a mod of its own, built from `translation-kit/`
(its README is the guide), and `docs/scene-playbook.md`, "Other languages",
is the mechanism.

## The cast: who is a body


Every character the player meets is one body, standing where they are met,
taken from this gig's own community. There is no voice-only actor parked off
the map and no second body spawned beside a first.

| Who | Where | Voice |
|---|---|---|
| Wakako | her office, and four calls | the game's own recordings |
| Yoko | the Dewdrop Inn | the game's own recordings |
| Char | the netrunner chair, and one video call | recorded, 4 lines |
| the merc | outside Afterlife | recorded, 9 lines |
| Toji | the Japantown stairs | silent |
| V, Johnny | throughout | the game's own recordings |

**The scenes take those bodies with the `community` acquisition plan**, not the
spawn-set one. The difference only shows after a save is reloaded, and then it
shows as every one of them going silent. Gotcha 102.

**Char is in two places and must look the same in both**, since she sits in the
chair and later calls V on video from the holocall studio. One appearance name,
pinned on the record, on the community entry and on the studio actor.

## The merc, outside Afterlife


He is the only source for the proof, so the gig cannot survive him dying by
accident. He is unkillable through the fight, drops at a third of his health,
and talks from the floor.

**He does not start it.** He is hostile but does not open fire; the player
does. The fight ends with him kneeling, not dead, and he stays kneeling: there
is no stand-up animation a mod can drive that does not read as a glitch, so he
holds the pose through the conversation and the choice.

**Then the player chooses.** Finish him, or let him go and watch him run. Both
close the beat and both are paid, differently.

**Only the shard is on him.** A downed body's loot list is whatever his record
dropped plus whatever the gig put there, so everything but the shard is
stripped, and his weapon with it. Looting a corpse for a gun in the middle of
this beat reads as robbing him.

**He is a man**, because the recorded voice is a man's: a masked Wraith grunt,
the appearance pinned on both the record and the community entry so nothing can
roll another.

## The parlor beat: a breach


Char's call names a hardline access point on the parlor wall. V jacks in and
plays the game's own breach-protocol minigame, and the dump goes back to her.

**It is the game's own device and its own grid**, not an imitation: a physical
access point the mod ships on the wall, with the daemon named from the mod's
own records. The gig watches for the breach and nothing else. `backlog.md` 37
has the recipe and the two shapes that render but do not work.

**Any build can open it.** Jacking in is an Intelligence check, and the level
an access point asks for is its own rather than the player's, so the box the gig
lifted arrived asking for 10. It asks for 3, the lowest an attribute goes, so a
character who never spent a point can still finish the leg.

**The box stays on that wall** whether or not the gig is running, because it is
part of the mod rather than something switched on for the leg. The mod page
says so.

**The map pin sits on the parlor, never on the box.** A pin on the box would
delete the search.

## The hit: an assassination, not a firefight


**It departs from the comic on purpose.** In the comic V decides there is no
quiet way in and rushes the street. Here Toji is the only person who has to
die, and the objective is to kill him without being seen.

**Nobody stands down.** The Tyger Claws around him never turn neutral, whatever
happens to Toji. They do not know V and they do not know who sent him, so the
reaction to bullets is bullets. Unseen, they never learn anything happened;
seen, it is a firefight and stays one. An early version had them lower their
guns the instant he dropped, which is the quest's knowledge leaking into the
world; `backlog.md` 43 keeps it.

**Being seen is a softer outcome than a fail.** It is watched from the moment
the objective goes up until V is clear, it changes the wording of both
objectives while they are open, and it decides which of two closing calls
Wakako makes and which fee she pays. It never ends the gig. A hard fail that
fires wrongly ends a playthrough with no recourse.

**Nobody speaks at the kill.** V reaches him and kills him. The quest waits on
his death and on nothing else, and his own body reports it the moment it
happens: from any range, with any weapon, whether or not V has come near the
stairs yet. A kill from a roof or with a quickhack from the street moves the
objective on without a walk to the top, and no guards are placed for a man
already dead. A knockout is not a kill: System Collapse, a blunt weapon or a
choke leave him breathing, and the objective stays open until he is dead. The
game pays its NCPD bounty on either, so the money landing does not mean he is
gone.

**Getting out is its own objective, and the area is drawn on the minimap.** The
shape is the hull of the walked ground, the stairs, the trash pile and the
walkway above, pushed out by 12 m, shipped as a trigger area the way-out pin
points at. The same corners drive the script's own test, generated rather than
copied. `map-pins-playbook.md` has the recipe.

## The two waits, and the place to take during each

Twice the gig asks the player to wait: half an in-game hour while Char runs the
trace, and twenty minutes while she reads the relay dump. Both are measured on
the world clock rather than on the player's, so the wait keeps running while
the phone is open and the HUD clock shows it passing.

**Each wait has somewhere to be.** A railing outside Yoko's stall in Kabuki,
and a chair outside the pachinko parlor in Japantown. The objective's map pin
points at it and is labelled "Waiting Spot", which is the game's own label
for the same thing.

Walk up and take it. V leans on the rail, or drops into the chair, and holds
it for a few seconds. The screen fades, the clock moves on by what is left of
the wait, and he is standing again as it fades back and the message arrives.
The fade is the game's own, the same one it uses either side of a wait in the
Claire races.

**It is offered, never required.** A player who does not find the spot, or does
not want it, waits exactly as before: the objective is the same, the message
arrives on the same clock. The quest runs the two against each other and takes
whichever comes first, which is the rule the gig follows everywhere a wait
exists to cover something: a wait must not be able to stop the story.

**The shape is the base game's.** Four legs of the Claire races carry an
objective named for waiting, each pinned at a place to take, two of them a sit
and two a lean. The one difference is that no clock runs there: Claire arrives
because V took the place. Here the time is real, because Char needs it, so
taking the place moves the clock rather than skipping past it. Char says half
an hour, and half an hour is what has passed.

The poses are the game's own player animations, one for leaning forward on a
rail and one for sitting back in a chair.

## Reward


Four completion records, one per outcome, handed to the game's own reward
routine so the money notice, the level-scaled XP and the telemetry are
vanilla's.

| Merc | Toji | Eddies | XP | Street Cred |
|---|---|---|---|---|
| killed | unseen | 15,000 | 1,000 | 1,136 |
| spared | unseen | 11,300 | 1,000 | 1,136 |
| killed | seen | 7,600 | 1,000 | 1,136 |
| spared | seen | 5,600 | 1,000 | 1,136 |

The numbers depend on Wakako's own nine Westbrook gigs, which pay 3,800 to
16,600. `backlog.md` 40 has how they were read and why the records are
clones.

**The top tier sits near the top of her range on purpose.** What V is paid
for is not the killing, which she could buy anywhere. It is that nobody
hears about it. A fixer buying silence about a man who forged her own
authorization pays what silence costs, and each thing that goes wrong takes
a share of that off: sparing the merc leaves someone alive who can talk, and
being seen at the staircase means the killing was public after she asked for
the opposite.

## Where the mod deliberately differs from the comic


- **The opening is a message and a call the player places**, not an incoming
  call, and V speaks first. "How the gig starts" has the reasons.
- **The hit is a stealth assassination in both directions and nobody is ever
  told**, where the comic has V rush the street, shoot through it and leave a
  witness to spread the word. Wakako's instruction is inverted with it: the
  comic's "make sure it is seen" became an order to keep it quiet. It comes from
  the premise rather than from the page: a fixer whose tag was forged for months
  cannot afford the question a public killing invites.
- **The parlor is a breach rather than a search.** The comic has V scan the
  machines and find the odd one out; the gig has him jack into a hardline on
  the wall and play the game's own code grid.
- **The merc can be talked out of the shard.** The comic only has the beating.
- **The merc cannot be killed.** The comic never has to solve this because a
  comic cannot lose its own witness.
- **Yoko's call was to carry her real avatar**, where the comic shows the
  anonymous placeholder tile. **It does not, and that is a measurement rather
  than a change of mind.** The base game ships 125 `PhoneAvatars.Avatar_*`
  records and none of them is Yoko; the same string table holds no `Character.`
  record and no atlas part for her under either Yoko or Tsuru. She is an
  unnamed Clouds NPC placed by a scene, so there is no real avatar to point at.
  Giving her one means shipping an inkatlas and a `PhoneAvatars` record of our
  own, which is a separate piece of work. Until then her contact carries the
  placeholder tile, which at least matches the source.
- **Base-game characters follow their canonical voice** where the comic's
  version of them disagrees.

If a difference is not written down somewhere, it is a bug, not a decision.

## Build status


Playable end to end, both endings, including the save-and-reload case.
Nothing outstanding.

## Where the history is


This file is the design as it stands. The route it took to get here is not
here:

- `docs/backlog.md` for the research and the dead ends, including 43 for three
  beats this gig built and removed.
- `docs/gotchas.md` for the traps, and `docs/architecture.md` for the decisions
  that outlive one gig.
- The playbooks for the recipes: map pins, scenes, the computer UI.
