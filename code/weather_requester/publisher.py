import os
import logging
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

class MQTTPublisher:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.username = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.topic = os.getenv("MQTT_TOPIC", "weather")
        self.client = mqtt.Client()

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        logging.debug(f"Connecting to MQTT broker {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, 60)

    def publish_weather_data(self, data):
        try:
            payload = json.dumps(data)
            logging.debug(f"Publishing to MQTT: {self.topic} - {payload}")
            self.client.publish(self.topic, payload)
        except Exception as e:
            logging.error(f"Error publishing to MQTT: {e}")
