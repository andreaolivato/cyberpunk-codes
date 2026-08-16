# WITHDRAWN: there was no ArchiveXL bug

This file used to hold a draft GitHub issue for psiberx/cp2077-archive-xl
claiming that journal-merged quest mappins never resolve on game 2.31.

**Do not post it. The claim was wrong.** ArchiveXL works correctly.

What actually happened: our map-pin journal entries were never activated. A
`gameJournalQuestMapPin` is a journal entry with its own state, and the engine
does not create a mappin, or query the mappin system at all, while that entry
is Inactive. Activating the quest, the phase and the objective is not enough.
Because nothing downstream was ever asked for a position, every layer beneath
looked broken in turn: ArchiveXL's hooks appeared dead, the cooked tables looked
inert, and even the reference mods (Californication, One More Light) showed no
pins when their objectives were force-activated out of context.

Once the quest phase activated the pin entries, native pins, journal distance,
tracking and GPS routing all worked. With ArchiveXL entirely unmodified.

The working recipe is in `docs/map-pins-playbook.md`. The investigation, and the
dead ends it produced (offset injection, RED4ext plugin, cooked-file overrides of
the base-game copy, scripted mappin workarounds), are recorded in
`docs/architecture.md` under "Map pins".

Kept as a caution: several confident, well-evidenced conclusions were drawn from
measurements taken while a precondition was missing. When a whole stack looks
broken, suspect the first link before rewriting the rest.
