module CyberpunkCodes.Fixer01

public abstract class Fixer01Portrait {
  public final static func Part() -> CName { return n"cc_f01_fixer"; }

  public final static func Ours() -> ResRef { return r"mod\\fixer01\\gui\\portrait.inkatlas"; }

  // 26 faces
  public final static func Sheet() -> ResRef { return r"base\\gameplay\\gui\\common\\icons\\avatars\\avatars_tooltips.inkatlas"; }

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
