from weather_api import (
    WeatherAPIError,
    get_current_weather,
    get_forecast,
    get_location,
)


def main() -> None:
    city = "Jaipur"

    try:
        print("Searching for location...")

        location = get_location(city)

        print("\nLOCATION")
        print("-" * 40)
        print(f"City:      {location['name']}")
        print(f"State:     {location['state']}")
        print(f"Country:   {location['country']}")
        print(f"Latitude:  {location['latitude']}")
        print(f"Longitude: {location['longitude']}")

        print("\nGetting current weather...")

        weather = get_current_weather(
            location["latitude"],
            location["longitude"],
        )

        print("\nCURRENT WEATHER")
        print("-" * 40)
        print(
            f"Temperature: "
            f"{weather['main']['temp']} °C"
        )
        print(
            f"Feels like:  "
            f"{weather['main']['feels_like']} °C"
        )
        print(
            f"Humidity:    "
            f"{weather['main']['humidity']}%"
        )
        print(
            f"Weather:     "
            f"{weather['weather'][0]['description']}"
        )
        print(
            f"Wind speed:  "
            f"{weather['wind']['speed']} m/s"
        )

        print("\nGetting forecast...")

        forecast = get_forecast(
            location["latitude"],
            location["longitude"],
        )

        print("\nFORECAST")
        print("-" * 40)
        print(
            f"Forecast entries received: "
            f"{len(forecast['list'])}"
        )

        print("\nFirst forecast:")

        first = forecast["list"][0]

        print(
            f"Temperature: "
            f"{first['main']['temp']} °C"
        )

        print(
            f"Weather: "
            f"{first['weather'][0]['description']}"
        )

        print("\nAPI LAYER WORKING!")

    except WeatherAPIError as error:
        print(
            f"\nWeather API Error: {error}"
        )


if __name__ == "__main__":
    main()