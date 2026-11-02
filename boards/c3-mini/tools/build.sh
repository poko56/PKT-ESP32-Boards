#!/bin/zsh
# Rebuild everything from design.py: schematic -> board -> checks -> fab outputs.
set -e
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents
CLI=$K/MacOS/kicad-cli; N=esp32c3_board; O=fab
python3 tools/gen_sch.py
$K/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/gen_pcb.py 2>/dev/null 
rm -rf $O; mkdir -p $O/gerber
$CLI sch erc --severity-all -o $O/erc.rpt $N.kicad_sch 2>/dev/null | grep Found
$CLI pcb drc --schematic-parity --severity-all -o $O/drc.rpt $N.kicad_pcb 2>/dev/null | grep Found
$CLI pcb export gerbers -l F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts --no-protel-ext -o $O/gerber/ $N.kicad_pcb 2>/dev/null | tail -1
$CLI pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 -o $O/gerber/ $N.kicad_pcb 2>/dev/null | tail -1
$CLI pcb export pos --format csv --units mm --side front --exclude-fp-th -o $O/positions.csv $N.kicad_pcb 2>/dev/null | tail -1
$CLI sch export pdf -o $O/schematic.pdf $N.kicad_sch 2>/dev/null | tail -1
for s in top bottom; do $CLI pcb render --width 1000 --height 1700 --side $s --background opaque --quality high -o $O/render_$s.png $N.kicad_pcb 2>/dev/null | tail -1; done
python3 tools/jlc.py
(cd $O/gerber && zip -q ../esp32c3_gerber.zip *)
ls $O $O/gerber | head -40
