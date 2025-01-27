import os
import json
import logging
import paho.mqtt.client as mqtt
from pathlib import Path
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Ustawienie poziomu logowania
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class MQTTSubscriber:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.username = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.topic = os.getenv("MQTT_SUBSCRIBE_TOPIC", "weather/#")
        self.data_dir = os.getenv("DATA_DIR", "./data")
        self.client = mqtt.Client(transport="tcp")

        # Debugowanie konfiguracji
        logging.debug(f"Loaded configuration: "
                      f"MQTT_BROKER={self.broker}, MQTT_PORT={self.port}, "
                      f"MQTT_USER={self.username}, MQTT_PASSWORD={self.password}, "
                      f"MQTT_SUBSCRIBE_TOPIC={self.topic}, DATA_DIR={self.data_dir}")

        # Ustawienie danych uwierzytelniających, jeśli są podane
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # Przypisanie callbacków
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

        logging.debug(f"Connecting to MQTT broker {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"Successfully connected to MQTT broker {self.broker}:{self.port}")
            logging.debug(f"Subscribing to topic: {self.topic}")
            self.client.subscribe(self.topic)
        else:
            logging.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            logging.debug(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
            topic_parts = msg.topic.split("/")
            logging.debug(f"Topic parts: {topic_parts}")

            # Walidacja formatu tematu
            if len(topic_parts) < 1:
                logging.error(f"Invalid topic format: {msg.topic}")
                return

            # Generowanie nazwy pliku
            file_name = f"{topic_parts[-2]}-{topic_parts[-1]}.json" if len(topic_parts) > 1 else f"{topic_parts[0]}.json"
            file_path = Path(self.data_dir) / file_name

            # Tworzenie katalogu, jeśli nie istnieje
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Zapisywanie danych do pliku
            logging.debug(f"Saving data to {file_path}")
            with open(file_path, "w") as f:
                f.write(msg.payload.decode())
            logging.info(f"Saved data to {file_path}")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def run(self):
        try:
            logging.info("Starting MQTT subscriber loop...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            logging.info("MQTT subscriber stopped by user.")

if __name__ == "__main__":
    subscriber = MQTTSubscriber()
    subscriber.run()
