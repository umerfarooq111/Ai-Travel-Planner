import httpx

async def destination_info(destination: str):
    try:
        url = f"https://restcountries.com/v3.1/name/{destination}?fullText=true"
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(url)
            
            # If fullText search fails (e.g. because destination is a city, not a country)
            if response.status_code != 200:
                url_fallback = f"https://restcountries.com/v3.1/name/{destination}"
                response = await client.get(url_fallback)
                
            if response.status_code == 200:
                country = response.json()[0]
                currencies = list(country.get("currencies", {}).keys())
                languages = list(country.get("languages", {}).values())
                return {
                    "country": country["name"]["common"],
                    "official_name": country["name"].get("official", country["name"]["common"]),
                    "capital": country.get("capital", ["N/A"])[0],
                    "currency": currencies[0] if currencies else "USD",
                    "language": languages if languages else ["English"],
                    "region": country.get("region", "Unknown"),
                    "population": country.get("population", 0),
                    "flag": country.get("flags", {}).get("png", "")
                }
    except Exception as e:
        print(f"Error in destination_info tool: {e}")

    # Solid fallback data to prevent planning crashes
    return {
        "country": destination,
        "official_name": destination,
        "capital": "N/A",
        "currency": "USD",
        "language": ["Local"],
        "region": "Global",
        "population": 0,
        "flag": ""
    }