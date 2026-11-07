r"""Strip comments from redscript and YAML, and prove the code did not change.

    python tools\strip_comments.py strip <folder or file> ...
    python tools\strip_comments.py same <file a> <file b>

`strip` rewrites every .reds, .yaml and .xl file it finds in place: each comment
goes, and blank lines never run to more than one. It refuses, and changes
nothing more, if the code of a file would differ afterwards or a comment is left.
`build-release.ps1` runs it on the staged copy, so a release ships plain code
while the source keeps its comments.

`same` exits 0 when two files hold the same code once comments are set aside.
`build-release.ps1` uses it to compare the zip with the copy in the game folder.

Strings are kept whole: a `//` or `#` inside quotes is code.
"""
import os
import sys

BS = chr(92)
EXTS = ('.reds', '.yaml', '.yml', '.xl')


def split_reds(line, in_block):
    """(code, comment, in_block) for one line, keeping strings intact."""
    code, comment, i, quote = [], [], 0, False
    while i < len(line):
        c = line[i]
        two = line[i:i + 2]
        if in_block:
            if two == '*/':
                comment.append(two)
                i += 2
                in_block = False
                continue
            comment.append(c)
        elif quote:
            code.append(c)
            if c == BS and i + 1 < len(line):
                code.append(line[i + 1])
                i += 1
            elif c == '"':
                quote = False
        elif two == '//':
            comment.append(line[i:])
            break
        elif two == '/*':
            comment.append(two)
            i += 2
            in_block = True
            continue
        else:
            code.append(c)
            if c == '"':
                quote = True
        i += 1
    return ''.join(code), ''.join(comment), in_block


def split_yaml(line, in_block):
    """Same for YAML. A quote only opens at the start of a value."""
    quote, prev = None, ' '
    for i, c in enumerate(line):
        if quote:
            if c == quote:
                quote = None
        elif c in '"\'' and prev in ' :-[{,':
            quote = c
        elif c == '#' and prev in ' \t':
            return line[:i], line[i:], False
        prev = c
    return line, '', False


def splitter(name):
    return split_reds if name.endswith('.reds') else split_yaml


def parse(text, split):
    rows, state = [], False
    for raw in text.splitlines():
        code, comment, state = split(raw, state)
        rows.append((code, comment))
    return rows


def code_only(text, split):
    return [c.rstrip() for c, _ in parse(text, split) if c.strip()]


def clean(text, split):
    """Code only: every comment goes, and blank lines never run to more than one."""
    eol = chr(13) + chr(10) if chr(13) in text else chr(10)
    out = []
    for code, comment in parse(text, split):
        if comment and not code.strip():
            continue
        line = code.rstrip()
        if line or (out and out[-1]):
            out.append(line)
    while out and not out[-1]:
        out.pop()
    return eol.join(out) + eol


def read(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return f.read()


def strip_file(path):
    split = splitter(path)
    before = read(path)
    after = clean(before, split)
    if code_only(before, split) != code_only(after, split):
        sys.exit('REFUSED: stripping changed the code of ' + path)
    left = [c for _, c in parse(after, split) if c]
    if left:
        sys.exit('REFUSED: a comment is left in %s: %s' % (path, left[0][:90]))
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(after)
    return before.count('\n') - after.count('\n')


def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for d, _, fs in os.walk(p):
            for f in sorted(fs):
                if f.endswith(EXTS):
                    yield os.path.join(d, f)


def main(argv):
    if len(argv) >= 2 and argv[0] == 'strip':
        n = lines = 0
        for path in files(argv[1:]):
            lines += strip_file(path)
            n += 1
        print('stripped %d file(s), %d comment or blank line(s) removed' % (n, lines))
        return 0
    if len(argv) == 3 and argv[0] == 'same':
        split = splitter(argv[1])
        return 0 if code_only(read(argv[1]), split) == code_only(read(argv[2]), split) else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
