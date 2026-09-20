module CyberpunkCodes.Gig01

public abstract class CCGig01Companions {

    @if(ModuleExists("DarkFuture.Main"))
    public static func DarkFuture() -> Bool { return true; }
    @if(!ModuleExists("DarkFuture.Main"))
    public static func DarkFuture() -> Bool { return false; }

    @if(ModuleExists("DarkFutureCore.Main"))
    public static func DarkFutureCore() -> Bool { return true; }
    @if(!ModuleExists("DarkFutureCore.Main"))
    public static func DarkFutureCore() -> Bool { return false; }

    @if(ModuleExists("MuchBetterAI.Core") || ModuleExists("MuchBetterAIConfig"))
    public static func MuchBetterAI() -> Bool { return true; }
    @if(!ModuleExists("MuchBetterAI.Core") && !ModuleExists("MuchBetterAIConfig"))
    public static func MuchBetterAI() -> Bool { return false; }

    private static func Note(qs: ref<QuestsSystem>, key: String, on: Bool) -> Int32 {
        let value: Int32 = on ? 1 : 0;
        if qs.GetFactStr("cc_g01_dbg_easy_" + key) != value {
            qs.SetFactStr("cc_g01_dbg_easy_" + key, value);
        }
        return value;
    }

    public static func Installed(qs: ref<QuestsSystem>) -> Int32 {
        let n: Int32 = 0;
        n += CCGig01Companions.Note(qs, "darkfuture", CCGig01Companions.DarkFuture());
        n += CCGig01Companions.Note(qs, "darkfuturecore", CCGig01Companions.DarkFutureCore());
        n += CCGig01Companions.Note(qs, "muchbetterai", CCGig01Companions.MuchBetterAI());
        return n;
    }

    public static func Publish(qs: ref<QuestsSystem>) -> Void {
        let n: Int32 = CCGig01Companions.Installed(qs);
        if qs.GetFactStr("cc_g01_dev_easy") > 0 && n == 0 {
            n = 1;
        }
        if qs.GetFactStr("cc_g01_easy") != n {
            qs.SetFactStr("cc_g01_easy", n);
        }
    }
}
