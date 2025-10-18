def calc(forecastCloudPrice):
    price = 0

    tariffs = forecastCloudPrice["tariffs"]
    for tariff in tariffs:
        price += tariff['price'] * tariff['count'] * forecastCloudPrice['days']

    return price
