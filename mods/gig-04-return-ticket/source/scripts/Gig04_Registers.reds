// Return Ticket: one of Hodan Warsame's gigs, counted on her map icon.
//
// The total on her icon ("0/1") is however many of her gigs are installed.
// Each gig registers itself at launch and her register writes the count onto
// her record (mods/fixer-01/source/scripts/Fixer01_Gigs.reds, which has the
// whole contract). TweakXL runs every class that extends `ScriptableTweak`
// after it has applied every mod's tweak files, so the load order of the two
// mods makes no difference.
//
// WITHOUT HER MOD THIS FILE COMPILES TO NOTHING. `@if(ModuleExists(...))` is
// a compile-time switch (gig 01's `Gig01_Companions.reds` has the pattern),
// and here it guards both the import and the class. She is a requirement of
// this gig, but a player who installs the gig without her must not lose every
// other script mod to a compile error: redscript builds one bundle
// (docs/conventions.md). Compiled both ways on 2026-09-30, with her module
// present and with a module name that does not exist. Without her the gig
// does nothing at all: its quest phase waits on a fact only her mod sets.
//
// `ScriptableTweak` needs no import: TweakXL declares it globally.
module CyberpunkCodes.Gig04
@if(ModuleExists("CyberpunkCodes.Fixer01"))
import CyberpunkCodes.Fixer01.*

@if(ModuleExists("CyberpunkCodes.Fixer01"))
public class Gig04Registers extends ScriptableTweak {
  protected cb func OnApply() -> Void {
    Fixer01Gigs.Register(n"cc_g04");
  }
}
