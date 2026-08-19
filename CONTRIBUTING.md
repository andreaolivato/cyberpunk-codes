# Contributing

Pull requests are welcome, for the framework and for the gigs. This file is
what a PR needs to pass review here, on top of the usual GitHub flow.

## Say what your change targets

Two kinds of change land in this repo, and the review is different for each,
so name the target in the PR title:

| Prefix | Target | Files |
|---|---|---|
| `questkit:` | the framework, reusable by every gig | `tools/questkit/`, the build and deploy scripts, `shared/scripts/` |
| `gig-01:` | one mod | `tools/gig01/`, `mods/gig-01-negative-balance/` |
| `docs:` | documentation only | `docs/`, the root markdown files |

A change that touches both the framework and a gig is two PRs. The framework
half must work for a gig that is not this one; the gig half proves it.

## Edit the generators, never their output

Everything under `mods/*/source/wkit/raw/` is generated, except the
hand-authored `.archive.xl`. A change to the mod's content is a change to a
generator (or its tables), never to the JSON:

1. Edit the generator under `tools/`.
2. Run it: `python .\tools\gen_<name>.py`.
3. Commit the generator and its regenerated output together.

`git status` after regenerating is the check: it must show your intended
change and nothing else. A diff you cannot explain in the generated files
means the generator change did something you did not mean.

## Before submitting

```powershell
python .\tools\gig01\gen_journal.py; python .\tools\gig01\gen_localization.py
python .\tools\gig01\gen_scenes.py; python .\tools\gig01\gen_questphase.py
.\tools\check-scripts-repo.ps1 gig-01   # redscript compiles, nothing deployed
```

The toolchain is Windows-only; versions and setup are in
[`BUILDING.md`](BUILDING.md). The generators alone need nothing but Python.

## What not to touch

- **Dialogue and on-screen text, without the audio to match**: every spoken
  line has a voice take, and the pacing and lipsync are derived from it, so a
  reworded line without new audio ships with a voice saying the old words. A
  wording PR therefore must include a WAV per changed line, in the character's
  existing voice; the pipeline regenerates the `.wem`, the durations and the
  lipsync from it. Since the story is not under the MIT licence (see
  [`LICENSE`](LICENSE)) and wording is a design call, propose the new line in
  an issue first, before recording anything.
- **Numbering in `docs/gotchas.md` and `docs/backlog.md`**: code comments cite
  both by number. Append new entries; never renumber or delete.

## Bug reports

- The gig misbehaving in game: the
  [Nexus bugs tab](https://www.nexusmods.com/cyberpunk2077/mods/32694?tab=bugs).
- The framework, a generator, a script or a doc: a GitHub issue on this repo.

Everything here was established against game 2.31 on one machine. "This does
not work for me" is a contribution by itself; name your game version, load
order and what you ran.
