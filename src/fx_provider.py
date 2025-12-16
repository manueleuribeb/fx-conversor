
# src/fx_provider.py
# Cliente para Frankfurter (ECB reference rates)
# Docs oficiales (sin API key; base y symbols soportados): https://frankfurter.dev/

from __future__ import annotations
import os
import requests
from typing import Dict, List, Optional

# Permite sobreescribir el host por variable de entorno (p.ej. FX_BASE_URL=https://api.frankfurter.app/v1)
DEFAULT_BASE_URL = "https://api.frankfurter.dev/v1"

def _clean_url(url: str) -> str:
    """Elimina espacios/saltos accidentales que rompen la URL."""
    return url.replace("\n", "").replace("\r", "").strip()

class FrankfurterProvider:
    """Cliente ligero para la API Frankfurter (tipos de cambio del ECB)."""

    def __init__(self, session: Optional[requests.Session] = None, timeout: int = 20):
        self.session = session or requests.Session()
        self.timeout = timeout
        base = os.getenv("FX_BASE_URL", DEFAULT_BASE_URL)
        self.base_url = _clean_url(base)  # evita saltos de línea en el string

    def _get(self, path: str, params: Dict) -> Dict:
        url = _clean_url(f"{self.base_url}{path}")
        r = self.session.get(url, params=params, timeout=self.timeout)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            # Si hay 404, probamos con el dominio alternativo .app
            if r.status_code == 404 and "frankfurter.dev" in self.base_url:
                alt = "https://api.frankfurter.app/v1"
                url_alt = _clean_url(f"{alt}{path}")
                r_alt = self.session.get(url_alt, params=params, timeout=self.timeout)
                r_alt.raise_for_status()
                return r_alt.json()
            # Re-lanza con detalle para diagnóstico
            raise requests.HTTPError(
                f"{e}\nURL: {url}\nParams: {params}\nBody: {r.text}"
            ) from None
        return r.json()

    def latest(self, base: str, symbols: Optional[List[str]] = None) -> Dict:
        """Obtiene tasas del último día hábil con base 'base' y (opcional) 'symbols'."""
        params = {"base": base.upper()}
        if symbols:
            params["symbols"] = ",".join(s.upper() for s in symbols)
        return self._get("/latest", params)

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convierte 'amount' de 'from_currency' a 'to_currency' usando tasas 'latest' del ECB."""
        data = self.latest(base=from_currency, symbols=[to_currency])
        rate = data["rates"][to_currency.upper()]
        return amount * rate

    def latest_with_meta(self, base: str, symbols: List[str]) -> Dict:
        """Devuelve el JSON completo por si quieres mostrar 'date'        """Devuelve el JSON completo por si quieres mostrar 'date' (disclaimer)."""
