from urllib import response
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


## funtion search flights
def search_flights(query):
    url = "https://api.aviationstack.com/v1/flights"

    params = {"access_key": API_KEY, "limit": 5}
    response = requests.get(url, params=params)
    data = response.json()
    flights = []

    if "data" in data:
        for flight in data["data"][:5]:
            airline = flight.get("airline", {}).get("name", "unkonwn")
            depature = flight.get("depature", {}).get("airport", "unknown")
            arrival = flight.get("arrival", {}).get("airport", "unknown")
            status = flight.get("flight_status", {})

            flights.append(f"""
            Airline :{airline},
            Deparute :{depature}
            Arrivak : {arrival}
            Status : {status}
            """)
            return "\n".join(flights)
        
        
