module CyberpunkCodes.Gig05

@wrapMethod(ItemAddedNotification)
private final func SetIcon(itemID: TweakDBID, rarity: CName) -> Void {
  wrappedMethod(itemID, rarity);
  if Equals(itemID, t"Items.cc_g05_outfit") {
    inkWidgetRef.SetScale(this.m_itemImage, new Vector2(0.90, 0.90));
  }
}
