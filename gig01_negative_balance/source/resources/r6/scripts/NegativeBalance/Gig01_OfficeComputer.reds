module CyberpunkCodes.Gig01

public abstract class CCG01Ledger {
    public static func TerminalPos() -> Vector4 { return new Vector4(-251.915, -1456.364, 14.600, 1.0); }
    public static func Radius() -> Float { return 6.0; }

    public static func ShardSpot() -> Vector4 {
        return new Vector4(-244.931, -1454.178, 15.400, 1.0);
    }

    public static func Count() -> Int32 { return 6; }

    // names hoshino
    public static func KeyIndex() -> Int32 { return 5; }

    public static func DocName(i: Int32) -> CName {
        switch i {
            case 0: return n"cc_g01_ledger_1";
            case 1: return n"cc_g01_ledger_2";
            case 2: return n"cc_g01_ledger_3";
            case 3: return n"cc_g01_ledger_4";
            case 4: return n"cc_g01_ledger_5";
            default: return n"cc_g01_ledger_6";
        }
    }

    // old saves
    public static func LegacyDocName() -> CName { return n"cc_g01_ledger"; }

    public static func ReadFact() -> CName { return n"cc_g01_ledger_read"; }
}

@addMethod(ComputerControllerPS)
private final func CCG01IsOfficeTerminal() -> Bool {
    let owner: ref<GameObject> = this.GetOwnerEntityWeak() as GameObject;
    if !IsDefined(owner) {
        return false;
    }
    return Vector4.Distance(owner.GetWorldPosition(), CCG01Ledger.TerminalPos()) <= CCG01Ledger.Radius();
}

@addMethod(ComputerControllerPS)
private final func CCG01MakeLedger(i: Int32) -> DataElement {
    let n: String = ToString(i + 1);
    let doc: DataElement;
    doc.documentName = CCG01Ledger.DocName(i);
    doc.title = GetLocalizedTextByKey(StringToName("cc-g01-file-" + n + "-title"));
    doc.content = GetLocalizedTextByKey(StringToName("cc-g01-file-" + n + "-body"));
    doc.owner = GetLocalizedTextByKey(n"cc-g01-file-owner");
    doc.date = GetLocalizedTextByKey(n"cc-g01-file-date");
    doc.isEnabled = true;
    doc.isEncrypted = false;
    if i == CCG01Ledger.KeyIndex() {
        doc.questInfo.factName = CCG01Ledger.ReadFact();
        doc.questInfo.isHighlighted = true;
    }
    return doc;
}

@addMethod(ComputerControllerPS)
private final func CCG01PromoteRead(wasRead: Bool) -> Void {
    if !wasRead {
        return;
    }
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if qs.GetFactStr("cc_g01_ledger_read") <= 0 {
        qs.SetFactStr("cc_g01_ledger_read", 1);
    }
}

@addMethod(ComputerControllerPS)
public final func CCG01EnsureLedger() -> Void {
    if !this.CCG01IsOfficeTerminal() {
        return;
    }
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if qs.GetFactStr("cc_g01_accepted") <= 0 {
        return;
    }
    if qs.GetFactStr("cc_g01_done") > 0 {
        return;
    }

    let folders: Int32 = ArraySize(this.m_computerSetup.m_filesStructure);

    let mine: Int32 = -1;
    let i: Int32 = 0;
    while i < folders && mine < 0 {
        let k: Int32 = 0;
        while k < ArraySize(this.m_computerSetup.m_filesStructure[i].content) {
            let dn: CName = this.m_computerSetup.m_filesStructure[i].content[k].documentName;
            if Equals(dn, CCG01Ledger.LegacyDocName()) {
                mine = i;
                break;
            }
            let j: Int32 = 0;
            while j < CCG01Ledger.Count() {
                if Equals(dn, CCG01Ledger.DocName(j)) {
                    mine = i;
                    break;
                }
                j += 1;
            }
            if mine >= 0 {
                break;
            }
            k += 1;
        }
        i += 1;
    }

    if mine < 0 && qs.GetFactStr("cc_g01_ledger_installed") > 0 && folders > 0 {
        // ours is always last
        mine = folders - 1;
    }

    if mine >= 0 {
        let old: array<DataElement> = this.m_computerSetup.m_filesStructure[mine].content;
        let rebuilt: array<DataElement>;
        let n: Int32 = 0;
        while n < CCG01Ledger.Count() {
            let doc: DataElement = this.CCG01MakeLedger(n);
            if n < ArraySize(old) {
                doc.wasRead = old[n].wasRead;
            }
            ArrayPush(rebuilt, doc);
            n += 1;
        }
        this.m_computerSetup.m_filesStructure[mine].name = GetLocalizedTextByKey(n"cc-g01-file-folder");
        this.m_computerSetup.m_filesStructure[mine].content = rebuilt;
        this.m_computerSetup.m_filesMenu = true;
        this.CCG01PromoteRead(rebuilt[CCG01Ledger.KeyIndex()].wasRead);
        return;
    }

    let folder: GenericDataContent;
    folder.name = GetLocalizedTextByKey(n"cc-g01-file-folder");
    let m: Int32 = 0;
    while m < CCG01Ledger.Count() {
        ArrayPush(folder.content, this.CCG01MakeLedger(m));
        m += 1;
    }
    ArrayPush(this.m_computerSetup.m_filesStructure, folder);
    this.m_computerSetup.m_filesMenu = true;
    qs.SetFactStr("cc_g01_ledger_installed", 1);
}

@wrapMethod(ComputerControllerPS)
public func RequestFileThumbnailWidgetsUpdate(blackboard: ref<IBlackboard>) -> Void {
    this.CCG01EnsureLedger();
    wrappedMethod(blackboard);
}

@wrapMethod(ComputerControllerPS)
public func RequestMenuButtonWidgetsUpdate(blackboard: ref<IBlackboard>) -> Void {
    this.CCG01EnsureLedger();
    wrappedMethod(blackboard);
}

@wrapMethod(ComputerControllerPS)
public func RequestMainMenuButtonWidgetsUpdate(blackboard: ref<IBlackboard>) -> Void {
    this.CCG01EnsureLedger();
    wrappedMethod(blackboard);
}
