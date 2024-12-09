import paho.mqtt.client as mqtt
import random
import time
import serial

# Configurația broker-ului (laptop)
broker = "192.168.186.241"  # Înlocuiește cu adresa IP a laptopului
port = 1883  # Portul broker-ului (implicit 1883)
topic = "umiditate"  # Topic-ul unde trimiți mesajele

ser = serial.Serial('/dev/ttyACM0', 9600)  # Înlocuiește cu portul corect
print("gggg")

# Funcția de callback pentru conectare
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectat cu succes la broker!")
    else:
        print(f"Eroare la conectare. Cod: {rc}")

# Funcția de callback pentru publicare
def on_publish(client, userdata, mid):
    print(f"Mesaj publicat cu ID: {mid}")

# Configurare client MQTT
client_id = f'python-mqtt-{random.randint(0, 1000)}'
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
client.on_connect = on_connect
client.on_publish = on_publish

# Conectare la broker
client.connect(broker, port)

# Funcția de citire a umidității de la senzorul HW-103
def citeste_umiditate():
    if ser.in_waiting > 0:  # Verifică dacă există date disponibile
        line = ser.readline().decode('utf-8').strip()  # Citește și decodifică datele
        print(f"Date brute citite: {line}")  # Afișează datele brute
        return line
    else:
        print("Nu sunt date disponibile")  # Verifică dacă nu există date
        return "Nu sunt date disponibile"

# Menține conexiunea și execută call-back-urile
client.loop_start()

try:
    while True:
        # Citește semnalul de la senzor
        umiditate = citeste_umiditate()
        print(f"Umiditatea este: {umiditate}")
        
        # Publică mesajul cu valoarea umidității pe topicul MQTT
        client.publish(topic, f"Starea umidității este: {umiditate}")
        
        # Așteaptă 10 secunde între publicări
        time.sleep(10)

except KeyboardInterrupt:
    print("Program întrerupt de utilizator.")
finally:
    # Închide conexiunea MQTT
    client.loop_stop()
    client.disconnect()
