# Only if you record Nisha and Brekke in your language

This voice map points each of the lines at a clip you supply. Put the
clips (`.wem`) under `source\archive\mod\trauma_team_translation\vo\` in
the project, named as the map says (`gig05_brief__l01.wem` and so on). Copy this
`vomap.json.json` next to `strings.json.json` under `raw`, right-click
`raw` and "Convert from JSON", and uncomment the `vomaps:` lines in the
manifest. Do that last, once every clip is in place: a voice map
registered without its clips leaves those lines silent in your
language. Left out, the English recordings play under your subtitles.
