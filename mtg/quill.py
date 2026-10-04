"""Light markdown -> Quill delta (Archidekt descriptions and primers).

Supported: '## heading', '- bullet', '**bold**', plain paragraphs. [[Card Name]] passes through
and Archidekt renders it as a card link.
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
