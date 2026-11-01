# Hodan Warsame

A fixer for Cyberpunk 2077, and a mod of her own. She sits on a couch in the
lobby of a tower on Palm Street, Charter Hill. She finds mercs for people who
have a problem with a corp. Each of her gigs is a separate mod that requires
this one.

## What she has

- A fixer icon on the map from her first call, with her gig count on it.
- Her portrait on the map tooltip and on her gigs in the journal.
- A contact V can call, and a conversation in person or on the phone.
- An entry in the codex, under Characters.

She calls V the first time V is in Charter Hill after the prologue.

## Who she is

Hodan Warsame is from Mogadishu. Orbital Air hired her out of law school to
write its labor contracts for the orbital stations. The contracts were written
so nobody could ever pay off the debt. She started helping the smugglers who
got people off the stations, and within a year she was running them. Orbital
Air ambushed a run, most of her crew died, and she escaped to Night City.

She takes no Orbital Air money, and she never hands a person over to a corp.
She speaks in whole sentences and uses the city's words (corp, suits, eddies,
job). She uses no street slang, never raises her voice and never swears.

## Writing a gig for her

1. Register the gig at launch, so her icon counts it. Copy this, with your
   own module and id:

   ```
   @if(ModuleExists("CyberpunkCodes.Fixer01"))
   import CyberpunkCodes.Fixer01.*

   @if(ModuleExists("CyberpunkCodes.Fixer01"))
   public class MyGigRegisters extends ScriptableTweak {
     protected cb func OnApply() -> Void {
       Fixer01Gigs.Register(n"my_gig");
     }
   }
   ```

2. Wait for the fact `cc_f01_intro_done` before the gig starts, so nobody gets
   a job from a fixer they have never met.
3. Add one to the fact `cc_f01_fixer_count` when the gig ends. Do it once.
4. Use her pieces instead of copies:
   - her contact: `contacts/cc_f01_fixer`
   - her body on the couch: entry `fixer` of the community
     `$/mod/cc_f01_cast/#cc_f01_cast_com`
   - her record for a video call: `Character.cc_f01_fixer`, appearance
     `fixer01`

## Where to look

- Her own project is `fixer01/`. The register is in
  `fixer01/source/resources/r6/scripts/Fixer01/Fixer01_Gigs.reds`.
- Return Ticket is a complete gig of hers, in `gig04_return_ticket/`. Its
  quest waits for `cc_f01_intro_done` and adds to `cc_f01_fixer_count`.
  `Gig04_Registers.reds` is its registration.
