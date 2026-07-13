def currency_converter(currency):
    rates = {
        "PKR":1,
        "USD":280,
        "EUR":300
    }
    return {
        "currency":currency,
        "rate":rates.get(currency,"unknown")
    }