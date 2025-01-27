import os
from wsgiref import headers
import requests
import json
import time
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

if os.path.exists(".env"):
    print("Plik .env istnieje i zostanie załadowany.")
else:
    print("Brak pliku .env w bieżącym katalogu!")
print("API_KEY:", os.getenv("API_KEY"))
print("LOCATION:", os.getenv("LOCATION"))

logging.basicConfig(level=logging.DEBUG)
print("MQTT module:", mqtt)

class MQTTPublisher:
    def __init__(self, location):
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.username = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.topic = f"weather/{location}"  # Dynamiczny temat z lokalizacją
        self.client = mqtt.Client()

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        logging.debug(f"Connecting to MQTT broker {self.broker}:{self.port}")
        try:
            self.client.connect(self.broker, self.port, 60)
            logging.debug("Successfully connected to MQTT broker.")
        except Exception as e:
            logging.error(f"Error connecting to MQTT broker: {e}")

    def publish_weather_data(self, data):
        try:
            payload = json.dumps(data, indent=2)  # Sformatowane dane
            logging.debug(f"Publishing to MQTT: {self.topic} - {payload}")
            self.client.publish(self.topic, payload)
        except Exception as e:
            logging.error(f"Error publishing to MQTT: {e}")


class WeatherRequester:
    def __init__(self, location: str):
        """
        Konstruktor klasy WeatherRequester
        :param location: Nazwa lokalizacji do zapytania
        """
        logging.debug("WeatherRequester initialized.")
        self.location = location
        self.api_url = "https://api.openaq.org/v2/latest/"  # Endpoint OpenAQ
        self.api_key = os.getenv("API_KEY")  # Pobranie klucza API ze zmiennej środowiskowej

        logging.debug(f"API Key: {self.api_key}")
        logging.debug(f"Location: {self.location}")

        if not self.api_key:
            raise ValueError("Klucz API nie został ustawiony. Dodaj go do zmiennej środowiskowej 'API_KEY'.")

    def fetch_weather_data(self):
        """
        Pobiera dane pogodowe dla zdefiniowanej lokalizacji.
        :return: Dane w formacie JSON
        """
        try:
            # Poprawna konstrukcja URL z separatorami
            logging.debug("Sending request to API...")
            headers = {"X-API-Key": self.api_key}
            url = f"{self.api_url}{self.location}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"API response: {data}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"Błąd podczas pobierania danych z API: {e}")
            logging.error(f"Błąd podczas pobierania danych z API: {e}")
            return None

        
    def format_and_print(self, weather_data):
        """
        Formatuje i printuje dane pogodowe jako JSON.
        :param weather_data: Dane pogodowe z API
        """
        if not weather_data or "results" not in weather_data:
            print("No data available for the specified location.")
            logging.error("No data available for the specified location.")
            return

        formatted_data = {
            "location": self.location,
            "timestamp": datetime.utcnow().isoformat(),
            "values": [
                {measurement["parameter"]: measurement["value"]}
                for result in weather_data["results"]
                for measurement in result["measurements"]
            ]
        }

        data_to_send = json.dumps(formatted_data, indent=2)
        print(data_to_send)
        logging.debug(f"Formatted data: {data_to_send}")
    def run(self):
        logging.debug("Starting cyclic requests...")
        mqtt_publisher = MQTTPublisher(self.location)  # Zainicjalizowanie klasy publikatora MQTT
        while True:
            weather_data = self.fetch_weather_data()
            self.format_and_print(weather_data)
            mqtt_publisher.publish_weather_data(weather_data)  # Publikowanie danych
            time.sleep(30)


if __name__ == "__main__":
    # Pobranie lokalizacji z zmiennej środowiskowej lub ustawienie domyślnej wartości
    location = os.getenv("LOCATION", "10776")
    logging.debug(f"Starting WeatherRequester with location: {location}")
    requester = WeatherRequester(location)
    requester.run()
