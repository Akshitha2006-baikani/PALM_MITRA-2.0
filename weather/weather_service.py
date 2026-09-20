"""
Palm Mitra - Weather Service

Fetches current weather information from OpenWeather.
The API key is loaded from the project .env file.
"""

import os

import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)


API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)

BASE_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
)


# ---------------------------------------------------------
# FETCH WEATHER
# ---------------------------------------------------------

def get_current_weather(city):

    if not city:
        raise ValueError(
            "A city or location is required."
        )

    if not API_KEY:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not configured "
            "in the .env file."
        )

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )


    # -----------------------------------------------------
    # HANDLE API ERRORS
    # -----------------------------------------------------

    if response.status_code != 200:

        try:
            error_data = response.json()

            message = error_data.get(
                "message",
                "Weather service request failed."
            )

        except Exception:

            message = (
                "Weather service request failed."
            )

        raise RuntimeError(
            message
        )


    data = response.json()


    # -----------------------------------------------------
    # EXTRACT WEATHER INFORMATION
    # -----------------------------------------------------

    main = data.get(
        "main",
        {}
    )

    weather = data.get(
        "weather",
        [{}]
    )[0]

    wind = data.get(
        "wind",
        {}
    )


    # -----------------------------------------------------
    # RETURN CLEAN RESULT
    # -----------------------------------------------------

    return {

        "location": data.get(
            "name",
            city
        ),

        "country": data.get(
            "sys",
            {}
        ).get(
            "country",
            ""
        ),

        "temperature": main.get(
            "temp"
        ),

        "feels_like": main.get(
            "feels_like"
        ),

        "humidity": main.get(
            "humidity"
        ),

        "pressure": main.get(
            "pressure"
        ),

        "condition": weather.get(
            "main",
            "Unknown"
        ),

        "description": weather.get(
            "description",
            ""
        ).title(),

        "wind_speed": wind.get(
            "speed"
        ),

        "cloudiness": data.get(
            "clouds",
            {}
        ).get(
            "all"
        ),

        "icon": weather.get(
            "icon"
        )
    }


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    result = get_current_weather(
        "Hyderabad, Telangana, India"
    )

    print(result)