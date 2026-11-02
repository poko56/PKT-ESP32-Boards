#!/bin/zsh
# Rebuild everything from design.py: schematic -> board -> checks -> fab outputs.
set -e
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents
CLI=$K/MacOS/kicad-cli; N=esp32_devboard; O=fab
python3 tools/gen_sch.py
$K/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/gen_pcb.py 2>/dev/null | grep -vE 'attempt'
rm -rf $O; mkdir -p $O/gerber
$CLI sch erc --severity-all -o $O/erc.rpt $N.kicad_sch 2>/dev/null | grep Found
$CLI pcb drc --schematic-parity --severity-all -o $O/drc.rpt $N.kicad_pcb 2>/dev/null | grep Found
$CLI pcb export gerbers -l F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts --no-protel-ext -o $O/gerber/ $N.kicad_pcb 2>/dev/null | tail -1
$CLI pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 -o $O/gerber/ $N.kicad_pcb 2>/dev/null | tail -1
$CLI pcb export pos --format csv --units mm --side both -o $O/positions.csv $N.kicad_pcb 2>/dev/null | tail -1
$CLI sch export pdf -o $O/schematic.pdf $N.kicad_sch 2>/dev/null | tail -1
for s in top bottom; do $CLI pcb render --width 1000 --height 1700 --side $s --background opaque --quality high -o $O/render_$s.png $N.kicad_pcb 2>/dev/null | tail -1; done
python3 - <<'P'
import csv, sys
sys.path.insert(0, 'tools')
from design import PARTS
g = {}
for r, p in PARTS.items():
    g.setdefault((p[2], p[3].split(':')[1], p[6]), []).append(r)
w = csv.writer(open('fab/bom.csv', 'w', newline=''))
w.writerow(['Qty', 'Designators', 'Value', 'Footprint', 'Part'])
for (v, f, m), rs in sorted(g.items(), key=lambda kv: kv[1][0]):
    w.writerow([len(rs), ' '.join(rs), v, f, m])
P
(cd $O/gerber && zip -q ../esp32_devboard_gerber.zip *)
ls $O $O/gerber | head -40
