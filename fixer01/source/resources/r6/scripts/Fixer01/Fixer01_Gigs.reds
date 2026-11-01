module CyberpunkCodes.Fixer01

public abstract class Fixer01Gigs {
  public final static func ListFlat() -> TweakDBID { return t"Character.cc_f01_fixer.gigs"; }
  public final static func TotalFlat() -> TweakDBID { return t"Character.cc_f01_fixer.amountOfQuests"; }

  public final static func Register(gig: CName) -> Void {
    let list: array<CName> = TweakDBInterface.GetCNameArray(Fixer01Gigs.ListFlat());
    // already counted
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
    FTLog(s"[CC.Fixer01] gig registered: \(NameToString(gig)), total \(total), list stored \(stored)");
  }

  public final static func Total() -> Int32 {
    return TweakDBInterface.GetInt(Fixer01Gigs.TotalFlat(), 0);
  }
}

@wrapMethod(WorldMapTooltipController)
public func SetData(const data: script_ref<WorldMapTooltipData>, menu: ref<WorldMapMenuGameController>) -> Void {
  wrappedMethod(data, menu);
  if Equals(inkImageRef.GetTexturePart(this.m_icon), Fixer01Portrait.Part()) && Fixer01Gigs.Total() <= 0 {
    this.m_gigProgress = 0.0;
    inkWidgetRef.SetVisible(this.m_fixerPanel, false);
  }
}
