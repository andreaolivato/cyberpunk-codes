# Acceptable Loss: the design

A side gig for Cyberpunk 2077. Dino Dinovic sends V to steal combat evaluation
data from a Militech site in the Badlands. The data says Militech buys mercs
through licensed fixer channels and shoots them as live-fire practice for its
trainees. V is found the moment the security room is opened, fights out of the
compound and out of the Badlands with Militech on the hunt, and then decides:
hand the data over, or wipe it and pay for that.

The comic (not part of this repo) is the source of truth for the plot and
the site. The comic's fixer is Regina Jones; the gig's is Dino, and the
section on the fixer below says why.

## The shape of it

A quiet job that stops being quiet, a chase home, and an argument on the way
that V has to settle with one reply.

Three things follow from that and they set every other decision:

**The plot is on a computer screen.** Three documents on one terminal carry the
whole reveal. Nobody explains it out loud, and nobody needs to, which is also
how the base game handles material this specific.

**Only V, Johnny and Dino speak.** All three are recorded by the base game, so
the gig needs no voice actors and invents no characters. Every soldier on the
site is a target, not a person with a name.

**The gig has no good ending, only a choice of which bad one.** Bring the data
and take half the money, with Dino furious; or wipe it, take nothing, pay the
client's advance back out of V's own pocket, and have Dino angrier still.
Johnny gets the last line either way and V never answers him. The choice is
made by text message, which is where V and Dino do their arguing.

## The fixer

Dino Dinovic, the City Center fixer, whose bar is in Downtown. His clientele
is corpos and politicians, his own briefs sell surveillance of a councilwoman
to the corp she regulates and order a merc killed to placate Zetatech ("I
need you to toss his head at their feet"), and his debriefs for a loud job
and a half-done job are the two rebukes this gig needed. A fixer who reads
a ledger of dead mercs and answers "who cares who" is Dino on any day of the
week.

Regina Jones is the comic's fixer and was the gig's until its first playtests
were done. Her base-game identity is the ex-media crusader whose cyberpsycho
programme exists to keep people alive, and every one of her lines pulled
against a plot that needs the fixer to shrug. Her recordings also had no
job line with a phone version, so her hire had to be spliced; Dino's hires
are recorded for the phone.

## The flow

### 1. The offer

Same three steps as *Dead Ringer*: a text message, then a short call, then a
second text with the details. The call is Dino saying he has scrolls to swipe,
the client is feeling generous, and the intel is attached. The specifics live
in the message, not in his mouth.

The call is not tied to a place. It arrives wherever the player happens to be.

The gig waits until Dino has been in touch on his own, which the base game
does the first time V spends time in City Center after the prologue. Until
then a message says so, once.

### 2. The site

The Militech detention centre in the Badlands, near the Tango Tors motel. The
perimeter was walked one corner at a time, and the terminal and the spot to
stand at it were captured in game.

The front gate is not the way in. The player goes over or through the perimeter,
past a turret and cameras, to an office with a computer in it.

On the way there is a hall with camping tents pitched on the floor. It is
scenery. The player walks past it and nothing in the gig refers to it.

### 3. The terminal, and then the shard

**The comic puts the whole reveal on one screen. The gig puts it in two
places**, and the second one is what gets V caught.

The terminal is a plain base-game computer in the north-west corner of the
compound. What it says is that the log Dino wants is not on the network at
all: it is on a shard, in the security room.

**It is deliberately not the computer in the office.** That one belongs to the
base game's own street story set at this site, with its own quest content
assigned to it. Nothing in this gig writes to it.

The shard stands on the cabinet in the security room, behind a door. **Opening
that door is what gets V found**: the trace starts on the door, not on the
shard. The player then takes the shard with [F] or reads it in place with [R],
and either one opens the objective to get out.

It carries the comic's own numbers, written as the site would write them:
contractor attrition 68% against personnel attrition 2%, a kill confirmation
rate, a recommendation to make the contractors more aggressive for realism, and
an acceptable loss threshold of fifteen contractor units per cycle. Nobody
writing it thinks they are describing anything but a training exercise, which is
the point of it.

Reading it is a separate objective from taking it, because a player can walk
away holding something unread, and it can be read during the escape or after.

### 4. The door, and the trace

The moment the security-room door opens, a netrunner on site traces V and
**always succeeds**, whatever the player's level, gear or build. It is a story
beat, not a skill check, and there is no stealth exit from it. A progress bar
reads TRACING YOUR LOCATION for six seconds; a red banner says the location is
compromised when it fills.

Until the bar fills, nothing else happens: the door only starts the trace.
When it fills, three things happen together:

- **Every Militech soldier in the compound turns on V**, at once, knowing
  where V is. Inside the wire they always know; once V is over the fence they
  have to look, so reaching the fence changes what they know.
- **Three more arrive at the gate**, in a line, facing into the compound,
  the way V came in. They are the same soldiers the site already has, and
  the gate is far enough from the security room that nobody appears in
  view.
- **Three stars land.** Out here that brings Militech, who are who V has just
  stolen from, so the response walks in by itself.

The door only counts when V opens it. A guard running through it on his way
somewhere does not start the trace.

The five civilians in the tents are left alone.

### 5. Out of the Badlands

Clear of the compound is not clear of Militech. The objective is to **leave the
Badlands**, and until V has, the three stars come back every time the game lets
them fade, the response is told where V is every few seconds, and three
Militech cars are kept on V and driven at V across the sand rather than
along the roads, so leaving the tarmac is no escape. The line is the game's
own district boundary, so any road out counts; the instant V crosses it the
stars go out and the response stands down.

### 6. The argument, and the decision

Once V is out of the Badlands, and out of the car if V was driving (the
objective says "Get out of the vehicle" until V is), the objective says to
message Dino, and V's two texts are replies the player taps in turn: the data
was rigged, half of Militech came after V, V got out with it. Then the part
that matters: Militech is using mercs as live targets for its training
exercises and zeroing a lot of them. Who is the client? Dino's answer is a
fixer's: who cares who, they want the data to replicate the results, swing by
the club and bring it in person.

This is a thread rather than a conversation because it has to be: nothing V
or Johnny recorded says any of it, and a text is where the base game lets V
say a thing in V's own words. Johnny keeps the moments his recordings can
carry: one line against each decision, and the last word at V's own door.

**Then V decides, on two replies.** "On my way", or "Not this one, Dino. I'm
wiping it."

### 7a. Bring it

Johnny gets two lines against it ("Don't do it, V", and the one about
ideals and eddies) and V shuts him down twice ("Not now, Johnny", then "I
said shut up! What's there to talk about? Job's a job, nothin' personal").
"Listen to Johnny" is the objective for as long as he speaks, here and again
at V's door on either ending.

The player goes to Dino's bar and stands at his stool, and he is furious in
his own words: he did not say "don't make a complete fuckin' mess" but did
not think he had to; he will count the job as done, but technically, just
barely; the eddies are on their way; and it had better be the last time,
because the city does not tolerate mediocrity. He pays half, and the
transfer lands as he finishes, before V walks out. The penalty is
what he says and nothing else: no later gig is locked, no fact gates anything
afterwards.

Outside V's own door, V is held still for a moment and Johnny appears in
front of V: "Hate to sound like your conscience, wouldn't ever want that
job... but dick move, V." V does not answer, he goes, V can move again, and
the gig ends there. The hold is so that a V walking away cannot walk past
him; it lasts for his line and never more than thirty seconds.

### 7b. Wipe it

Johnny gets the moment ("Finally, something we agree on"), the shard leaves
V's backpack with a banner saying so, and Johnny says the gig's own answer to
its own question: give up your ideals, and no amount of eddies buys them back.
V's reply is "There you go."

Dino's next message is three lines: what is wrong with V, the client fronted
5,000 for this and it is coming out of V's account, get over here.

At his bar he is angrier than in the other ending and pays nothing: V fucked
up, no cred for that move, and Dino needs a drink. As the scene ends the 5,000
leaves V's wallet, and the game's own money readout, the same popup the fee
arrives on, shows the change. That is what the loyal ending costs: no fee,
and the advance.

Outside V's own door, Johnny: "'S OK, V. You're allowed to be a little proud
of yourself." It is the only warm line in the gig, and it is the ending V paid
for.

## Dino's bar

He sits at the bar on his own stool, the spot the base game keeps him on, and
the gig's own copy of him sits on the same stool the same way while the leg
runs, so nothing changes about the bar but what he says. The scene plays the
barstool itself, the way his own base-game conversation does, which is what
lets it turn his head to V and move his mouth; left to the community's own
use of the stool, his face did neither. The game's own Dino is switched off
as V comes within 35 metres and back on once V is 35 metres away again, so
the swap is never in view. "Leave Dino's bar" draws that circle on the
minimap, the way *Dead Ringer* draws its way out, and the objective closes
at its edge. No street door is known at the bar; Regina's building had one,
and the code that unlocked it went with her.

## Languages

The gig follows the player's voice-over language. Every spoken line is one
of the game's own recordings, so Dino, V and Johnny speak whatever the
voice pack speaks, and the four cut lines are cut again in each dub with
the dub's own words as subtitles. The gig's own text is English until a
translation exists; a translation is a mod of its own, built from
`translation-kit/` (its README is the guide), and `docs/scene-playbook.md`,
"Other languages", is the mechanism.

## What the voice rules cost this gig

Dino and Johnny speak only in recordings the base game already made. That is
affordable here in a way it would not be for most stories, because Dino
closes every base-game gig with a call and half of those calls are him being
angry at V for making a mess. His rebuke register is small but exact.

What his recordings cannot say is anything naming Militech, the breach, the
trace, the number 12,500 or the number 5,000. Those are plot specifics, and
plot specifics go where the base game puts them: in the message thread, on the
terminal, and on the transfer readout the game draws itself. The argument
between V and Dino is a message thread for the same reason: V's side of it
does not exist in V's recordings either, and a reply in a thread is where the
base game lets V state a position.
