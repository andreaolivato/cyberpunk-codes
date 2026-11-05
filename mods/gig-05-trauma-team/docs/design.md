# Trauma Team: design

V signs on with Trauma Team International and works shifts in one of its
AVs. A shift is a flight out from Little China, up to three
incidents, and a flight back. Every incident is a Trauma Team client down
somewhere in the city, with someone standing over them who wants them dead
or wants their chrome.

This is the first gig here that repeats. It closes nothing: the job stays in
the journal, and the AV is back on its pad for the next shift.

PC only. It needs RED4ext, ArchiveXL, TweakXL, Codeware and redscript. Its own
script calls only the game's functions, and the release's shared scripts need Codeware.

## What the player does

1. After the prologue, wherever V is, a text from Trauma Team Dispatch
   arrives: probation crews wanted, interviews in person at the Medical
   Center. A marker shows the recruiter.
2. The recruiter waits outside the Medical Center. A short interview, and V
   is hired on probation.
3. The staff elevator is the glass lift in the tank yard behind the building,
   in a steel frame of its own. V walks in and presses the keypad, then
   crosses a closed walkway to the armory on the roof. The objective is
   "Get changed in the armory". At the shelves of helmets and shirts V
   presses "Get changed." and gets the uniform and the SMG, with the game's
   "new item" card the first time. This happens every shift. V goes out through
   the room's door to the pad, where the AV waits with its crew, and Brekke
   speaks as V comes near. V walks to the AV's open side and gets "Board the AV".
4. V stands at the open door, holding on. The AV lifts off. The crew lead
   reads out the call while Little China drops away.
5. The AV flies across the city and sets down at the call. The soldier
   calls the landing and V steps off beside the door.
6. The client lies on the ground and Scavs are around him. The medic
   kneels at the client, the soldier stands guard at the AV with a rifle,
   and the lead goes after the Scavs with V.
7. With the Scavs down, the lead calls it clear and walks back to the AV.
   A short fade, and the crew stand in the cabin; V walks aboard past them
   and the AV lifts off for the next call.
8. Three calls a shift: a hotel roof, a street by the water, a Kabuki
   plaza. After the third the AV flies home to the roof. V gets out and
   takes the lift down the side of the building, by the keypad. The pay for
   the three calls arrives with the game's own money and XP notices.

Later shifts start at step 3.

## The first encounter

The sign-up and the first shift are one fixed sequence, the same for every
player, so it can be voiced and tested as written.

### The text

The contact is Trauma Team International, with the game's unknown-caller
picture. It sends one text, the job ad, with the gig card attached. It
arrives wherever V is, once the prologue is over and before the point of
no return. A picture of the AV on its roof is on the gig card.

### The recruiter

An invented character, recorded by an actor. She wears the green Trauma
Team suit with her head bare, always the same look. She stands where Career
Opportunities stages its two Trauma Team people for the hand scan. Her lines
are intake paperwork read aloud: short, procedural, never selling the job.

The interview is seven lines of hers and three of V's, with two prompts.

V speaks only lines the game already recorded (`docs/conventions.md`).

### The first flight

Fixed: the roof to a hotel roof, 1.9 km, about a minute in the air.
The briefing plays during the climb. The client is a Platinum whose
biomonitor went flat on the roof. Five Scavs are pulling his cyberware.

The crew are introduced here. The lead speaks the briefing. The soldier
calls the landing, and the medic speaks over the client, both in the game's
own recordings of The Rescue's Trauma Team crew.

### The uniform and the first pay

V puts on the Trauma Team uniform (`Items.Trauma_Team_Outfit`) at the locker
room's shelves, which adds it to the backpack first unless Career
Opportunities already gave it. After the shift, changing back at the same
shelves is an optional objective. Taken, V's own outfit and weapon go back and
the uniform stays in the backpack. Left, V goes home in the uniform.

The SMG (`Items.Preset_Dian_Trauma`) comes with the uniform, with the game's own
item node and its item card. Back on the street, after the elevator down: the
three calls' fees through the game's own reward node.

## The AV ride

Every piece of it is a shape the game already uses for an AV. The research
behind each is in the repo's research notes; the short form:

- **The AV** is The Rescue's Trauma Team Atlus (`av_trauma.ent`). It is the
  only Atlus with places to stand in the cabin: `player_standing`, V holding
  on at the open door, and `tt_1` and `tt_2`, two crew standing with
  rifles. It stands on its pad as an entry of the gig's community, the way
  The Rescue and The Hunt place theirs.
- **The pad** is the Medical Center's top roof, the highest point there, so
  the flight home comes in over the building and not through it. The way
  up and down is the game's own glass lift in the tank yard (`gen_lift.py`),
  the street to the roof, about 37 s, with no fade. It runs in a steel frame of
  four columns and ring beams. A closed walkway, 50 m, joins the car to the roof's
  east edge. Its door to the shaft is locked unless the car is there. V works the
  lift with its keypad. A call panel beside the door at each stop brings the car,
  and the game offers Call Elevator at the roof door as well. The quest follows
  V's height.
- **The armory** stands between the walkway and the pad, 12 m square, in gig
  04's kit in two skins (one facing in, one facing out). Its furniture is the
  game's own: a wall of lockers, three racks, lab counters, a clothes rail, a
  laundry trolley. Sliding doors join it to the walkway, a double door to the roof.
- **Boarding** is a prompt scene at the AV's open side. Taking it seats V on
  `player_standing` with the game's own seat node. Away from the pad the AV
  is switched off and on again at the call's spot first: a seat node on an
  AV that has flown away from where it was placed puts V on the pad first,
  behind two loading screens. The AV's own Enter prompt is switched off.
- **The crew aboard** stand in the cabin in a scene pose anchored on the
  AV's place `tt_2`: the soldier on it at the door, the lead a metre
  forward and the medic a metre in, moved with the pose's own offset.
  `weyland` and `rogue` are within 30 cm of `tt_2`. The seat node does not take
  NPCs onto those places. V is not in that scene: a pose for V on the AV's
  slot crashes the game.
- **Flying** is the game's own node for every AV flight in its quests: the
  AV follows a flight path laid in the world, start to end. The gig ships
  its paths. The first follows the hotel roof's own arrival in at the end,
  cruising at 420 m. The other three follow lines flown by hand through
  the city, at one cruise height a little above the highest point flown.
  Every takeoff and landing is a straight line along the AV's nose, the
  shape of the first flight: 3 m up in the first 4 m, then a steady climb;
  nearly flat for the last 10 m of a landing. No path goes straight up or
  down, and no turn is tighter than 90 m (60 m leaving Kabuki).
- **Which way each AV comes in and goes out** is measured. At each spot a
  probe casts rays every 10 degrees round at climbs of 8 to 50 degrees,
  the AV's width apart. The hotel roof and the pad are open almost all
  round. The coast street is open only along the street to the east-south-
  east, so the AV comes in along it at 25 degrees and leaves along it. The
  Kabuki street is open from the north-north-west round to the south-
  south-west: the AV comes in from the south-south-west and leaves to the
  north-north-west. Where the way in and the way out differ, the AV is
  turned in the fade as V boards.
- **Speeds** are the game's climb off the ground, 33 m/s at cruise,
  12 m/s from 160 m out, 2.5 m/s for the last 15 m.
- **The briefing** is a scene staged at V and played beside the flight, the
  way Last Caress plays its conversation while its AV flies.
- **Getting out** is a short fade, 2.5 s after touchdown. Under it V is
  let go and stood at the door facing the Scavs, the team's SMG is drawn,
  the AV is put back on its spot with its doors open, the riding crew are
  switched off and a second set of the same three men is switched on at
  their posts: the men who had ridden never fired a shot. V can fire as
  the screen comes back. At the pad after the last call the same fade puts
  the crew on the pad beside the AV, where they stay.
- **The SMG** goes into a free weapon slot when the uniform goes on, or
  into the first slot with V's own weapon put back after the shift. Each
  step-off draws it.
- **On the pad**: Brekke speaks as V comes within 7 m of him, before the
  boarding prompt, and again when V steps off after the last call. The
  three stand on the pad in standing poses, on a floor the gig adds at the
  height the roof is drawn. V steps off the last flight past Brekke, on the
  side he looks at. In the cabin the medic and the soldier sit on the far
  wall's seats and Brekke stands in the middle with his arms folded, a step
  farther from V than the first version. Ten standing poses were compared side
  by side on the roof, and this one looks most like a man riding in his own AV.
  A grab bar along the top of the door gives V's raised hand something to hold.
- **Markers on the roof** have no route. The game's route finder has no path
  through the walkway, so these pins are plain markers. The pin to the lift on
  the street keeps its route.
- **The uniform** is the game's own, given once. After the shift it is under
  Inventory, the Outfit slot, in Special Outfits.
- **Skipping a flight**: once the briefing has been said, "Skip the
  flight." is offered until the AV nears its last stretch. Taken, the screen
  goes black, the world runs at 8x until V is 420 m from the landing, or on the
  flight home, whose path loops round the pad, 90 m from a point 300 m before
  the end of the path, and the screen comes back for the landing. If the AV
  never reaches that point, the screen comes back after 30 seconds anyway.
- **During the flight** V cannot get out or draw a weapon. That is Last
  Caress's own restriction for its flight, as the gig's unsavable copy.

Each flight has a path of its own: pad to site, site to site, site to pad.

## The fight

The game has a Trauma Team crew fighting a gang already: a world story in
Heywood, with the Tyger Claws. The gig copies its shape.

- The crew, the Scavs and the client each have an attitude group. Scavs are
  hostile to the crew, the client and V. The crew are friendly to V and the
  client.
- Each Scav is pointed at a first target with the game's own node: the
  lead, the client or V. That is how the Heywood fight makes a gang shoot
  at the crew and not only at V.
- The crew keep the orders the lead gives in the briefing. The lead fights
  and roams. The soldier stands guard at the AV in the game's rifle guard
  pose and does not move. The medic kneels at the client. The soldier and
  the medic are in a group of their own the gang has no quarrel with, with
  no reactions, so the fight never pulls them out of their poses. A
  fighting soldier told to hold his ground with the game's hold order
  walked 15 m in 45 seconds.
- A script wakes each Scav and the lead against each other, the way the
  gigs before this one wake their guards.
- The police are switched off for the shift, with the request quests use
  to keep the NCPD out of a scripted fight. The game's own Trauma Team is
  friendly to V for the shift. Without both, the street call drew police
  heat and the clinic's Trauma Team guards next to it turned on V.
- The crew cannot die. A crew bullet cannot hurt V. Crew kills give V no
  XP.
- The client cannot die: hits stop at 1 percent of his health.
- The client is not carried aboard on screen. He is switched off behind
  the boarding fade. The Rescue carries its client on a stretcher with
  synced animations tied to its own scene marker.

The roof is clear when no Scav is left standing.

## Shifts after the first

Not built yet. The plan:

- **When.** The AV is on its pad at any hour. A shift starts when V
  boards and takes as long as it takes on the world clock.
- **Starting.** "Board the AV" at the pad. No phone dispatch.
- **Length.** Three incidents, then home (the design call). The first
  shift flies the three fixed calls.
- **What is drawn.** A script draws a site, a cover tier, a threat and a
  twist per incident and writes each as a fact. The site is never the same
  twice in a shift.
- **Twists.** A second wave of the same gang. A flatline clock: stable in
  90 seconds or the client is lost. Without a clock, a client cannot die.
- **Pay.** Per incident, through the game's own reward records: Silver
  1,500, Gold 2,500, Platinum 4,000, a lost client 500 at any tier. An
  incident is about one NCPD hustle's fight, and a Platinum call pays the
  median hustle (3,900 across the game). A job V can repeat daily stays
  under the one-off gigs (median about 8,000).
- **Rank.** Probationer, then Operator after 5 shifts (Platinum clients,
  pay up 15 percent), then Senior Operator after 15 (pay up 30 percent). A short
  voiced beat at each.
- **Restrictions.** No fast travel, no car called in, no time skip during a
  shift, each the mod's own unsavable copy. Fast travel comes back when the
  shift ends.

## The crew

Three Trauma Team operators, the same three every shift. Trauma Team has one
body in the game, a male one, so the crew are men.

- **Brekke, the lead.** Invented, recorded by an actor. Radio habits:
  names, numbers, no adjectives.
- **Wrona, the soldier.** The Rescue's Trauma Team soldier's voice: "Landing,
  stand clear! Initiating security protocol. Follow all instructions."
- **Raman, the medic.** The Rescue's Trauma Team medic's voice:
  "Stimulants being administered..."

The pilot is never seen and never speaks.

## Saves and loads

The game's own rule: it locks saving in combat, in scenes, and while V is
on a moving platform, and its Autodrive adds a save lock while the car
drives itself. The gig does the same. Saving is locked while V is aboard
the AV and allowed on the ground between flights. A save made on the
ground loads where it was made, with the flight restriction off.

## First playtest

Load a save from after the prologue, with V away from Watson. Open the dev
menu, "Trauma Team [DEV]".

1. Travel to Little China. A text from Trauma Team International arrives.
   Good: the text, the gig in the journal, a marker on the recruiter. Bad:
   no text after a minute in Watson; set `cc_g05_ad_go` to 1 in the dev
   menu and note it.
2. Walk to the recruiter. Good: a woman in the green suit, no helmet, a
   prompt over her.
   Talk. Good: her lines as subtitles, V's lines spoken, the Body option
   drawn with its check.
3. Follow the marker to the glass lift in the tank yard. Walk in and
   press the top button on the keypad. Good: the car rises, the door opens
   on the corridor, the objective becomes "Get changed in the armory".
   Press "Get changed." at the shelves: the item card, the uniform on, the
   SMG in hand, and "Talk to the crew leader". Follow the marker through the
   room's door to the AV. Good: a Trauma Team AV on the roof,
   engines quiet, two crew visible standing in the cabin. Bad: no AV, an AV
   in the air, an AV sunk in the ground, an AV on fire.
4. In the dev menu's AV lab, look at the AV and press READ. Note what it
   says about each slot. Screenshot it.
5. Walk to the AV's open side. Good: "Board the AV". Take it. Good: V
   standing at the door, holding on, facing out. Bad: V in a seat, V beside
   the AV, V inside the floor.
6. The AV lifts off. Good: V rides it, the crew ride it, the lead's lines
   play, the city goes past under V. Bad: the AV leaves without V, or does
   not move. Note whether it hits anything on the way.
7. At the roof. Good: the AV sets down level, the soldier's line plays, V
   is standing beside the door, the crew get out and spread out, the client
   lies on the roof.
8. The fight. Good: the Scavs shoot at the crew and the client as well as
   V, the crew shoot back and stay near the AV, nobody on the crew dies,
   their bullets do not hurt V. Bad: the crew stand idle, or chase the Scavs
   off the roof, or shoot V.
9. Clear the roof. Good: the lead's line, the medic's line, "Board the AV"
   at the AV. Bad: nothing after the last Scav falls; set
   `cc_g05_site_clear` to 1 and note it.
10. Board and fly back. Good: the same ride home, the lead's two lines, V
    standing beside the AV on the roof afterwards, "Take the elevator
    down" and the optional "Change back into your own clothes". Change back
    at the shelves, or leave it. The keypad in the lift, the car going down,
    V on the street, the money notice.
    Good: V's own outfit and weapon back if V changed, the uniform still on
    if not, the optional objective gone either way.
11. Save on the roof during the fight, load that save, and note where V is
    and what the journal says.

Screenshots at steps 3, 4, 5, 7 and 8 are the most useful.

## What is still open

- A female Trauma Team look, if the crew should not be all men.
