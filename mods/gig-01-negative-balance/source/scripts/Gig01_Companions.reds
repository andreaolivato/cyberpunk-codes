// Gig 01 - Negative Balance: THE GIG EASES ITSELF FOR SOME OTHER MODS.
//
// Two places in this gig are guarded so that a player has to fight: the office
// at the industrial park, where the ledger is read, and the house at the North
// Oak estate, where Hoshino waits and the malware goes in. Thirty men stand at
// the first site and twenty-nine at the second, each at a post somebody walked
// to and captured in game, and that count was tuned by playtest on the game as
// shipped.
//
// Some mods make every fight in the game harder, and a player running one of
// them meets the same posts with better shots behind them. So the gig eases
// itself: when one of the mods below is installed, a few posts at each site
// stand down, the ones standing on the objective itself, so a quiet approach
// has somewhere to go. Which posts is decided in
// `tools/gig01/gen_estate_guards.py` and `gen_compound_guards.py`, under
// STAND_DOWN, with the distances that picked them and the player feedback
// they answer.
//
// ---------------------------------------------------------------------------
// HOW ANOTHER MOD IS DETECTED
//
// `@if(ModuleExists("..."))` is a redscript compile-time switch: of the two
// functions carrying the same name below, only the one whose condition holds
// is compiled, so `DarkFuture()` returns true on a machine where that module
// compiles alongside this one and false anywhere else. That is the shape the
// redscript documentation gives for it and the shape Much Better AI itself
// uses to detect Immersive Shooting AI. It needs redscript 0.5.18 or later for
// the class-member form used here; this project ships against 0.5.31.
//
// A module name is the string after `module` at the top of the other mod's
// own .reds files, and it was READ OUT OF EACH MOD'S RELEASE ARCHIVE, not
// guessed: a wrong name compiles clean and answers false for everyone, which
// is the gig as shipped, and nothing would ever say why.
//
//   Dark Future        r6\scripts\Dark Future\Main\DFMainSystem.reds
//                      `module DarkFuture.Main`      (2.0.3 for 2.31)
//   Dark Future Core   the same file in the lighter edition
//                      `module DarkFutureCore.Main`  (read off its repository)
//   Much Better AI     r6\scripts\MuchBetterAI\Core\Compatibility.reds
//                      `module MuchBetterAI.Core`, and every file of it imports
//                      `MuchBetterAIConfig`, so either name means the mod is
//                      there                          (2.15)
//
// ---------------------------------------------------------------------------
// TO ADD A MOD
//
//   1. Find its module name: open its archive, read the `module` line of one
//      of its .reds files. Prefer a file the rest of the mod imports from.
//   2. Add a pair of probes below, one `@if(ModuleExists(...))` returning true
//      and one `@if(!ModuleExists(...))` returning false, under one name.
//   3. Add the probe to `Installed()`, with its readout key.
//
// Nothing else changes: the quest phase reads one fact and the roster says
// which posts stand down. A mod that is installed but has its scripts disabled
// is not detected, because the switch is a compile-time one; that is the right
// answer, since a disabled mod is not making anything harder.
//
// ---------------------------------------------------------------------------
// THE FACT, AND WHEN IT IS WRITTEN
//
// `cc_g01_easy` is how many of the mods below are installed, written on the
// first check `Gig01_Start` makes after a load, about half a minute in. Every
// session, because facts persist in the save and the answer can change between
// sessions: a player who removes Dark Future should get the gig as shipped
// next time, and one who adds it should get the eased one. The quest phase
// reads the fact once, at the beat that switches each detail on, which is
// minutes after the gig starts and so always after the first check. A mod
// installed later than that beat changes nothing at that site, on purpose: the
// posts have already been placed and a detail that thins itself while V is in
// it would be men vanishing in front of him.
//
// `cc_g01_dev_easy`, 0 by default, is the tester's switch: above zero it
// counts as one installed mod, so the eased gig can be played on a machine
// with none of them. It is in the dev menu next to `cc_g01_dev_hold`.
//
// `cc_g01_dbg_easy_<mod>` says which probe answered yes, one fact per mod, so
// the panel can show which mod eased the gig rather than only that one did.
//
module CyberpunkCodes.Gig01

public abstract class CCGig01Companions {

    // ---------------------------------------------------------- the probes
    //
    // One pair per mod. Only one of each pair exists in the compiled bundle.

    @if(ModuleExists("DarkFuture.Main"))
    public static func DarkFuture() -> Bool { return true; }
    @if(!ModuleExists("DarkFuture.Main"))
    public static func DarkFuture() -> Bool { return false; }

    @if(ModuleExists("DarkFutureCore.Main"))
    public static func DarkFutureCore() -> Bool { return true; }
    @if(!ModuleExists("DarkFutureCore.Main"))
    public static func DarkFutureCore() -> Bool { return false; }

    @if(ModuleExists("MuchBetterAI.Core") || ModuleExists("MuchBetterAIConfig"))
    public static func MuchBetterAI() -> Bool { return true; }
    @if(!ModuleExists("MuchBetterAI.Core") && !ModuleExists("MuchBetterAIConfig"))
    public static func MuchBetterAI() -> Bool { return false; }

    // ------------------------------------------------------------ the count
    //
    // Writes one readout fact per probe and returns how many answered yes.
    // The readout is written whatever the answer, so a 0 in the panel means
    // "looked, not there" and not "never looked".
    private static func Note(qs: ref<QuestsSystem>, key: String, on: Bool) -> Int32 {
        let value: Int32 = on ? 1 : 0;
        if qs.GetFactStr("cc_g01_dbg_easy_" + key) != value {
            qs.SetFactStr("cc_g01_dbg_easy_" + key, value);
        }
        return value;
    }

    public static func Installed(qs: ref<QuestsSystem>) -> Int32 {
        let n: Int32 = 0;
        n += CCGig01Companions.Note(qs, "darkfuture", CCGig01Companions.DarkFuture());
        n += CCGig01Companions.Note(qs, "darkfuturecore", CCGig01Companions.DarkFutureCore());
        n += CCGig01Companions.Note(qs, "muchbetterai", CCGig01Companions.MuchBetterAI());
        return n;
    }

    // ------------------------------------------------------------- the fact
    //
    // Called once per session from `NegativeBalanceStart.Tick`, after the
    // quest system is known to be there. Idempotent: writing the value the fact
    // already holds is skipped, the same as every other fact this gig keeps.
    public static func Publish(qs: ref<QuestsSystem>) -> Void {
        let n: Int32 = CCGig01Companions.Installed(qs);
        if qs.GetFactStr("cc_g01_dev_easy") > 0 && n == 0 {
            n = 1;
        }
        if qs.GetFactStr("cc_g01_easy") != n {
            qs.SetFactStr("cc_g01_easy", n);
        }
    }
}
