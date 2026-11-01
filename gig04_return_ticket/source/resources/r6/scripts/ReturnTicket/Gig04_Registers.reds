module CyberpunkCodes.Gig04
@if(ModuleExists("CyberpunkCodes.Fixer01"))
import CyberpunkCodes.Fixer01.*

@if(ModuleExists("CyberpunkCodes.Fixer01"))
public class Gig04Registers extends ScriptableTweak {
  protected cb func OnApply() -> Void {
    // her map icon
    Fixer01Gigs.Register(n"cc_g04");
  }
}
