r"""Which gig a tool is being run for, resolved once.

`--gig 02` on any tool that serves more than one gig. The number picks the
gig's own directory under `tools\` and its config module
(`gig02_config.py`), which is where `docs/conventions.md` says a gig's paths
and prefixes live.

READ BEFORE argparse, not by it. A tool that imports one of the gig's
generators at module level needs the number before the import runs, so the
flag is picked out of `sys.argv` by hand and argparse declares it again only
so that `--help` shows it (2026-09-06).
"""
import importlib
import os
import sys

GIGS = ('01', '02', '03', '04')
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def from_argv(default='01', argv=None):
    """The `--gig` value, or `default`. Accepts `--gig 02` and `--gig=02`."""
    argv = sys.argv if argv is None else argv
    gig = default
    for i, a in enumerate(argv):
        if a == '--gig' and i + 1 < len(argv):
            gig = argv[i + 1]
        elif a.startswith('--gig='):
            gig = a.split('=', 1)[1]
    if gig not in GIGS:
        raise SystemExit('--gig takes %s, not %r'
                         % (', '.join(GIGS), gig))
    return gig


def config(gig):
    """That gig's config module, with its own directory on the path."""
    d = os.path.join(TOOLS, 'gig' + gig)
    if d not in sys.path:
        sys.path.insert(0, d)
    return importlib.import_module('gig%s_config' % gig)


def add_argument(parser, default='01'):
    """Declare `--gig` so --help shows it; from_argv is what reads it."""
    parser.add_argument('--gig', default=default, choices=list(GIGS),
                        help='which gig to check (default %s)' % default)
