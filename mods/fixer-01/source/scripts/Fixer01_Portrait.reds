// Fixer 01: her face in the three places the game draws a fixer's.
//
// WHERE THE GAME DRAWS A FIXER'S FACE. The map tooltip on the hands icon
// (`WorldMapTooltipController.SetData`, the FixerVariant branch, onto
// `m_icon`), the map tooltip on one of her gigs' pins (the same method, the
// gig branch, onto `m_fixerIcon`), and the gig card in the journal
// (`SimpleQuestListItemController.UpdateFixerData`, onto its `m_fixerIcon`).
// All three call `inkImageRef.SetTexturePart` with the part name off a
// `UIIcon` record and nothing else: the widget's ATLAS is fixed in the
// widget file, and it is the game's sheet of 26 faces
// (`base\gameplay\gui\common\icons\avatars\avatars_tooltips.inkatlas`). A
// part that is not on the sheet draws a blank square, which is what the first
// playtest of 2026-09-18 showed.
//
// WHAT THIS FILE DOES. After each of those methods has run, it reads the
// part the widget was just given. If it is hers, the widget's atlas becomes
// her own one-part atlas (tools/fixer01/gen_photo.py); if it is anyone
// else's, the atlas is put back to the game's sheet, because the same widget
// is reused for the next tooltip and the next card. Two swaps, no state.
//
// WHY A SCRIPT AND NOT DATA. ArchiveXL patches `.ent`, `.app` and `.mesh`
// resources and not an atlas, so her part cannot be added to the sheet.
//
// A RESOURCE PATH IN REDSCRIPT DOUBLES ITS BACKSLASHES: `r"a\\b"` is the
// spelling the game's own scripts use (`mappinsContainers.swift`), and a
// single backslash is a syntax error at the first one.
//
// `GetTexturePart` and `SetAtlasResource` are both natives on `inkImageRef`
// (orphans.swift 31616 and 31649 in the decompiled scripts). The wrapped
// methods are script and take a `@wrapMethod`; `SetData` is public, the card's
// `UpdateFixerData` is private final, which redscript wraps all the same.

module CyberpunkCodes.Fixer01

public abstract class Fixer01Portrait {
  public final static func Part() -> CName { return n"cc_f01_fixer"; }

  public final static func Ours() -> ResRef { return r"mod\\fixer01\\gui\\portrait.inkatlas"; }

  public final static func Sheet() -> ResRef { return r"base\\gameplay\\gui\\common\\icons\\avatars\\avatars_tooltips.inkatlas"; }

  // The widget was just given a part; point its atlas at whichever sheet
  // holds that part.
  public final static func Fix(widget: inkImageRef) -> Void {
    if Equals(inkImageRef.GetTexturePart(widget), Fixer01Portrait.Part()) {
      inkImageRef.SetAtlasResource(widget, Fixer01Portrait.Ours());
    } else {
      inkImageRef.SetAtlasResource(widget, Fixer01Portrait.Sheet());
    }
  }
}

@wrapMethod(WorldMapTooltipController)
public func SetData(const data: script_ref<WorldMapTooltipData>, menu: ref<WorldMapMenuGameController>) -> Void {
  wrappedMethod(data, menu);
  Fixer01Portrait.Fix(this.m_icon);
  Fixer01Portrait.Fix(this.m_fixerIcon);
}

@wrapMethod(SimpleQuestListItemController)
private final func UpdateFixerData() -> Void {
  wrappedMethod();
  Fixer01Portrait.Fix(this.m_fixerIcon);
}
