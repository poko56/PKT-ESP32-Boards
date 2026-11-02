"""Single source of truth: parts, nets, placement. x is relative to board centre, y from top edge."""
NAME = 'esp32_devboard'
W, H = 29.0, 54.6
OX, OY = 100.0, 100.0   # board top-left on the KiCad sheet
CX = OX + W / 2

HDR_Y = 8.4   # first header pin, just below the module's antenna courtyard
R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
LED = 'LED_SMD:LED_0603_1608Metric'
SWF = 'Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2'

J2_NETS = ['+3V3', 'EN', 'IO36', 'IO39', 'IO34', 'IO35', 'IO32', 'IO33', 'IO25', 'IO26', 'IO27',
           'IO14', 'IO12', 'GND', 'IO13', '+5V', 'GND']
J3_NETS = ['GND', 'IO23', 'IO22', 'ESP_TX', 'ESP_RX', 'IO21', 'IO19', 'IO18', 'IO5', 'IO17', 'IO16',
           'IO4', 'IO0', 'IO2', 'IO15', '+3V3', 'GND']
ESP = {'[1,15,38,39]': 'GND', '2': '+3V3', '3': 'EN', '4': 'IO36', '5': 'IO39', '6': 'IO34', '7': 'IO35',
       '8': 'IO32', '9': 'IO33', '10': 'IO25', '11': 'IO26', '12': 'IO27', '13': 'IO14', '14': 'IO12',
       '16': 'IO13', '23': 'IO15', '24': 'IO2', '25': 'IO0', '26': 'IO4', '27': 'IO16', '28': 'IO17',
       '29': 'IO5', '30': 'IO18', '31': 'IO19', '33': 'IO21', '34': 'ESP_RX', '35': 'ESP_TX',
       '36': 'IO22', '37': 'IO23'}
USB = {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND',
       'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
       'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DN', 'B7': 'USB_DN'}
CH340 = {'1': 'GND', '2': 'ESP_RX', '3': 'ESP_TX', '4': '+3V3', '5': 'USB_DP', '6': 'USB_DN',
         '13': 'DTR', '14': 'RTS', '16': '+3V3'}


def hdr(nets):
    return {str(i + 1): n for i, n in enumerate(nets)}


# ref: (lib, symbol, value, footprint, pin->net, (x, y, rot), MPN)
PARTS = {
    'U1': ('RF_Module', 'ESP32-WROOM-32E', 'ESP32-WROOM-32E', 'RF_Module:ESP32-WROOM-32E', ESP, (0, 12.75, 0), 'ESP32-WROOM-32E-N4'),
    'U2': ('Interface_USB', 'CH340C', 'CH340C', 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', CH340, (4.5, 36.8, 0), 'CH340C'),
    'U3': ('Regulator_Linear', 'AMS1117-3.3', 'AMS1117-3.3', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
           {'1': 'GND', '2': '+3V3', '3': '+5V'}, (-5.3, 37.0, 0), 'AMS1117-3.3'),
    'J1': ('Connector', 'USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', USB, (0, 51.4, 0), 'HRO TYPE-C-31-M-12'),
    'J2': ('Connector', 'Conn_01x17_Pin', 'Left', 'Connector_PinHeader_2.54mm:PinHeader_1x17_P2.54mm_Vertical', hdr(J2_NETS), (-12.7, HDR_Y, 0), '2.54mm 1x17 header'),
    'J3': ('Connector', 'Conn_01x17_Pin', 'Right', 'Connector_PinHeader_2.54mm:PinHeader_1x17_P2.54mm_Vertical', hdr(J3_NETS), (12.7, HDR_Y, 0), '2.54mm 1x17 header'),
    'D1': ('Device', 'D_Schottky', 'SS14', 'Diode_SMD:D_SMA', {'1': '+5V', '2': 'VBUS'}, (-6.3, 42.9, 0), 'SS14'),
    'D2': ('Device', 'LED', 'PWR', LED, {'1': 'GND', '2': 'LED_PWR'}, (-9.0, 47.3, 0), 'LED 0603 red'),
    'D3': ('Device', 'LED', 'IO2', LED, {'1': 'GND', '2': 'LED_IO2'}, (9.0, 47.3, 180), 'LED 0603 blue'),
    'Q1': ('Transistor_BJT', 'MMBT3904', 'MMBT3904', 'Package_TO_SOT_SMD:SOT-23', {'1': 'Q1_B', '2': 'RTS', '3': 'EN'}, (-0.7, 28.6, 0), 'MMBT3904'),
    'Q2': ('Transistor_BJT', 'MMBT3904', 'MMBT3904', 'Package_TO_SOT_SMD:SOT-23', {'1': 'Q2_B', '2': 'DTR', '3': 'IO0'}, (5.0, 28.6, 0), 'MMBT3904'),
    'R1': ('Device', 'R', '5.1k', R0603, {'1': 'CC1', '2': 'GND'}, (-1.6, 44.3, 90), '5.1k 1% 0603'),
    'R2': ('Device', 'R', '5.1k', R0603, {'1': 'CC2', '2': 'GND'}, (3.2, 44.3, 90), '5.1k 1% 0603'),
    'R3': ('Device', 'R', '10k', R0603, {'1': 'DTR', '2': 'Q1_B'}, (2.0, 28.6, 90), '10k 1% 0603'),
    'R4': ('Device', 'R', '10k', R0603, {'1': 'RTS', '2': 'Q2_B'}, (7.8, 28.6, 90), '10k 1% 0603'),
    'R5': ('Device', 'R', '10k', R0603, {'1': '+3V3', '2': 'EN'}, (-3.8, 28.6, 90), '10k 1% 0603'),
    'R6': ('Device', 'R', '1k', R0603, {'1': '+3V3', '2': 'LED_PWR'}, (-9.0, 45.75, 180), '1k 1% 0603'),
    'R7': ('Device', 'R', '1k', R0603, {'1': 'IO2', '2': 'LED_IO2'}, (9.0, 45.75, 0), '1k 1% 0603'),
    'C1': ('Device', 'C', '10uF', C0805, {'1': '+5V', '2': 'GND'}, (-7.6, 31.6, 0), '10uF 16V X7R 0805'),
    'C2': ('Device', 'C', '22uF', C0805, {'1': '+3V3', '2': 'GND'}, (-3.0, 31.6, 0), '22uF 10V X5R 0805'),
    'C3': ('Device', 'C', '10uF', C0603, {'1': '+3V3', '2': 'GND'}, (-7.0, 28.6, 90), '10uF 10V X5R 0603'),
    'C4': ('Device', 'C', '100nF', C0603, {'1': '+3V3', '2': 'GND'}, (-8.6, 28.6, 90), '100nF 16V X7R 0603'),
    'C5': ('Device', 'C', '100nF', C0603, {'1': '+3V3', '2': 'GND'}, (9.2, 36.0, 90), '100nF 16V X7R 0603'),
    'C6': ('Device', 'C', '1uF', C0603, {'1': 'EN', '2': 'GND'}, (-5.4, 28.6, 90), '1uF 16V X7R 0603'),
    'SW1': ('Switch', 'SW_Push', 'EN', SWF, {'1': 'EN', '2': 'GND'}, (-9.4, 52.7, 0), 'CK KMR2'),
    'SW2': ('Switch', 'SW_Push', 'BOOT', SWF, {'1': 'IO0', '2': 'GND'}, (9.4, 52.7, 0), 'CK KMR2'),
}
POWER = {'+3V3', '+5V', 'VBUS'}
