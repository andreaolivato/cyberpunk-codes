# Return Ticket: the design

A gig for Cyberpunk 2077, sold by Hodan Warsame, the fixer of
`mods/fixer-01`. It requires her mod.

## The story

Reynaldo Manalo signed a fifteen-year contract with Orbital Air to clean rooms
on the Crystal Palace. The flight up and the rent in the workers' hotel come
out of the salary, and after seven years he owed more than on the day he
signed. Liban Jama, a smuggler from Hodan's old crew in Mogadishu, got him
down to Night City in cargo.

Reynaldo hid at his sister Maricel's noodle stall in Kabuki Market. He
wanted a new name and went to Stamps, a man in the market who sells one
cheap. Stamps asked who he was running from and where he was staying,
sold the answer to Orbital Air, and sent the Tyger Claws to take him.
The Claws held him first in the back of their van, then moved him to a
shuttered shop in Little China, because Orbital Air did not like the
van. Orbital Air's team comes for him within hours.

Maricel called Liban. Liban sent her to Hodan. Hodan calls V.

## What V does

1. Talks to Maricel at her stall. She says Reynaldo went to Stamps.
2. Finds Stamps's couch empty and his shard on its seat: his barkeep has
   his stool waiting, and he got paid today.
3. Finds Stamps at the bar. Scares him (Body), sells him on Hodan's
   custom (Intelligence), pays him 1,000, or beats him down. Stamps says
   the Claws are keeping Reynaldo in their van. V can kill him afterwards or
   leave him.
4. Finds the Claws' van in a yard in south-west Little China and
   scans three clues round it. A shard behind it says they moved him to
   the shop in Little China.
5. Gets past three Tyger Claws and finds Reynaldo.
6. Fights off Orbital Air's team, one car and three guards, inside the
   building. Reynaldo says goodbye and runs to his sister.
7. Takes Hodan's call. Reynaldo has left Night City by road. She pays.

## What is the game's and what is the gig's

The game's own texts: the Crystal Palace is "sponsored by Orbital Air, among
other entities", and Orbital Air flies the shuttle to it. The station's job
advert offers "15, 20, and 25-year contracts" with "flight costs and rent in
the worker's hotel" deducted from the salary. Goods and people are smuggled
to and from orbit past "OA customs". A new identity costs "300K eddies" from
a ripper clinic. The Tyger Claws hold Kabuki.

The gig's own: Reynaldo, Maricel, Stamps and Liban; Orbital Air hiring station
cleaners itself; Orbital Air paying to get a worker back; Stamps selling his
customers.

The gig runs on game 2.31 and 2.5, with or without Phantom Liberty. Its
room's navigation sector is built from the expansion's 2.5 copy of that
area and written in the 2.31 file format, so one file loads on both
versions (gotcha 144). Inside the building the floor is the same in every
copy. With the expansion, Orbital Air's own guards come for Reynaldo.
Without it, the game's corporate security does.

## What is built

The code calls Maricel `ligaya` and Reynaldo `bayani`, their working names:
her record, his facts, their files and the comments that describe them.

Maricel keeps the noodle stall from the start, in place of the game's own
vendor, and stays there after the gig. The gig waits until V has taken
Hodan's introduction call. Then the gig's icon is on the map at her stall.
The call is armed once V has been 250 m from both the stall and Stamps's
bar. Maricel is switched on as the introduction ends, and Stamps as the
call is armed. A person switched on beside the player appears only after
the player has been away (gotcha 132). The icon is the
game's "SOS: Merc Needed" icon, not yet discovered.

When V comes within 50 m of the stall, out of combat and not in another
conversation, Hodan rings, on video, with the job. She rings once, for
up to 30 seconds, as the game's own fixers do. Rejected or not answered,
the job arrives as her text. With fixer calls muted on V's phone there
is no ring at all. Her closing call works the same way, with her closing
lines sent as a text. The game's own gigs are offered the same way: tied
to a place, with the fixer's call when V gets near it. After the call
the gig is in the journal with her face on the card and her briefing.
Her text arrives with the same briefing in full, in the game's "Gig type
/ Objective / Location / Details" layout, and the gig card carries a
picture of Maricel at her stall. One objective is tracked.

Maricel stands behind the counter of her noodle stall in Kabuki Market.
Walking up to her offers one prompt; her six lines and V's two follow,
and the conversation ends on her last line or when V walks off. Only
three people knew where Reynaldo was: her, Liban, and Stamps, who sells
new identities and sits on a couch in the alley behind the market. She
does not accuse him; she tells V to ask him who else he told.

Stamps's couch is empty. His shard lies on its seat: Kaz, his
barkeep, about his tab, and Stamps answering that he got paid today and
is on his way. Taking it and reading it are two objectives. The game's
own five crowd seats in the booth are deleted, so no stranger sits
there.

Stamps drinks at a two-stool bar on the raised walkway west of the
market, with a barkeep behind the counter. The game's own crowd seat on
his stool is deleted, and a passer-by the crowd seats on it anyway is
removed, so the face on that stool is always his. His prompt opens
three lines. Reynaldo wanted a new name, he told Stamps he was running
from Orbital Air, and Orbital Air paid Stamps better for the tip. They
have paid already, so he loses nothing by selling the address again, but
not for free. Then a choice of three, all the game's own checks: Body,
Intelligence, or 1,000 eddies. Body and Intelligence ask
for the number the game's own Kabuki gigs ask for and are red and cannot
be picked below it. The payment is red below 1,000 and the game takes the
money when V picks it. A fourth button needs nothing and always works:
V starts a fight. Stamps cannot die in it, and at a third of his health
he goes down on the floor and talks from there. Any of the four gets the
same answer: the Claws are keeping Reynaldo in their van, in a yard in
Little China, and Orbital Air's coming for him, so V has a few hours. He
does not know they have moved him. V can walk off from either set of
buttons. Coming back after his three lines goes straight to the buttons.

Stamps cannot die until he has talked. Hurting him or knocking him out
before that, during the conversation or before it, starts the same fight
as the fourth button. Stars that V gets for hitting him are cleared, but
only if V was not already wanted when the fight began. Hitting Maricel or
Reynaldo does not bring the police. Once he has talked V can kill him, and
Hodan's last call says so. Only V's own hits count, and only once V is
looking for him. In the fight he fights back with his fists, a Kabuki
Tyger Claw's behaviour on his own body and face, and the map marks the
bar.

The van is a Tyger Claws Columbus, locked, parked in a yard in
south-west Little China, 810 m from the bar and 450 m from the building.
No one is there. Within 20 m of it Johnny appears beside V with his own
"Look around and connect the dots.". "Find the Tyger Claws' van" gives
way to "Scan the area for clues", with a "[0/3]" counter: the game's own
clue hunt. The minimap draws the search area round the three clues. The
three clues are behind the van: blood by the back doors, a pair of
unlocked handcuffs, and Reynaldo's duffel bag. The scanner names
each and says what it means. Each one scanned adds one to the counter.
Then the shard on the pallets behind the van: they kept him in the van and
moved him to the shop in Little China. Taking it and reading it are two
objectives, and the map marks the van for all three. A V who takes the
shard before scanning all three clues skips the rest of the hunt.

The building is the gig's own. A shuttered shop in Little China has a
decorative double door drawn on it. The gig removes that door and puts a
real one in the same frame. Behind it the gig builds three rooms from the
game's own interior kit: floor, walls, ceiling, lights and the collision
that makes them solid. A lobby behind the street door, 12 m by 5 m; an
L-shaped hall round it, 19.6 m across and 18 m deep, with the
scavengers' couches along its left wall and their shelves, cases, rags
and blood. At the back right is a 5 m by 5 m cell with its own sliding
door, where Reynaldo sits on the floor against the
wall beside a braindance rig and a medical cart. The hall's left wall
stands 0.3 m inside a wall of the shell's own, so nothing of the shell
shows through.

The game bakes no navigation mesh inside a building nobody was meant to
enter, so the gig adds the room's floor to the game's own navigation
tiles (gotcha 129). The game's own floor at the doorway runs through the
room's walls, and the gig switches those polygons off. The room's floor
starts at the inner face of the wall. One threshold polygon across the
door line joins it to the street's floor, and it is the only way in
(gotcha 130).

Three Tyger Claws hold the place: one stands guard outside the door,
facing the street, one just inside it in the lobby, and one deep in the
hall. They are hostile to V and to nobody else, and start looking once V
is near the door. The game places them in two groups: Reynaldo and the
Claw in the hall first, the two by the door once V is within 120 m of
Reynaldo. Four people placed at once froze the game for a second or two
on the way in (gotcha 143). The map marks the door; the objective changes to "Find
Reynaldo" as V reaches the street outside. Reynaldo sits on the cell's
floor and cannot be killed, and he reads as a friend on the scanner, so
V does not shoot him in the fight. His prompt opens his four lines and
V's three.

His prompt is offered only once all three Claws are down, or the ones
left have neither moved nor seen V for 45 seconds, and only with V in his
cell's doorway. Orbital Air pulls up while V talks to him: a black
corporate car on the street outside the door, and three guards on the
pavement by the front wall, out of V's sight. V ends the talk with the
game's own "Looks like we got company...". As V says it the guards turn
hostile and sprint in through the street door.

The objective is "Fight off Orbital Air's security", with no other way
through. Their car is locked. The guards are Orbital Air's own with
Phantom Liberty installed and the game's Corpo Plaza security without
it, chosen by the game's own check for the expansion. Reynaldo stays in
the cell, unhurt, until all three are down. The guards are switched on
as V steps into his cell, out of V's sight. Reynaldo gets up on "Yes. I
can walk." and steps to a standing spot inside the cell by its door,
where he waits out the fight. The guards stop chasing once V is outside,
where they can see V. A guard who stays in one spot unhurt for 15
seconds dies if he is out of V's view. After 45 seconds he dies in view
too, so a guard stuck in the geometry cannot hold the fight open. A
guard who can see V is never counted as stuck. The dead stay dead after
a reload, the room's Claws and Orbital Air's guards alike. The bodies
and the car stay until V is 150 m from the door.

Then "Talk to Reynaldo": the two doors open if they are shut, and he
walks out of the cell to a standing spot in the middle of the hall. His
goodbye is offered once he is on it, or a minute after the fight if he
never gets there. He thanks V, says he is going to Maricel, and V tells
him to get out. Both of his talks are offered within 2.6 m of him in the cell
and 3.5 m in the hall, so neither opens through a wall.

Then "Leave the area", drawn on the minimap. He sprints out of the hall,
through the lobby and 200 m down the street. Then he walks the rest of
the 860 m through Little China to his sister's stall in Kabuki Market
and stops in front of her. The route is the gig's own, and the order is
the game's own patrol order. The objective closes when V leaves the
circle and becomes "Wait for Hodan's call", and she rings two hours
later on the world clock. The objective's marker is a railing 48 m west
of the building, labelled "Waiting Spot": its prompt has the game's wait
icon and is not offered in combat. Leaning on it moves the clock on by
what is left of the two hours behind a short fade, with the game's own
glitch at both ends of it, as in the Claire races. Her call rings six
seconds after V lets go of the rail. Reynaldo and the Claws' van are
taken out of the world only once he is out of V's sight, whenever that
is. The fee's notice comes a second before the completion notice.

Her last call says his sister called, he is out of Night City, and her
friend drove him out. It has two versions: one has a line about Stamps
being dead.

After it the gig pays 9,000 eddies with the game's own reward notice, adds
one to the counter on her map icon and closes. The gig registers on her icon
at launch, so the icon reads "0/1" before the gig and "1/1" after.

Hodan, Maricel, Stamps and Reynaldo are performed by human voice actors.
V and Johnny speak only in the game's own recordings.
