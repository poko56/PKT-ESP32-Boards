"""Minimal S-expression reader/writer for KiCad files."""
import re
TOK = re.compile(r'\s*("(?:[^"\\]|\\.)*"|[()]|[^\s()"]+)')

class Q(str):
    """A token that was quoted in the source."""

def parse(text):
    stack, cur, pos = [], [], 0
    n = len(text)
    while pos < n:
        m = TOK.match(text, pos)
        if not m:
            break
        pos = m.end()
        t = m.group(1)
        if t == '(':
            stack.append(cur); cur = []
        elif t == ')':
            p = stack.pop(); p.append(cur); cur = p
        elif t[0] == '"':
            cur.append(Q(t[1:-1].replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')))
        else:
            cur.append(t)
    return cur[0]

def dump(x, ind=0):
    if isinstance(x, list):
        pad = '\t' * ind
        if not any(isinstance(i, list) for i in x):
            return pad + '(' + ' '.join(atom(i) for i in x) + ')'
        head = [i for i in x if not isinstance(i, list)]
        rest = [i for i in x if isinstance(i, list)]
        s = pad + '(' + ' '.join(atom(i) for i in head)
        return s + '\n' + '\n'.join(dump(i, ind + 1) for i in rest) + '\n' + pad + ')'
    return atom(x)

def atom(i):
    if isinstance(i, Q):
        return '"' + i.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    return str(i)

def find(x, key):
    return [i for i in x if isinstance(i, list) and i and i[0] == key]

def first(x, key):
    r = find(x, key)
    return r[0] if r else None
