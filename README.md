<p align="center">
  <img src="assets/pkt-logo.png" alt="PKT POKOTEAM" width="420">
</p>

<h1 align="center">PKT ESP32 Boards</h1>

<p align="center">
  ชุดบอร์ด ESP32 ของ <b>POKOTEAM</b> ออกแบบด้วย KiCad 10 และสร้างจากสคริปต์ทั้งหมด
</p>

<p align="center">
  <img src="https://img.shields.io/badge/KiCad-10-314CB0?style=flat-square" alt="KiCad 10">
  <img src="https://img.shields.io/badge/boards-3-0B7FC4?style=flat-square" alt="3 boards">
  <img src="https://img.shields.io/badge/PCB-2%20layers-5CC8F5?style=flat-square" alt="2-layer PCB">
</p>

---

## บอร์ดทั้งหมด

### PKT ESP32-C3 Mini

<img align="right" src="boards/c3-mini/docs/pcb_top.png" width="210" alt="PKT ESP32-C3 Mini">

บอร์ดไร้สายขนาดจิ๋ว 20 × 34 มม. เหมาะกับโหนด ESP-NOW, เซนเซอร์ไร้สาย และอุปกรณ์ในกล่องเล็ก
มี USB-C ในตัว ไฟเลี้ยงเป็น LDO ล้วน และมีโลโก้ PKT ด้านหลัง

- โมดูล ESP32-C3-MINI-1
- อุปกรณ์ SMD ด้านเดียว สั่ง PCBA ผ่าน JLCPCB ได้
- **สถานะ:** ไฟล์พร้อมสั่ง

[ดูรายละเอียดและวงจร](boards/c3-mini)

<br clear="right">

### ESP32 Dev Board

<img align="right" src="boards/esp32-devboard/docs/pcb_top.png" width="170" alt="ESP32 Dev Board">

บอร์ดพัฒนาขนาด 29 × 54.6 มม. สำหรับเรียนรู้และทำต้นแบบบน breadboard
เสียบ USB-C แล้วอัปโหลดโค้ดได้เลย

- โมดูล ESP32-WROOM-32E
- CH340C พร้อมวงจร auto-reset
- **สถานะ:** มี Gerber

[ดูรายละเอียดและวงจร](boards/esp32-devboard)

<br clear="right">

### Robot Arm Controller

<img align="right" src="boards/arm-controller/docs/pcb_placement_top.png" width="300" alt="Robot Arm Controller">

บอร์ดควบคุมแขนกล 5 แกน ขนาด 80 × 64 มม. สำหรับ SG90/MG90S ใช้ adapter 12V
แยกไฟ servo กับ logic มี E-stop และวัดกระแสได้

- PCA9685 + 74AHCT541 + TPS54560B + INA219
- พอร์ต DIO, ADC, I2C และ UART
- **สถานะ:** วงจรเสร็จ เดินลายยังไม่เสร็จ ยังสั่งผลิตไม่ได้

[ดูรายละเอียดและวงจร](boards/arm-controller)

<br clear="right">

> ยังไม่มีบอร์ดใดผ่านการทดสอบกับของจริง ตรวจด้วย ERC และ DRC ของ KiCad แล้วเท่านั้น

## โครงสร้าง repo

```text
PKT-ESP32-Boards
├── assets/                  โลโก้
└── boards/
    ├── c3-mini/             PKT ESP32-C3 Mini
    ├── esp32-devboard/      ESP32 Dev Board
    └── arm-controller/      Robot Arm Controller
```

แต่ละบอร์ดมีโครงสร้างเดียวกัน

| โฟลเดอร์ | เนื้อหา |
|---|---|
| `docs/` | ภาพวงจร ภาพบอร์ด และคำอธิบาย |
| `fab/` | Gerber, BOM, ตำแหน่งอุปกรณ์ และรายงาน ERC/DRC |
| `tools/` | สคริปต์สร้าง schematic และ PCB จาก `design.py` |

## Branch

| Branch | ใช้ทำอะไร |
|---|---|
| `main` | รวมทุกบอร์ด |
| `board/c3-mini` | งานของ ESP32-C3 Mini เท่านั้น |
| `board/esp32-devboard` | งานของ Dev Board เท่านั้น |
| `board/arm-controller` | งานของ Arm Controller เท่านั้น |

แก้บอร์ดไหนให้ทำใน branch ของบอร์ดนั้น แล้วค่อย merge เข้า `main`

## วิธีเปิดและสั่งผลิต

เปิดไฟล์ `.kicad_pro` ของบอร์ดใน KiCad 10

สั่ง C3 Mini ผ่าน JLCPCB ตามขั้นตอนใน [HOW_TO_ORDER.txt](boards/c3-mini/fab/HOW_TO_ORDER.txt)

แก้แบบจาก `tools/design.py` แล้วรัน `tools/build.sh` ในบอร์ดที่มีสคริปต์นี้ สคริปต์ใช้ KiCad บน macOS ที่ `/Applications/KiCad`
