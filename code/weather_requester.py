import os
import time
import json
import requests
from datetime import datetime

class WeatherRequester:
    def __init__(self, location):
        self.location = location
        self.api_url = "https://api.openaq.org/v2/latest"
    
    def fetch_data(self):
        try:
            response = requests.get(self.api_url, params={"city": self.location})
            response.raise_for_status()
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                measurements = [
                    {measurement["parameter"]: measurement["value"]}
                    for measurement in data["results"][0]["measurements"]
                ]
                return {
                    "location": self.location,
                    "timestamp": datetime.now().isoformat(),
                    "values": measurements,
                }
            else:
                return {
                    "location": self.location,
                    "timestamp": datetime.now().isoformat(),
                    "values": [{"error": "No data available"}],
                }
        except Exception as e:
            return {
                "location": self.location,
                "timestamp": datetime.now().isoformat(),
                "values": [{"error": str(e)}],
            }

    def start_polling(self):
        while True:
            data = self.fetch_data()
            data_to_send = json.dumps(data, indent=4)
            print(data_to_send)
            time.sleep(30)

if __name__ == "__main__":
    location = os.getenv("LOCATION", "Warsaw")  # Default to Warsaw if not set
    requester = WeatherRequester(location)
    requester.start_polling()