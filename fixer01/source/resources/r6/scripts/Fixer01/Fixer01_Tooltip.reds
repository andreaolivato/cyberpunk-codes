module CyberpunkCodes.Fixer01

public abstract class Fixer01 {
  public final static func Record() -> TweakDBID { return t"Character.cc_f01_fixer"; }
  public final static func ShimFact() -> CName { return n"cc_f01_tooltip_shim"; }

  // murmur3-32
  public final static func PoiHash() -> Uint32 { let POI_HASH: Uint32 = 3103048154u; return POI_HASH; }

  public final static func TooltipData(questSystem: ref<QuestsSystem>, characterID: TweakDBID) -> FixerTooltipMapData {
    let fixerData: FixerTooltipMapData;
    let i: Int32;
    let thresholdsAmount: Int32;
    let thresholdsArray: array<Int32>;
    fixerData.fixerLocKey = TweakDBInterface.GetCharacterRecord(characterID).FullDisplayName();
    fixerData.fixerIcon = TweakDBInterface.GetUIIconRecord(TDB.GetForeignKey(characterID + t".tooltipAvatar"));
    fixerData.allQuestsAmount = TweakDBInterface.GetInt(characterID + t".amountOfQuests", 0);
    fixerData.generalQuestsProgress = questSystem.GetFact(TweakDBInterface.GetCName(characterID + t".factCounterName", n"None"));
    fixerData.additionalDescriptionKey = TweakDBInterface.GetCName(characterID + t".additionalDescription", n"None");
    thresholdsArray = TweakDBInterface.GetIntArray(characterID + t".thresholds");
    thresholdsAmount = ArraySize(thresholdsArray);
    if thresholdsAmount == 0 {
      fixerData.currentPackageProgress = fixerData.generalQuestsProgress;
      fixerData.allQuestsInCurrentPackage = fixerData.allQuestsAmount;
      return fixerData;
    };
    if fixerData.generalQuestsProgress > thresholdsArray[thresholdsAmount - 1] {
      fixerData.currentPackageProgress = fixerData.generalQuestsProgress - thresholdsArray[thresholdsAmount - 1];
      fixerData.allQuestsInCurrentPackage = fixerData.allQuestsAmount - thresholdsArray[thresholdsAmount - 1];
      return fixerData;
    };
    i = 0;
    while i < thresholdsAmount {
      if fixerData.generalQuestsProgress < thresholdsArray[i] {
        if i == 0 {
          fixerData.currentPackageProgress = fixerData.generalQuestsProgress;
          fixerData.allQuestsInCurrentPackage = thresholdsArray[i];
          return fixerData;
        };
        fixerData.currentPackageProgress = fixerData.generalQuestsProgress - thresholdsArray[i - 1];
        fixerData.allQuestsInCurrentPackage = thresholdsArray[i] - thresholdsArray[i - 1];
        return fixerData;
      };
      i += 1;
    };
    return fixerData;
  }
}

@wrapMethod(MappinUIUtils)
public final static func GetFixerVariantData(questSystem: ref<QuestsSystem>, mappin: ref<IMappin>) -> FixerTooltipMapData {
  let poi: ref<PointOfInterestMappin> = mappin as PointOfInterestMappin;
  if !IsDefined(poi) || questSystem.GetFact(Fixer01.ShimFact()) == 0 {
    return wrappedMethod(questSystem, mappin);
  }
  if poi.GetJournalPathHash() != Fixer01.PoiHash() {
    return wrappedMethod(questSystem, mappin);
  }
  return Fixer01.TooltipData(questSystem, Fixer01.Record());
}
