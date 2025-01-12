import os
import logging
import paho.mqtt.client as mqtt
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

class MQTTSubscriber:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.username = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.topic = os.getenv("MQTT_SUBSCRIBE_TOPIC", "weather/#")
        self.data_dir = os.getenv("DATA_DIR", "./data")
        self.client = mqtt.Client()

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

        logging.debug(f"Connecting to MQTT broker {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        logging.debug(f"Connected to MQTT broker with code {rc}")
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            logging.debug(f"Message received on topic {msg.topic}: {msg.payload}")
            topic_parts = msg.topic.split("/")
            file_name = f"{topic_parts[-2]}-{topic_parts[-1]}.json"
            file_path = Path(self.data_dir) / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(msg.payload.decode())
            logging.info(f"Saved data to {file_path}")
        except Exception as e:
            logging.error(f"Error saving message: {e}")

    def run(self):
        self.client.loop_forever()

if __name__ == "__main__":
    subscriber = MQTTSubscriber()
    subscriber.run()
