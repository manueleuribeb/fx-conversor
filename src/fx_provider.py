from __future__ import annotations

import requests
from typing import Dict, List

BASE_URL = "https://open.er-api.com/v6/latest"


class FrankfurterProvider:
    """
    Cliente sencillo para open.er-api.com (tipos de cambio diarios, sin API key).
    """

    def latest(self, base: str, symbols: List[str]) -> Dict:
        url = f"{BASE_URL}/{base.upper()}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()

        if data.get("result") != "success":
            raise ValueError(f"Respuesta inesperada de la API: {data}")

        # Filtramos solo las monedas que nos interesan
        rates = data.get("rates", {})
        filtered = {code.upper(): rates[code.upper()] for code in symbols if code.upper() in rates}

        if not filtered:
            raise ValueError(f"No encontré tasas para {symbols} con base {base}")

        return {"base_code": data["base_code"], "rates": filtered}

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        data = self.latest(base=from_currency, symbols=[to_currency])
        rate = data["rates"][to_currency.upper()]
        return amount * rate
