// Gig 01, Negative Balance: the ledger on the office terminal's own screen.
//
// There is a real narrative computer ~1.6 m from the marked desk spot
// (`q112_dvc_narrative_computer`, sector exterior_-3_-24_0_0). Rather than
// printing the ledger as on-screen messages when V walks close enough, we push
// a file into that computer's Files menu and let V read it there.
//
// EVERYTHING BELOW WAS READ OUT OF THE DECOMPILED SCRIPTS, do not guess method
// names in this file. Sources (https://codeberg.org/adamsmasher/cyberpunk):
//   cyberpunk/devices/masters/computerController.swift
//   cyberpunk/devices/masters/computer.swift
//   cyberpunk/devices/UI/computer/computerGameController.swift
//
// What the vanilla code actually gives us:
//
//   * `ComputerControllerPS.m_computerSetup.m_filesStructure` is an
//     `array<GenericDataContent>`; each folder is `name` + `content:
//     array<DataElement>`. `m_filesMenu` toggles the Files tab, and the tab is
//     only offered at all when that array is non-empty.
//
//   * The UI never touches the setup directly. It queues events that land on
//     three NON-final PS methods, RequestFileThumbnailWidgetsUpdate,
//     RequestMenuButtonWidgetsUpdate, RequestMainMenuButtonWidgetsUpdate - 
//     which turn the setup into widget packages on the device blackboard.
//     Wrapping those three and topping the data up first is all it takes; one
//     of them runs whenever a computer menu is shown.
//
//   * READING NEEDS NO HOOK. ComputerInkGameController.OpenDocument calls
//     ResolveQuestInfo, which is literally
//     `AddFact(game, questInfo.factName, 1)`. A DataElement carrying
//     `questInfo.factName` therefore sets the fact the moment V opens it.
//     Caveat: AddFact INCREMENTS. Re-reading takes the fact to 2, 3, ... so
//     every consumer must test `> 0`, never `== 1`. The quest phase already
//     compares Greater-than-0 (gen_questphase.add_pause_fact); Gig01_Encounter
//     was fixed to match.

module CyberpunkCodes.Gig01

public abstract class CCG01Ledger {
    // Captured desk spot. The computer entity sits ~1.6 m away, so 6 m of slack
    // identifies it without reaching anything else in the room.
    public static func TerminalPos() -> Vector4 { return new Vector4(-251.915, -1456.364, 14.600, 1.0); }
    public static func Radius() -> Float { return 6.0; }

    // THE SHARD ON THE OFFICE DESK (comic p23) - the VANILLA one, dumped in
    // game 2026-08-13 with the dev menu's look-at capture.
    //
    // Nothing of ours is spawned here any more. Two attempts shipped a custom
    // shard entity and neither rendered; the room already contains a readable
    // shard on the desk the objective points at, and playtesting said so twice
    // before it was taken seriously: "the shard is already in the room so maybe
    // you can use its location and override the content."
    //
    // This constant is now where the quest PIN points, so the marker sits on
    // the object the player actually has to read. Gig01_Shard.reds swaps our
    // note in for its content when V reads it.
    public static func ShardSpot() -> Vector4 {
        return new Vector4(-244.931, -1454.178, 15.400, 1.0);
    }

    // SIX files, not one. The comic's terminal (p20) is a LIST of audit-log
    // entries all reading ACCOUNT CLOSED; the pattern is the evidence. Five
    // per-account clearance notices, then the authorization from p21 that names
    // Hoshino.
    public static func Count() -> Int32 { return 6; }

    // Index of the authorization - the last one, and the only one that fires the
    // read fact. Reading one dead stranger's account is not the discovery;
    // finding the signature on all of them is.
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

    // The single-file version shipped under this name. Kept ONLY so a save made
    // against that build finds its old folder and has it rewritten in place,
    // instead of growing a second folder beside it.
    public static func LegacyDocName() -> CName { return n"cc_g01_ledger"; }

    // Set by the engine when V opens the authorization. NOT the objective fact:
    // the copy beats and the Johnny exchange play first, and the last line of
    // that exchange sets cc_g01_terminal_done.
    public static func ReadFact() -> CName { return n"cc_g01_ledger_read"; }
}

// The owner entity is always streamed in when these run, the UI is open.
@addMethod(ComputerControllerPS)
private final func CCG01IsOfficeTerminal() -> Bool {
    let owner: ref<GameObject> = this.GetOwnerEntityWeak() as GameObject;
    if !IsDefined(owner) {
        return false;
    }
    return Vector4.Distance(owner.GetWorldPosition(), CCG01Ledger.TerminalPos()) <= CCG01Ledger.Radius();
}

// One definition of a document, shared by the create and repair paths.
//
// LocKeys are built from the index: cc-g01-file-<n>-title / -body, 1-based to
// match how they read in gen_localization.py.
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
    // Only the authorization advances the quest. Vanilla fires this for us the
    // moment V opens it (ComputerInkGameController.OpenDocument -> ResolveQuestInfo
    // -> AddFact). Leaving factName blank on the other five is deliberate: they
    // are the texture, not the trigger.
    if i == CCG01Ledger.KeyIndex() {
        doc.questInfo.factName = CCG01Ledger.ReadFact();
        doc.questInfo.isHighlighted = true;
    }
    return doc;
}

// Second, reload-proof source of "V has read the ledger".
//
// questInfo.factName is the instant path, but questInfo is NOT persistent: an
// element restored from a save can come back with it blank, and then opening
// the file fires no fact at all and the objective sticks on "read the ledger".
// wasRead IS persistent, and vanilla SetOpenedFileAdress sets it the moment the
// document is opened and then calls RequestMenuButtonWidgetsUpdate, which we
// wrap, so this runs immediately after the read as well as on any later visit.
// Idempotent: the fact is only ever pushed from 0 to 1.
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

// Called before every widget build, so the file is present no matter which menu
// V opens first, and correct even if the strings changed since it was created.
@addMethod(ComputerControllerPS)
public final func CCG01EnsureLedger() -> Void {
    if !this.CCG01IsOfficeTerminal() {
        return;
    }
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if qs.GetFactStr("cc_g01_accepted") <= 0 {
        return;
    }
    // ...AND ONLY UNTIL THE GIG IS OVER. cc_g01_accepted never returns to 0, so
    // it was the whole gate and the ledger was rebuilt into this computer on
    // every visit for the rest of the save. Leaving the folder in place is the
    // right outcome - V read it, it is evidence, and pulling it back out would
    // be a mod deleting something the player found - so this stops writing
    // rather than reverting.
    if qs.GetFactStr("cc_g01_done") > 0 {
        return;
    }

    let folders: Int32 = ArraySize(this.m_computerSetup.m_filesStructure);

    // Find OUR folder: the one holding any of our document names, or the legacy
    // single-file name from the build before this one.
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

    // m_filesStructure is persistent, but of DataElement only isEnabled/wasRead/
    // isEncrypted are. Title and documentName are NOT. So a save/reload hands
    // our folder back with blank names, the search above misses it, and
    // appending again would grow the array by one folder per load. The fact
    // below is the durable "we already installed it" marker, and we always
    // append last, so the last folder is ours.
    if mine < 0 && qs.GetFactStr("cc_g01_ledger_installed") > 0 && folders > 0 {
        mine = folders - 1;
    }

    if mine >= 0 {
        // Rewrite in place. wasRead is persistent and is the one thing worth
        // carrying over, so a reload does not un-read what V has read - matched
        // BY POSITION, since the names it would otherwise be matched on are the
        // very thing that did not survive.
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

// --------------------------------------------------------------- the wraps
// All three are non-final and are the only route from the UI to the setup data.

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

// NOTE: there was a @wrapMethod on OnToggleZoomInteraction here to detect V
// backing out of the screen. It does NOT fire when a computer screen is closed
//. Exiting takes a different route, so the download sat waiting on the
// distance fallback and the objective took a long time to complete. Detection
// moved to PlayerStateMachine.IsUIZoomDevice, polled in Gig01_Encounter's tick.
// Don't reinstate the hook.
