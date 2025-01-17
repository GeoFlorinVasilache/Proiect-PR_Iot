#define AO_PIN A0  // Pin analogic pentru AO
#include <DHT.h>

#define DHTPIN 2          // Pinul la care este conectat senzorul DATA
#define DHTTYPE DHT11     // Tipul senzorului

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);  // Inițializează comunicația serială
  pinMode(AO_PIN, INPUT);
  dht.begin();
}

void loop() {
  int analogValue = analogRead(AO_PIN);  // Citește valoarea analogică
  float temperature = dht.readTemperature();
  // Verifică dacă citirea este validă
  if (isnan(temperature)) {
    Serial.println("Eroare la citirea senzorului!");
    return;
  }
  // Trimite datele către Raspberry Pi
  Serial.print("Umiditate: ");
  Serial.print(analogValue);  // Trimite valoarea pe o linie separată
  Serial.print(" ");
  Serial.print("Temperatura: ");
  Serial.println(temperature);

  Serial.flush();  // Asigură-te că datele sunt trimise complet

  delay(10000);  // Așteaptă 10 secunde înainte de a repeta
}
