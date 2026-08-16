// NegativeBalanceMappins v1.0, native map pins for mod-added journal quests.
//
// Background (game 2.31): journal entries merged by ArchiveXL never receive map
// pins, GPS routes or journal distances, for ANY quest mod, including the
// reference ones. Investigation established why:
//   * The system object is genuinely gamemappinsMappinSystem (verified by RTTI),
//     but the cooked mappin resources ArchiveXL writes into (offsets 0x58/0x68)
//     are not retained there on 2.31: a full 99 KB scan of the object finds no
//     cooked table at all. The engine ingests the resource at load and keeps its
//     own structure, so appending to "the resource" is a silent no-op.
//   * Growing an unpopulated RED4ext DynArray is fatal: its allocator lives
//     after the entries buffer, so an empty array yields a garbage allocator.
//     That caused the crashes seen while testing the injection approach.
//
// Therefore this plugin does not inject data anywhere. It answers the engine's
// own lookups for our journal hashes with statically allocated cooked entries.
// The interception is done by assembly stubs (Hook.asm): unknown hashes tail-
// jump to the original with every register untouched, ours return a pointer in
// rax. This sidesteps the r8/r9 convention that forces ArchiveXL to save those
// registers manually inside its C++ detour.

#include <cstdint>
#include <windows.h>

#include <RED4ext/RED4ext.hpp>
#include <RED4ext/Relocation.hpp>
#include <RED4ext/Scripting/Natives/Generated/Vector3.hpp>
#include <RED4ext/Scripting/Natives/Generated/game/CookedMappinData.hpp>
#include <RED4ext/Scripting/Natives/Generated/game/CookedPointOfInterestMappinData.hpp>
#include <RED4ext/Scripting/Natives/Generated/game/mappins/IMappinVolume.hpp>

// AddressLib hashes (game 2.31, via ArchiveXL v1.27.1)
constexpr uint32_t kGetMappinDataHash = 3299551353;
constexpr uint32_t kGetPoiDataHash = 620961393;

// --- Gig 01 "Negative Balance" pins (see docs/architecture.md) --------------
struct PinDef
{
    uint32_t hash;
    float x, y, z;
};

constexpr PinDef kQuestPins[] = {
    {1684563311u, -177.761f, -1472.829f, 7.477f},  // .../obj_office/pin_office
    {3541212944u, -1259.598f, -989.166f, 12.037f}, // .../obj_epilogue/pin_coyote
};
constexpr PinDef kPoiPins[] = {
    {2166634032u, -177.761f, -1472.829f, 7.477f}, // points_of_interest/street_stories/...
};
// ----------------------------------------------------------------------------

// Lookup rows shared with the assembly stubs: { hash, pad, data pointer }.
struct LookupRow
{
    uint32_t hash;
    uint32_t pad;
    void* data;
};

namespace
{
RED4ext::game::CookedMappinData s_questData[sizeof(kQuestPins) / sizeof(PinDef)]{};
RED4ext::game::CookedPointOfInterestMappinData s_poiData[sizeof(kPoiPins) / sizeof(PinDef)]{};

LookupRow s_questRows[sizeof(kQuestPins) / sizeof(PinDef) + 1]{};
LookupRow s_poiRows[sizeof(kPoiPins) / sizeof(PinDef) + 1]{};

const RED4ext::v1::Sdk* s_sdk = nullptr;
RED4ext::v1::PluginHandle s_handle = nullptr;
} // namespace

// Consumed by Hook.asm.
extern "C"
{
void* g_questTable = nullptr;
void* g_poiTable = nullptr;
void* g_questOriginal = nullptr;
void* g_poiOriginal = nullptr;

void* GetMappinDataStub();
void* GetPoiDataStub();

// Called from Hook.asm when the engine asks about one of our hashes.
void NB_LogHit(uint32_t aHash);
}

extern "C" void NB_LogHit(uint32_t aHash)
{
    static int budget = 30;
    if (budget-- > 0 && s_sdk && s_sdk->logger)
    {
        s_sdk->logger->InfoF(s_handle, "[SERVED] engine asked for our hash %u", aHash);
    }
}

namespace
{
void BuildTables()
{
    for (size_t i = 0; i < sizeof(kQuestPins) / sizeof(PinDef); ++i)
    {
        s_questData[i].journalPathHash = kQuestPins[i].hash;
        s_questData[i].position.X = kQuestPins[i].x;
        s_questData[i].position.Y = kQuestPins[i].y;
        s_questData[i].position.Z = kQuestPins[i].z;

        s_questRows[i].hash = kQuestPins[i].hash;
        s_questRows[i].data = &s_questData[i];
    }
    for (size_t i = 0; i < sizeof(kPoiPins) / sizeof(PinDef); ++i)
    {
        s_poiData[i].journalPathHash = kPoiPins[i].hash;
        s_poiData[i].position.X = kPoiPins[i].x;
        s_poiData[i].position.Y = kPoiPins[i].y;
        s_poiData[i].position.Z = kPoiPins[i].z;

        s_poiRows[i].hash = kPoiPins[i].hash;
        s_poiRows[i].data = &s_poiData[i];
    }
    // Terminator rows stay zeroed.
    g_questTable = s_questRows;
    g_poiTable = s_poiRows;
}
} // namespace

RED4EXT_C_EXPORT void RED4EXT_CALL Query(RED4ext::v1::PluginInfo* aInfo)
{
    aInfo->name = L"NegativeBalanceMappins";
    aInfo->author = L"Cyberpunk.Codes";
    aInfo->version = RED4EXT_V1_SEMVER(1, 0, 0);
    aInfo->runtime = RED4EXT_V1_RUNTIME_VERSION_2_31;
    aInfo->sdk = RED4EXT_V1_SDK_VERSION_CURRENT;
}

RED4EXT_C_EXPORT uint32_t RED4EXT_CALL Supports()
{
    return RED4EXT_API_VERSION_1;
}

RED4EXT_C_EXPORT bool RED4EXT_CALL Main(RED4ext::v1::PluginHandle aHandle, RED4ext::v1::EMainReason aReason,
                                        const RED4ext::v1::Sdk* aSdk)
{
    switch (aReason)
    {
    case RED4ext::v1::EMainReason::Load:
    {
        s_handle = aHandle;
        s_sdk = aSdk;
        BuildTables();

        RED4ext::UniversalRelocFunc<void* (*)()> mappinTarget(kGetMappinDataHash);
        RED4ext::UniversalRelocFunc<void* (*)()> poiTarget(kGetPoiDataHash);

        const bool a = aSdk->hooking->Attach(aHandle, reinterpret_cast<void*>(static_cast<void* (*)()>(mappinTarget)),
                                             reinterpret_cast<void*>(&GetMappinDataStub), &g_questOriginal);
        const bool b = aSdk->hooking->Attach(aHandle, reinterpret_cast<void*>(static_cast<void* (*)()>(poiTarget)),
                                             reinterpret_cast<void*>(&GetPoiDataStub), &g_poiOriginal);

        aSdk->logger->InfoF(aHandle, "v1.0 attached (quest hook=%s, poi hook=%s, %u quest pins, %u poi pins)",
                            a ? "ok" : "FAILED", b ? "ok" : "FAILED",
                            static_cast<unsigned>(sizeof(kQuestPins) / sizeof(PinDef)),
                            static_cast<unsigned>(sizeof(kPoiPins) / sizeof(PinDef)));
        break;
    }
    case RED4ext::v1::EMainReason::Unload:
    {
        RED4ext::UniversalRelocFunc<void* (*)()> mappinTarget(kGetMappinDataHash);
        RED4ext::UniversalRelocFunc<void* (*)()> poiTarget(kGetPoiDataHash);
        aSdk->hooking->Detach(aHandle, reinterpret_cast<void*>(static_cast<void* (*)()>(mappinTarget)));
        aSdk->hooking->Detach(aHandle, reinterpret_cast<void*>(static_cast<void* (*)()>(poiTarget)));
        break;
    }
    }
    return true;
}
