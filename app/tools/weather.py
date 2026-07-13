def weather_tool(destination):


    fake_weather={

        "Turkey":
        "15-25°C, sunny",

        "Dubai":
        "30-35°C"

    }


    return {

        "destination":destination,

        "weather":
        fake_weather.get(
            destination,
            "Unknown"
        )

    }