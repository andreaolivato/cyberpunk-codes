; Register-safe interception of MappinSystem::GetMappinData / GetPoiData.
;
; The game calls these with a non-standard convention that expects r8/r9 to
; survive (ArchiveXL saves them by hand inside its C++ detour). These stubs
; avoid the problem entirely:
;   * unknown hash  -> tail-jump to the original, every register untouched
;   * our hash      -> return our static cooked entry in rax, nothing clobbered
;
; Args (Win64): rcx = mappin system, edx = journal path hash.
; Table layout: 16 bytes per row { uint32 hash, pad, void* data }, hash 0 = end.

.data
extern g_questTable:QWORD
extern g_poiTable:QWORD
extern g_questOriginal:QWORD
extern g_poiOriginal:QWORD

.code
extern NB_LogHit:proc

GetMappinDataStub proc
        mov     rax, qword ptr [g_questTable]
        test    rax, rax
        je      QuestFallthrough
QuestLoop:
        cmp     dword ptr [rax], 0
        je      QuestFallthrough
        cmp     dword ptr [rax], edx
        je      QuestFound
        add     rax, 16
        jmp     QuestLoop
QuestFound:
        ; We return without calling the original, so clobbering is safe here.
        mov     r10, qword ptr [rax+8]
        sub     rsp, 38h
        mov     qword ptr [rsp+20h], r10
        mov     ecx, edx
        call    NB_LogHit
        mov     rax, qword ptr [rsp+20h]
        add     rsp, 38h
        ret
QuestFallthrough:
        jmp     qword ptr [g_questOriginal]
GetMappinDataStub endp

GetPoiDataStub proc
        mov     rax, qword ptr [g_poiTable]
        test    rax, rax
        je      PoiFallthrough
PoiLoop:
        cmp     dword ptr [rax], 0
        je      PoiFallthrough
        cmp     dword ptr [rax], edx
        je      PoiFound
        add     rax, 16
        jmp     PoiLoop
PoiFound:
        mov     r10, qword ptr [rax+8]
        sub     rsp, 38h
        mov     qword ptr [rsp+20h], r10
        mov     ecx, edx
        call    NB_LogHit
        mov     rax, qword ptr [rsp+20h]
        add     rsp, 38h
        ret
PoiFallthrough:
        jmp     qword ptr [g_poiOriginal]
GetPoiDataStub endp

end
