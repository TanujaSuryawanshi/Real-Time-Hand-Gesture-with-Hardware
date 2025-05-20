int ledPin = 13;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    char data = Serial.read();
    if (data == '1') {
      digitalWrite(ledPin, HIGH);
    } else if (data == '0') {
      digitalWrite(ledPin, LOW);
    }
  }
}
