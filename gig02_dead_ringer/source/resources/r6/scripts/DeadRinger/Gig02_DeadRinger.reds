module CyberpunkCodes.Gig02

public abstract class CCGig02Places {

    public static func Afterlife() -> Vector4 {
        return new Vector4(-1465.155029, 1046.971069, 22.759001, 1.0);
    }

    public static func Group1() -> Vector4 {
        return new Vector4(-1467.443115, 1052.567993, 22.708999, 1.0);
    }

    // 3.6m from group 1
    public static func Group2() -> Vector4 {
        return new Vector4(-1470.627991, 1050.988037, 22.722000, 1.0);
    }

    // the merc's
    public static func Group3() -> Vector4 {
        return new Vector4(-1470.163086, 1044.158936, 22.722000, 1.0);
    }

    public static func GroupRadius() -> Float { return 3.0; }

    // dewdrop, kabuki
    public static func Inn() -> Vector4 {
        return new Vector4(-1179.864014, 2037.655029, 20.087000, 1.0);
    }

    public static func Char() -> Vector4 {
        return new Vector4(-1183.542114, 2045.510010, 20.487000, 1.0);
    }

    // railing
    public static func LeanPose() -> Vector4 {
        return new Vector4(-1177.941000, 2033.495000, 20.078000, 1.0);
    }

    // chair by the parlor door
    public static func SitPose() -> Vector4 {
        return new Vector4(-653.355000, 828.668000, 19.350000, 1.0);
    }

    public static func Parlor() -> Vector4 {
        return new Vector4(-657.332031, 826.690979, 19.521999, 1.0);
    }

    public static func AccessPoint() -> Vector4 {
        return new Vector4(-663.50, 822.33, 20.90, 1.0);
    }

    // ideka
    public static func Counter() -> Vector4 {
        return new Vector4(-662.989014, 827.049988, 19.521999, 1.0);
    }

    public static func Office() -> Vector4 {
        return new Vector4(-671.492004, 822.323975, 19.598000, 1.0);
    }

    public static func HitSite() -> Vector4 {
        return new Vector4(-399.587006, 1318.163086, 42.167000, 1.0);
    }

    public static func Trash() -> Vector4 {
        return new Vector4(-391.115997, 1284.479004, 25.910000, 1.0);
    }

    // bottom step
    public static func TojiPost() -> Vector4 {
        return new Vector4(-381.087006, 1233.990112, 23.428000, 1.0);
    }

    // top to bottom
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

    // facing up the stairs
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

public abstract class CCGig02Facts {
    public static func Start() -> CName { return n"cc_g02_start"; }
    public static func Accepted() -> CName { return n"cc_g02_accepted"; }
    public static func Done() -> CName { return n"cc_g02_done"; }
    public static func Paid() -> CName { return n"cc_g02_paid"; }
}
