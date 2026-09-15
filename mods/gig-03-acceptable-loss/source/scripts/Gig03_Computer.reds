// Gig 03, Acceptable Loss: the files on the compound's terminal.
//
// Three documents pushed into a base-game computer's Files menu. Reading the
// third is what tells V the log Dino wants is not on the network at all, and
// it is what opens the objective that sends the player to the security room.
//
// EVERYTHING HERE IS THE SHAPE GIG 01 PROVED. `Gig01_OfficeComputer.reds` and
// `docs/computer-ui-playbook.md` carry the full account and the sources; this
// header records only what is different.
//
// ---------------------------------------------------------------------------
// WHICH COMPUTER, AND WHICH ONE IT MUST NOT BE
//
// The one this gig uses stands in the NORTH-WEST corner of the compound, at
// -133.173, -5193.786. It is a plain `Devices.Computer`, and it belongs to no
// quest.
//
// THE COMPUTER IN THE OFFICE IS OFF LIMITS. That one is `ina_05_dvc_comp`, the
// quest device of the base game's own street story at this site, with three
// `DeviceContentAssignment.sts_bls_ina_05` nodes within five metres of it.
// Pushing our files into a live quest's device risks both directions, and the
// radius below is tight enough that it can never be reached: the two machines
// are 39 m apart.
//
// ---------------------------------------------------------------------------
// READING NEEDS NO HOOK, AND THE FACT INCREMENTS
//
// `ComputerInkGameController.OpenDocument` calls `ResolveQuestInfo`, which is
// `AddFact(game, questInfo.factName, 1)`. A DataElement carrying a factName
// therefore sets that fact the moment V opens it.
//
// AddFact INCREMENTS. Re-reading takes the fact to 2, 3 and up, so every
// consumer tests `> 0` and never `== 1`. The quest phase already compares
// greater-than-zero.
//
// `questInfo` is NOT persistent, so an element restored from a save can come
// back with the factName blank and opening the file would fire nothing.
// `wasRead` IS persistent, which is the second route below.

module CyberpunkCodes.Gig03

public abstract class CCG03Files {
    // The terminal, captured in game with the device probe.
    public static func TerminalPos() -> Vector4 {
        return new Vector4(-133.173, -5193.786, 88.564, 1.0);
    }

    // Tight on purpose. The nearest other computer is 39 m away and is the
    // street story's quest device, so this can never reach it.
    public static func Radius() -> Float { return 6.0; }

    // THREE FILES, which is the comic's own terminal: a summary, an attrition
    // report, and the oversight note. The pattern is the evidence, so the first
    // two are the texture and the third is where it becomes unmistakable.
    public static func Count() -> Int32 { return 3; }

    // The last one, and the only one that fires the fact. It is the oversight
    // note: fatalities are performance outcomes, do not notify next-of-kin, and
    // the log itself is held in the security room.
    public static func KeyIndex() -> Int32 { return 2; }

    public static func DocName(i: Int32) -> CName {
        switch i {
            case 0: return n"cc_g03_file_1";
            case 1: return n"cc_g03_file_2";
            default: return n"cc_g03_file_3";
        }
    }

    // Set by the engine when V opens the third file. The quest phase waits on
    // it to open the objective that sends the player to the shard.
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

// One definition of a document, shared by the create and repair paths. LocKeys
// are built from the index, 1-based, to match gen_localization.py.
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

// The reload-proof second route. `wasRead` is persistent and vanilla sets it the
// moment a document is opened, then calls one of the wrapped methods below, so
// this runs immediately after the read as well as on any later visit.
// Idempotent: the fact is only ever pushed from 0 to 1.
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
    // Only while the gig is live. Before it starts, and after it ends, this
    // computer is the base game's.
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

    // `m_filesStructure` is persistent, but of a DataElement only isEnabled,
    // wasRead and isEncrypted are. Title and documentName are NOT, so a reload
    // hands our folder back with blank names, the search above misses it, and
    // appending again would grow the array by one folder per load. This fact is
    // the durable "already installed" marker, and we always append last.
    if mine < 0 && qs.GetFactStr("cc_g03_files_installed") > 0 && folders > 0 {
        mine = folders - 1;
    }

    if mine >= 0 {
        // Rewrite in place, carrying `wasRead` across BY POSITION, since the
        // names it would otherwise be matched on are the very thing that did
        // not survive the save.
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

// --------------------------------------------------------------- the wraps
// All three are non-final and are the only route from the UI to the setup data.
// One of them runs whenever a computer menu is shown, so the files are present
// whichever menu V opens first.

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
