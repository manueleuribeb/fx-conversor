
import re
from dataclasses import dataclass
from typing import Optional, Tuple
from .fx_provider import FrankfurterProvider  # ✅ nombre correcto

# ✅ Lista de monedas ISO que vamos a soportar
CURRENCIES = [
    'USD', 'AUD', 'EUR', 'GBP',
    'ARS', 'BRL', 'CLP', 'COP', 'MXN', 'PEN'
]

# ✅ Alias en español (singular/plural y variantes acentuadas) → código ISO
ALIASES = {
    # USD
    'dolares': 'USD', 'dólares': 'USD', 'dólar': 'USD', 'dolar': 'USD',
    'dólares americanos': 'USD', 'dolares americanos': 'USD',
    'usd': 'USD', 'dolares us': 'USD', 'dólares us': 'USD',

    # AUD
    'dolares australianos': 'AUD', 'dólares australianos': 'AUD',
    'dolar australiano': 'AUD', 'dólar australiano': 'AUD', 'aud': 'AUD',

    # EUR
    'euros': 'EUR', 'euro': 'EUR', 'eur': 'EUR',

    # GBP
    'libras esterlinas': 'GBP', 'libra esterlina': 'GBP', 'gbp': 'GBP', 'libras': 'GBP',

    # ARS
    'pesos argentinos': 'ARS', 'peso argentino': 'ARS', 'ars': 'ARS',

    # BRL
    'reales brasileños': 'BRL', 'real brasileño': 'BRL', 'brl': 'BRL', 'reales': 'BRL',

    # CLP
    'pesos chilenos': 'CLP', 'peso chileno': 'CLP', 'clp': 'CLP',

    # COP
    'pesos colombianos': 'COP', 'peso colombiano': 'COP', 'cop': 'COP', 'pesos': 'COP',

    # MXN
    'pesos mexicanos': 'MXN', 'peso mexicano': 'MXN', 'mxn': 'MXN',

    # PEN
    'soles peruanos': 'PEN', 'sol peruano': 'PEN', 'pen': 'PEN', 'soles': 'PEN'
}

def _normalize_amount(raw: str) -> float:
    """Normaliza montos con separadores ES/US.
    Ejemplos: '10,000' -> 10000; '1.234,56' -> 1234.56; '2.50' -> 2.50
    """
    if ',' in raw and '.' not in raw:
        raw = raw.replace(',', '')
    elif ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    return float(raw)

class Parser:
    """Extrae monto y monedas desde una pregunta en español."""

    def parse(self, text: str) -> Optional[Tuple[float, str, str]]:
        q = text.lower()

        # 1) Monto
        m = re.search(r'([\d\.,]+)', q)
        if not m:
            return None
        amount = _normalize_amount(m.group(1))

        # 2) Recolectar códigos ISO y alias en orden de aparición
        codes = []
        for code in [c.lower() for c in CURRENCIES]:
            for mt in re.finditer(rf'\b{code}\b', q):
                codes.append((mt.start(), code.upper()))
        for alias, code in ALIASES.items():
            for mt in re.finditer(alias, q):
                codes.append((mt.start(), code.upper()))
        codes = [c for _, c in sorted(codes, key=lambda x: x[0])]

        # 3) Destino por preposición "en|a <code>" (ahora incluye todos los codes del catálogo)
        #    Nota: usamos un grupo con las monedas soportadas en minúscula.
        dest_pattern = r'(?:en|a)\s+(usd|aud|eur|gbp|ars|brl|clp|cop|mxn|pen)'
        m3 = re.search(dest_pattern, q)
        to_code = m3.group(1).upper() if m3 else None

        if to_code and codes:
            from_code = next((c for c in codes if c != to_code), None)
            if from_code:
                return amount, from_code, to_code

        # 4) Fallback: si detectamos >=2 monedas, tomamos la primera como origen y la segunda como destino
        if len(codes) >= 2:
            return amount, codes[0], codes[1]

        return None

@dataclass
class CurrencyAgent:
    provider: FrankfurterProvider
    parser: Parser

    def answer(self, question: str) -> str:
        parsed = self.parser.parse(question)
        if parsed:
            amount, f, t = parsed
            # ✅ llamada correcta al método del provider
            converted = self.provider.convert(amount, f, t)
            return f"{amount:,.2f} {f} ≈ {converted:,.2f} {t}"
        else:
            return ("La tasa de cambio es el precio de una moneda expresado en otra; ")
                   
