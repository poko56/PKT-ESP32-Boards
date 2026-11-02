"""Write the BOM and CPL in the column layout JLCPCB/EasyEDA asks for."""
import csv, sys
sys.path.insert(0, 'tools')
from design import PARTS, OX, OY, H
g = {}
for r, p in PARTS.items():
    if 'header' in p[6]:
        continue
    g.setdefault((p[6], p[3].split(':')[1], p[7], p[8]), []).append(r)
w = csv.writer(open('fab/JLC_BOM.csv', 'w', newline='', encoding='utf-8-sig'))
w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Check'])
for (c, f, l, ok), rs in sorted(g.items(), key=lambda kv: kv[1][0]):
    w.writerow([c, ','.join(rs), f, l, 'verified' if ok else ('confirm in JLC' if l else 'pick part in JLC')])
rows = list(csv.DictReader(open('fab/positions.csv')))
w = csv.writer(open('fab/JLC_CPL.csv', 'w', newline='', encoding='utf-8-sig'))
w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
for r in rows:
    if r['Ref'] in ('J2', 'J3'):
        continue
    x, y = float(r['PosX']) - OX, float(r['PosY']) + OY + H    # board-relative, origin at the bottom left
    w.writerow([r['Ref'], '%.3fmm' % x, '%.3fmm' % y, 'Top', '%.0f' % float(r['Rot'])])
print('BOM lines', len(g), 'placements', len(rows))
