from flask import Flask, render_template_string
import paho.mqtt.client as mqtt
from datetime import datetime
import re
import ssl

app = Flask(__name__)

# Variabilă globală pentru stocarea datelor
humidity_data = []

# Callback când clientul MQTT primește un mesaj
def on_message(client, userdata, message):
    try:
        if message.payload.decode('latin-1') == "Nu sunt date disponibile":
            humidity_data.append({"time": datetime.now().strftime("%H:%M:%S"), "value": "Nu sunt date disponibile!", "temperature": "Nu sunt date disponibile!"})
        else:
            match = re.search(r"(\d+)", message.payload.decode('latin-1'))
            matc1 = re.search(r'(\d+\.\d+)', message.payload.decode('latin-1'))
            if match and matc1:
                humidity = float(match.group())
                humidity = float(humidity / 10)  # Conversie la procente
                timestamp = datetime.now().strftime("%H:%M:%S")
                temperature = float(matc1.group(1))
                humidity_data.append({"time": timestamp, "value": humidity, "temperature": temperature})

        # Păstrăm doar ultimele 10 măsurători
        if len(humidity_data) > 10:
            humidity_data.pop(0)
    except:
        print("Eroare la procesarea mesajului")

# Setarea clientului MQTT
broker = "localhost"
port = 8883  # Port pentru MQTT cu SSL
topic = "umiditate"

# Căile către certificate (actualizează cu căile tale Windows)
ca_cert = "C:/Users/Home/OneDrive/Desktop/Proiect/chei/ca.crt"
client_cert = "C:/Users/Home/OneDrive/Desktop/Proiect/chei/client.crt"
client_key = "C:/Users/Home/OneDrive/Desktop/Proiect/chei/client.key"

# Setarea clientului MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

# Configurare SSL/TLS
mqtt_client.tls_set(
    ca_certs=ca_cert,
    certfile=client_cert,
    keyfile=client_key,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS,
    ciphers=None
)

# Dezactivăm verificarea hostname-ului pentru certificate self-signed
mqtt_client.tls_insecure_set(True)

# Conectare la broker
mqtt_client.connect(broker, port, 60)
mqtt_client.subscribe("umiditate")
mqtt_client.loop_start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitor Umiditate</title>
    <meta charset="utf-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(rgba(255,255,255,0.5), rgba(255,255,255,0.5)),
                        url('/static/images/clouds.jpg') no-repeat center center fixed;
            background-size: cover;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .device-image {
            width: 150px;
            height: 150px;
            object-fit: contain;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 30px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .chart-container {
            height: 200px;
            margin-top: 20px;
        }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/static/images/termometru.jpg" alt="Termometru" class="device-image">
            <h1>Monitor Umiditate si Temperatura în Timp Real</h1>
            <img src="/static/images/higrometru.jpg" alt="Higrometru" class="device-image">
        </div>

        <table>
            <tr>
                <th>Timp</th>
                <th>Umiditate (%)</th>
                <th>Temperatura (°C)</th>
            </tr>
            {% for data in humidity_data|reverse %}
            <tr>
                <td>{{ data.time }}</td>
                <td>{{ data.value }}</td>
                <td>{{ data.temperature }}</td>
            </tr>
            {% endfor %}
        </table>

        <div class="chart-container">
            <canvas id="humidityChart"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="temperatureChart"></canvas>
        </div>
    </div>

    <script>
        var ctx = document.getElementById('humidityChart').getContext('2d');

        function isCritical(value) {
            const critical_threshold_min = 20;
            const critical_threshold_max = 80;
            return value <= critical_threshold_min || value >= critical_threshold_max;
        }
        var humidityValues = {{ humidity_data|map(attribute='value')|list|tojson }};

        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ humidity_data|map(attribute='time')|list|tojson }},
                datasets: [{
                    label: 'Umiditate (%)',
                    data: {{ humidity_data|map(attribute='value')|list|tojson }},
                    borderColor: 'rgb(75, 192, 192)',
                    pointBackgroundColor: humidityValues.map(value => isCritical(value) ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)'), // Culoarea punctelor
                    pointBorderColor: humidityValues.map(value => isCritical(value) ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)'), // Granița punctelor
                    segment: {
                        borderColor: function(context) {
                            const currentIndex = context.p0DataIndex;
                            const nextValue = humidityValues[currentIndex + 1];
                            return nextValue !== undefined && isCritical(nextValue)
                                ? 'rgb(255, 99, 132)' // Segment roșu dacă următorul punct este critic
                                : 'rgb(75, 192, 192)'; // Segment albastru în caz contrar
                        }
                    },
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                animation: false
            }
        });
    </script>

    <script>
        var ctx = document.getElementById('temperatureChart').getContext('2d');

        function isCritical(value) {
            const critical_threshold_min = 18;
            const critical_threshold_max = 28;
            return value <= critical_threshold_min || value >= critical_threshold_max;
        }
        var temperatureValues = {{ humidity_data|map(attribute='temperature')|list|tojson }};

        var chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ humidity_data|map(attribute='time')|list|tojson }},
                datasets: [{
                    label: 'Temperatura (°C)',
                    data: {{ humidity_data|map(attribute='temperature')|list|tojson }},
                    borderColor: 'rgb(75, 192, 192)',
                    pointBackgroundColor: temperatureValues.map(value => isCritical(value) ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)'), // Culoarea punctelor
                    pointBorderColor: temperatureValues.map(value => isCritical(value) ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)'), // Granița punctelor
                    segment: {
                        borderColor: function(context) {
                            const currentIndex = context.p0DataIndex;
                            const nextValue = temperatureValues[currentIndex + 1];
                            return nextValue !== undefined && isCritical(nextValue)
                                ? 'rgb(255, 99, 132)' // Segment roșu dacă următorul punct este critic
                                : 'rgb(75, 192, 192)'; // Segment roșu în caz contrar
                        }
                    },
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                animation: false
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, humidity_data=humidity_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
