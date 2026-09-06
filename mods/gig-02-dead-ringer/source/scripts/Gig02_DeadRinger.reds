// Gig 02, Dead Ringer: the gig's five places, and the radius each one uses.
//
// EVERY COORDINATE HERE IS A BASE-GAME NODE'S OWN POSITION, read out of the
// three always-loaded streaming sectors and kept in step with
// tools/gig02/gig02_config.py, which is where the same numbers become map-pin
// anchors. Nothing here was captured by standing on a spot in game, because
// nobody could: see that file, and the gig's design.md, for what that costs and
// what a capture pass would replace.
//
// The consequence for this file is that a radius has to be generous. A captured
// coordinate is where the player will actually stand; a marker's coordinate is
// somewhere in the right room, so the test has to allow for the difference.
//
// THE Z BAND IS ASYMMETRIC ON PURPOSE, and it is not fussiness. Night City has
// roads tunnelling under buildings, so a trigger whose floor reaches far enough
// down fires for a player driving past underneath. `CCSharedWorld.Near` takes
// `below` and `above` separately for exactly that: keep `below` tight and let
// `above` be generous.

module CyberpunkCodes.Gig02

public abstract class CCGig02Places {

    // LOCATION 1: the top of the stairs outside Afterlife, Watson, which is the
    // base game's own Afterlife entrance mappin. Comic pp. 10-35.
    public static func Afterlife() -> Vector4 {
        return new Vector4(-1465.155029, 1046.971069, 22.759001, 1.0);
    }

    // THE THREE GROUPS OUTSIDE AFTERLIFE. There are always three knots of
    // people standing there, and each one is a place to walk to and something
    // to overhear. The man talking in the third is the merc.
    //
    // KEEP THESE IN STEP WITH tools/gig02/gig02_config.py's GROUP_POS, which
    // is where the same numbers become map pins. A disagreement is a pin on one
    // spot and a trigger on another, which reads as a marker that does nothing.
    //
    // ALL THREE MUST BE OUTSIDE THE CLUB'S SAFE AREA. Inside one the player
    // cannot draw a weapon, so the merc cannot be fought and the leg cannot be
    // finished. Gig02_Encounter asks the game directly rather than assuming,
    // through SafeAreaManager, and reports the answer to the dev menu.
    //
    // CAPTURED IN GAME 2026-08-26, all three, by standing with each group.
    public static func Group1() -> Vector4 {
        return new Vector4(-1467.443115, 1052.567993, 22.708999, 1.0);
    }

    public static func Group2() -> Vector4 {
        return new Vector4(-1470.627991, 1050.988037, 22.722000, 1.0);
    }

    public static func Group3() -> Vector4 {
        return new Vector4(-1470.163086, 1044.158936, 22.722000, 1.0);
    }

    // HOW CLOSE COUNTS AS STANDING WITH A GROUP.
    //
    // GROUPS 1 AND 2 ARE 3.6 M APART, so no radius can separate them on its
    // own: anything wide enough to be reachable while walking covers both, and
    // anything narrow enough to cover one is missed by a player who does not
    // stop on the exact metre. Gig02_Encounter picks the NEARER group instead,
    // and this number only decides how close counts as "standing with them".
    public static func GroupRadius() -> Float { return 3.0; }

    // LOCATION 2: the netrunner, on the upper walkway in KABUKI, WATSON.
    // Comic pp. 41-54.
    //
    // THE ONLY CAPTURED POSITION IN THIS FILE. Walked to and recorded in game
    // 2026-08-26, so unlike every other spot here it is where the player
    // actually stands rather than where a base-game marker happens to sit. The
    // radius that reads it can therefore be tight.
    //
    // It replaces an Arroyo guess that came from the voice corpus, which
    // answers where a name is SPOKEN and not where a scene is SET. See
    // gig02_config.py.
    public static func Inn() -> Vector4 {
        return new Vector4(-1179.864014, 2037.655029, 20.087000, 1.0);
    }

    // CHAR'S CHAIR, 9 m in from Yoko. CAPTURED IN GAME 2026-08-26: the position
    // is where the PLAYER stands beside it, which is what the pin points at.
    //
    // She used to be a voice with no location at all, and the verdict played
    // wherever V happened to be standing after a wait. Playtest, 2026-08-26:
    // "who's Char? She's not there and I have no interactions." The walk to
    // the chair is what makes her somewhere rather than nowhere.
    public static func Char() -> Vector4 {
        return new Vector4(-1183.542114, 2045.510010, 20.487000, 1.0);
    }

    // LOCATION 3: the pachinko parlor floor, Japantown. Comic pp. 56-68.
    public static func Parlor() -> Vector4 {
        return new Vector4(-657.332031, 826.690979, 19.521999, 1.0);
    }

    // THE HIT AREA IS NOT HERE. Its corners are generated into
    // Gig02_Area.reds by tools/gig02/hit_area.py, which is also what writes
    // the outline of the trigger area node the minimap draws, so the two
    // cannot drift. `CCGig02Area.X()` and `CCGig02Area.Y()`.

    // The box on the parlor's south wall. THE GENERATOR IS THE AUTHORITY:
    // `AP_POS` in tools/gig02/gen_sector.py is what the node actually ships at,
    // and this is a copy of it. It drifted 0.25 m when the box was nudged west
    // out of the wall's edge on 2026-09-05 and the copy was not followed;
    // corrected 2026-09-06. Only ever read as a centre to measure from, so the
    // drift was invisible.
    public static func AccessPoint() -> Vector4 {
        return new Vector4(-663.50, 822.33, 20.90, 1.0);
    }

    // The parlor counter, where Ideka is. CAPTURED IN GAME 2026-08-26, standing
    // in front of her.
    //
    // THIS IS WHY THE GIG STALLED AT THE ATTENDANT. The spot here was a guess
    // off a base-game marker and it is 21 m from where she actually stands, so
    // the trigger could never fire however long the player waited at the
    // counter, and a wait that cannot end looks exactly like a broken quest.
    //
    // She is only 4 m from the relay cabinet, so the walk is a step rather than
    // a journey and the radius is tight to make it at least that.
    public static func Counter() -> Vector4 {
        return new Vector4(-662.989014, 827.049988, 19.521999, 1.0);
    }

    // LOCATION 4: Wakako's office. `#wakako_sm_okada_default` is the spot the
    // real Wakako Okada stands on when nothing else is going on, so it is her
    // office by definition. Comic pp. 69-72.
    public static func Office() -> Vector4 {
        return new Vector4(-671.492004, 822.323975, 19.598000, 1.0);
    }

    // LOCATION 5: A JAPANTOWN STAIRCASE. Comic pp. 74-92, and the one site in
    // this gig that was in completely the wrong place.
    //
    // It was a street data terminal 900 m south, picked off the files for the
    // empty space around it. The comic stages this beat on a staircase V
    // descends before jumping down onto a trash pile, and playtesting said so.
    // All nine positions below were walked and captured in game 2026-08-26.
    //
    // The staircase falls 19 m over 85 m. THE TRASH IS 8 M BELOW ITS MIDDLE and
    // about 2.5 m above the ground at the bottom, so dropping onto it is a way
    // past the men holding the lower steps rather than a shortcut for its own
    // sake.
    //
    // KEEP IN STEP WITH tools/gig02/gig02_config.py's STAIR and TRASH.

    // The top of the stairs, where V arrives and where the pin sits.
    public static func HitSite() -> Vector4 {
        return new Vector4(-399.587006, 1318.163086, 42.167000, 1.0);
    }

    // The trash pile, and the only place in the gig the player is asked to
    // jump. The radius that reads it is generous in Z because a player who
    // lands on it and rolls off is still someone who made the jump.
    public static func Trash() -> Vector4 {
        return new Vector4(-391.115997, 1284.479004, 25.910000, 1.0);
    }

    // Where Toji waits: the bottom step.
    public static func TojiPost() -> Vector4 {
        return new Vector4(-381.087006, 1233.990112, 23.428000, 1.0);
    }

    // THE FIVE POSTS THE CLAWS HOLD, down the staircase between V and Toji.
    // Indexed rather than named one function each: the caller walks them.
    public static func ClawPost(i: Int32) -> Vector4 {
        switch i {
            case 0: return new Vector4(-395.667004, 1302.593994, 41.464001, 1.0);
            case 1: return new Vector4(-393.149004, 1290.089111, 37.449001, 1.0);
            case 2: return new Vector4(-381.960999, 1262.020996, 29.458000, 1.0);
            case 3: return new Vector4(-382.123993, 1254.921021, 27.458000, 1.0);
            case 4: return new Vector4(-385.081993, 1242.322998, 23.428000, 1.0);
        }
        return new Vector4(-395.667004, 1302.593994, 41.464001, 1.0);
    }

    // WHICH WAY EACH ONE FACES: back up the stairs, at whoever is coming down.
    // The captured yaw is the direction the player was looking while walking
    // DOWN, so a guard watching the way in is that plus 180.
    public static func ClawYaw(i: Int32) -> Float {
        switch i {
            case 0: return 13.4;
            case 1: return 37.6;
            case 2: return 11.9;
            case 3: return -6.6;
            case 4: return 20.0;
        }
        return 0.0;
    }

    public static func ClawPosts() -> Int32 { return 5; }
}

// The fact names, in one place, so a typo is a compile error rather than a
// wait that never ends.
//
// A FACT NAMED HERE AND NOWHERE ELSE IS A FACT NOTHING SETS, which reads
// exactly like a fact nothing waits on. The quest phase's header lists which
// side owns each one and this file does not repeat it.
public abstract class CCGig02Facts {
    public static func Start() -> CName { return n"cc_g02_start"; }
    public static func Accepted() -> CName { return n"cc_g02_accepted"; }
    public static func Done() -> CName { return n"cc_g02_done"; }
    public static func Paid() -> CName { return n"cc_g02_paid"; }
}
