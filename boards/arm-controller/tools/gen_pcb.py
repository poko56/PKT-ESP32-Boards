"""Place, route and pour the board. Run with KiCad's bundled Python."""
import heapq, math, os, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from pcbnew import FromMM as MM, ToMM, VECTOR2I, F_Cu, B_Cu
from design import *
from sexpr import parse, find, first
NEAR = 1.2                  # wide tracks neck down to SIG this close to a pad

FP = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', NAME + '.kicad_pcb')
G = 0.1                     # routing grid
CLR = 0.15                  # routed clearance; the fab rule in the project is 0.127
SIG = 0.2                   # default track width
VIA, DRILL = 0.6, 0.3
ANT_Y = 6.6                 # the module footprint carries the full-width antenna keepout
COLS, ROWS = int(W / G) + 1, int(H / G) + 1
FREE, BLOCK, CONFLICT = 0, 255, 254
LAYERS = (F_Cu, B_Cu)


def pt(x, y):
    return VECTOR2I(MM(CX + x), MM(OY + y))


board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.m_MinClearance, ds.m_TrackMinWidth, ds.m_ViasMinSize, ds.m_MinThroughDrill = MM(0.127), MM(0.15), MM(0.5), MM(0.2)
ds.m_CopperEdgeClearance, ds.m_HoleClearance, ds.m_HoleToHoleMin = MM(0.25), MM(0.2), MM(0.25)

nets = {}


def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]


# Net names and symbol links come from the schematic so the board passes parity.
SCH = OUT.replace('.kicad_pcb', '.kicad_sch')
tmp = tempfile.mktemp(suffix='.net')
subprocess.check_call(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli', 'sch', 'export', 'netlist',
                       '--format', 'kicadsexpr', '-o', tmp, SCH], stderr=subprocess.DEVNULL)
nl = parse(open(tmp).read())
stamp = {first(c, 'ref')[1]: first(c, 'tstamps')[1] for c in find(first(nl, 'components'), 'comp')}
pinnet = {}
for n in find(first(nl, 'nets'), 'net'):
    for d in find(n, 'node'):
        pinnet[(first(d, 'ref')[1], first(d, 'pin')[1])] = first(n, 'name')[1]
MX = PARTS['U5'][5][0]
KN = {}     # design net name -> schematic net name

pads = []   # dicts: net, x0,y0,x1,y1 (mm relative), cx,cy, round, layers, ref
for ref, (lib, sym, val, fpid, netmap, (x, y, rot), mpn) in PARTS.items():
    fl, fn = fpid.split(':')
    fp = pcbnew.FootprintLoad(FP + fl + '.pretty', fn)
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(rot)
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetVisible(False)
    fp.SetFPID(pcbnew.LIB_ID(fl, fn))
    fp.SetPath(pcbnew.KIID_PATH('/' + stamp[ref]))
    fp.SetSheetname('Root'); fp.SetSheetfile(NAME + '.kicad_sch')
    fp.SetField('MPN', mpn)
    for field in fp.GetFields():
        if field.GetName() == 'MPN':
            field.SetVisible(False)
            field.SetLayer(pcbnew.F_Fab)
    if ref == 'J3':
        fp.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
    board.Add(fp)
    if ref == 'U5':
        lookup = {'1': 'GND', '15': 'GND', '38': 'GND', '39': 'GND'}
        lookup.update({k: v for k, v in netmap.items() if not k.startswith('[')})
    else:
        lookup = netmap
    for p in fp.Pads():
        num = p.GetNumber()
        name = lookup.get(num)
        kname = pinnet.get((ref, num))
        if kname:
            p.SetNet(net(kname))
        if name:
            KN[name] = kname
        bb = p.GetBoundingBox()
        ax, ay = ToMM(bb.GetLeft()) - CX, ToMM(bb.GetTop()) - OY
        bx, by = ToMM(bb.GetRight()) - CX, ToMM(bb.GetBottom()) - OY
        attr = p.GetAttribute()
        th = attr == pcbnew.PAD_ATTRIB_PTH
        npth = attr == pcbnew.PAD_ATTRIB_NPTH
        smd_top = p.IsOnLayer(F_Cu)
        pads.append(dict(ref=ref, num=num, net=name, x0=ax, y0=ay, x1=bx, y1=by,
                         cx=(ax + bx) / 2, cy=(ay + by) / 2, th=th or npth, npth=npth,
                         round=p.GetShape(F_Cu) == pcbnew.PAD_SHAPE_CIRCLE and th))


# ---- grid ------------------------------------------------------------------
netid = {}
for i, n in enumerate(sorted(KN), 1):
    netid[n] = i
idname = {v: k for k, v in netid.items()}


def cell(x, y):
    return int(round((x + W / 2) / G)), int(round(y / G))


def disk(r):
    k = int(math.ceil(r / G))
    return [(dx, dy) for dx in range(-k, k + 1) for dy in range(-k, k + 1) if math.hypot(dx, dy) * G <= r]


def paint_rect(g, x0, y0, x1, y1, nid, halo):
    # Only cells strictly inside the halo: rounding outward would seal off 0.5 mm pitch pads.
    cx0 = math.ceil((x0 - halo + W / 2) / G - 1e-6); cy0 = math.ceil((y0 - halo) / G - 1e-6)
    cx1 = math.floor((x1 + halo + W / 2) / G + 1e-6); cy1 = math.floor((y1 + halo) / G + 1e-6)
    for yy in range(max(cy0, 0), min(cy1, ROWS - 1) + 1):
        for xx in range(max(cx0, 0), min(cx1, COLS - 1) + 1):
            paint(g, xx + yy * COLS, nid)


def paint(g, i, nid):
    v = g[i]
    if v == FREE:
        g[i] = nid
    elif v != nid and v != BLOCK:
        g[i] = CONFLICT


POUR_NETS = set(POURS)
_base = []


def inside(poly_, x, y):
    c = False
    for (x0, y0), (x1, y1) in zip(poly_, poly_[1:] + poly_[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def edge_dist(poly_, x, y):
    best = 1e9
    for (x0, y0), (x1, y1) in zip(poly_, poly_[1:] + poly_[:1]):
        dx, dy = x1 - x0, y1 - y0
        t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - x0 - t * dx, y - y0 - t * dy))
    return best


def in_pour(name, x, y):
    return name in POURS and inside(POURS[name], x, y)


def poly_cells(poly_, grow):
    """Cells inside the polygon, grown (or shrunk, if negative) by `grow` mm."""
    xs, ys = [q[0] for q in poly_], [q[1] for q in poly_]
    x0, y0 = cell(min(xs) - abs(grow), min(ys) - abs(grow))
    x1, y1 = cell(max(xs) + abs(grow), max(ys) + abs(grow))
    for yy in range(max(y0, 0), min(y1, ROWS - 1) + 1):
        for xx in range(max(x0, 0), min(x1, COLS - 1) + 1):
            x, y = xx * G - W / 2, yy * G
            ins, d = inside(poly_, x, y), edge_dist(poly_, x, y)
            if (ins and (grow >= 0 or d >= -grow)) or (not ins and grow > 0 and d <= grow):
                yield xx, yy


def base_grid():
    if _base:
        return [bytearray(_base[0]), bytearray(_base[1])]
    grids = [bytearray(COLS * ROWS), bytearray(COLS * ROWS)]
    halo = 0.127 + SIG / 2 - 1e-3
    for p in pads:
        nid = netid.get(p['net'], CONFLICT)
        if p['npth']:
            for g in grids:
                paint_rect(g, p['x0'], p['y0'], p['x1'], p['y1'], BLOCK, 0.25 + SIG / 2)
            continue
        for l in (0, 1) if p['th'] else (0,):
            if p['round']:
                r = (p['x1'] - p['x0']) / 2 + halo
                cx, cy = cell(p['cx'], p['cy'])
                for dx, dy in disk(r):
                    xx, yy = cx + dx, cy + dy
                    if 0 <= xx < COLS and 0 <= yy < ROWS:
                        paint(grids[l], xx + yy * COLS, nid)
            else:
                paint_rect(grids[l], p['x0'], p['y0'], p['x1'], p['y1'], nid, halo)
    for name, pl in POURS.items():
        for xx, yy in poly_cells(pl, 0.2 + SIG / 2):
            paint(grids[0], xx + yy * COLS, netid[name])
    # Module underside on top copper, antenna keepout and board edge.
    ex = int(0.4 / G)
    for yy in range(ROWS):
        for xx in range(COLS):
            x, y = xx * G - W / 2, yy * G
            i = xx + yy * COLS
            if abs(x - MX) < 9.0 and y < 25.4 and grids[0][i] in (FREE, CONFLICT):
                grids[0][i] = BLOCK
            if abs(x - MX) < 24.3 and y < ANT_Y:
                grids[0][i] = grids[1][i] = BLOCK
            if xx < ex or yy < ex or xx >= COLS - ex or yy >= ROWS - ex:
                grids[0][i] = grids[1][i] = BLOCK
    _base[:] = [bytes(grids[0]), bytes(grids[1])]
    return base_grid()


def terminals(p):
    """Grid cells that land inside a pad."""
    r = []
    x0, y0 = cell(p['x0'], p['y0'])
    x1, y1 = cell(p['x1'], p['y1'])
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            x, y = xx * G - W / 2, yy * G
            if p['x0'] + 0.04 <= x <= p['x1'] - 0.04 and p['y0'] + 0.04 <= y <= p['y1'] - 0.04:
                if p['round'] and math.hypot(x - p['cx'], y - p['cy']) > (p['x1'] - p['x0']) / 2 - 0.05:
                    continue
                for l in (0, 1) if p['th'] else (0,):
                    r.append((xx, yy, l))
    return r


DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
VIA_ST = disk(VIA / 2 - SIG / 2 + 0.03)


def route(grids, nid, sources, targets, width, near, limit=1500000):
    """Multi-source A* with a turn penalty; returns [(x, y, layer), ...]."""
    tset = set(targets)
    tx0 = min(t[0] for t in tset); tx1 = max(t[0] for t in tset)
    ty0 = min(t[1] for t in tset); ty1 = max(t[1] for t in tset)
    sten = disk((width - SIG) / 2 + 0.01) if width > SIG else [(0, 0)]
    one = [(0, 0)]

    def h(x, y):
        dx = max(tx0 - x, 0, x - tx1); dy = max(ty0 - y, 0, y - ty1)
        return 1.25 * (max(dx, dy) + 0.414 * min(dx, dy))

    def free(x, y, l, st):
        g = grids[l]
        for dx, dy in st:
            xx, yy = x + dx, y + dy
            if not (0 <= xx < COLS and 0 <= yy < ROWS):
                return False
            v = g[xx + yy * COLS]
            if v != FREE and v != nid:
                return False
        return True

    best, prev, heap = {}, {}, []
    for s in sources:
        st = (s[0], s[1], s[2], -1)
        best[st] = 0.0
        heapq.heappush(heap, (h(s[0], s[1]), 0.0, st))
    n = 0
    while heap:
        f, c, st = heapq.heappop(heap)
        if c > best.get(st, 1e18):
            continue
        x, y, l, d = st
        if (x, y, l) in tset:
            path = [(x, y, l)]
            while st in prev:
                st = prev[st]
                path.append((st[0], st[1], st[2]))
            return path[::-1]
        n += 1
        if n > limit:
            return None
        for i, (dx, dy) in enumerate(DIRS):
            nx, ny = x + dx, y + dy
            if not free(nx, ny, l, one if (nx, ny) in near else sten):
                continue
            nc = c + (1.0 if i < 4 else 1.414) * (1.0 if l == 0 else 1.15)
            if d != -1 and d != i:
                nc += 1.2
            ns = (nx, ny, l, i)
            if nc < best.get(ns, 1e18):
                best[ns] = nc; prev[ns] = st
                heapq.heappush(heap, (nc + h(nx, ny), nc, ns))
        if free(x, y, 0, VIA_ST) and free(x, y, 1, VIA_ST):
            ns = (x, y, 1 - l, d)
            nc = c + 18
            if nc < best.get(ns, 1e18):
                best[ns] = nc; prev[ns] = st
                heapq.heappush(heap, (nc + h(x, y), nc, ns))
    return None


def mark(grids, path, nid, width, near=()):
    tr = disk(width / 2 + CLR + SIG / 2)
    thin = disk(SIG / 2 + CLR + SIG / 2)
    vi = disk(VIA / 2 + CLR + SIG / 2)
    for k, (x, y, l) in enumerate(path):
        for dx, dy in (thin if (x, y) in near else tr):
            xx, yy = x + dx, y + dy
            if 0 <= xx < COLS and 0 <= yy < ROWS:
                paint(grids[l], xx + yy * COLS, nid)
        if k and path[k - 1][2] != l:
            for g in grids:
                for dx, dy in vi:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < COLS and 0 <= yy < ROWS:
                        paint(g, xx + yy * COLS, nid)


bynet = {}
for p in pads:
    if p['net'] and p['net'] != 'GND':
        bynet.setdefault(p['net'], []).append(p)


def span(n):
    ps = bynet[n]
    return max(p['cy'] for p in ps) - min(p['cy'] for p in ps) + max(p['cx'] for p in ps) - min(p['cx'] for p in ps)


order = sorted(bynet, key=lambda n: (n not in WIDE and n not in POURS, -span(n)))


def route_all(order):
    grids = base_grid()
    done = []
    for name in order:
        nid, ps = netid[name], list(bynet[name])
        width = WIDE.get(name, SIG)
        near = set()
        if width > SIG:
            k = disk(NEAR)
            for p in ps:
                cx, cy = cell(p['cx'], p['cy'])
                near.update((cx + a, cy + b) for a, b in k)
        if name in POURS:
            tree = set((x, y, 0) for x, y in poly_cells(POURS[name], -0.3))
            rest = [p for p in ps if not in_pour(name, p['cx'], p['cy'])]
        else:
            tree = set(terminals(ps[0]))
            rest = ps[1:]
        while rest:
            p = rest.pop(0)
            ts = terminals(p)
            if not ts or tree & set(ts):
                tree |= set(ts)
                continue
            path = route(grids, nid, tree, ts, width, near)
            if path is None:
                return name, done
            mark(grids, path, nid, width, near)
            done.append((name, path, width, near))
            tree |= set(path)
    return None, done, grids


t0 = time.time()
for attempt in range(0 if os.environ.get('PLACE_ONLY') else 40):
    r = route_all(order)
    if r[0] is None:
        routes, grids = r[1], r[2]
        break
    print('attempt', attempt, 'failed on', r[0], 'routed', len(r[1]), '%.0fs' % (time.time() - t0), flush=True)
    order.remove(r[0]); order.insert(0, r[0])
else:
    if not os.environ.get('PLACE_ONLY'):
        sys.exit('routing failed')
    routes, grids = [], base_grid()
print('routed', len(routes), 'paths in %.0fs' % (time.time() - t0), flush=True)


# ---- emit copper -----------------------------------------------------------
def gxy(c):
    return c[0] * G - W / 2, c[1] * G


def add_via(x, y, name):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y)); v.SetWidth(MM(VIA)); v.SetDrill(MM(DRILL))
    v.SetNet(net(KN[name])); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F_Cu, B_Cu)
    board.Add(v)


def add_track(a, b, l, width, name):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pt(*a)); t.SetEnd(pt(*b)); t.SetWidth(MM(width)); t.SetLayer(l); t.SetNet(net(KN[name]))
    board.Add(t)


def emit(name, path, width, near=()):
    run = [path[0]]
    for c in path[1:] + [None]:
        last = run[-1]
        if c is not None and c[2] != last[2]:
            flush(run, name, width, near)
            add_via(*gxy(c), name)
            run = [c]
            continue
        if c is None:
            flush(run, name, width, near)
            break
        run.append(c)


def flush(run, name, width, near=()):
    if len(run) < 2:
        return
    a = run[0]
    w = lambda c: SIG if (c[0], c[1]) in near else width
    for i in range(1, len(run)):
        b = run[i]
        nxt = run[i + 1] if i + 1 < len(run) else None
        if nxt and w(b) == w(a) and w(nxt) == w(a) and \
                (nxt[0] - b[0], nxt[1] - b[1]) == (b[0] - run[i - 1][0], b[1] - run[i - 1][1]):
            continue
        add_track(gxy(a), gxy(b), LAYERS[a[2]], min(w(a), w(b)), name)
        a = b


for name, path, width, near in routes:
    emit(name, path, width, near)

# GND: every SMD ground pad gets a nearby via into the planes.
gid = netid['GND']
n_gnd = 0
seen = set()
placed_ = []
for p in pads:
    if p['net'] != 'GND' or p['th'] or (p['ref'] == 'U5' and p['num'] == '39') or (p['ref'] == 'U1' and p['num'] == '9'):
        continue
    if (p['cx'], p['cy']) in seen:      # USB A1/B12 share one pad position
        continue
    seen.add((p['cx'], p['cy']))
    src = terminals(p)
    best, bd = None, 1e9
    sx, sy = cell(p['cx'], p['cy'])
    for dy in range(-30, 31):
        for dx in range(-30, 31):
            x, y = sx + dx, sy + dy
            if 0 <= x < COLS and 0 <= y < ROWS and math.hypot(dx, dy) < bd and \
                    all(math.hypot(x - q[0], y - q[1]) > 9 for q in placed_):
                ok = all(0 <= x + a < COLS and 0 <= y + b < ROWS and
                         grids[l][x + a + (y + b) * COLS] in (FREE, gid)
                         for l in (0, 1) for a, b in disk(VIA / 2 - SIG / 2 + 0.03))
                if ok:
                    bd, best = math.hypot(dx, dy) + 0.0, (x, y)
    if best is None:
        print('no via spot for', p['ref'], p['num'])
        continue
    path = route(grids, gid, set(src), [(best[0], best[1], 0)], SIG, set())
    if path is None:
        print('no gnd path for', p['ref'], p['num'])
        continue
    placed_.append(best)
    path = path + [(best[0], best[1], 1)]
    mark(grids, path, gid, SIG)
    emit('GND', path, SIG)
    n_gnd += 1

# Stitching vias on a coarse grid.
stitch = 0
for yy in range(int(8 / G), ROWS, int(4.0 / G)):
    for xx in range(int(2 / G), COLS, int(4.0 / G)):
        st = disk(VIA / 2 + CLR + 0.1)
        ok = all(0 <= xx + a < COLS and 0 <= yy + b < ROWS and
                 grids[l][xx + a + (yy + b) * COLS] in (FREE,)
                 for l in (0, 1) for a, b in st)
        if ok:
            add_via(*gxy((xx, yy)), 'GND')
            path = [(xx, yy, 0), (xx, yy, 1)]
            mark(grids, path, gid, SIG)
            stitch += 1
print('gnd vias', n_gnd, 'stitch', stitch)


# ---- outline, planes, keepout, silk ----------------------------------------
def line(a, b, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(*a)); s.SetEnd(pt(*b)); s.SetLayer(layer); s.SetWidth(MM(w))
    board.Add(s)


def arc(center, start, end):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(pt(*start), pt(*center), pt(*end))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    board.Add(s)


hw, r = W / 2, 1.0
s2 = r * (1 - math.sqrt(0.5))
line((-hw + r, 0), (hw - r, 0)); line((hw, r), (hw, H - r)); line((hw - r, H), (-hw + r, H)); line((-hw, H - r), (-hw, r))
arc0 = [((-hw + r, 0), (-hw + s2, s2), (-hw, r)), ((hw - r, 0), (hw - s2, s2), (hw, r)),
        ((hw, H - r), (hw - s2, H - s2), (hw - r, H)), ((-hw, H - r), (-hw + s2, H - s2), (-hw + r, H))]


def arc3(a, m, b):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(pt(*a), pt(*m), pt(*b))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
    board.Add(s)


for a, m, b in arc0:
    arc3(a, m, b)


def poly(z, ptsl):
    o = z.Outline()
    o.NewOutline()
    for x, y in ptsl:
        q = pt(x, y)
        o.Append(q.x, q.y)


for l in LAYERS:
    z = pcbnew.ZONE(board)
    z.SetLayer(l)
    z.SetNet(net(KN['GND']))
    poly(z, [(-hw, 0), (hw, 0), (hw, H), (-hw, H)])
    z.SetLocalClearance(MM(0.2))
    z.SetMinThickness(MM(0.2))
    z.SetThermalReliefGap(MM(0.25))
    z.SetThermalReliefSpokeWidth(MM(0.35))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName('GND_' + ('F' if l == F_Cu else 'B'))
    board.Add(z)

for name, pl in POURS.items():
    z = pcbnew.ZONE(board)
    z.SetLayer(F_Cu)
    z.SetNet(net(KN[name]))
    poly(z, pl)
    z.SetLocalClearance(MM(0.2))
    z.SetMinThickness(MM(0.2))
    z.SetAssignedPriority(1)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetZoneName(name)
    board.Add(z)


def text(s, x, y, layer, size=0.8, rot=0, mirror=False, just=None):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s); t.SetPosition(pt(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(MM(size), MM(size))); t.SetTextThickness(MM(size * 0.15))
    t.SetTextAngleDegrees(rot); t.SetMirrored(mirror)
    if just is not None:
        t.SetHorizJustify(just)
    board.Add(t)


F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
for label_, x, y in (('SERVO 1-5', -25.9, 54.4), ('DIO 1-5', 6.1, 54.4), ('ADC 1-4', 18.8, 54.4),
                     ('I2C', 27.8, 51.9), ('UART', 32, 51.9), ('ESTOP', 36.2, 49.6), ('EN', 35.5, 43.9), ('BOOT', 29.5, 43.9),
                     ('12V IN', -29, 19), ('STAT', 16.4, 41.6), ('3V3', 25, 43.6), ('SERVO', -5, 50.2)):
    text(label_, x, y, F, 0.8)
text('ESP32 ROBOT ARM CONTROLLER', 8, 30, B, 1.4, 0, True)
text('REV B   12V IN   ROWS: S + -', 8, 33, B, 1.0, 0, True)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
print('unconnected', board.GetConnectivity().GetUnconnectedCount(True))
pcbnew.SaveBoard(OUT, board)
print('saved')
