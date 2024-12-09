#define AO_PIN A0  // Pin analogic pentru AO

void setup() {
  Serial.begin(9600);  // Inițializează comunicația serială
  pinMode(AO_PIN, INPUT);
}

void loop() {
  int analogValue = analogRead(AO_PIN);  // Citește valoarea analogică

  // Trimite datele către Raspberry Pi
  Serial.print("Umiditate citita: ");
  Serial.println(analogValue);  // Trimite valoarea pe o linie separată

  Serial.flush();  // Asigură-te că datele sunt trimise complet

  delay(10000);  // Așteaptă 10 secunde înainte de a repeta
}
