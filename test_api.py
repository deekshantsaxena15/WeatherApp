import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    print("ERROR: OPENWEATHER_API_KEY was not found.")
    print("Check your .env file.")
    raise SystemExit(1)


url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": "Jaipur,IN",
    "appid": API_KEY,
    "units": "metric",
}


try:
    response = requests.get(url, params=params, timeout=10)

    print(f"HTTP Status Code: {response.status_code}")

    data = response.json()

    if response.status_code == 200:
        print("\nAPI CONNECTION SUCCESSFUL!")
        print(f"City: {data['name']}")
        print(f"Temperature: {data['main']['temp']} °C")
        print(f"Humidity: {data['main']['humidity']}%")
        print(f"Weather: {data['weather'][0]['description']}")
        print(f"Wind Speed: {data['wind']['speed']} m/s")

    elif response.status_code == 401:
        print("\nERROR: Invalid or inactive API key.")

    elif response.status_code == 404:
        print("\nERROR: City not found.")

    else:
        print("\nAPI ERROR:")
        print(data)

except requests.exceptions.Timeout:
    print("\nERROR: Request timed out.")

except requests.exceptions.ConnectionError:
    print("\nERROR: Could not connect to OpenWeather.")

except requests.exceptions.RequestException as error:
    print(f"\nERROR: {error}")
    