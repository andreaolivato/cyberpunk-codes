module CyberpunkCodes.Gig03

public abstract class CCG03Files {
    // north-west corner
    public static func TerminalPos() -> Vector4 {
        return new Vector4(-133.173, -5193.786, 88.564, 1.0);
    }

    // next computer is 39m
    public static func Radius() -> Float { return 6.0; }

    public static func Count() -> Int32 { return 3; }

    // oversight note
    public static func KeyIndex() -> Int32 { return 2; }

    public static func DocName(i: Int32) -> CName {
        switch i {
            case 0: return n"cc_g03_file_1";
            case 1: return n"cc_g03_file_2";
            default: return n"cc_g03_file_3";
        }
    }

    public static func ReadFact() -> CName { return n"cc_g03_data"; }
}

@addMethod(ComputerControllerPS)
private final func CCG03IsOurTerminal() -> Bool {
    let owner: ref<GameObject> = this.GetOwnerEntityWeak() as GameObject;
    if !IsDefined(owner) {
        return false;
    }
    return Vector4.Distance(owner.GetWorldPosition(), CCG03Files.TerminalPos())
        <= CCG03Files.Radius();
}

@addMethod(ComputerControllerPS)
private final func CCG03MakeFile(i: Int32) -> DataElement {
    let n: String = ToString(i + 1);
    let doc: DataElement;
    doc.documentName = CCG03Files.DocName(i);
    doc.title = GetLocalizedTextByKey(StringToName("cc-g03-file-" + n + "-title"));
    doc.content = GetLocalizedTextByKey(StringToName("cc-g03-file-" + n + "-body"));
    doc.owner = GetLocalizedTextByKey(n"cc-g03-file-owner");
    doc.date = GetLocalizedTextByKey(n"cc-g03-file-date");
    doc.isEnabled = true;
    doc.isEncrypted = false;
    if i == CCG03Files.KeyIndex() {
        doc.questInfo.factName = CCG03Files.ReadFact();
        doc.questInfo.isHighlighted = true;
    }
    return doc;
}

@addMethod(ComputerControllerPS)
private final func CCG03PromoteRead(wasRead: Bool) -> Void {
    if !wasRead {
        return;
    }
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if qs.GetFactStr("cc_g03_data") <= 0 {
        qs.SetFactStr("cc_g03_data", 1);
    }
}

@addMethod(ComputerControllerPS)
public final func CCG03EnsureFiles() -> Void {
    if !this.CCG03IsOurTerminal() {
        return;
    }
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if qs.GetFactStr("cc_g03_start") <= 0 || qs.GetFactStr("cc_g03_done") > 0 {
        return;
    }

    let folders: Int32 = ArraySize(this.m_computerSetup.m_filesStructure);

    let mine: Int32 = -1;
    let i: Int32 = 0;
    while i < folders && mine < 0 {
        let k: Int32 = 0;
        while k < ArraySize(this.m_computerSetup.m_filesStructure[i].content) {
            let dn: CName = this.m_computerSetup.m_filesStructure[i].content[k].documentName;
            let j: Int32 = 0;
            while j < CCG03Files.Count() {
                if Equals(dn, CCG03Files.DocName(j)) {
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

    if mine < 0 && qs.GetFactStr("cc_g03_files_installed") > 0 && folders > 0 {
        mine = folders - 1;
    }

    if mine >= 0 {
        let old: array<DataElement> = this.m_computerSetup.m_filesStructure[mine].content;
        let rebuilt: array<DataElement>;
        let n: Int32 = 0;
        while n < CCG03Files.Count() {
            let doc: DataElement = this.CCG03MakeFile(n);
            if n < ArraySize(old) {
                doc.wasRead = old[n].wasRead;
            }
            ArrayPush(rebuilt, doc);
            n += 1;
        }
        this.m_computerSetup.m_filesStructure[mine].name =
            GetLocalizedTextByKey(n"cc-g03-file-folder");
        this.m_computerSetup.m_filesStructure[mine].content = rebuilt;
        this.m_computerSetup.m_filesMenu = true;
        this.CCG03PromoteRead(rebuilt[CCG03Files.KeyIndex()].wasRead);
        return;
    }

    let folder: GenericDataContent;
    folder.name = GetLocalizedTextByKey(n"cc-g03-file-folder");
    let m: Int32 = 0;
    while m < CCG03Files.Count() {
        ArrayPush(folder.content, this.CCG03MakeFile(m));
        m += 1;
    }
    ArrayPush(this.m_computerSetup.m_filesStructure, folder);
    this.m_computerSetup.m_filesMenu = true;
    qs.SetFactStr("cc_g03_files_installed", 1);
}

@wrapMethod(ComputerControllerPS)
public func RequestFileThumbnailWidgetsUpdate(blackboard: ref<IBlackboard>) -> Void {
    this.CCG03EnsureFiles();
    wrappedMethod(blackboard);
}

@wrapMethod(ComputerControllerPS)
public func RequestMenuButtonWidgetsUpdate(blackboard: ref<IBlackboard>) -> Void {
    this.CCG03EnsureFiles();
    wrappedMethod(blackboard);
}

@wrapMethod(ComputerControllerPS)
public func RequestMainMenuButtonWidgetsUpdate(blackboard: ref<IBlackboard>) -> Void {
    this.CCG03EnsureFiles();
    wrappedMethod(blackboard);
}
