"""The CR2W envelope every generated resource shares.

WolvenKit reads and writes its JSON with a header naming the versions it was
produced against. The values were stated in ten places across the generators and
this toolkit, which is nine too many: they move together, every time WolvenKit or
the game is updated.

Bump WOLVENKIT to match the WolvenKit that will import the JSON, and GAME to the
game build the archive targets.
"""

WOLVENKIT = '8.20.0'
WKIT_JSON = '0.0.9'
GAME = 2310


def header(archive_file_name):
    """The Header block, named after the resource it will be imported as.

    `archive_file_name` is the file's own name, not a depot path: WolvenKit
    takes the folder from where the JSON sits in the raw tree.
    """
    return {
        'WolvenKitVersion': WOLVENKIT,
        'WKitJsonVersion': WKIT_JSON,
        'GameVersion': GAME,
        'DataType': 'CR2W',
        'ArchiveFileName': archive_file_name,
    }
