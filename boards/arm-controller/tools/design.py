"""ESP32 5-servo robot arm controller: parts, nets, placement.
x is relative to board centre, y from the top edge."""
NAME = 'esp32_arm_controller'
W, H = 80.0, 64.0
OX, OY = 100.0, 100.0
CX = OX + W / 2

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
C1210 = 'Capacitor_SMD:C_1210_3225Metric'
LED = 'LED_SMD:LED_0603_1608Metric'
SWF = 'Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2'
HDR = 'Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical'
SOT23 = 'Package_TO_SOT_SMD:SOT-23'

PARTS = {}


def part(ref, lib, sym, val, fp, nets, pos, mpn=None):
    PARTS[ref] = (lib, sym, val, fp, nets, tuple(pos) + (0,) * (3 - len(pos)), mpn or val)


def R(ref, val, a, b, pos):
    part(ref, 'Device', 'R', val, R0603, {'1': a, '2': b}, pos, val + ' 1% 0603')


def C(ref, val, a, b, pos, fp=C0603, mpn=None):
    part(ref, 'Device', 'C', val, fp, {'1': a, '2': b}, pos, mpn or val + ' X7R ' + fp[-16:-12])


def CONN(ref, n, val, nets, pos):
    part(ref, 'Connector', 'Conn_01x%02d_Pin' % n, val, HDR % n,
         {str(i + 1): x for i, x in enumerate(nets)}, pos, '2.54mm 1x%d header' % n)


# --- input protection: 12V adapter, 9-16V --------------------------------------
part('J1', 'Connector', 'Barrel_Jack_Switch', '12V IN', 'Connector_BarrelJack:BarrelJack_CUI_PJ-063AH_Horizontal',
     {'1': 'VIN_RAW', '2': 'GND', '3': 'GND'}, (-30, 11.8, 270), 'CUI PJ-063AH')
part('F1', 'Device', 'Polyfuse', '3A', 'Fuse:Fuse_1812_4532Metric', {'1': 'VIN_RAW', '2': 'VIN_FUSED'}, (-21.5, 5.8, 0), 'PTC 1812 hold 3A, >=16V')
part('D1', 'Device', 'D_TVS', 'SMBJ16A', 'Diode_SMD:D_SMB', {'1': 'GND', '2': 'VIN_FUSED'}, (-21.5, 10.8, 0), 'SMBJ16A')
part('Q1', 'Transistor_FET', 'SUD50P06-15', 'SUD50P06-15', 'Package_TO_SOT_SMD:TO-252-2',
     {'1': 'Q1_G', '2': 'VIN_FUSED', '3': 'VIN_P'}, (-13.5, 8, 90), 'SUD50P06-15')
part('D2', 'Device', 'D_Zener', '12V', 'Diode_SMD:D_SOD-123', {'1': 'VIN_P', '2': 'Q1_G'}, (-21.5, 14.3, 0), 'BZT52C12 12V zener')
R('R1', '100k', 'Q1_G', 'GND', (-25.4, 14.3))
# --- servo buck: TI SLVSF00 section 8.2.2 values ----------------------------
part('U1', 'Regulator_Switching', 'TPS54560BDDA', 'TPS54560B', 'Package_SO:Texas_R-PDSO-G8_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias',
     {'1': 'BOOT', '2': 'VIN_P', '3': 'BUCK_EN', '4': 'RT', '5': 'FB', '6': 'COMP', '7': 'GND', '8': 'SW', '9': 'GND'}, (-28.5, 26, 0), 'TPS54560BDDAR')
C('C1', '4.7uF', 'VIN_P', 'GND', (-37.2, 29.4, 270), C1210, '4.7uF 50V X7R 1210')
C('C2', '4.7uF', 'VIN_P', 'GND', (-34, 29.4, 270), C1210, '4.7uF 50V X7R 1210')
C('C4', '100nF', 'BOOT', 'SW', (-29.6, 21.6, 0), C0603, '100nF 16V X7R 0603')
R('R2', '442k', 'VIN_P', 'BUCK_EN', (-30, 32.3))
R('R3', '78.7k', 'BUCK_EN', 'GND', (-26, 32.3))
R('R4', '243k', 'RT', 'GND', (-30, 34.3))
R('R5', '16.9k', 'COMP', 'COMP_RC', (-21.5, 30.3))
C('C5', '4.7nF', 'COMP_RC', 'GND', (-21.5, 32.3))
C('C6', '47pF', 'COMP', 'GND', (-21.5, 34.3))
R('R6', '53.6k', '+5V_BUCK', 'FB', (-17.5, 32.3))
R('R7', '10.2k', 'FB', 'GND', (-17.5, 34.3))
part('D3', 'Device', 'D_Schottky', 'B340B', 'Diode_SMD:D_SMB', {'1': 'SW', '2': 'GND'}, (-22.4, 20.5, 90), 'B340B 40V 3A')
part('L1', 'Device', 'L', '6.8uH', 'Inductor_SMD:L_Bourns-SRN8040_8x8.15mm', {'1': 'SW', '2': '+5V_BUCK'}, (-15, 24, 0), '6.8uH Isat>=5A 8x8mm')
for i, y in enumerate((20.8, 24.5, 28.2)):
    C('C%d' % (7 + i), '47uF', '+5V_BUCK', 'GND', (-7.4, y, 0), C1210, '47uF 10V X5R 1210')
part('R8', 'Device', 'R', '10m', 'Resistor_SMD:R_2512_6332Metric', {'1': '+5V_BUCK', '2': 'VSERVO'}, (-9.5, 35, 270), '10mR 1% 2W 2512')
part('U4', 'Sensor_Energy', 'INA219AxD', 'INA219', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
     {'1': 'GND', '2': '+3V3', '3': 'SDA', '4': 'SCL', '5': '+3V3', '6': 'GND', '7': 'VSERVO', '8': '+5V_BUCK'}, (-2.5, 36, 0), 'INA219AIDR')
C('C10', '100nF', '+3V3', 'GND', (-2.5, 40.5, 0))
part('C11', 'Device', 'C_Polarized', '470uF', 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm', {'1': 'VSERVO', '2': 'GND'}, (-15, 55, 90), '470uF 10V low-ESR D8')
C('C29', '22uF', 'VSERVO', 'GND', (-6.9, 48, 0), C0805, '22uF 10V X5R 0805')
C('C30', '22uF', 'VSERVO', 'GND', (-6.9, 51, 0), C0805, '22uF 10V X5R 0805')
# --- servo enable / e-stop --------------------------------------------------
part('Q2', 'Transistor_FET', '2N7002', '2N7002', SOT23, {'1': 'EN_KILL', '2': 'GND', '3': 'BUCK_EN'}, (-36.5, 34.5, 0), '2N7002')
part('Q3', 'Transistor_FET', '2N7002', '2N7002', SOT23, {'1': 'SERVO_EN', '2': 'ESTOP', '3': 'EN_KILL'}, (-36.5, 38.5, 0), '2N7002')
R('R9', '100k', 'VIN_L', 'EN_KILL', (-30, 36.3))
part('D4', 'Device', 'D_Zener', '4V7', 'Diode_SMD:D_SOD-123', {'1': 'EN_KILL', '2': 'GND'}, (-26, 36.3, 0), 'BZT52C4V7 zener')
R('R10', '100k', 'SERVO_EN', 'GND', (-22, 36.3))
# --- logic supply: isolated from the servo buck by D5 + hold-up --------------
part('D5', 'Device', 'D_Schottky', 'SS34', 'Diode_SMD:D_SMA', {'1': 'VIN_L', '2': 'VIN_P'}, (-3.5, 17.4, 180), 'SS34')
part('C12', 'Device', 'C_Polarized', '100uF', 'Capacitor_SMD:CP_Elec_6.3x7.7', {'1': 'VIN_L', '2': 'GND'}, (-3.2, 11.4, 270), '100uF 25V')
C('C13', '10uF', 'VIN_L', 'GND', (1.5, 11, 90), C1206, '10uF 25V X7R 1206')
part('U2', 'Regulator_Switching', 'AP63205WU', 'AP63205', 'Package_TO_SOT_SMD:TSOT-23-6',
     {'1': '+5V', '2': 'VIN_L', '3': 'VIN_L', '4': 'GND', '5': 'SW2', '6': 'BST2'}, (-0.6, 20.8, 0), 'AP63205WU-7')
C('C14', '100nF', 'BST2', 'SW2', (-4.2, 21.4, 90))
part('L2', 'Device', 'L', '4.7uH', 'Inductor_SMD:L_Bourns-SRN4018', {'1': 'SW2', '2': '+5V'}, (-0.5, 25, 0), '4.7uH Isat>=3A 4x4mm')
C('C15', '22uF', '+5V', 'GND', (-0.5, 29, 0), C0805, '22uF 10V X5R 0805')
C('C16', '22uF', '+5V', 'GND', (-0.5, 31, 0), C0805, '22uF 10V X5R 0805')
part('D6', 'Device', 'D_Schottky', 'SS14', 'Diode_SMD:D_SMA', {'1': '+5V', '2': 'VBUS'}, (34.5, 27.8, 180), 'SS14')
part('U3', 'Regulator_Linear', 'AMS1117-3.3', 'AMS1117-3.3', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
     {'1': 'GND', '2': '+3V3', '3': '+5V'}, (8, 34.2, 0), 'AMS1117-3.3')
C('C17', '22uF', '+3V3', 'GND', (6, 39.4, 0), C0805, '22uF 10V X5R 0805')
C('C18', '10uF', '+3V3', 'GND', (10, 39.4, 0), C0805, '10uF 10V X5R 0805')
part('FB1', 'Device', 'FerriteBead', '600R', 'Inductor_SMD:L_0805_2012Metric', {'1': '+3V3', '2': '3V3_S'}, (15, 37, 0), '600R@100MHz 0805')
C('C19', '10uF', '3V3_S', 'GND', (19, 37, 0), C0805, '10uF 10V X5R 0805')
part('F2', 'Device', 'Polyfuse', '500mA', 'Fuse:Fuse_1206_3216Metric', {'1': '+5V', '2': '5V_S'}, (15, 34, 0), 'PTC 1206 hold 500mA')
C('C20', '10uF', '5V_S', 'GND', (19, 34, 0), C0805, '10uF 10V X5R 0805')
R('R11', '100k', 'VIN_P', 'VIN_SENSE', (-8.5, 13))
R('R12', '18k', 'VIN_SENSE', 'GND', (-8.5, 11))
C('C21', '100nF', 'VIN_SENSE', 'GND', (-8.5, 9))
# --- MCU -------------------------------------------------------------------
ESP = {'[1,15,38,39]': 'GND', '2': '+3V3', '3': 'EN', '4': 'ADC1', '5': 'ADC2', '7': 'VIN_SENSE', '8': 'ADC3', '9': 'ADC4',
       '10': 'SERVO_EN', '11': 'PCA_OE', '13': 'UART_TX', '16': 'UART_RX', '24': 'IO2', '25': 'IO0',
       '27': 'DIO1', '28': 'DIO2', '30': 'DIO3', '31': 'DIO4', '33': 'SDA', '34': 'ESP_RX', '35': 'ESP_TX', '36': 'SCL', '37': 'DIO5'}
part('U5', 'RF_Module', 'ESP32-WROOM-32E', 'ESP32-WROOM-32E', 'RF_Module:ESP32-WROOM-32E', ESP, (15, 12.75, 0), 'ESP32-WROOM-32E-N4')
C('C22', '10uF', '+3V3', 'GND', (3.5, 15.5, 90), C0805, '10uF 10V X5R 0805')
C('C23', '100nF', '+3V3', 'GND', (3.5, 12, 90))
R('R13', '10k', '+3V3', 'EN', (3.8, 19.5, 90))
C('C24', '1uF', 'EN', 'GND', (3.8, 22.5, 90))
part('SW1', 'Switch', 'SW_Push', 'EN', SWF, {'1': 'EN', '2': 'GND'}, (35.5, 42, 0), 'CK KMR2')
part('SW2', 'Switch', 'SW_Push', 'BOOT', SWF, {'1': 'IO0', '2': 'GND'}, (29.5, 42, 0), 'CK KMR2')
R('R14', '1k', 'IO2', 'LED_STAT', (13.2, 39.4))
part('D7', 'Device', 'LED', 'STAT', LED, {'1': 'GND', '2': 'LED_STAT'}, (13.2, 37.6, 0), 'LED 0603 blue')
R('R15', '1k', '+3V3', 'LED_3V3', (22, 37.6))
part('D8', 'Device', 'LED', '3V3', LED, {'1': 'GND', '2': 'LED_3V3'}, (22, 39.6, 0), 'LED 0603 green')
R('R16', '1k', 'VSERVO', 'LED_SERVO', (-5, 42.5))
part('D9', 'Device', 'LED', 'SERVO', LED, {'1': 'GND', '2': 'LED_SERVO'}, (-5, 44.5, 0), 'LED 0603 red')
# --- USB-UART ---------------------------------------------------------------
part('J3', 'Connector', 'USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
     {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
      'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_C_P', 'B6': 'USB_C_P', 'A7': 'USB_C_N', 'B7': 'USB_C_N'}, (36.8, 19.5, 90), 'HRO TYPE-C-31-M-12')
R('R17', '5.1k', 'CC1', 'GND', (29, 23.5))
R('R18', '5.1k', 'CC2', 'GND', (29, 15.5))
part('U6', 'Power_Protection', 'USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6',
     {'1': 'USB_C_P', '6': 'USB_DP', '3': 'USB_C_N', '4': 'USB_DN', '2': 'GND', '5': '+5V'}, (28, 19.5, 0), 'USBLC6-2SC6')
part('U7', 'Interface_USB', 'CH340C', 'CH340C', 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',
     {'1': 'GND', '2': 'ESP_RX', '3': 'ESP_TX', '4': '+3V3', '5': 'USB_DP', '6': 'USB_DN', '13': 'DTR', '14': 'RTS', '16': '+3V3'}, (27, 33, 0), 'CH340C')
C('C25', '100nF', '+3V3', 'GND', (33, 32, 90))
part('Q4', 'Transistor_BJT', 'MMBT3904', 'MMBT3904', SOT23, {'1': 'Q4_B', '2': 'RTS', '3': 'EN'}, (9, 28.4, 0), 'MMBT3904')
part('Q5', 'Transistor_BJT', 'MMBT3904', 'MMBT3904', SOT23, {'1': 'Q5_B', '2': 'DTR', '3': 'IO0'}, (20, 28.5, 0), 'MMBT3904')
R('R19', '10k', 'DTR', 'Q4_B', (12.2, 28.4, 90))
R('R20', '10k', 'RTS', 'Q5_B', (17, 28.5, 90))
# --- servo PWM --------------------------------------------------------------
pca = {'1': 'GND', '2': 'GND', '3': 'GND', '4': 'GND', '5': 'GND', '24': 'GND', '25': 'GND', '14': 'GND',
       '23': 'PCA_OE', '26': 'SCL', '27': 'SDA', '28': '+3V3'}
pca.update({str(6 + i): 'PWM%d' % i for i in range(5)})
part('U8', 'Driver_LED', 'PCA9685PW', 'PCA9685', 'Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm', pca, (-18.6, 41.6, 0), 'PCA9685PW')
C('C26', '100nF', '+3V3', 'GND', (-18.4, 35.8, 0))
C('C27', '10uF', '+3V3', 'GND', (-14.5, 35.8, 90), C0805, '10uF 10V X5R 0805')
R('R21', '10k', '+3V3', 'PCA_OE', (-12.7, 41.5))
R('R22', '4.7k', '+3V3', 'SDA', (-12.7, 43.5))
R('R23', '4.7k', '+3V3', 'SCL', (-12.7, 45.5))
buf = {'1': 'GND', '19': 'GND', '10': 'GND', '20': '+5V', '7': 'GND', '8': 'GND', '9': 'GND'}
for i in range(5):
    buf[str(6 - i)] = 'PWM%d' % i     # reversed so PWM, buffer and ports run without crossings
    buf[str(14 + i)] = 'SIG%d' % i
part('U9', '74xx', '74AHCT541', '74AHCT541', 'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm', buf, (-28, 41.6, 180), 'SN74AHCT541PWR')
C('C28', '100nF', '+5V', 'GND', (-33.2, 41, 90))
PITCH = 2.54
ROW = 52.5
for i in range(5):
    x = -31.5 + PITCH * i
    R('R%d' % (24 + i), '220', 'SIG%d' % i, 'S%d' % (i + 1), (x, 48.3, 90))
    part('J%d' % (4 + i), 'Connector', 'Conn_01x03_Pin', 'SERVO%d' % (i + 1), HDR % 3,
         {'1': 'S%d' % (i + 1), '2': 'VSERVO', '3': 'GND'}, (x, ROW, 0), '2.54mm 1x3 header')
# --- sensor ports: same S/+/- row order as the servos -----------------------
for i in range(5):
    x = 1 + PITCH * i
    n = 'DIO%d' % (i + 1)
    R('R%d' % (30 + i), '1k', n + '_P', n, (x, 48, 90))
    R('R%d' % (35 + i), '10k', '3V3_S', n + '_P', (x, 45, 90))
    C('C%d' % (34 + i), '100nF', n, 'GND', (x, 42, 90))
    CONN('J%d' % (9 + i), 3, n, [n + '_P', '3V3_S', 'GND'], (x, ROW, 0))
for i in range(4):
    x = 15 + PITCH * i
    n = 'ADC%d' % (i + 1)
    R('R%d' % (40 + i), '1k', n + '_P', n, (x, 48, 90))
    C('C%d' % (39 + i), '100nF', n, 'GND', (x, 45, 90))
    CONN('J%d' % (14 + i), 3, n, [n + '_P', '3V3_S', 'GND'], (x, ROW, 0))
CONN('J18', 4, 'I2C1', ['GND', '3V3_S', 'SCL', 'SDA'], (26.5, 50, 0))
CONN('J19', 4, 'I2C2', ['GND', '3V3_S', 'SCL', 'SDA'], (29.04, 50, 0))
CONN('J20', 4, 'UART', ['GND', '5V_S', 'UART_TX', 'UART_RX'], (31.58, 50, 0))
CONN('J21', 2, 'ESTOP', ['ESTOP', 'GND'], (36.2, 47.5, 0))
for i, (x, y) in enumerate(((-37, 57), (37.4, 57), (37, 10), (-37, 3.2))):
    part('H%d' % (i + 1), 'Mechanical', 'MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', {}, (x, y, 0), 'M3 hole')

# Lower band sits 4 mm further down: it was laid out first and shifted to give the logic room.
for ref, p_ in list(PARTS.items()):
    x_, y_, r_ = p_[5]
    if y_ >= 37.5:
        PARTS[ref] = p_[:5] + ((x_, y_ + 4, r_),) + p_[6:]

# Copper pours for high-current nets: polygons in board coordinates, top layer.
POURS = {
    'VIN_RAW': [(-31.2, 4), (-22.8, 4), (-22.8, 7.7), (-26.8, 7.7), (-26.8, 14), (-31.2, 14)],
    'VIN_FUSED': [(-20.6, 3.2), (-10.4, 3.2), (-10.4, 10.4), (-17, 10.4), (-17, 12.4), (-20.6, 12.4)],
    'VIN_P': [(-12.4, 11.7), (-10, 11.7), (-10, 15.2), (-4.3, 15.2), (-4.3, 18.2), (-6.9, 18.2), (-6.9, 16.8), (-34, 16.8), (-34, 25.1), (-31.7, 25.1),
              (-31.7, 25.75), (-32.4, 25.75), (-32.4, 28.6), (-38.6, 28.6), (-38.6, 17.5), (-34.9, 17.5), (-34.9, 15.2), (-12.4, 15.2)],
    'SW': [(-23.9, 21.3), (-16.6, 21.3), (-16.6, 26.6), (-24.3, 26.6), (-24.3, 24.7), (-26.4, 24.7), (-26.4, 23.8), (-23.9, 23.8)],
    '+5V_BUCK': [(-13.6, 18.5), (-8.3, 18.5), (-8.3, 32.8), (-13.6, 32.8)],
    'VSERVO': [(-11.2, 37.2), (-7.8, 37.2), (-7.8, 60.2), (-33, 60.2), (-33, 57.9), (-11.2, 57.9)],
    '3V3_S': [(-0.5, 57.9), (23.8, 57.9), (23.8, 60.2), (-0.5, 60.2)],
}
WIDE = {'+5V': 0.6, '+3V3': 0.5, 'VIN_L': 0.6, 'VBUS': 0.4, '3V3_S': 0.4, '5V_S': 0.4, 'SW2': 0.6, 'VIN_P': 0.6}
