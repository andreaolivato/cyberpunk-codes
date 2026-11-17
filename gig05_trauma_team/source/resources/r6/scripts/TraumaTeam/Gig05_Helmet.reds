module CyberpunkCodes.Gig05

public class TraumaTeamHelmet {

    private let m_root: ref<inkCanvas>;
    private let m_tint: ref<inkCanvas>;
    private let m_clock: ref<inkText>;
    private let m_rate: ref<inkText>;
    private let m_beat: Int32;
    private let m_monOn: Bool;
    private let m_monState: Int32;
    private let m_monHp: Float;
    private let m_monLeft: Int32;
    private let m_monCrit: Bool;
    private let m_monHostiles: Int32;
    private let m_monCard: String;
    private let m_panel: ref<inkCanvas>;
    private let m_segs: array<ref<inkRectangle>>;
    private let m_pState: ref<inkText>;
    private let m_pPct: ref<inkText>;
    private let m_pClock: ref<inkText>;
    private let m_pClockLabel: ref<inkText>;
    private let m_pHost: ref<inkText>;
    private let m_pCard: ref<inkText>;
    private let m_pGlow: ref<inkImage>;
    private let m_pShown: Int32;
    private let m_quiet: Bool;
    private let m_scanning: Bool;
    private let m_inMenu: Bool;
    private let m_photo: Bool;
    private let m_watching: Bool;
    private let m_scanCb: ref<CallbackHandle>;
    private let m_menuCb: ref<CallbackHandle>;
    private let m_photoCb: ref<CallbackHandle>;
    private let m_note: ref<inkCanvas>;
    private let m_game: GameInstance;
    private let m_hint: Int32;
    private let m_kbm: Bool;

    public static func Green() -> HDRColor { return new HDRColor(0.46, 0.78, 0.46, 1.0); }
    public static func Red() -> HDRColor { return new HDRColor(1.05, 0.13, 0.15, 1.0); }
    public static func Pale() -> HDRColor { return new HDRColor(0.96, 1.04, 0.90, 1.0); }
    public static func Font() -> String { return "base\\gameplay\\gui\\fonts\\raj\\raj.inkfontfamily"; }
    public static func Atlas() -> ResRef { return r"mod\\trauma_team\\gui\\hud.inkatlas"; }
    public static func DesignHeight() -> Float { return 1600.0; }
    public static func FrameLayer() -> CName { return n"inkGameNotificationsLayer"; }
    public static func TintLayer() -> CName { return n"inkHUDLayer"; }

    private func Window(layer: CName) -> ref<inkCompoundWidget> {
        let wrapper: ref<inkLayerWrapper> = GameInstance.GetInkSystem().GetLayer(layer);
        if !IsDefined(wrapper) {
            return null;
        }
        let window: ref<inkCompoundWidget> = wrapper.GetVirtualWindow();
        if !IsDefined(window) {
            return null;
        }
        let size: Vector2 = window.GetSize();
        if size.Y < 1.0 {
            return null;
        }
        return window;
    }

    private func On(w: ref<inkWidget>) -> Bool {
        return IsDefined(w) && IsDefined(w.GetParentWidget());
    }

    public func IsShown() -> Bool {
        return this.On(this.m_root) && this.On(this.m_tint);
    }

    public func Show(player: ref<PlayerPuppet>, arm: Bool) -> Void {
        this.HideNote();
        this.Watch(player.GetGame());
        if !this.On(this.m_tint) {
            let tw: ref<inkCompoundWidget> = this.Window(TraumaTeamHelmet.TintLayer());
            if IsDefined(tw) {
                let tint: ref<inkCanvas> = new inkCanvas();
                tint.SetName(n"cc_g05_helmet_tint");
                tint.SetAnchor(inkEAnchor.Fill);
                tint.SetInteractive(false);
                tint.Reparent(tw);
                tw.ReorderChild(tint, 0);
                this.m_tint = tint;
                this.m_quiet = !arm;
                this.BuildTint(tint);
                this.m_quiet = false;
            }
        }
        if !this.On(this.m_root) {
            let w: ref<inkCompoundWidget> = this.Window(TraumaTeamHelmet.FrameLayer());
            if !IsDefined(w) {
                return;
            }
            let root: ref<inkCanvas> = new inkCanvas();
            root.SetName(n"cc_g05_helmet");
            root.SetAnchor(inkEAnchor.Fill);
            root.SetInteractive(false);
            root.Reparent(w);
            w.ReorderChild(root, 0);
            this.m_root = root;
            this.m_quiet = !arm;
            this.Build(root, w.GetSize());
            this.m_quiet = false;
            if arm {
                GameObjectEffectHelper.StartEffectEvent(player, n"health_monitor");
            }
            this.Refresh();
            this.Hint(this.m_hint, true);
            return;
        }
        this.Refresh();
    }

    private func Watch(game: GameInstance) -> Void {
        this.m_game = game;
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject() as PlayerPuppet;
        if IsDefined(player) {
            this.m_kbm = player.PlayerLastUsedKBM();
        }
        let bbs: ref<BlackboardSystem> = GameInstance.GetBlackboardSystem(game);
        let scan: ref<IBlackboard> = bbs.Get(GetAllBlackboardDefs().UI_Scanner);
        let ui: ref<IBlackboard> = bbs.Get(GetAllBlackboardDefs().UI_System);
        let photo: ref<IBlackboard> = bbs.Get(GetAllBlackboardDefs().PhotoMode);
        if IsDefined(scan) {
            this.m_scanning = scan.GetBool(GetAllBlackboardDefs().UI_Scanner.UIVisible);
        }
        if IsDefined(ui) {
            this.m_inMenu = ui.GetBool(GetAllBlackboardDefs().UI_System.IsInMenu);
        }
        if IsDefined(photo) {
            this.m_photo = photo.GetBool(GetAllBlackboardDefs().PhotoMode.IsActive);
        }
        if this.m_watching {
            return;
        }
        this.m_watching = true;
        if IsDefined(scan) {
            this.m_scanCb = scan.RegisterListenerBool(GetAllBlackboardDefs().UI_Scanner.UIVisible, this, n"OnScanner");
        }
        if IsDefined(ui) {
            this.m_menuCb = ui.RegisterListenerBool(GetAllBlackboardDefs().UI_System.IsInMenu, this, n"OnMenu");
        }
        if IsDefined(photo) {
            this.m_photoCb = photo.RegisterListenerBool(GetAllBlackboardDefs().PhotoMode.IsActive, this, n"OnPhoto");
        }
    }

    protected cb func OnScanner(on: Bool) -> Bool {
        this.m_scanning = on;
        this.Refresh();
    }

    protected cb func OnMenu(on: Bool) -> Bool {
        this.m_inMenu = on;
        this.Refresh();
    }

    protected cb func OnPhoto(on: Bool) -> Bool {
        this.m_photo = on;
        this.Refresh();
    }

    private func Refresh() -> Void {
        let show: Bool = !this.m_scanning && !this.m_inMenu && !this.m_photo;
        if IsDefined(this.m_root) {
            this.m_root.SetVisible(show);
        }
        if IsDefined(this.m_tint) {
            this.m_tint.SetVisible(show);
        }
        if IsDefined(this.m_note) {
            this.m_note.SetVisible(show);
        }
        let want: Int32 = 0;
        if show && this.m_kbm {
            if this.On(this.m_note) {
                want = 2;
            } else {
                if this.On(this.m_root) {
                    want = 1;
                }
            }
        }
        this.Hint(want, false);
    }

    private func Hint(want: Int32, force: Bool) -> Void {
        if want == this.m_hint && !force {
            return;
        }
        if this.m_hint != 0 || force {
            this.SendHint(false, "");
        }
        this.m_hint = want;
        if want != 0 {
            this.SendHint(true, want == 1 ? "Helmet HUD Off" : "Helmet HUD On");
        }
    }

    private func SendHint(show: Bool, label: String) -> Void {
        let data: InputHintData;
        data.action = n"shooter_switchWeapon";
        data.source = n"cc_g05_visor";
        data.localizedLabel = label;
        data.holdIndicationType = inkInputHintHoldIndicationType.Hold;
        data.sortingPriority = 1;
        let evt: ref<UpdateInputHintEvent> = new UpdateInputHintEvent();
        evt.data = data;
        evt.show = show;
        evt.targetHintContainer = n"GameplayInputHelper";
        GameInstance.GetUISystem(this.m_game).QueueEvent(evt);
    }

    public func Poll(player: ref<PlayerPuppet>) -> Void {
        let kbm: Bool = player.PlayerLastUsedKBM();
        if NotEquals(kbm, this.m_kbm) {
            this.m_kbm = kbm;
            this.Refresh();
        }
    }

    public func ShowNote(game: GameInstance) -> Void {
        if this.On(this.m_note) {
            return;
        }
        let window: ref<inkCompoundWidget> = this.Window(TraumaTeamHelmet.FrameLayer());
        if !IsDefined(window) {
            return;
        }
        this.Watch(game);
        let k: Float = window.GetSize().Y / TraumaTeamHelmet.DesignHeight();
        let note: ref<inkCanvas> = new inkCanvas();
        note.SetName(n"cc_g05_helmet_note");
        note.SetAnchor(inkEAnchor.Fill);
        note.Reparent(window);
        this.m_note = note;
        let g: ref<inkCanvas> = this.Group(note, inkEAnchor.TopCenter, new Vector2(0.5, 0.0),
                                           new inkMargin(0.0, 24.0 * k, 0.0, 0.0), 400.0, 40.0, k);
        let t: ref<inkText> = this.Words(g, "HUD OFF", 11, n"Medium", TraumaTeamHelmet.Green(), 0.8, 6,
                                         200.0, 20.0, 0.5, 0.5);
        this.Fade(t, 0.8, 0.3, 4.0, 1.5, false);
        this.Refresh();
    }

    public func HideNote() -> Void {
        this.Drop(this.m_note);
        this.m_note = null;
    }

    private func Drop(w: ref<inkWidget>) -> Void {
        if IsDefined(w) {
            let parent: ref<inkCompoundWidget> = w.GetParentWidget() as inkCompoundWidget;
            if IsDefined(parent) {
                parent.RemoveChild(w);
            }
        }
    }

    public func Hide() -> Void {
        this.Drop(this.m_root);
        this.Drop(this.m_tint);
        this.m_root = null;
        this.m_tint = null;
        this.m_clock = null;
        this.m_rate = null;
        this.m_panel = null;
        this.m_pState = null;
        ArrayClear(this.m_segs);
        this.m_pShown = -1;
    }

    public func HideAll() -> Void {
        this.Hide();
        this.HideNote();
        this.Hint(0, false);
    }

    public func Update(game: GameInstance) -> Void {
        if IsDefined(this.m_clock) {
            let t: GameTime = GameInstance.GetTimeSystem(game).GetGameTime();
            this.m_clock.SetText(this.Two(GameTime.Hours(t)) + ":" + this.Two(GameTime.Minutes(t)));
        }
        if IsDefined(this.m_rate) {
            let red: Bool = false;
            if this.m_monOn {
                this.m_beat = this.m_monState == 3 ? 0
                    : Cast<Int32>(150.0 - this.m_monHp * 0.7) + RandRange(-3, 4);
                red = this.m_monState == 3 || this.m_monState == 0 && (this.m_monCrit || this.m_monHp < 30.0);
            } else {
                this.m_beat = 68 + RandRange(0, 10);
            }
            this.m_rate.SetText("HR " + (this.m_beat < 100 ? "0" : "") + (this.m_beat < 10 ? "0" : "")
                                + IntToString(this.m_beat));
            this.m_rate.SetTintColor(red ? TraumaTeamHelmet.Red() : TraumaTeamHelmet.Pale());
        }
        this.Panel();
    }

    public func SetMonitor(state: Int32, hp: Float, left: Int32, critical: Bool, hostiles: Int32, card: String) -> Void {
        this.m_monOn = state >= 0;
        this.m_monState = state;
        this.m_monHp = hp;
        this.m_monLeft = left;
        this.m_monCrit = critical;
        this.m_monHostiles = hostiles;
        this.m_monCard = card;
        this.Panel();
    }

    public static func Amber() -> HDRColor { return new HDRColor(1.10, 0.62, 0.12, 1.0); }

    private func Panel() -> Void {
        if !IsDefined(this.m_panel) {
            return;
        }
        this.m_panel.SetVisible(this.m_monOn);
        if !this.m_monOn {
            this.m_pShown = -1;
            return;
        }
        let st: Int32 = this.m_monState;
        let word: String;
        let color: HDRColor;
        if st == 3 {
            word = CCG05Shift.Text(n"cc-g05-hud-flatline", "Flatline");
            color = TraumaTeamHelmet.Red();
        } else {
            if st == 2 {
                word = CCG05Shift.Text(n"cc-g05-hud-stable", "Stable");
                color = TraumaTeamHelmet.Green();
            } else {
                if st == 1 {
                    word = CCG05Shift.Text(n"cc-g05-hud-stabilizing", "Stabilizing");
                    color = TraumaTeamHelmet.Green();
                } else {
                    if this.m_monCrit || this.m_monHp < 30.0 {
                        word = CCG05Shift.Text(n"cc-g05-hud-critical", "Critical");
                        color = TraumaTeamHelmet.Red();
                    } else {
                        word = CCG05Shift.Text(n"cc-g05-hud-unstable", "Unstable");
                        color = TraumaTeamHelmet.Amber();
                    }
                }
            }
        }
        this.m_pState.SetText(word);
        this.m_pState.SetTintColor(color);
        this.m_pGlow.SetTintColor(color);
        let lit: Int32 = Cast<Int32>(this.m_monHp / 5.0 + 0.5);
        let i: Int32 = 0;
        while i < ArraySize(this.m_segs) {
            let on: Bool = i < lit && st != 3;
            this.m_segs[i].SetTintColor(st == 3 ? TraumaTeamHelmet.Red() : (on ? color : TraumaTeamHelmet.Green()));
            this.m_segs[i].SetOpacity(on ? 0.95 : (st == 3 ? 0.35 : 0.14));
            i += 1;
        }
        this.m_pPct.SetText(IntToString(Cast<Int32>(this.m_monHp + 0.5)) + "%");
        let s: Int32 = Max(0, this.m_monLeft);
        this.m_pClock.SetText(st == 0 ? this.Two(s / 60) + ":" + this.Two(s % 60) : "--:--");
        this.m_pClock.SetTintColor(st == 0 && (this.m_monCrit || s < 30) ? TraumaTeamHelmet.Red() : TraumaTeamHelmet.Pale());
        this.m_pClockLabel.SetText(st == 0 && this.m_monCrit
            ? CCG05Shift.Text(n"cc-g05-hud-flatline-fast", "Flatline in  x2")
            : CCG05Shift.Text(n"cc-g05-hud-flatline-in", "Flatline in"));
        this.m_pHost.SetText(IntToString(this.m_monHostiles));
        this.m_pHost.SetTintColor(this.m_monHostiles > 0 ? TraumaTeamHelmet.Red() : TraumaTeamHelmet.Green());
        this.m_pCard.SetText(this.m_monCard);
        if st != this.m_pShown {
            this.m_pState.StopAllAnimations();
            this.m_pState.SetOpacity(1.0);
            this.m_pGlow.StopAllAnimations();
            if st == 3 {
                this.Fade(this.m_pState, 1.0, 0.2, 0.45, 0.0, true);
                this.Fade(this.m_pGlow, 0.25, 0.0, 0.45, 0.0, true);
            } else {
                this.m_pGlow.SetOpacity(st == 2 ? 0.18 : 0.08);
                if this.m_pShown >= 0 {
                    let q: Bool = this.m_quiet;
                    this.m_quiet = false;
                    this.Boot(this.m_pState, 0.0);
                    this.m_quiet = q;
                }
            }
            this.m_pShown = st;
        }
    }

    private func Two(n: Int32) -> String {
        return n < 10 ? "0" + IntToString(n) : IntToString(n);
    }

    private func BuildTint(root: ref<inkCanvas>) -> Void {
        let hue: ref<inkRectangle> = new inkRectangle();
        hue.SetAnchor(inkEAnchor.Fill);
        hue.SetTintColor(TraumaTeamHelmet.Green());
        hue.SetOpacity(0.008);
        hue.Reparent(root);
        if !this.m_quiet {
            hue.SetOpacity(0.0);
            this.Fade(hue, 0.0, 0.008, 0.6, 0.0, false);
        }
        let edge: ref<inkImage> = new inkImage();
        edge.SetAtlasResource(TraumaTeamHelmet.Atlas());
        edge.SetTexturePart(n"edge");
        edge.SetAnchor(inkEAnchor.Fill);
        edge.SetTintColor(TraumaTeamHelmet.Green());
        edge.SetOpacity(0.0);
        edge.Reparent(root);
        this.Fade(edge, 0.006, 0.014, 3.2, 0.0, true);
    }

    private func Build(root: ref<inkCanvas>, size: Vector2) -> Void {
        let k: Float = size.Y / TraumaTeamHelmet.DesignHeight();
        this.Header(root, k);
        this.Corners(root, k);
        this.Side(root, k, true);
        this.Side(root, k, false);
        this.Footer(root, k);
        this.ClientPanel(root, k);
    }

    private func ClientPanel(root: ref<inkCanvas>, k: Float) -> Void {
        let w: Float = 400.0;
        let g: ref<inkCanvas> = this.Group(root, inkEAnchor.CenterLeft, new Vector2(0.0, 0.5),
                                           new inkMargin(210.0 * k, 0.0, 0.0, 0.0), w, 300.0, k);
        this.m_panel = g;
        this.Bar(g, 0.0, 20.0, 3.0, 22.0, TraumaTeamHelmet.Red(), 0.95, 0.0, 0.5);
        this.Words(g, CCG05Shift.Text(n"cc-g05-hud-client", "Client"), 18, n"Semi-Bold", TraumaTeamHelmet.Pale(),
                   0.95, 4, 12.0, 20.0, 0.0, 0.5);
        this.Words(g, "//  BIOMON LINK", 12, n"Medium", TraumaTeamHelmet.Green(), 0.75, 6, 96.0, 21.0, 0.0, 0.5);
        this.Bar(g, 0.0, 44.0, w, 2.0, TraumaTeamHelmet.Green(), 0.5, 0.0, 0.5);
        this.Bar(g, w - 30.0, 44.0, 30.0, 4.0, TraumaTeamHelmet.Red(), 0.9, 0.0, 0.5);
        this.m_pGlow = this.Picture(g, n"glow", 90.0, 80.0, 260.0, 56.0, TraumaTeamHelmet.Green(), 0.08, 0.5, 0.5);
        this.m_pState = this.Words(g, "", 30, n"Semi-Bold", TraumaTeamHelmet.Pale(), 1.0, 5, 0.0, 80.0, 0.0, 0.5);
        ArrayClear(this.m_segs);
        let i: Int32 = 0;
        while i < 20 {
            let seg: ref<inkRectangle> = this.Bar(g, Cast<Float>(i) * 20.0, 120.0, 16.0, 14.0,
                                                  TraumaTeamHelmet.Green(), 0.14, 0.0, 0.5);
            ArrayPush(this.m_segs, seg);
            i += 1;
        }
        this.Words(g, CCG05Shift.Text(n"cc-g05-hud-stability", "Stability"), 12, n"Medium", TraumaTeamHelmet.Green(),
                   0.8, 6, 0.0, 148.0, 0.0, 0.5);
        this.m_pPct = this.Words(g, "", 16, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.95, 3, w, 148.0, 1.0, 0.5);
        this.m_pClockLabel = this.Words(g, "", 12, n"Medium", TraumaTeamHelmet.Green(), 0.8, 6, 0.0, 184.0, 0.0, 0.5);
        this.m_pClock = this.Words(g, "", 30, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.95, 4, w, 182.0, 1.0, 0.5);
        this.Words(g, CCG05Shift.Text(n"cc-g05-hud-hostiles", "Hostiles"), 12, n"Medium", TraumaTeamHelmet.Green(),
                   0.8, 6, 0.0, 220.0, 0.0, 0.5);
        this.m_pHost = this.Words(g, "", 16, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.95, 3, w, 220.0, 1.0, 0.5);
        this.Bar(g, 0.0, 242.0, w, 1.0, TraumaTeamHelmet.Green(), 0.35, 0.0, 0.5);
        this.m_pCard = this.Words(g, "", 12, n"Medium", TraumaTeamHelmet.Pale(), 0.8, 4, 0.0, 262.0, 0.0, 0.5);
        this.m_pShown = -1;
        this.Panel();
    }

    private func Header(root: ref<inkCanvas>, k: Float) -> Void {
        let w: Float = 900.0;
        let g: ref<inkCanvas> = this.Group(root, inkEAnchor.TopCenter, new Vector2(0.5, 0.0),
                                           new inkMargin(0.0, 24.0 * k, 0.0, 0.0), w, 120.0, k);
        let mid: Float = w / 2.0;
        let brow: Float = 30.0;

        this.Picture(g, n"glow", mid, brow, 300.0, 70.0, TraumaTeamHelmet.Green(), 0.06, 0.5, 0.5);
        this.Boot(this.Picture(g, n"logo", mid - 86.0, brow, 30.0, 30.0, TraumaTeamHelmet.Red(), 1.0, 0.5, 0.5), 0.45);
        this.Boot(this.Bar(g, mid - 64.0, brow, 2.0, 26.0, TraumaTeamHelmet.Red(), 0.95, 0.5, 0.5), 0.5);
        this.Boot(this.Words(g, "TRAUMA TEAM", 24, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.95, 3,
                             mid - 54.0, brow - 4.0, 0.0, 0.5), 0.55);
        this.Boot(this.Words(g, "INTERNATIONAL", 10, n"Semi-Bold", TraumaTeamHelmet.Green(), 0.9, 7,
                             mid - 53.0, brow + 13.0, 0.0, 0.5), 0.65);

        for s in [-1.0, 1.0] {
            let inner: Float = mid + s * 158.0;
            let outer: Float = mid + s * 400.0;
            let line: ref<inkRectangle> = this.Bar(g, MinF(inner, outer), brow, 242.0, 2.0,
                                                   TraumaTeamHelmet.Green(), 0.7, 0.0, 0.5);
            this.Grow(line, true, 0.2);
            let chip: ref<inkRectangle> = this.Bar(g, inner + s * 16.0, brow, 20.0, 5.0,
                                                   TraumaTeamHelmet.Red(), 0.95, 0.5, 0.5);
            chip.SetShear(new Vector2(-0.9 * s, 0.0));
            this.Boot(chip, 0.7);
            let i: Int32 = 0;
            while i < 9 {
                let tall: Float = i % 4 == 0 ? 8.0 : 4.0;
                this.Bar(g, outer - s * (18.0 + Cast<Float>(i) * 10.0), brow + 1.0, 2.0, tall,
                         TraumaTeamHelmet.Green(), 0.5, 0.5, 0.0);
                i += 1;
            }
            this.Boot(this.Ray(g, outer, brow, 24.0, s > 0.0 ? 130.0 : 50.0, 2.0, TraumaTeamHelmet.Green(), 0.7), 0.55);
        }
        this.Boot(this.Ray(g, mid - 6.0, brow + 26.0, 9.0, 35.0, 2.0, TraumaTeamHelmet.Green(), 0.6), 0.7);
        this.Boot(this.Ray(g, mid + 6.0, brow + 26.0, 9.0, 145.0, 2.0, TraumaTeamHelmet.Green(), 0.6), 0.7);

        let row: Float = brow + 28.0;
        let lx: Float = mid - 370.0;
        let lamp: ref<inkImage> = this.Picture(g, n"glow", lx, row, 30.0, 30.0, TraumaTeamHelmet.Red(), 0.9, 0.5, 0.5);
        this.Fade(lamp, 0.9, 0.1, 0.75, 0.0, true);
        let dot: ref<inkRectangle> = this.Bar(g, lx, row, 7.0, 7.0, TraumaTeamHelmet.Red(), 1.0, 0.5, 0.5);
        dot.SetRotation(45.0);
        this.Fade(dot, 1.0, 0.25, 0.75, 0.0, true);
        this.Boot(this.Words(g, "REC", 16, n"Semi-Bold", TraumaTeamHelmet.Red(), 1.0, 3, lx + 15.0, row, 0.0, 0.5), 0.8);
        this.Boot(this.Words(g, "LIVE", 16, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.9, 3, lx + 60.0, row, 0.0, 0.5), 0.85);
        this.Boot(this.Words(g, "//  TEAM FEED", 13, n"Medium", TraumaTeamHelmet.Green(), 0.8, 5,
                             lx + 104.0, row + 1.0, 0.0, 0.5), 0.9);

        let rx: Float = mid + 370.0;
        let b: Int32 = 0;
        while b < 4 {
            let bar: ref<inkRectangle> = this.Bar(g, rx - Cast<Float>(3 - b) * 5.0, row + 6.0, 3.0,
                                                  3.0 + Cast<Float>(b) * 3.0, TraumaTeamHelmet.Green(), 0.85, 0.5, 1.0);
            if b == 3 {
                this.Fade(bar, 0.85, 0.1, 0.4, 0.0, true);
            }
            b += 1;
        }
        this.m_clock = this.Words(g, "--:--", 16, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.9, 3, rx - 22.0, row, 1.0, 0.5);
        this.Boot(this.m_clock, 0.85);
        this.Boot(this.Words(g, "CH 07  //", 13, n"Medium", TraumaTeamHelmet.Green(), 0.8, 5,
                             rx - 82.0, row + 1.0, 1.0, 0.5), 0.9);

    }

    private func Corners(root: ref<inkCanvas>, k: Float) -> Void {
        let w: Float = 1300.0;
        let h: Float = 760.0;
        let g: ref<inkCanvas> = this.Group(root, inkEAnchor.Centered, new Vector2(0.5, 0.5),
                                           new inkMargin(0.0, 0.0, 0.0, 0.0), w, h, k);
        let i: Int32 = 0;
        while i < 4 {
            let right: Bool = i == 1 || i == 2;
            let low: Bool = i >= 2;
            let c: ref<inkImage> = this.Picture(g, n"corner", right ? w : 0.0, low ? h : 0.0, 64.0, 64.0,
                                                TraumaTeamHelmet.Green(), 0.3, right ? 1.0 : 0.0, low ? 1.0 : 0.0);
            c.SetRotation(Cast<Float>(i) * 90.0);
            this.Boot(c, 0.4 + Cast<Float>(i) * 0.05);
            i += 1;
        }
    }

    private func Side(root: ref<inkCanvas>, k: Float, left: Bool) -> Void {
        let s: Float = left ? 1.0 : -1.0;
        let g: ref<inkCanvas> = left
            ? this.Group(root, inkEAnchor.CenterLeft, new Vector2(0.0, 0.5), new inkMargin(64.0 * k, 0.0, 0.0, 0.0), 120.0, 560.0, k)
            : this.Group(root, inkEAnchor.CenterRight, new Vector2(1.0, 0.5), new inkMargin(0.0, 0.0, 64.0 * k, 0.0), 120.0, 560.0, k);
        let x: Float = left ? 30.0 : 90.0;
        let spine: ref<inkRectangle> = this.Bar(g, x, 280.0, 2.0, 400.0, TraumaTeamHelmet.Green(), 0.55, 0.5, 0.5);
        this.Grow(spine, false, 0.3);
        this.Boot(this.Ray(g, x, 80.0, 34.0, left ? 45.0 : 135.0, 2.0, TraumaTeamHelmet.Green(), 0.55), 0.6);
        this.Boot(this.Ray(g, x, 480.0, 34.0, left ? -45.0 : -135.0, 2.0, TraumaTeamHelmet.Green(), 0.55), 0.6);
        let i: Int32 = 0;
        while i < 21 {
            let long: Bool = i % 5 == 0;
            let w: Float = long ? 14.0 : 7.0;
            this.Bar(g, x + s * (4.0 + w / 2.0), 100.0 + Cast<Float>(i) * 18.0, w, 2.0, TraumaTeamHelmet.Green(),
                     long ? 0.55 : 0.3, 0.5, 0.5);
            i += 1;
        }
        let mark: ref<inkRectangle> = this.Bar(g, x + s * 13.0, 280.0, 20.0, 4.0, TraumaTeamHelmet.Red(), 0.95, 0.5, 0.5);
        this.Ride(mark, 0.0, 170.0, left ? 3.4 : 4.1, false);
        let label: ref<inkText> = this.Words(g, left ? "BIOMON  //  SYNC" : "RAPID  RESPONSE", 14, n"Medium",
                                             TraumaTeamHelmet.Green(), 0.55, 8, x - s * 16.0, 280.0, 0.5, 0.5);
        label.SetRotation(left ? -90.0 : 90.0);
        this.Boot(label, 0.9);
    }

    private func Footer(root: ref<inkCanvas>, k: Float) -> Void {
        let w: Float = 1240.0;
        let m: Float = w / 2.0;
        let g: ref<inkCanvas> = this.Group(root, inkEAnchor.BottomCenter, new Vector2(0.5, 1.0),
                                           new inkMargin(0.0, 0.0, 0.0, 14.0 * k), w, 60.0, k);
        this.Grow(this.Picture(g, n"fade", m, 50.0, 1100.0, 5.0, TraumaTeamHelmet.Green(), 0.6, 0.5, 0.5), true, 0.35);
        this.Bar(g, m, 50.0, 40.0, 3.0, TraumaTeamHelmet.Red(), 0.95, 0.5, 0.5);
        this.Boot(this.Words(g, "AV-04  //  PROBATIONARY CREW", 14, n"Semi-Bold", TraumaTeamHelmet.Green(), 0.7, 10,
                             m, 32.0, 0.5, 0.5), 1.0);
        for s in [-1.0, 1.0] {
            let cx: Float = m + s * 405.0;
            this.Boot(this.Picture(g, n"ecg", cx, 26.0, 220.0, 28.0, TraumaTeamHelmet.Green(), 0.6, 0.5, 0.5), 1.1);
            let spot: ref<inkImage> = this.Picture(g, n"glow", cx, 26.0, 22.0, 22.0, TraumaTeamHelmet.Pale(), 0.9, 0.5, 0.5);
            this.Ride(spot, 106.0, 0.0, 2.0, true);
        }
        this.m_rate = this.Words(g, "HR 072", 18, n"Semi-Bold", TraumaTeamHelmet.Pale(), 0.9, 4, m + 600.0, 26.0, 1.0, 0.5);
        this.Boot(this.m_rate, 1.1);
        this.Boot(this.Words(g, "BIOMON", 18, n"Semi-Bold", TraumaTeamHelmet.Red(), 0.95, 4, m - 600.0, 26.0, 0.0, 0.5), 1.1);
    }

    private func Group(root: ref<inkCanvas>, anchor: inkEAnchor, point: Vector2, margin: inkMargin,
                       w: Float, h: Float, k: Float) -> ref<inkCanvas> {
        let g: ref<inkCanvas> = new inkCanvas();
        g.SetAnchor(anchor);
        g.SetAnchorPoint(point);
        g.SetMargin(margin);
        g.SetSize(new Vector2(w, h));
        g.SetRenderTransformPivot(point);
        g.SetScale(new Vector2(k, k));
        g.Reparent(root);
        return g;
    }

    private func Place(w: ref<inkWidget>, x: Float, y: Float, width: Float, height: Float, px: Float, py: Float) -> Void {
        w.SetAnchor(inkEAnchor.TopLeft);
        w.SetAnchorPoint(new Vector2(px, py));
        w.SetMargin(new inkMargin(x, y, 0.0, 0.0));
        if width > 0.0 {
            w.SetSize(new Vector2(width, height));
        }
    }

    private func Bar(g: ref<inkCanvas>, x: Float, y: Float, w: Float, h: Float, color: HDRColor,
                     opacity: Float, px: Float, py: Float) -> ref<inkRectangle> {
        let r: ref<inkRectangle> = new inkRectangle();
        r.SetTintColor(color);
        r.SetOpacity(opacity);
        r.Reparent(g);
        this.Place(r, x, y, w, h, px, py);
        return r;
    }

    private func Ray(g: ref<inkCanvas>, x0: Float, y0: Float, len: Float, angle: Float, thick: Float,
                     color: HDRColor, opacity: Float) -> ref<inkRectangle> {
        let r: Float = Deg2Rad(angle);
        let b: ref<inkRectangle> = this.Bar(g, x0 + CosF(r) * len / 2.0, y0 + SinF(r) * len / 2.0, len, thick,
                                            color, opacity, 0.5, 0.5);
        b.SetRotation(angle);
        return b;
    }

    private func Picture(g: ref<inkCanvas>, part: CName, x: Float, y: Float, w: Float, h: Float,
                         color: HDRColor, opacity: Float, px: Float, py: Float) -> ref<inkImage> {
        let i: ref<inkImage> = new inkImage();
        i.SetAtlasResource(TraumaTeamHelmet.Atlas());
        i.SetTexturePart(part);
        i.SetTintColor(color);
        i.SetOpacity(opacity);
        i.Reparent(g);
        this.Place(i, x, y, w, h, px, py);
        return i;
    }

    private func Words(g: ref<inkCanvas>, s: String, size: Int32, style: CName, color: HDRColor,
                       opacity: Float, tracking: Int32, x: Float, y: Float, px: Float, py: Float) -> ref<inkText> {
        let t: ref<inkText> = new inkText();
        t.SetFontFamily(TraumaTeamHelmet.Font());
        t.SetFontStyle(style);
        t.SetFontSize(size);
        t.SetLetterCase(textLetterCase.UpperCase);
        t.SetTracking(tracking);
        t.SetTintColor(color);
        t.SetOpacity(opacity);
        t.SetText(s);
        t.Reparent(g);
        this.Place(t, x, y, 0.0, 0.0, px, py);
        return t;
    }

    private func Fade(w: ref<inkWidget>, from: Float, to: Float, time: Float, delay: Float, loop: Bool) -> Void {
        let def: ref<inkAnimDef> = new inkAnimDef();
        let a: ref<inkAnimTransparency> = new inkAnimTransparency();
        a.SetStartTransparency(from);
        a.SetEndTransparency(to);
        a.SetDuration(time);
        a.SetStartDelay(delay);
        a.SetType(inkanimInterpolationType.Linear);
        a.SetMode(inkanimInterpolationMode.EasyIn);
        def.AddInterpolator(a);
        if loop {
            w.PlayAnimationWithOptions(def, GetAnimOptionsInfiniteLoop(inkanimLoopType.PingPong));
        } else {
            w.PlayAnimation(def);
        }
    }

    private func Boot(w: ref<inkWidget>, delay: Float) -> Void {
        if this.m_quiet {
            return;
        }
        let full: Float = w.GetOpacity();
        w.SetOpacity(0.0);
        let def: ref<inkAnimDef> = new inkAnimDef();
        let steps: array<Float> = [0.0, full, full * 0.15, full];
        let i: Int32 = 1;
        while i < 4 {
            let a: ref<inkAnimTransparency> = new inkAnimTransparency();
            a.SetStartTransparency(steps[i - 1]);
            a.SetEndTransparency(steps[i]);
            a.SetDuration(0.04);
            a.SetStartDelay(delay + Cast<Float>(i - 1) * 0.06);
            def.AddInterpolator(a);
            i += 1;
        }
        w.PlayAnimation(def);
    }

    private func Grow(w: ref<inkWidget>, across: Bool, delay: Float) -> Void {
        if this.m_quiet {
            return;
        }
        let start: Vector2 = across ? new Vector2(0.0, 1.0) : new Vector2(1.0, 0.0);
        let def: ref<inkAnimDef> = new inkAnimDef();
        let a: ref<inkAnimScale> = new inkAnimScale();
        a.SetStartScale(start);
        a.SetEndScale(new Vector2(1.0, 1.0));
        a.SetDuration(0.5);
        a.SetStartDelay(delay);
        a.SetType(inkanimInterpolationType.Quintic);
        a.SetMode(inkanimInterpolationMode.EasyOut);
        def.AddInterpolator(a);
        w.SetScale(start);
        w.PlayAnimation(def);
    }

    private func Ride(w: ref<inkWidget>, dx: Float, dy: Float, time: Float, run: Bool) -> Void {
        let def: ref<inkAnimDef> = new inkAnimDef();
        let a: ref<inkAnimTranslation> = new inkAnimTranslation();
        a.SetStartTranslation(new Vector2(-dx, -dy));
        a.SetEndTranslation(new Vector2(dx, dy));
        a.SetDuration(time);
        a.SetType(run ? inkanimInterpolationType.Linear : inkanimInterpolationType.Sinusoidal);
        a.SetMode(inkanimInterpolationMode.EasyInOut);
        def.AddInterpolator(a);
        w.PlayAnimationWithOptions(def, GetAnimOptionsInfiniteLoop(run ? inkanimLoopType.Cycle : inkanimLoopType.PingPong));
    }
}
