import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    pass


class WeatherAPI:
    """Handles communication with the OpenWeather API."""

    BASE_URL = "https://api.openweathermap.org"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

        if not self.api_key:
            raise WeatherAPIError(
                "OpenWeather API key is missing. "
                "Please check your .env file."
            )

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any]
    ) -> Any:
        """Send a GET request and handle common errors."""

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10
            )

        except requests.exceptions.Timeout:
            raise WeatherAPIError(
                "Network timeout. "
                "Please check your internet connection "
                "and try again."
            )

        except requests.exceptions.ConnectionError:
            raise WeatherAPIError(
                "Unable to connect to OpenWeather. "
                "Please check your internet connection."
            )

        except requests.exceptions.RequestException as error:
            raise WeatherAPIError(
                f"Network error: {error}"
            )

        if response.status_code == 401:
            raise WeatherAPIError(
                "Invalid or inactive OpenWeather API key."
            )

        if response.status_code == 404:
            raise WeatherAPIError(
                "Location not found. "
                "Please check the city or ZIP code."
            )

        if response.status_code == 429:
            raise WeatherAPIError(
                "OpenWeather API rate limit reached. "
                "Please try again later."
            )

        if response.status_code != 200:
            try:
                error_data = response.json()
                message = error_data.get(
                    "message",
                    "Unknown API error."
                )
            except ValueError:
                message = f"HTTP error {response.status_code}"

            raise WeatherAPIError(
                f"Weather API error: {message}"
            )

        try:
            return response.json()

        except ValueError:
            raise WeatherAPIError(
                "OpenWeather returned invalid JSON data."
            )

    # =====================================================
    # LOCATION
    # =====================================================

    def _is_postal_code(
        self,
        location: str
    ) -> bool:
        """Check whether input looks like a ZIP/PIN code."""

        cleaned = location.strip()

        if not cleaned:
            return False

        postal_part = cleaned.split(",", 1)[0].strip()

        return postal_part.isdigit()

    def _get_postal_country(
        self,
        location: str
    ) -> str:
        """Determine country code for a postal code."""

        cleaned = location.strip()

        if "," in cleaned:
            parts = cleaned.split(",", 1)
            country = parts[1].strip()

            if country:
                return country.upper()

        postal_part = cleaned.split(",", 1)[0].strip()

        # Six-digit PIN → India
        if len(postal_part) == 6:
            return "IN"

        # Five-digit ZIP → USA
        if len(postal_part) == 5:
            return "US"

        return "IN"

    def get_location(
        self,
        location: str
    ) -> dict[str, Any]:
        """
        Resolve a city name or ZIP/PIN code.

        Returns:
            name
            state
            country
            latitude
            longitude
        """

        if not isinstance(location, str):
            raise WeatherAPIError(
                "Location must be text."
            )

        location = location.strip()

        if not location:
            raise WeatherAPIError(
                "Location cannot be empty."
            )

        # -------------------------------------------------
        # ZIP / PIN CODE
        # -------------------------------------------------

        if self._is_postal_code(location):

            postal_code = location.split(
                ",",
                1
            )[0].strip()

            country = self._get_postal_country(
                location
            )

            data = self._get(
                "/geo/1.0/zip",
                {
                    "zip": f"{postal_code},{country}",
                    "appid": self.api_key
                }
            )

            if not data:
                raise WeatherAPIError(
                    "ZIP/postal code not found."
                )

            return {
                "name": data.get(
                    "name",
                    postal_code
                ),
                "state": "",
                "country": data.get(
                    "country",
                    country
                ),
                "latitude": data["lat"],
                "longitude": data["lon"]
            }

        # -------------------------------------------------
        # CITY NAME
        # -------------------------------------------------

        data = self._get(
            "/geo/1.0/direct",
            {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
        )

        if not data:
            raise WeatherAPIError(
                "Location not found. "
                "Please enter a valid city or ZIP code."
            )

        result = data[0]

        return {
            "name": result.get(
                "name",
                location
            ),
            "state": result.get(
                "state",
                ""
            ),
            "country": result.get(
                "country",
                ""
            ),
            "latitude": result["lat"],
            "longitude": result["lon"]
        }

    # =====================================================
    # CURRENT WEATHER
    # =====================================================

    def _get_current_weather_raw(
        self,
        latitude: float,
        longitude: float
    ) -> dict[str, Any]:
        """Return raw OpenWeather current-weather JSON."""

        return self._get(
            "/data/2.5/weather",
            {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
        )

    def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> dict[str, Any]:
        """Return processed current weather for the GUI."""

        data = self._get_current_weather_raw(
            latitude,
            longitude
        )

        weather = data.get(
            "weather",
            [{}]
        )[0]

        main = data.get(
            "main",
            {}
        )

        wind = data.get(
            "wind",
            {}
        )

        system = data.get(
            "sys",
            {}
        )

        return {
            "city": data.get(
                "name",
                "Unknown"
            ),
            "country": system.get(
                "country",
                ""
            ),
            "temperature": main.get(
                "temp",
                0
            ),
            "feels_like": main.get(
                "feels_like",
                0
            ),
            "humidity": main.get(
                "humidity",
                0
            ),
            "pressure": main.get(
                "pressure",
                0
            ),
            "wind_speed": wind.get(
                "speed",
                0
            ),
            "wind_direction": wind.get(
                "deg",
                0
            ),
            "visibility": data.get(
                "visibility",
                0
            ),
            "description": weather.get(
                "description",
                "Unknown"
            ),
            "condition": weather.get(
                "main",
                "Unknown"
            ),
            "icon": weather.get(
                "icon",
                ""
            ),
            "sunrise": system.get(
                "sunrise"
            ),
            "sunset": system.get(
                "sunset"
            )
        }

    # =====================================================
    # FORECAST
    # =====================================================

    def get_forecast(
        self,
        latitude: float,
        longitude: float
    ) -> dict[str, Any]:
        """Return raw 5-day / 3-hour forecast."""

        return self._get(
            "/data/2.5/forecast",
            {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
        )

    # =====================================================
    # COMPLETE WEATHER
    # =====================================================

    def get_weather(
        self,
        location: str
    ) -> dict[str, Any]:
        """Get location, current weather and forecast."""

        location_data = self.get_location(
            location
        )

        latitude = location_data["latitude"]
        longitude = location_data["longitude"]

        current = self.get_current_weather(
            latitude,
            longitude
        )

        forecast = self.get_forecast(
            latitude,
            longitude
        )

        return {
            "location": {
                "name": location_data["name"],
                "country": location_data["country"],
                "state": location_data["state"],
                "lat": latitude,
                "lon": longitude
            },
            "current": current,
            "forecast": forecast
        }


# =========================================================
# BACKWARD-COMPATIBILITY FUNCTIONS
# =========================================================

def get_location(
    city: str
) -> dict[str, Any]:
    """Resolve a city or ZIP/PIN code."""

    api = WeatherAPI()

    return api.get_location(
        city
    )


def get_current_weather(
    latitude: float,
    longitude: float
) -> dict[str, Any]:
    """
    Return raw current weather JSON.

    This preserves compatibility with test_weather_api.py.
    """

    api = WeatherAPI()

    return api._get_current_weather_raw(
        latitude,
        longitude
    )


def get_forecast(
    latitude: float,
    longitude: float
) -> dict[str, Any]:
    """Return raw forecast JSON."""

    api = WeatherAPI()

    return api.get_forecast(
        latitude,
        longitude
    )


def get_coordinates(
    location: str
) -> dict[str, Any]:
    """Backward-compatible coordinate helper."""

    api = WeatherAPI()

    data = api.get_location(
        location
    )

    return {
        "name": data["name"],
        "state": data["state"],
        "country": data["country"],
        "lat": data["latitude"],
        "lon": data["longitude"]
    }


def get_weather(
    location: str
) -> dict[str, Any]:
    """Backward-compatible complete weather helper."""

    api = WeatherAPI()

    return api.get_weather(
        location
    )