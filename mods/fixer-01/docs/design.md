# Hodan Warsame: the design

A fixer for Cyberpunk 2077, and a mod of her own. She does business from a
couch in the lobby of a Charter Hill tower and sends mercs against the
corps. Some of her work is quiet and some of it is not, and each gig is a
separate mod that requires this one.

## What she is made of

Everything the game gives its own seven fixers and nobody else, built from
the same data the game uses for them:

- **The hands icon on the map**, from the first time she calls, for the rest
  of the save. A point of interest with the fixer variant, following her
  body when V is within 30 m and sitting on her couch otherwise.
- **The gig counter on that icon.** Hovering it shows her name, her portrait
  and her completed gigs over the total, "0/1" with gig 04 installed and
  not yet done. The count is a fact of hers that each of her gigs adds one
  to as it closes. The total is the number of her gigs that are installed,
  which each gig registers at launch (below). With none installed the
  tooltip shows her name and face and no bar.
- **Her portrait**, on the tooltip and on the card of every gig of hers in
  the journal. The game draws those from one fixed sheet of faces. A
  script points the picture square at her own sheet when the face it was
  given is hers, and back at the game's when it is not.
- **Her body**, sitting on her couch. A face made in the game's own
  character creator and turned into an NPC on the NPV recipe: her entity
  and appearance are the mod's, every mesh is the game's. Default head
  shape, and everything else the creator allows: skin, hair, eyes, brows,
  makeup, tattoos, scars, piercings, cyberware, nails. She wears a black
  spiked leather jacket, a torn tank, leather pants and biker boots.
- **Her contact**, with her face on it, callable, with her card as its
  first text.
- **Her conversation**, in person and on the phone, with the same questions
  the game's fixers take: who she is, what is going on in her district,
  whether she has work, how business is, why she meets people where she
  does, and a goodbye.
- **Her codex entry**, beside the game's own fixers under Characters.

## Who she is

Hodan Warsame, Somali. In the game's own world Somalia is a member of the
Pan-African Alliance, "the #1 tourism destination of 2075 according to
Night City Journal" (a billboard in the game). It has the largest
spaceport on Earth, which belongs to Orbital Air, the Kenyan corporation
that owns most of the planet's spaceports. She comes from a country on its
way up, not out of a war.

The game has already written the wrong she worked against. A shard, *The
Long Return: Aftermath of the Great Nomad Tragedy*, says Orbital Air's
lobbyists pushed border closures so migrants would be forced into "the
notoriously difficult labor conditions" of orbit and the Moon. She is
from a good family in Mogadishu, and Orbital Air hired her out of law
school to write those contracts. She read what she was writing: people
signed for years on an orbital station and never paid off the debt,
because the contracts were written so nobody could. She started helping
the smugglers who got people off the stations, and within a year she was
running them. Then Orbital Air found out and ambushed a run. Most of her
crew and passengers died, and she escaped to Night City, which she
cannot leave by air because Orbital Air runs the spaceport here too. So
she finds mercs for people instead, mostly people who have a problem
with a corp. She has done both halves of the work herself: the quiet
kind and the kind where somebody dies.

Most of her clients have a problem with a corp. The game allows a fixer
that side and has one already: El Capitan, in his own conversation, "Corpo
world's a disease. Power's gotta get back in the hands of the people." No
fixer in the game refuses corp money outright, and neither does she. El
Capitan sells V a job for "a client who needs help with some internal
corpo skullduggery"; Regina's client, once, is China. So one suit's money
against another suit is business to her, and she has two limits instead of
a ban: she takes no Orbital Air money, and she does not hand a person over to
a corp. Both are her own history: Orbital Air killed her crew, and she
spent years getting people out from under its contracts and is not going
to put anyone back under one.

She says all of this once, in a few plain sentences. In the game's own
words the people are corpos and suits and the companies are corps; nobody
in Night City says "anti-corporate", and neither does she.

She speaks in whole sentences, the way the game's fixers do. She uses the
city's words (corp, suits, eddies, job) and none of the street's slang,
because she came to the city as an adult from somewhere else. She names V
on the first call, as every game fixer does. She does not raise her voice
and does not swear.

She is invented, so a voice actor records her. Her lines play as recorded
apart from the phone effect on a call.

## The introduction

The first time V is inside Charter Hill after the prologue, which is the
game's own condition for its fixers ("after the prologue, in my district":
Wakako rings on entering Westbrook, Dino on entering City Center), the
phone rings. V also has to be within 900 m of her sofa: the district check
alone can be left on by a teleport or a load. It is a video call, with her
on the studio floor, arms crossed. She says three things:

1. Her name, and that she works in Charter Hill with the best.
2. Some of her work is quiet and some is not, and most of her clients
   have a problem with a corp.
3. Her number is on its way, and V should call if V wants work.

After her first line V asks "Know my name... how?", one of V's own
recordings, and her second line answers it.
That is the game's own shape: Dino, Regina, El Capitan, Mr. Hands and
Padre each give V one reply in the middle of the introduction and keep
the last word.

If V declines or lets it ring out, she rings again a minute later, and
keeps ringing until the call is taken. Nothing about missing it is lost.

As the call ends, V stops and Johnny appears beside V: "Hm. Maybe we CAN
just get along.", his own recording. V is held still for it and freed when
he goes.

After the call: her contact, her codex entry and her map icon appear, and
her card arrives as a text a few seconds later.

## Her conversation

Walk up to her on the couch and a prompt hangs over her, the way it does
over Dino at his bar or Wakako at her desk. Ring her from the contact list
and she answers on video, standing in the studio the way she introduced
herself, with the same prompt on the screen. Either way it is one hub of
six:

| On the button | V says | She answers with |
|---|---|---|
| What's your story? | "What's your story? Who are you?" | a good family and law school. Orbital Air hired her as a lawyer at the spaceport. She read the contracts and found they were written so nobody ever paid off the debt. She helped the smugglers who got people out, until she was running them. Orbital Air found out and ambushed a run; most of her crew and passengers died, and she escaped to Night City. Now she finds mercs, for suits fighting other suits and for people who have a problem with a corp, as she does |
| What's new around here? | "What's new in the neighborhood?" | the divorce upstairs: a politician, his ex-wife who got the penthouse and his depository receipts, and somebody in Japantown paid to get them back. Once V has finished that gig (*Until Death Do Us Part*, which marks itself done on its own fact), the same button gets a second answer. All quiet: somebody came back down with the receipts, she has not seen the wife since, and she kept a copy |
| Any work? | "I was wondering... wouldn't happen to have any gigs for me?" | she will be in touch. No catch: her two rules are Orbital Air money and handing a person to a corp. Anything else can be talked about |
| How's business? | "How's biz?" | can't complain: somebody is always paying to steal from a corp. Data, usually, sometimes a person. Getting a person out pays more, and taking a suit out pays the most |
| Nice place. | "Nice place, quaintly slick." | the suits upstairs walk past her every day; nobody has ever asked a single question |
| Later. | "Talk later." | "Take care, V." |

Each button is a short exchange, the shape of the game's own fixers.
Their seven default scenes have 39 buttons that are not a goodbye. On 28
of them V follows up with a second recorded line, and on 11 the fixer
keeps talking. The fixer's lines are two to four short ones, median 11
words. Hers are cut the same way:

- "There's a divorce going on upstairs." / V: "And?" / the rest in two
  lines.
- "Can't complain. Somebody's always paying to steal from a corp." / V:
  "Like what?" / "Data, usually. Sometimes a person."
- The Nice place answer runs on in two lines with no follow-up, as Dino's
  party answer does.

V's follow-ups are the game's short generic recordings, present in both
voices: "So?", "Why'd you leave?", "And?", "What's the catch?", "Like
what?".

Each exchange returns to the hub; the goodbye ends the talk, and on the
phone it hangs up. The district answer is the one that forks on the save.
The conversation checks the gig's own finished fact at the moment the
button is pressed. Wakako's debrief call for that gig forks the same way,
on whether V was seen (the scene playbook's fact branch). So a player who
comes to her after doing the job upstairs is not told it is still on. V's
questions are the game's own recordings, whole, the same lines V asks on
the streets of the Glen and of Charter Hill, and of Rogue, El Capitan and
Padre. Her answers are the actor's.

The divorce is the game's own: Emilio Gutierrez, a politician, lost the
penthouse and his depository receipts to his ex-wife Nina, and Wakako sells
V the job of stealing the receipts back. "Depository receipts" is that
gig's own phrase. Nina is dead in the game's world, under the Japantown
bridge, with a shard of her last messages to Emilio about the receipts;
that is why Hodan's second answer says only that she has not seen her
since.

In person the talk is offered whenever V is within 10 m of her after the
introduction, and it withdraws on its own when V is 16 m away, so nothing
is left open behind V. On the phone she is dialled like any fixer: the
contact list, her name, call.

## Her couch

The ground-floor lobby of an apartment tower on Palm Street in Charter
Hill, the district the game built for the corporations' middle managers.
A corporate couch faces a low table with a book and a whiskey glass on
it. A second couch is opposite, and the elevators are a few metres away.
She sits there, day and night, and looks at whoever comes in. A fixer
who works against the corps, in a tower full of their managers, and she
is the only one who knows it.

The tower is the one the gig *Until Death Do Us Part* plays out in. That
gig owns the floor above and never the lobby: it switches the lift's upper
floor on when it starts and off when it is done. The ground floor stays
open before, during and after. Its people are a drone and three guards
upstairs. She is unaffected by it, and a player who has never taken it walks
in off the street and finds her.

## What a gig of hers does

Every gig is a mod of its own that requires this one, and this is the whole
of what it has to do to be hers:

1. **Register at launch.** TweakXL runs every class that extends its
   `ScriptableTweak` after it has applied every mod's tweak files. The gig
   ships one, whose `OnApply` calls `Fixer01Gigs.Register(n"cc_gNN")` with
   the gig's own id. The register keeps a list of the ids on her record and
   writes the list's length onto it as her total. So the total on her icon
   is the gigs that are installed: no more, no fewer, whatever order they
   load in. `source/scripts/Fixer01_Gigs.reds` has the five lines to copy.
2. **Add one to `cc_f01_fixer_count` as the gig closes.** A quest fact,
   shared by every quest in the save, the way the game's own gigs add one to
   their district's counter. Once, at the ending.
3. **Use her pieces rather than shipping copies.** Her contact is
   `contacts/cc_f01_fixer`, and a gig's texts and calls hang under it. Her
   body for a conversation in person is the entry `fixer` of the community
   `$/mod/cc_f01_cast/#cc_f01_cast_com`, already on the couch. Her record
   for a call on the studio floor is `Character.cc_f01_fixer`, appearance
   `fixer01`, with the studio set her introduction uses.
4. **Start it from a place, after her introduction call.** The game's
   own gigs are offered when V comes near them, and each has its icon on
   the map before that. Gig 04 shows its icon once her introduction is
   done. It rings when V comes within 50 m of its client's stall, after V
   has been 250 m away from it since her introduction. Her gigs then ring
   on different days without a shared clock, and none waits on another.

   **The clock, if a gig ever needs one.** `cc_f01_intro_time` is the
   world clock, in seconds of game time, as her introduction call ended
   (`source/scripts/Fixer01_Stamp.reds` writes it once). No gig of hers
   reads it. A gig that waits a day would read the clock against that
   fact, so a player who meets her and installs the gig a week later is
   counted from her call. 0 is a call not yet taken, and a gig does not
   start on it. A save with her call taken and no stamp gets the stamp on
   its first load, and counts from there. A quest-graph delay counts from
   the first load with the gig installed instead, which is the wrong
   clock.
