// Fixer 01: the register of her gigs, which is how the "3" in "1/3" is
// counted from the gig mods that are installed.
//
// THE TWO NUMBERS ON HER ICON ARE TWO KINDS OF THING. The count of finished
// gigs is a game fact, `cc_f01_fixer_count`, and facts are one shared table
// in the save: every gig of hers adds 1 to it as it closes, the way the
// game's own gigs add 1 to their district's counter, and nothing here is
// involved. The TOTAL is `amountOfQuests` on her character record, read by
// the map tooltip at hover time (`MappinUIUtils.GetFixerVariantData`), and
// a record is built at launch from the tweak files. On its own it cannot
// mean "the gigs that are installed". This file makes it mean that.
//
// HOW. TweakXL applies every mod's tweak files, then instantiates every
// class that extends `ScriptableTweak` and calls its `OnApply`. Her own
// tweak file sets the total to 0. Each gig of hers ships one such class
// whose `OnApply` calls `Fixer01Gigs.Register` with the gig's id, and
// Register adds the id to a list on her record and writes the list's
// length back as the total. So an installed gig counts, an uninstalled
// one does not, a gig installed twice under one id counts once, and the
// order the mods load in makes no difference, because every gig's call
// lands after every tweak file. Gig 04 registers from its own mod this way.
//
// WHAT A GIG NEEDS TO DO, the whole contract with her:
//
//   1. Ship this, with its own id (cc_<gig prefix>, docs/conventions.md):
//
//        module CyberpunkCodes.<YourGig>
//        import CyberpunkCodes.Fixer01.*
//        // ScriptableTweak needs no import: TweakXL declares it globally.
//        public class <YourGig>Registers extends ScriptableTweak {
//          protected cb func OnApply() -> Void { Fixer01Gigs.Register(n"cc_gNN"); }
//        }
//
//   2. Add 1 to the fact `cc_f01_fixer_count` in its quest phase as the gig
//      closes (`add_addvar`), once.
//   3. Its contact-side texts and calls go under her contact,
//      `contacts/cc_f01_fixer`; her body for an in-person scene is the
//      community entry `fixer` of `$/mod/cc_f01_cast/#cc_f01_cast_com`; her
//      record for a studio call is `Character.cc_f01_fixer`, appearance
//      `fixer01`.
//
// GUARD BOTH WITH `@if(ModuleExists("CyberpunkCodes.Fixer01"))`, the import
// and the class, as gig 04 does. She is a requirement of every gig of hers,
// but a gig installed without her must compile to nothing rather than fail:
// one failed file takes down every script mod the player has.
//
// RELOADS. TweakXL's reload puts the tweak files back (the total to 0) and
// runs every `OnApply` again. The list on the record may survive that
// reload, so an id already on the list still writes the list's length back
// as the total; only the push is skipped.
//
// `TweakDBInterface.GetCNameArray` and `GetInt` are the game's own flat
// readers; `TweakDBManager.SetFlat` is TweakXL's writer, which creates a
// flat that does not exist yet. Whether the list flat is created on the
// first call or only found from the second is unmeasured, so the total is
// never read back off the list alone: it is the list's length when the
// write succeeded and the old total plus one when it did not.

// `ScriptableTweak` and `TweakDBManager` are declared in the global scope
// by TweakXL's own script file, so nothing is imported.
module CyberpunkCodes.Fixer01

public abstract class Fixer01Gigs {
  public final static func ListFlat() -> TweakDBID { return t"Character.cc_f01_fixer.gigs"; }
  public final static func TotalFlat() -> TweakDBID { return t"Character.cc_f01_fixer.amountOfQuests"; }

  // Count a gig in. Safe to call more than once with the same id.
  public final static func Register(gig: CName) -> Void {
    let list: array<CName> = TweakDBInterface.GetCNameArray(Fixer01Gigs.ListFlat());
    let known: Bool = ArrayContains(list, gig);
    if !known {
      ArrayPush(list, gig);
    }
    let stored: Bool = TweakDBManager.SetFlat(Fixer01Gigs.ListFlat(), ToVariant(list));
    let total: Int32;
    if stored {
      total = ArraySize(list);
    } else {
      total = TweakDBInterface.GetInt(Fixer01Gigs.TotalFlat(), 0);
      if !known {
        total += 1;
      }
    }
    TweakDBManager.SetFlat(Fixer01Gigs.TotalFlat(), ToVariant(total));
    // FTLog writes to red4ext\logs, the same log the deploy script says to read.
    FTLog(s"[CC.Fixer01] gig registered: \(NameToString(gig)), total \(total), list stored \(stored)");
  }

  // The total as the tooltip will read it.
  public final static func Total() -> Int32 {
    return TweakDBInterface.GetInt(Fixer01Gigs.TotalFlat(), 0);
  }
}

// THE STUB JOB NO LONGER REGISTERS ITSELF (2026-09-30). It did, exactly as a
// gig mod would, until her first gig existed; gig 04's
// `Gig04_Registers.reds` is that block now, so her total counts real gigs
// only. The stub job itself went on 2026-10-15, once gig 04 had been
// played.

// NO GIG INSTALLED, NO BAR. The tooltip divides the count by the total for
// its bar and prints both, so with nothing registered it would read "0/0"
// over a bar of nothing. When the icon is hers and the total is zero, the
// whole fixer panel is hidden and the name and the portrait stand alone.
// Fixer01_Portrait.reds wraps the same method for the atlas; both wraps run.
@wrapMethod(WorldMapTooltipController)
public func SetData(const data: script_ref<WorldMapTooltipData>, menu: ref<WorldMapMenuGameController>) -> Void {
  wrappedMethod(data, menu);
  if Equals(inkImageRef.GetTexturePart(this.m_icon), Fixer01Portrait.Part()) && Fixer01Gigs.Total() <= 0 {
    this.m_gigProgress = 0.0;
    inkWidgetRef.SetVisible(this.m_fixerPanel, false);
  }
}
