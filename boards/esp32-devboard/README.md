<p align="center">
  <img src="docs/pcb_top.png" width="300" alt="ESP32 Dev Board ด้านบน">
  <img src="docs/pcb_bottom.png" width="300" alt="ESP32 Dev Board ด้านหลัง">
</p>

<h1 align="center">ESP32 Dev Board</h1>

<p align="center">บอร์ดพัฒนา ESP32-WROOM-32E ขนาด 29 × 54.6 มม. เสียบ breadboard ได้</p>

## บอร์ดนี้คืออะไร

บอร์ดพัฒนาทั่วไปสำหรับเรียนรู้ ทดลอง และทำต้นแบบ เสียบ USB-C แล้วอัปโหลดโค้ดได้เลย
เพราะมีวงจร auto-reset ไม่ต้องกดปุ่มเอง

## เหมาะกับงานแบบไหน

- เรียนรู้ ESP32 ด้วย Arduino หรือ PlatformIO
- ทำต้นแบบ IoT, Wi-Fi และ Bluetooth
- ใช้สอนในห้องเรียนหรือเวิร์กช็อป

## สเปก

| รายการ | ค่า |
|---|---|
| ขนาด | 29 × 54.6 มม. PCB 2 ชั้น |
| โมดูล | ESP32-WROOM-32E |
| USB | USB-C ผ่าน CH340C พร้อม auto-reset |
| ไฟเลี้ยง | 5V ผ่าน SS14 และ AMS1117-3.3 |
| ปุ่มและไฟ | EN, BOOT, LED PWR, LED IO2 |
| ขา I/O | header 17 ขา 2 แถว ห่างกัน 25.4 มม. |

## วงจร

![วงจร ESP32 Dev Board](docs/schematic.png)

ดูแบบซูมได้ที่ [schematic.pdf](docs/schematic.pdf)

> สถานะ: มี Gerber ใน [`fab/`](fab) ไม่มี DRC error แต่ยังไม่ได้ทดสอบกับบอร์ดจริง
> ERC มี error 1 รายการโดยตั้งใจ จากขา V3 ของ CH340C ที่ต่อกับ VCC ตาม datasheet
