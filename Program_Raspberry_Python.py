import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

# Ustawienia GPIO
FAN1_PIN = 17  # Pin sterujący wentylatorem w kuchni (przekaźnik 1)
FAN2_PIN = 27  # Pin sterujący wentylatorem w garażu (przekaźnik 2)
GATE_SENSOR_PIN = 22  # Pin czujnika stanu bramy

# MQTT konfiguracja
MQTT_BROKER = "IP_TWOJEGO_BROKERA_MQTT"
MQTT_PORT = 1883
MQTT_TOPIC_FAN1 = "home/kitchen/fan1"
MQTT_TOPIC_FAN2 = "home/garage/fan2"
MQTT_TOPIC_GATE = "home/gate/status"

# Konfiguracja GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(FAN1_PIN, GPIO.OUT)
GPIO.setup(FAN2_PIN, GPIO.OUT)
GPIO.setup(GATE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Funkcje do sterowania wentylatorami
def fan1_on():
    GPIO.output(FAN1_PIN, GPIO.HIGH)

def fan1_off():
    GPIO.output(FAN1_PIN, GPIO.LOW)

def fan2_on():
    GPIO.output(FAN2_PIN, GPIO.HIGH)

def fan2_off():
    GPIO.output(FAN2_PIN, GPIO.LOW)

# MQTT callback dla wiadomości
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    if message.topic == MQTT_TOPIC_FAN1:
        if payload == "ON":
            fan1_on()
        elif payload == "OFF":
            fan1_off()
    elif message.topic == MQTT_TOPIC_FAN2:
        if payload == "ON":
            fan2_on()
        elif payload == "OFF":
            fan2_off()

# Inicjalizacja MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe([(MQTT_TOPIC_FAN1, 0), (MQTT_TOPIC_FAN2, 0)])

# Główna pętla
try:
    client.loop_start()
    while True:
        # Odczyt stanu bramy
        gate_open = GPIO.input(GATE_SENSOR_PIN) == GPIO.LOW  # LOW oznacza brama otwarta
        gate_status = "open" if gate_open else "closed"
        client.publish(MQTT_TOPIC_GATE, gate_status)

        # Wyłączanie wentylatorów, jeśli brama jest otwarta
        if gate_open:
            fan1_off()
            fan2_off()

        time.sleep(1)

except KeyboardInterrupt:
    print("Zatrzymano program")
    GPIO.cleanup()
    client.loop_stop()
