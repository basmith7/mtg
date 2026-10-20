"""Light markdown <-> Quill delta (Archidekt descriptions and primers).

Supported: '## heading', '- bullet', '**bold**', plain paragraphs. [[Card Name]] passes through
and Archidekt renders it as a card link. from_delta keeps the text of anything else (colour, code,
links, ordered lists, other heading levels) and reports the formatting it dropped. Plain lines become
paragraphs, so a primer written on the site may gain blank lines on its first pull and push; our own
primers round-trip exactly.
"""
import json
import re


def to_delta(text):
    ops = []

    def inline(t):
        for i, part in enumerate(re.split(r'\*\*', t)):
            if part:
                ops.append({'insert': part, **({'attributes': {'bold': True}} if i % 2 else {})})

    for line in text.strip().split('\n'):
        if not line.strip():
            continue
        if line.startswith('## '):
            inline(line[3:])
            ops.append({'insert': '\n', 'attributes': {'header': 2}})
        elif line.startswith('- '):
            inline(line[2:])
            ops.append({'insert': '\n', 'attributes': {'list': 'bullet'}})
        else:
            inline(line)
            ops.append({'insert': '\n\n'})
    return json.dumps({'ops': ops})


def from_delta(delta):
    """(markdown, dropped): the inverse of to_delta. dropped is a sorted list of formatting names
    with no markdown here (their text is kept), e.g. ['color', 'list:ordered']."""
    dropped, lines, line = set(), [], []
    for op in json.loads(delta)['ops'] if delta else []:
        text, attrs = op.get('insert'), op.get('attributes') or {}
        if not isinstance(text, str):
            dropped.add('embed')
            continue
        *full, rest = text.split('\n')
        for part in full:  # each '\n' ends a line; its attributes format that line
            _inline(line, part, attrs, dropped)
            lines.append(_line(''.join(line), attrs, dropped))
            line = []
        _inline(line, rest, attrs, dropped)
    if line:
        lines.append(''.join(line))
    md = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()
    return md, sorted(dropped)


def _inline(line, text, attrs, dropped):
    if text:
        dropped.update(k for k in attrs if k not in ('bold', 'header', 'list'))
        line.append(f'**{text}**' if attrs.get('bold') else text)


def _line(text, attrs, dropped):
    dropped.update(k for k in attrs if k not in ('bold', 'header', 'list'))
    if attrs.get('header'):
        if attrs['header'] != 2:
            dropped.add(f"header:{attrs['header']}")
        return '## ' + text
    if attrs.get('list'):
        if attrs['list'] != 'bullet':
            dropped.add(f"list:{attrs['list']}")
        return '- ' + text
    return text
