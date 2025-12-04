// /*
//   ESP32 - MindWave Mobile 2 via HC-05 (UART2)

//   Mô tả:
//   - HC-05 kết nối với MindWave Mobile 2 (Bluetooth-to-Serial bridge).
//   - HC-05 TX -> ESP32 RX2 (GPIO 16 by default) ; HC-05 RX -> ESP32 TX2 (GPIO 17)
//   - Chương trình này đọc dữ liệu ThinkGear từ Serial2 (UART2), phân tích các gói
//     và in các trường chính lên Serial (USB) để xem trên Serial Monitor.

//   Lưu ý về chân UART2 (theo mặc định trên ESP32 Arduino):
//     - RX2 (U2RXD): GPIO16
//     - TX2 (U2TXD): GPIO17

//   Nếu bạn đã nối HC-05 tới chân khác, hãy chỉnh các tham số trong Serial2.begin.
// */

// #include <Arduino.h>

// // UART2 pins (thay đổi nếu bạn dùng chân khác)
// const int RX2_PIN = 16; // HC-05 TX -> ESP32 RX2
// const int TX2_PIN = 17; // HC-05 RX <- ESP32 TX2
// const int STATE_PIN = 5; // HC-05 STATE pin (nếu dùng, để kiểm tra kết nối Bluetooth)

// // Biến lưu trữ các chỉ số ThinkGear
// int poorSignal = -1;
// int attention = -1;
// int meditation = -1;
// int blink = -1;

// // Hàm phân tích ThinkGear từng byte (robust):
// // - Buffer toàn bộ payload, kiểm tra checksum (sum of payload bytes only).
// // - Sau khi checksum hợp lệ, duyệt payload theo phần tử: xử lý ExCode (0x55),
// //   các data code 1-byte (ví dụ 0x02,0x04,0x05,0x16) và các data code multi-byte
// //   (theo chuẩn ThinkGear: mã dài có 1 byte length tiếp theo).
// void parseThinkGearByte(uint8_t b) {
//   const int MAX_PAYLOAD = 170;
//   static int state = 0;
//   static uint8_t payload[MAX_PAYLOAD];
//   static int payload_length = 0;
//   static int payload_pos = 0;
//   static int checksum_acc = 0;

//   switch (state) {
//     case 0: // chờ 0xAA
//       if (b == 0xAA) state = 1;
//       break;
//     case 1: // chờ 2nd 0xAA
//       if (b == 0xAA) {
//         state = 2;
//       } else {
//         state = 0;
//       }
//       break;
//     case 2: // payload length
//       payload_length = b;
//       if (payload_length > 0 && payload_length <= MAX_PAYLOAD) {
//         payload_pos = 0;
//         checksum_acc = 0;
//         state = 3;
//       } else {
//         // invalid length, reset
//         state = 0;
//       }
//       break;
//     case 3: // nhận payload bytes
//       if (payload_pos < payload_length) {
//         payload[payload_pos++] = b;
//         checksum_acc += b; // sum only payload bytes
//         if (payload_pos >= payload_length) {
//           state = 4; // next byte will be checksum
//         }
//       } else {
//         // overflow or unexpected, reset
//         state = 0;
//       }
//       break;
//     case 4: // checksum byte
//       {
//         uint8_t calc = (uint8_t)(~checksum_acc & 0xFF);
//         if (b == calc) {
//           // checksum OK -> parse payload buffer
//           int i = 0;
//           while (i < payload_length) {
//             // handle ExCode chain
//             while (i < payload_length && payload[i] == 0x55) {
//               i++; // skip excode bytes
//             }
//             if (i >= payload_length) break;

//             uint8_t code = payload[i++];

//             // Single-byte value codes
//             if (code == 0x02 && i < payload_length) { // PoorSignal
//               poorSignal = payload[i++];
//             } else if (code == 0x04 && i < payload_length) { // Attention
//               attention = payload[i++];
//             } else if (code == 0x05 && i < payload_length) { // Meditation
//               meditation = payload[i++];
//             } else if (code == 0x16 && i < payload_length) { // Blink
//               blink = payload[i++];
//             } else {
//               // Multi-byte codes: next byte is length, then length bytes of data
//               if (i < payload_length) {
//                 uint8_t len = payload[i++];
//                 // skip len bytes (or process if needed)
//                 i += len;
//               } else {
//                 // malformed -> break
//                 break;
//               }
//             }
//           }
//         } else {
//           // checksum failed - ignore payload
//           //Serial.println("Checksum failed");
//         }
//         // reset state for next packet
//         state = 0;
//       }
//       break;
//   }
// }

// void setup() {
//   Serial.begin(115200);
//   pinMode(STATE_PIN, INPUT); // nếu dùng STATE pin để kiểm tra kết nối Bluetooth
//   while (!Serial) { delay(10); }
//   Serial.println("ESP32 MindWave via HC-05 (UART2) - Starting...");

//   // Khởi tạo Serial2 cho UART2 với baud mặc định của HC-05 (thường 9600 hoặc 57600)
//   // MindWave qua HC-05 thường chạy 57600, nhưng HC-05 mặc định là 9600.
//   // Chỉnh theo cấu hình HC-05 của bạn. Nếu không chắc, thử 9600 trước.
//   const unsigned long hc05Baud = 57600; // nếu HC-05 được set để nối với MindWave ở 57600
//   Serial2.begin(hc05Baud, SERIAL_8N1, RX2_PIN, TX2_PIN);

//   Serial.print("Serial2 begun at "); Serial.println(hc05Baud);
//   Serial.println("Waiting for data from MindWave (via HC-05)...");
//   pinMode(2, OUTPUT);
// }

// unsigned long lastPrint = 0;

// void loop() {
//   // while (Serial2.available()) {
//   //   uint8_t b = (uint8_t)Serial2.read();
//   //   parseThinkGearByte(b);
//   // }
//   // if( digitalRead(STATE_PIN) != HIGH) {
//   //   poorSignal = -1;
//   //   attention = -1;
//   //   meditation = -1;
//   //   blink = -1;
//   //   // HC-05 not connect 
//   // } 
//   // In các chỉ số lên Serial mỗi 1 giây
//   if (millis() - lastPrint > 500) {
//     poorSignal = random(0, 100); // Giả lập dữ liệu cho ví dụ
//     attention = random(0, 100);
//     meditation = random(0, 100);
//     blink = random(0, 1);
//     Serial.print(poorSignal); Serial.print(", ");
//     Serial.print(attention); Serial.print(", ");
//     Serial.print(meditation); Serial.print(", ");
//     Serial.println(blink);
//     digitalWrite(2, !digitalRead(2)); // Đảo LED để thấy hoạt động
//     lastPrint = millis();
//   }
// }


/*
  ESP32 - MindWave Mobile 2 via HC-05 (UART2)
  + Hiển thị lên LCD 16x2 I2C
*/

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

// ==== LCD I2C 16x2 ====
LiquidCrystal_I2C lcd(0x27, 16, 2);  
// Nếu không hiện → đổi sang: LiquidCrystal_I2C lcd(0x3F, 16, 2);

// UART2 pins
const int RX2_PIN = 16;
const int TX2_PIN = 17;
const int STATE_PIN = 5;

// ThinkGear values
int poorSignal = -1;
int attention = -1;
int meditation = -1;
int blink = -1;

void parseThinkGearByte(uint8_t b) {
  const int MAX_PAYLOAD = 170;
  static int state = 0;
  static uint8_t payload[MAX_PAYLOAD];
  static int payload_length = 0;
  static int payload_pos = 0;
  static int checksum_acc = 0;

  switch (state) {
    case 0:
      if (b == 0xAA) state = 1;
      break;

    case 1:
      if (b == 0xAA) state = 2;
      else state = 0;
      break;

    case 2:
      payload_length = b;
      if (payload_length > 0 && payload_length <= MAX_PAYLOAD) {
        payload_pos = 0;
        checksum_acc = 0;
        state = 3;
      } else state = 0;
      break;

    case 3:
      if (payload_pos < payload_length) {
        payload[payload_pos++] = b;
        checksum_acc += b;
        if (payload_pos >= payload_length) state = 4;
      } else state = 0;
      break;

    case 4:
      {
        uint8_t calc = (uint8_t)(~checksum_acc & 0xFF);
        if (b == calc) {
          int i = 0;
          while (i < payload_length) {
            while (i < payload_length && payload[i] == 0x55) i++;

            if (i >= payload_length) break;
            uint8_t code = payload[i++];

            if (code == 0x02 && i < payload_length)
              poorSignal = payload[i++];
            else if (code == 0x04 && i < payload_length)
              attention = payload[i++];
            else if (code == 0x05 && i < payload_length)
              meditation = payload[i++];
            else if (code == 0x16 && i < payload_length)
              blink = payload[i++];
            else {
              if (i < payload_length) {
                uint8_t len = payload[i++];
                i += len;
              } else break;
            }
          }
        }
        state = 0;
      }
      break;
  }
}

// ==== HIỂN THỊ LÊN LCD 16x2 ====
void displayOnLCD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("A:");
  lcd.print(attention);
  lcd.setCursor(7, 0);
  lcd.print(" M:");
  lcd.print(meditation);

  lcd.setCursor(0, 1);
  lcd.print("P:");
  lcd.print(poorSignal);
  lcd.setCursor(7, 1);
  lcd.print(" B:");
  lcd.print(blink);
}

unsigned long lastPrint = 0;

void setup() {
  Serial.begin(115200);
  pinMode(STATE_PIN, INPUT);
  pinMode(2, OUTPUT);

  // ==== LCD init ====
  lcd.begin();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("MindWave ESP32");
  lcd.setCursor(0, 1);
  lcd.print("LCD 16x2 Ready");

  // ==== UART2 init ====
  const unsigned long hc05Baud = 57600;
  Serial2.begin(hc05Baud, SERIAL_8N1, RX2_PIN, TX2_PIN);
  Serial.println("LCD + UART ready.");
}

void loop() {
  // Nếu dùng dữ liệu thật:
  // while (Serial2.available()) {
  //   parseThinkGearByte(Serial2.read());
  // }

  // Demo bằng random (như code của bạn)
  if (millis() - lastPrint > 500) {
    poorSignal = random(0, 100);
    attention  = random(0, 100);
    meditation = random(0, 100);
    blink      = random(0, 2);
// Dùng snprintf để định dạng chuỗi nhanh hơn
    char logBuffer[50];
    snprintf(logBuffer, 50, "%d,%d,%d,%d", 
             poorSignal, attention, meditation, blink);
    
    Serial.println(logBuffer); // Chỉ gọi Serial.println MỘT LẦN

    displayOnLCD();  // <-- hiển thị lên LCD

   // digitalWrite(2, !digitalRead(2));
    lastPrint = millis();
  }
}
