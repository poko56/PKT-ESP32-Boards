"""Smallest ESP32-C3 board for JLCPCB/EasyEDA PCBA: one-sided SMD, native USB, LDO only.
x from centre, y from top."""
NAME = 'esp32c3_board'
W, H = 20.0, 34.0
OX, OY = 100.0, 100.0
CX = OX + W / 2
R0402 = 'Resistor_SMD:R_0402_1005Metric'
C0402 = 'Capacitor_SMD:C_0402_1005Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
LED = 'LED_SMD:LED_0603_1608Metric'
SWF = 'Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2'
HDR = 'Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical'
MODULE = 'U1'
MODULE_X = 6.7       # half width of the module body
MODULE_Y = 16.7      # bottom of the module body
ANT_Y = 5.6          # bottom of the footprint's antenna keepout
HDR_Y = 7.4
PARTS = {}


def part(ref, lib, sym, val, fp, nets, pos, mpn=None, lcsc='', ok=False):
    PARTS[ref] = (lib, sym, val, fp, nets, tuple(pos) + (0,) * (3 - len(pos)), mpn or val, lcsc, ok)


def R(ref, val, a, b, pos, lcsc=''):
    part(ref, 'Device', 'R', val, R0402, {'1': a, '2': b}, pos, val + ' 1% 0402', lcsc)


def C(ref, val, a, b, pos, fp=C0402, lcsc=''):
    part(ref, 'Device', 'C', val, fp, {'1': a, '2': b}, pos, val + ' X5R/X7R ' + fp.split('_')[-2], lcsc)


J2 = ['+3V3', 'IO2', 'IO3', 'GND', 'IO0', 'IO1', 'IO10']
J3 = ['IO21', 'IO20', 'IO7', 'IO6', 'IO5', 'IO4', '5V_IN']
mod = {'3': '+3V3', '5': 'IO2', '6': 'IO3', '8': 'EN', '12': 'IO0', '13': 'IO1', '16': 'IO10', '18': 'IO4', '19': 'IO5',
       '20': 'IO6', '21': 'IO7', '22': 'IO8', '23': 'IO9', '26': 'USB_DN', '27': 'USB_DP', '30': 'IO20', '31': 'IO21'}
for n in [1, 2, 11, 14] + list(range(36, 54)):
    mod[str(n)] = 'GND'
part('U1', 'local', 'ESP32-C3-MINI-1', 'ESP32-C3-MINI-1', 'RF_Module:ESP32-C6-MINI-1', mod, (0, 11.1), 'ESP32-C3-MINI-1-N4', 'C2838502', True)
part('J2', 'Connector', 'Conn_01x07_Pin', 'LEFT', HDR, {str(i + 1): n for i, n in enumerate(J2)}, (-7.62, HDR_Y), '2.54mm 1x7 header (not assembled)')
part('J3', 'Connector', 'Conn_01x07_Pin', 'RIGHT', HDR, {str(i + 1): n for i, n in enumerate(J3)}, (7.62, HDR_Y), '2.54mm 1x7 header (not assembled)')
part('J1', 'Connector', 'USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
     {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
      'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_C_P', 'B6': 'USB_C_P', 'A7': 'USB_C_N', 'B7': 'USB_C_N'}, (0, 31.2), 'HRO TYPE-C-31-M-12', 'C165948')
R('R1', '5.1k', 'CC1', 'GND', (0.2, 24.8, 0), 'C25905')
R('R2', '5.1k', 'CC2', 'GND', (2.6, 24.8, 0), 'C25905')
part('U2', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
     {'1': 'USB_C_P', '6': 'USB_DP', '3': 'USB_C_N', '4': 'USB_DN', '2': 'GND', '5': 'VBUS'}, (3.7, 19.2), 'USBLC6-2SC6', 'C7519')
part('D1', 'Device', 'D_Schottky', 'B5819W', 'Diode_SMD:D_SOD-123', {'1': '5V_IN', '2': 'VBUS'}, (-3.2, 24.7, 0), 'B5819W', 'C8598', True)
part('FB1', 'Device', 'FerriteBead', '120R', 'Inductor_SMD:L_0603_1608Metric', {'1': '5V_IN', '2': '+5V'}, (-7.4, 26, 90), '120R@100MHz >=1A 0603')
C('C1', '10uF', '+5V', 'GND', (-4.35, 22.4, 0), C0603, 'C19702')
part('U3', 'Regulator_Linear', 'AP2112K-3.3', 'AP2112K-3.3', 'Package_TO_SOT_SMD:SOT-23-5',
     {'1': '+5V', '2': 'GND', '3': '+5V', '5': '+3V3'}, (-3.6, 19.2, 0), 'AP2112K-3.3TRG1', 'C51118', True)
C('C2', '22uF', '+3V3', 'GND', (0, 19, 90), C0805, 'C45783')
C('C3', '10uF', '+3V3', 'GND', (-1.3, 22.4, 0), C0603, 'C19702')
C('C4', '100nF', '+3V3', 'GND', (2.8, 22.6, 90), lcsc='C1525')
R('R3', '10k', '+3V3', 'EN', (3.88, 22.6, 90), 'C25744')
C('C5', '1uF', 'EN', 'GND', (4.96, 22.6, 90), lcsc='C52923')
R('R4', '10k', '+3V3', 'IO2', (0.65, 22.6, 90), 'C25744')
R('R5', '10k', '+3V3', 'IO8', (1.72, 22.6, 90), 'C25744')
part('SW1', 'Switch', 'SW_Push', 'RST', SWF, {'1': 'EN', '2': 'GND'}, (-7.2, 30.6, 90), 'SMD tact 4.2x2.8mm')
part('SW2', 'Switch', 'SW_Push', 'BOOT', SWF, {'1': 'IO9', '2': 'GND'}, (7.2, 30.6, 90), 'SMD tact 4.2x2.8mm')
R('R6', '1k', '+3V3', 'LED_IO', (7.7, 25.2), 'C11702')
part('D2', 'Device', 'LED', 'IO8', LED, {'1': 'IO8', '2': 'LED_IO'}, (7.7, 26.5, 0), 'LED 0603 blue')

POURS = {}
WIDE = {'VBUS': 0.4, '5V_IN': 0.4, '+5V': 0.4, '+3V3': 0.5}
