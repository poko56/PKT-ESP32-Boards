"""Generate the KiCad project + schematic from design.py."""
import copy, json, os, sys, uuid
sys.path.insert(0, os.path.dirname(__file__))
from sexpr import parse, dump, find, first, Q
from design import *

LIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/'
OUT = os.path.join(os.path.dirname(__file__), '..')
ROOT = str(uuid.uuid5(uuid.NAMESPACE_DNS, NAME))
_n = [0]


def uid():
    _n[0] += 1
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, 'item%d' % _n[0]))


libs = {}


def load(lib, name):
    """Return a self-contained symbol, with `extends` flattened."""
    if lib not in libs:
        libs[lib] = {s[1]: s for s in find(parse(open(LIB + lib + '.kicad_sym').read()), 'symbol')}
    s = libs[lib][name]
    e = first(s, 'extends')
    if not e:
        s = copy.deepcopy(s)
    else:
        base = copy.deepcopy(libs[lib][e[1]])
        props = {p[1]: p for p in find(s, 'property')}
        out = []
        for it in base:
            if isinstance(it, list) and it[0] == 'property' and it[1] in props:
                out.append(copy.deepcopy(props.pop(it[1])))
            elif isinstance(it, list) and it[0] == 'symbol':
                it[1] = Q(it[1].replace(e[1], name, 1))
                out.append(it)
            else:
                out.append(it)
        s = out + [copy.deepcopy(v) for v in props.values()]
        names = [i for i in s if isinstance(i, list) and i[0] == 'symbol']
        s = [i for i in s if not (isinstance(i, list) and i[0] == 'symbol')] + names
    s[1] = Q(lib + ':' + name)
    return s


def pins(sym):
    r = []
    for u in find(sym, 'symbol'):
        for p in find(u, 'pin'):
            r.append((first(p, 'number')[1], first(p, 'at')))
    return r


def f(v):
    return '%g' % round(v, 4)


def prop(k, v, x, y, hide=False):
    p = ['property', Q(k), Q(v), ['at', f(x), f(y), '0'],
         ['effects', ['font', ['size', '1.27', '1.27']]] + ([['hide', 'yes']] if hide else [])]
    return p


def inst(ref):
    return ['instances', ['project', Q(NAME), ['path', Q('/' + ROOT), ['reference', Q(ref)], ['unit', '1']]]]


def placed(lib_id, ref, val, fp, x, y, pinnums, extra=()):
    s = ['symbol', ['lib_id', Q(lib_id)], ['at', f(x), f(y), '0'], ['unit', '1'],
         ['in_bom', 'no' if ref[0] == '#' else 'yes'], ['on_board', 'no' if ref[0] == '#' else 'yes'],
         ['dnp', 'no'], ['uuid', Q(uid())],
         prop('Reference', ref, x + 2, y - 2.5, ref[0] == '#'), prop('Value', val, x + 2, y + 2.5, ref[0] == '#'),
         prop('Footprint', fp, x, y, True), prop('Datasheet', '', x, y, True), prop('Description', '', x, y, True)]
    s += list(extra)
    for n in pinnums:
        s.append(['pin', Q(n), ['uuid', Q(uid())]])
    s.append(inst(ref))
    return s


items, used, pwr = [], {}, [0]


def snap(v):
    return round(v / 1.27) * 1.27


def need(lib, name):
    used.setdefault(lib + ':' + name, load(lib, name))
    return used[lib + ':' + name]


def power(net, x, y):
    pwr[0] += 1
    items.append(placed('power:' + net, '#PWR%03d' % pwr[0], net, '', x, y, ['1']))
    need('power', net)


def label(net, x, y, ang):
    just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
    items.append(['label', Q(net), ['at', f(x), f(y), str(ang)],
                  ['effects', ['font', ['size', '1.27', '1.27']], ['justify', just, 'bottom']],
                  ['uuid', Q(uid())]])


# Shelf layout: parts in design order, so functional blocks stay together on the sheet.
cx, cy, shelf = 30.0, 45.0, 0.0
for ref, (lib, name, val, fp, netmap, _, mpn) in PARTS.items():
    sym = need(lib, name)
    ps = pins(sym)
    xs = [float(a[1]) for _, a in ps] or [0]
    ys = [float(a[2]) for _, a in ps] or [0]
    w, h = max(xs) - min(xs) + 38, max(ys) - min(ys) + 18
    if cx + w > 560:
        cx, cy, shelf = 30.0, cy + shelf, 0.0
    x, y = snap(cx - min(xs) + 16), snap(cy + max(ys) + 7)
    cx += w
    shelf = max(shelf, h)
    items.append(placed(lib + ':' + name, ref, val, fp, x, y, [p[0] for p in ps], [prop('MPN', mpn, x, y, True)]))
    for num, at in ps:
        px, py = x + float(at[1]), y - float(at[2])
        out = (int(float(at[3])) + 180) % 360
        net = netmap.get(num)
        if net in ('GND', '+3V3', '+5V'):
            power(net, px, py)
        elif net:
            label(net, px, py, out)
        else:
            items.append(['no_connect', ['at', f(px), f(py)], ['uuid', Q(uid())]])

# Power sources: the net flags satisfy ERC for connectors and the diode output.
FLAGS = ('VIN_RAW', 'VIN_FUSED', 'VIN_P', 'VIN_L', '+5V', 'GND', 'VBUS', '+5V_BUCK', 'VSERVO', '3V3_S', '5V_S')
x = snap(30)
y = snap(30)
for net in FLAGS:
    pwr[0] += 1
    items.append(placed('power:PWR_FLAG', '#FLG%03d' % pwr[0], 'PWR_FLAG', '', x, y, ['1']))
    need('power', 'PWR_FLAG')
    if net[0] == '+' and net in ('+3V3', '+5V') or net == 'GND':
        power(net, x, y)
    else:
        label(net, x, y, 180)
    x += snap(20)

sch = ['kicad_sch', ['version', '20250114'], ['generator', Q('eeschema')], ['generator_version', Q('10.0')],
       ['uuid', Q(ROOT)], ['paper', Q('A1')],
       ['title_block', ['title', Q('ESP32 Robot Arm Controller')], ['rev', Q('A')], ['date', Q('2026-11-02')]],
       ['lib_symbols'] + list(used.values())] + items + \
      [['sheet_instances', ['path', Q('/'), ['page', Q('1')]]], ['embedded_fonts', 'no']]

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + '.kicad_sch'), 'w').write(dump(sch) + '\n')
pro = {'meta': {'filename': NAME + '.kicad_pro', 'version': 3},
       'board': {'design_settings': {'rules': {'min_clearance': 0.127, 'min_track_width': 0.15,
                                               'min_via_diameter': 0.5, 'min_through_hole_diameter': 0.2,
                                               'min_copper_edge_clearance': 0.25, 'min_hole_clearance': 0.2,
                                               'min_hole_to_hole': 0.25, 'min_silk_clearance': 0.0}}},
       'net_settings': {'meta': {'version': 4}, 'classes': [{'name': 'Default', 'clearance': 0.127, 'track_width': 0.2, 'via_diameter': 0.6, 'via_drill': 0.3, 'microvia_diameter': 0.3, 'microvia_drill': 0.1, 'diff_pair_width': 0.2, 'diff_pair_gap': 0.25, 'diff_pair_via_gap': 0.25, 'bus_width': 12, 'wire_width': 6, 'line_style': 0, 'priority': 2147483647}]},
       'sheets': [[ROOT, 'Root']]}
json.dump(pro, open(os.path.join(OUT, NAME + '.kicad_pro'), 'w'), indent=2)
print('symbols', len(PARTS), 'power', pwr[0])
