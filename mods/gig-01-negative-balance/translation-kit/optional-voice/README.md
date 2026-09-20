# Only if you record Elena and Hoshino in your language

This voice map points each of their lines at a clip you supply. Put the
clips (`.wem`) under `source\archive\mod\negative_balance_translation\vo\` in
the project, named as the map says (`gig01_elena_call__e01.wem` and so on). Copy this
`vomap.json.json` next to `strings.json.json` under `raw`, right-click
`raw` and "Convert from JSON", and uncomment the `vomaps:` lines in the
manifest. Do that last, once every clip is in place: a voice map
registered without its clips leaves those lines silent in your
language. Left out, the English recordings play under your subtitles.
