from datetime import datetime
from typing import Any


def parse_current_weather(data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert OpenWeather current-weather JSON
    into clean application data.
    """

    weather_info = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})
    system = data.get("sys", {})

    return {
        "city": data.get("name", "Unknown"),
        "country": system.get("country", ""),

        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "temp_min": main.get("temp_min"),
        "temp_max": main.get("temp_max"),

        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),

        "visibility": data.get("visibility"),

        "weather_main": weather_info.get("main"),
        "description": weather_info.get("description"),
        "icon": weather_info.get("icon"),

        "wind_speed": wind.get("speed"),
        "wind_direction": wind.get("deg"),

        "clouds": data.get("clouds", {}).get("all"),

        "sunrise": system.get("sunrise"),
        "sunset": system.get("sunset"),

        "timezone": data.get("timezone", 0),

        "timestamp": data.get("dt"),
    }


def parse_forecast(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert OpenWeather 5-day/3-hour forecast JSON
    into a clean list of forecast entries.
    """

    forecast_entries = []

    for item in data.get("list", []):
        weather_info = item["weather"][0]
        main = item["main"]
        wind = item.get("wind", {})

        forecast_entries.append(
            {
                "timestamp": item.get("dt"),

                "date_time": item.get(
                    "dt_txt",
                    "",
                ),

                "temperature": main.get("temp"),
                "feels_like": main.get("feels_like"),

                "temp_min": main.get("temp_min"),
                "temp_max": main.get("temp_max"),

                "humidity": main.get("humidity"),
                "pressure": main.get("pressure"),

                "weather_main": weather_info.get("main"),
                "description": weather_info.get("description"),
                "icon": weather_info.get("icon"),

                "wind_speed": wind.get("speed"),
                "wind_direction": wind.get("deg"),

                "clouds": item.get(
                    "clouds",
                    {},
                ).get("all"),

                "rain_3h": item.get(
                    "rain",
                    {},
                ).get("3h", 0),

                "pop": item.get("pop", 0),
            }
        )

    return forecast_entries


def get_next_forecast_entries(
    forecast: list[dict[str, Any]],
    count: int = 2,
) -> list[dict[str, Any]]:
    """
    Return the next few forecast entries.

    The free OpenWeather forecast provides data
    at approximately 3-hour intervals, so two
    entries represent roughly the next 6 hours.
    """

    return forecast[:count]


def group_forecast_by_date(
    forecast: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Group forecast entries by calendar date.
    """

    grouped: dict[str, list[dict[str, Any]]] = {}

    for entry in forecast:
        date_time = entry.get("date_time", "")

        if not date_time:
            continue

        date = date_time.split(" ")[0]

        if date not in grouped:
            grouped[date] = []

        grouped[date].append(entry)

    return grouped


def get_daily_forecast(
    forecast: list[dict[str, Any]],
    days: int = 5,
) -> list[dict[str, Any]]:
    """
    Create a simplified daily forecast from
    the 3-hour forecast data.
    """

    grouped = group_forecast_by_date(forecast)

    daily_forecast = []

    for date, entries in list(grouped.items())[:days]:

        temperatures = [
            entry["temperature"]
            for entry in entries
            if entry["temperature"] is not None
        ]

        if not temperatures:
            continue

        weather_entry = entries[len(entries) // 2]

        daily_forecast.append(
            {
                "date": date,

                "temperature_min": min(
                    temperatures
                ),

                "temperature_max": max(
                    temperatures
                ),

                "weather_main": weather_entry[
                    "weather_main"
                ],

                "description": weather_entry[
                    "description"
                ],

                "icon": weather_entry["icon"],

                "humidity": weather_entry[
                    "humidity"
                ],

                "wind_speed": weather_entry[
                    "wind_speed"
                ],
            }
        )

    return daily_forecast


def unix_to_time(timestamp: int) -> str:
    """Convert Unix timestamp to readable time."""

    return datetime.fromtimestamp(
        timestamp
    ).strftime("%I:%M %p")


def unix_to_date(timestamp: int) -> str:
    """Convert Unix timestamp to readable date."""

    return datetime.fromtimestamp(
        timestamp
    ).strftime("%a, %d %b")