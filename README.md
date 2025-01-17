# Proiect-PR_Iot
Proiectul consta in realizarea unui sistem ce depisteaza temperatura din aer si umiditatea din sol intr-o sera, date ce sunt trimise si afisate de un server.
Poriectul contine fisierul cu codul incarcat pe arduino, placuta doar citeste pe pinul serial
date de la senzorul HW-103 si pe un pin digital datele de la senzorul de temperatura si le trasmite pe interfata seriala la raspberry.
Fisierul cu codul incarcat pe raspberry foloseste o biblioteca de client mqtt, si cuprinde functia de receptie de pe port-ul USB, a datelor trasmise de arduino, 
si publicare acestora pe topicul "umiditate" , si bineinteles functia de conectare la broker-ul Mosquitto rulat local pe PC.
Comanda cu care este initializat broker-ul: mosquitto -v -c “C:\Program Files\mosquitto\mosquitto.conf”.
Am folosit SSL pentru a cripta traficul pe care rasbery il transmite la broker si pe care clientul/server-ul il citeste de la broker.
