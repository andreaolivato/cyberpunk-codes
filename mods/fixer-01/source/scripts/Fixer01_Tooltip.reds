// Fixer 01: the map tooltip's fallback for the fixer's icon.
//
// WHAT THE TOOLTIP DOES ON ITS OWN. Hovering a fixer's hands icon on the
// world map runs `MappinUIUtils.GetFixerVariantData`, which asks the icon for
// its character record (`PointOfInterestMappin.GetCharacterRecordID`, a
// native) and reads the name, the portrait and the "3/10" off that record.
// Where the icon keeps that record id is the one thing the desk research
// could not find on disk. The reading is that it comes from the body the
// icon's journal entry names, through the community system; ours names our
// community, and playtesting showed the icon finds her that way.
//
// WHAT THIS FILE IS FOR. If it does not, the icon still draws and the counter
// still counts, but hovering gives an empty tooltip: the native returns no
// record, and the function reads five flats off nothing. This wrap answers
// for our icon instead, with our record, and it is the whole tooltip panel's
// only source of data, so it makes the panel complete.
//
// IT IS OFF BY DEFAULT and switched on by the fact `cc_f01_tooltip_shim`
// from the dev menu, so one build measures both routes: hover with it at 0
// to see what the game does on its own, set it to 1 and hover again. A fact
// is read at runtime, so no rebuild between the two.
//
// HOW OUR ICON IS RECOGNISED. `GetJournalPathHash` on the icon is the
// Murmur3-32 of its journal path, and POI_HASH below is that number for
// `points_of_interest/service_points/cc_f01_fixer`. tools/fixer01/gen_journal.py
// computes the same hash and refuses to run if this constant disagrees with
// it, so the two cannot drift apart in silence.
//
// WHEN THE SHIM ANSWERS, IT ANSWERS FIRST. The wrapped function is not
// called for our icon at all, because a null record inside it is exactly the
// case being guarded against. For every other icon it is a pass-through.
//
// The body below is `GetFixerVariantData` from the decompiled scripts
// (`cyberpunk/UI/mappins/mappinUtils.swift`, 2.31) with the record id fixed,
// including its handling of `thresholds`, so the panel gets the same struct
// it would have got from the game.

module CyberpunkCodes.Fixer01

public abstract class Fixer01 {
  public final static func Record() -> TweakDBID { return t"Character.cc_f01_fixer"; }
  public final static func ShimFact() -> CName { return n"cc_f01_tooltip_shim"; }

  // Murmur3-32 of `points_of_interest/service_points/cc_f01_fixer`.
  // gen_journal.py checks this line against its own computation.
  public final static func PoiHash() -> Uint32 { let POI_HASH: Uint32 = 3103048154u; return POI_HASH; }

  // `GetFixerVariantData` with the record id fixed. One difference from the
  // decompiled body, on purpose: past the last threshold the game indexes
  // `thresholdsArray[thresholdsAmount]`, one past the end; this reads the
  // last element, which is what the arithmetic means.
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
