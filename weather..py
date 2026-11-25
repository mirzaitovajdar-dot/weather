import requests
from datetime import datetime
from Util_Functions import (
    wind_degree_to_direction,
    unix_timestamp_to_localtime,
    convert_temperature,
)


def fetch_weather(api_key, location):
    """
    Function to fetch weather data from OpenWeatherMap API.

    Parameters:
    api_key (str): API key.
    location (str): City name.

    Returns:
    dict: The parsed JSON response, or None on request failure.
    """
    try:
        complete_api_link = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={location}&appid={api_key}"
        )

        api_link = requests.get(complete_api_link, timeout=10)
        api_data = api_link.json()
        return api_data

    except requests.exceptions.RequestException as e:
        print("Error fetching weather data:", e)
        return None
    except ValueError:
        # The response is not valid JSON (e.g. HTML error page)
        print("Error: received a non-JSON response from the API.")
        return None


def write_to_file(weather_data, temperature_unit):
    """
    Function to write weather information to a text file.

    Parameters:
    weather_data (dict): The parsed API response.
    temperature_unit (str): 'C' for Celsius, 'F' for Fahrenheit.
    """
    try:
        with open("weatherinfo.txt", "w", encoding="utf-8") as f:
            date_time = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

            if (
                "name" in weather_data
                and "sys" in weather_data
                and "country" in weather_data["sys"]
            ):
                f.write(
                    "-------------------------------------------------------------\n"
                )
                f.write(
                    f"Статистика погоды для - {weather_data['name']} | "
                    f"{weather_data['sys']['country']} | {date_time}\n"
                )
                f.write(
                    "-------------------------------------------------------------\n"
                )

            if "main" in weather_data and "temp" in weather_data["main"]:
                f.write(
                    "\tТекущая температура составляет :"
                    + convert_temperature(
                        weather_data["main"]["temp"], temperature_unit
                    )
                    + "\n"
                )

            if "weather" in weather_data and weather_data["weather"]:
                f.write(
                    "\tТекущее описание погоды: "
                    + weather_data["weather"][0].get("description", "unknown")
                    + "\n"
                )

            if "main" in weather_data and "humidity" in weather_data["main"]:
                f.write(
                    "\tТекущая влажность: {} %\n".format(
                        weather_data["main"]["humidity"]
                    )
                )

            if "wind" in weather_data and "speed" in weather_data["wind"]:
                f.write(
                    "\tТекущая скорость ветра: {} km/h \n".format(
                        weather_data["wind"]["speed"]
                    )
                )

            if "wind" in weather_data and "deg" in weather_data["wind"]:
                f.write(
                    "\tТекущее направление ветра: "
                    + wind_degree_to_direction(weather_data["wind"]["deg"])
                    + " \n"
                )

            if (
                "sys" in weather_data
                and "sunrise" in weather_data["sys"]
                and "timezone" in weather_data
            ):
                f.write(
                    "\tСегодняшнее время восхода солнца: "
                    + unix_timestamp_to_localtime(
                        weather_data["sys"]["sunrise"], weather_data["timezone"]
                    )
                    + " \n"
                )

            if (
                "sys" in weather_data
                and "sunset" in weather_data["sys"]
                and "timezone" in weather_data
            ):
                f.write(
                    "\tСегодняшнее время захода солнца: "
                    + unix_timestamp_to_localtime(
                        weather_data["sys"]["sunset"], weather_data["timezone"]
                    )
                    + " \n"
                )

        print("Weather information written to weatherinfo.txt")

    except IOError as e:
        print("Error writing to file:", e)


def print_weather(weather_data, temperature_unit):
    """Safely prints weather info to console without KeyError."""
    name = weather_data.get("name", "unknown")
    country = weather_data.get("sys", {}).get("country", "")

    print("Текущий город          :", name + ", " + country)

    temp = weather_data.get("main", {}).get("temp")
    if temp is not None:
        print("Текущая температура составляет:", convert_temperature(temp, temperature_unit))

    weather_list = weather_data.get("weather") or []
    if weather_list:
        print("Текущее описание погоды:", weather_list[0].get("description", "unknown"))

    humidity = weather_data.get("main", {}).get("humidity")
    if humidity is not None:
        print("Текущая влажность:", humidity, "%")

    wind = weather_data.get("wind", {})
    if "speed" in wind:
        print("Текущая скорость ветра :", wind["speed"], "kmph")
    if "deg" in wind:
        print("Текущее направление ветра:", wind_degree_to_direction(wind["deg"]))

    timezone = weather_data.get("timezone")
    sys_data = weather_data.get("sys", {})
    if timezone is not None:
        if "sunrise" in sys_data:
            print(
                "Сегодняшнее время восхода солнца:",
                unix_timestamp_to_localtime(sys_data["sunrise"], timezone),
            )
        if "sunset" in sys_data:
            print(
                "Сегодняшнее время захода солнца :",
                unix_timestamp_to_localtime(sys_data["sunset"], timezone),
            )


def main():
    """
    Main function.
    """
    print("Добро пожаловать в приложение для получения информации о погоде!")
    print("Вам нужен API-ключ для доступа к данным о погоде из OpenWeatherMap.")
    print(
        "Вы можете получить свой API-ключ, зарегистрировавшись по адресу "
        "https://home.openweathermap.org/users/sign_up"
    )

    api_key = input("Пожалуйста, введите свой API-ключ OpenWeatherMap: ").strip()
    location = input("Введите название города: ").strip()
    temperature_unit = input(
        "Введите единицу измерения температуры. 'C' означает градус Цельсия, 'F' - градус Фаренгейта.:: "
    ).strip().upper()

    if temperature_unit not in ("C", "F"):
        print("Temperature unit must either be 'C' or be 'F'.")
        return

    if not api_key or not location:
        print("API key and city name must not be empty.")
        return

    weather_data = fetch_weather(api_key, location)

    if not weather_data:
        print("Failed to fetch weather data. Please check your input and try again.")
        return

    # Universal check: treat any non-200 response as an error.
    # The 'cod' field may come as a string or as an int, so we cast it.
    cod = str(weather_data.get("cod", ""))
    if cod != "200":
        print(f"API error (code {cod}):", weather_data.get("message", "unknown error"))
        return

    write_to_file(weather_data, temperature_unit)
    print_weather(weather_data, temperature_unit)


if __name__ == "__main__":
    main()
