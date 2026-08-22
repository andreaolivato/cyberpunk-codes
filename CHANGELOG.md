# Changelog

Negative Balance releases, newest first. The same changelog is on the mod's
[Nexus page](https://www.nexusmods.com/cyberpunk2077/mods/32694).

---

## 1.2.4 (2026-08-22)

Safe to install mid-save. Nothing to restart. A save in which Hoshino has
already been spoken to is handled.

- **Fixed: the Arasaka security at the North Oak estate did not fight.** None of
  them treated V as an enemy, so V could walk in among them and stand in front
  of a guard without being challenged. The office detail was unaffected.
- **Fixed: the estate security appeared while the player was watching.** They
  now start arriving 120 m from the gate rather than 45 m, which covers the
  North Oak fast travel point, so the grounds are held by the time anyone looks.
- **Fixed: Hoshino left his desk and crossed the estate to join a firefight.**
  He was being treated as a combatant at war with the estate's own security. He
  now waits where the marker says he is, and his marker stays right.
- **Added: Hoshino cannot be killed before he has been spoken to.** No lock-on
  and no damage until his conversation has finished, so a shot from the garden
  can no longer skip the meeting he exists for.
- **Changed: Hoshino turns on V when their conversation ends**, rather than
  standing there until shot.
- **Fixed: Hoshino's name read "Hoshino Soldier" on the scanner.**
- **Fixed: the Arasaka compound repopulated with security after a reload.**
  Returning to the industrial park later in the gig spawned the whole office
  detail again, on a leg the player had finished hours before.

---

## 1.2.3 (2026-08-21)

Safe to install mid-save. Nothing to restart.

- **Fixed: Johnny no longer talks to you from somewhere you have already
  driven past.** He is staged beside V at the moment his scene starts, so
  answering a call at speed left him behind within a second. Calls now wait
  until V is on foot, and V cannot get into a vehicle between a call starting
  and the beat after it finishing. Affects the three beats that can happen
  anywhere: after Elena's call, on the crosswalk, and after Nix gives up the
  address.
- **Added: the game says why a vehicle cannot be entered.** "ACTION BLOCKED"
  while one of those beats is pending, and a prompt to get off your vehicle
  when a call to Nix is waiting on it.

---

## 1.2.2 (2026-08-19)

Safe to install mid-save. Nothing to restart.

- **Changed: callers now sound like they are on the phone.** Elena's and Nix's
  holocall lines get the same treatment the base game gives its own calls,
  instead of playing as the flat studio take used for a line spoken in the room.
  17 lines.

---

## 1.2.1 (2026-08-18)

Safe to install mid-save. Nothing to restart.

- **Fixed: the gig could dead-end at El Coyote Cojo.** The base game keeps that
  bar locked until *Heroes* is finished. Elena's call now waits for it and says
  so once on screen, instead of starting a gig that cannot be completed.
- **Removed: dead code and data.** The stand-in Mama Welles, the spawner behind
  her, the second epilogue built around her, and three record properties the
  game had been discarding since they were written. One scene, six subtitles and
  four voiceover entries gone.
- **Changed: the mod's world sector no longer covers the map.** Its streaming
  box was 10,000 m a side and its grid cell was another mod's, so the sector
  stayed resident for the whole session. Both are now derived from the shard's
  position.

---

## 1.2.0 (2026-08-17)

Safe to install mid-save. Nothing to restart.

The headline is a new proven way to spawn Johnny directly on scene without doubles.
One complete change on how we spawn him and it fixes the T-pose, 
the mid-air arrival and a clash with other mods all at once.

- **Fixed: Johnny no longer T-poses or arrives in mid-air.** When we didn't
  have a fixed anchor (e.g. while V was walking), he used to be
  assembled in two halves, one of them buried under the floor, and moving him
  between them is what flashed the T pose and bad placements. 
  Each appearance is now staged entirely by its own scene, so he arrives already 
  standing, already facing you, on the ground. *(Reported by Petrowsky88).*
- **Fixed: Johnny could be the wrong Johnny.** The old approach searched a 40 m
  radius for a Silverhand and used whatever it found, which on a large load
  order can be another mod's copy. Nothing searches any more.
- **Added: Johnny glitches out when he leaves**, instead of blinking out of
  existence.
- **Fixed: the Arasaka office guards could be missing, then appear on top of
  you.** Two separate bugs. The trigger was a circle drawn around the gate
  that did not quite reach the office, so a route that avoided the gate found an
  empty building; and every guard was requested in a single instant at the
  moment you arrived, so they streamed in behind you. Guards are now triggered
  from the whole compound, by any route, and arrive over a few seconds while you
  walk in. *(Reported by Petrowsky88).*
- **Fixed: the North Oak estate guards, the same way.** Approach the estate from
  any direction, including over the wall, and the grounds are populated. Guards
  whose part of the estate has not loaded yet are placed as you get there,
  rather than being quietly dropped.  *(Reported by ProTacos and dubzilla).*
- **Fixed: a second Hoshino appearing indoors, then vanishing.** His voice came
  from a hidden stand-in body, tucked below the terrace where you meet him. On
  the villa that spot is not under the ground, it is the room downstairs, so the
  stand-in could be seen standing in it and then disappeared the moment the
  conversation ended. He no longer has a body anywhere near the estate: he
  sounds exactly the same, and the only Hoshino in the house is the one you came
  for. *(Reported by ProTacos).*
- **Fixed: guards could ignore you.** The gig gave up
  waiting for an enemy to finish loading before telling it you are a target. It
  now waits six times as long in case anything is slow for other mods or hw.
- **Fixed: fast travel could be blocked for minutes at a time.** Ignoring the
  phone a few times could leave every fast travel point unavailable, because the
  block meant to cover the eight seconds of ringing was covering the whole gap
  until the next call. It now covers the ringing and nothing else.
- **Fixed: declining a call with a long press.** The call was declined and then
  immediately answered anyway. Decline now hangs up at once, and the caller
  tries again later, as a missed call always has.
- **Changed: the gig switches itself off when it is over.** Once the eddies are
  in, nothing of the gig runs again on that save: no timers, no checks on doors, no
  checks on computers. This was investigated after a report of the game turning
  choppy. To be straight about it, the idle cost that was measured is too small to obviously explain that, so this is more good practice rather than a proven fix for it.   *(Reported by  florinabelmont).*

Still open, and not forgotten: a report of save reloads crashing on a 400+ mod
install. No cause has been found, and the mod contains no native code that could
fault directly. The spawning work above reduces the heaviest thing it does, so
it may help. *(Reported by Petrowsky88).*

## 1.1.3 (2026-08-16)

Safe to install mid-save. Nothing to restart.

- **Fixed: the Arasaka office could be impossible to enter.** Until you have
  played Gimme Danger, the main-story mission that goes into the Arasaka
  Industrial Park with Takemura, the base game keeps the office doors switched
  off, with no prompt at all, so the gig sent you to a building you could not
  get into. The gig now switches those doors on once it is under way, and
  leaves them on. Only the five doors of that one building are touched; the
  vehicle gates are not. *(Reported by pharazon001 and HardyPilgrim, who
  pinned it to that mission).*

## 1.1.2 (2026-08-15)

Safe to install mid-save.

- **Fixed: the call to Nix can be skipped**, like every other call in the gig.
- **Smaller download.** An early version delivered the opening as text messages
  before it became phone calls, and the unused message system was still
  shipping. It is gone; the mod's journal data is about a quarter smaller.

## 1.1.1 (2026-08-15)

- **Fast travel is blocked while the phone is ringing**, the way the base game
  does it. A call can no longer be cut short by a loading screen you started
  after it began. *(Suggested by anygoodname).*

## 1.1.0 (2026-08-15)

Fixes for everything reported after launch. Safe to install mid-save.

- **Fixed: the way into the North Oak estate.** The way in is a climb up the
  rocks below the gate, and the gig used to drop a single marker at the bottom
  and leave you to it. Six markers now lead you up, one at a time. However you
  get over the wall, being inside the grounds now counts. *(Reported by
  anygoodname and PanPacifico).*
- **Fixed: Hoshino no longer talks after you have killed him.** Take him out
  before he speaks, from anywhere you like, and the gig skips straight to the
  next objective.
- **Fixed: Mama Welles talks about the job on the first approach.** Her usual
  bar chat could get in first. *(Reported by PanPacifico).*
- **Fixed: "ghost" phone calls after loading a save.** Calls you had already
  taken could ring again and hang up before you could answer. *(Reported by
  anygoodname, who also pointed at the fix, and by PanPacifico and
  florinabelmont).*
- **Fixed: calls no longer ring over a fast-travel loading screen.** A call
  that was already ringing when you set off hangs up and tries again once you
  have landed. *(Reported by anygoodname).*
- **Changed: Nix takes about two in-game hours to dig through the ledger**
  before he calls back with a name. Go do something else, he will ring.
  *(Pacing noted by anygoodname).*

The North Oak markers draw no GPS route on purpose: there is no road to the way
in, so the game's navigation would route you around the wrong side of the hill.
Hoshino's marker is the same, for the same reason: he is indoors.

## 1.0.0 (2026-08-14)

First release: the full gig, adapted from the comic. Map pins, objectives and a
payout, fully voiced with lip sync, Johnny along for the ride and talking back.
Starts on its own once the prologue is behind you.
