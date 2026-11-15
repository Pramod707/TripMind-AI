from urllib import response
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


## function search flights
def search_flights(query, departure, arrival):
    url = "https://api.aviationstack.com/v1/flights"

    params = {
    "access_key": API_KEY,
    "dep_iata": departure,
    "arr_iata": arrival,
    "limit": 5
}
    response = requests.get(url, params=params)
    data = response.json()
    flights = []

    if "data" in data:
        for flight in data["data"][:5]:
            airline = flight.get("airline", {}).get("name", "unknown")

            # FIX 1: Corrected departure spelling
            departure = flight.get("departure", {}).get("airport", "unknown")

            arrival = flight.get("arrival", {}).get("airport", "unknown")
            status = flight.get("flight_status", "unknown")

            flights.append(f"""
            Airline: {airline}
            Departure: {departure}
            Arrival: {arrival}
            Status: {status}
            """)

        # FIX 2: Moved return outside the for loop
        return "\n".join(flights)

    # FIX 3: Return a message when no flight data exists
    return "No flight data available"