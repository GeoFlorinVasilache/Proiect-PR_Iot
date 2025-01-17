import paho.mqtt.client as mqtt
import random
import time
import serial
import ssl

# Configurația broker-ului (laptop)
broker = "192.168.63.241"  # Înlocuiește cu adresa IP a laptopului
port = 8883  # Portul broker-ului (implicit 1883)
topic = "umiditate"  # Topic-ul unde trimiți mesajele

ca_cert = "/home/artemis/Desktop/chei/ca.crt"
client_cert = "/home/artemis/Desktop/chei/client.crt"
client_key = "/home/artemis/Desktop/chei/client.key"

ser = serial.Serial('/dev/ttyACM0', 9600)  # Înlocuiește cu portul corect

# Funcția de callback pentru conectare
# def on_connect(client, userdata, flags, rc):
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Conectat cu succes la broker!")
    else:
        print(f"Eroare la conectare. Cod: {rc}")
        print(mqtt.connack_string(rc))

# Funcția de callback pentru publicare
# def on_publish(client, userdata, mid):
def on_publish(client, userdata, mid, reason_code=0, properties=None):
    print(f"Mesaj publicat cu ID: {mid}")

# # Configurare client MQTT
# client_id = f'python-mqtt-{random.randint(0, 1000)}'
# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
# client.on_connect = on_connect
# client.on_publish = on_publish

# # Conectare la broker
# client.connect(broker, port)

# Funcția de citire a umidității de la senzorul HW-103
def citeste_umiditate():
    if ser.in_waiting > 0:  # Verifică dacă există date disponibile
        line = ser.readline().decode('utf-8').strip()  # Citește și decodifică datele
        print(f"Date brute citite: {line}")  # Afișează datele brute
        return line
    else:
        print("Nu sunt date disponibile")  # Verifică dacă nu există date
        return "Nu sunt date disponibile"

# # Menține conexiunea și execută call-back-urile
# client.loop_start()

# try:
#     while True:
#         # Citește semnalul de la senzor
#         umiditate = citeste_umiditate()
#         print(f"Datele sunt: {umiditate}")
        
#         # Publică mesajul cu valoarea umidității pe topicul MQTT
#         client.publish(topic, f"{umiditate}")
        
#         # Așteaptă 10 secunde între publicări
#         time.sleep(10)

# except KeyboardInterrupt:
#     print("Program întrerupt de utilizator.")
# finally:
#     # Închide conexiunea MQTT
#     client.loop_stop()
#     client.disconnect()

try:
    # Configurare client MQTT
    client_id = f'python-mqtt-{random.randint(0, 1000)}'
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
    
    client.on_connect = on_connect
    client.on_publish = on_publish

    # Configurare SSL/TLS
    # client.tls_set(
    #     ca_certs=ca_cert,
    #     certfile=client_cert,
    #     keyfile=client_key,
    #     cert_reqs=ssl.CERT_REQUIRED,  # Modificat pentru a se potrivi cu require_certificate true
    #     tls_version=ssl.PROTOCOL_TLS,
    #     ciphers=None
    # )

    # client.tls_insecure_set(True)
    client.tls_set(
        ca_certs=ca_cert,
        certfile=client_cert,
        keyfile=client_key,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
        ciphers=None
    )
    client.tls_insecure_set(True)

    print("Încercare conectare la broker...")
    try:
        client.connect(broker, port, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"Eroare la conectare: {e}")
        raise e

    while True:
        try:
            umiditate = citeste_umiditate()
            print(f"Datele sunt: {umiditate}")
            
            result = client.publish(topic, f"{umiditate}", qos=1)
            result.wait_for_publish()
            
            time.sleep(10)

        except Exception as e:
            print(f"Eroare în timpul publicării: {e}")
            time.sleep(5)

except KeyboardInterrupt:
    print("Program întrerupt de utilizator.")
except Exception as e:
    print(f"Eroare generală: {e}")
    if 'client' in locals():
        client.loop_stop()
        client.disconnect()
    if 'ser' in locals():
        ser.close()
finally:
    print("Închidere conexiuni...")
    if 'client' in locals():
        client.loop_stop()
        client.disconnect()
    if 'ser' in locals():
        ser.close()
