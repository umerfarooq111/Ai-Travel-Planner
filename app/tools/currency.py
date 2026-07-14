import httpx

# Pre-defined fallback rates in case API fails or doesn't support the currency (relative to USD)
FALLBACK_RATES_TO_USD = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.77,
    "PKR": 278.0,
    "TRY": 32.8,
    "AED": 3.67,
}

async def currency_converter(
    amount: float,
    from_currency: str,
    to_currency: str,
):
    """
    Convert one currency into another using Frankfurter API with pre-defined fallback matrix.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    try:
        url = (
            f"https://api.frankfurter.app/latest"
            f"?amount={amount}"
            f"&from={from_currency}"
            f"&to={to_currency}"
        )

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(url)

        if response.status_code == 200:
            data = response.json()
            return {
                "amount": amount,
                "from": from_currency,
                "to": to_currency,
                "converted_amount": data["rates"][to_currency],
                "rate": data["rates"][to_currency] / amount,
            }
    except Exception as e:
        print(f"Error in currency_converter tool: {e}")

    # Matrix Fallback conversion
    from_rate = FALLBACK_RATES_TO_USD.get(from_currency, 1.0)
    to_rate = FALLBACK_RATES_TO_USD.get(to_currency, 1.0)
    
    usd_val = amount / from_rate
    conv_val = usd_val * to_rate
    rate = to_rate / from_rate

    return {
        "amount": amount,
        "from": from_currency,
        "to": to_currency,
        "converted_amount": round(conv_val, 2),
        "rate": round(rate, 4),
    }