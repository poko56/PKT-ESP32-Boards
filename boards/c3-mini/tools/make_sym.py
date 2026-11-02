"""Local symbol for ESP32-C3-MINI-1; pin table from Espressif datasheet v2.2, table 3-1."""
import os
L = [(1, 'GND'), (2, 'GND'), (3, '3V3'), (4, 'NC'), (5, 'IO2'), (6, 'IO3'), (7, 'NC'), (8, 'EN'), (9, 'NC'), (10, 'NC'), (11, 'GND'),
     (12, 'IO0'), (13, 'IO1'), (14, 'GND'), (15, 'NC'), (16, 'IO10'), (17, 'NC'), (18, 'IO4'), (19, 'IO5'), (20, 'IO6'), (21, 'IO7'),
     (22, 'IO8'), (23, 'IO9'), (24, 'NC'), (25, 'NC'), (26, 'IO18'), (27, 'IO19')]
Rr = [(28, 'NC'), (29, 'NC'), (30, 'RXD0'), (31, 'TXD0'), (32, 'NC'), (33, 'NC'), (34, 'NC'), (35, 'NC')] + [(n, 'GND') for n in range(36, 54)]


def pin(n, name, x, y, ang):
    t = 'power_in' if name in ('GND', '3V3') else 'no_connect' if name == 'NC' else 'input' if name == 'EN' else 'bidirectional'
    return ('(pin %s line (at %g %g %d) (length 2.54) (name "%s" (effects (font (size 1.27 1.27)))) '
            '(number "%d" (effects (font (size 1.27 1.27)))))' % (t, x, y, ang, name, n))


h = 2.54 * max(len(L), len(Rr)) / 2
p = [pin(n, m, -15.24, h - 2.54 * (i + 1), 0) for i, (n, m) in enumerate(L)]
p += [pin(n, m, 15.24, h - 2.54 * (i + 1), 180) for i, (n, m) in enumerate(Rr)]
s = '''(kicad_symbol_lib (version 20241209) (generator "pkt") (generator_version "1")
 (symbol "ESP32-C3-MINI-1" (exclude_from_sim no) (in_bom yes) (on_board yes)
  (property "Reference" "U" (at 0 %g 0) (effects (font (size 1.27 1.27))))
  (property "Value" "ESP32-C3-MINI-1" (at 0 %g 0) (effects (font (size 1.27 1.27))))
  (property "Footprint" "RF_Module:ESP32-C6-MINI-1" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Description" "ESP32-C3 module" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
  (symbol "ESP32-C3-MINI-1_0_1" (rectangle (start -12.7 %g) (end 12.7 %g) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "ESP32-C3-MINI-1_1_1"
   %s
  )
 )
)
''' % (h + 2.54, -h - 2.54, h, -h - 1, '\n   '.join(p))
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
open(os.path.join(root, 'local.kicad_sym'), 'w').write(s)
open(os.path.join(root, 'sym-lib-table'), 'w').write('(sym_lib_table\n (version 7)\n (lib (name "local")(type "KiCad")(uri "${KIPRJMOD}/local.kicad_sym")(options "")(descr ""))\n)\n')
