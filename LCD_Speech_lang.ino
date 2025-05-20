#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); // Check your LCD I2C address

String receivedText = "";

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Waiting...");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(receivedText);
      receivedText = "";
    } else {
      receivedText += c;
    }
  }
}
