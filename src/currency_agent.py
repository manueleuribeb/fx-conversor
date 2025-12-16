# src/currency_agent.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple, List

from .fx_provider import FrankfurterProvider


SUPPORTED_CODES = [
    "USD", "AUD", "EUR", "GBP",
    "ARS", "BRL", "CLP", "COP",
    "MXN", "PEN",
]


class Parser:
    """
    Parser sencillo en español que:
    - Extrae monto numérico
    - Detecta monedas origen/destino
    - Decide si es pregunta de conversión (tool) o conceptual (sin tool)
    """

    def _find_amount(self, text: str) -> Optional[float]:
        # Acepta formatos como "10,000", "1.000,50", "500"
        m = re.search(r"(\d[\d\.\,]*)", text)
        if not m:
            return None
        raw = m.group(1).replace(".", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None

    def _find_currency_codes(self, text: str) -> List[str]:
        # Busca códigos tipo USD, COP, EUR, etc. sin distinguir mayúsculas
        codes = []
        up = text.upper()
        for code in SUPPORTED_CODES:
            if code in up:
                codes.append(code)
        return list(dict.fromkeys(codes))  # sin duplicados, preserva orden

    def parse(self, question: str) -> Optional[Tuple[float, str, str]]:
        """
        Devuelve (amount, from_code, to_code) si es consulta de conversión.
        Si no puede interpretar la pregunta como conversión, devuelve None.
        """
        q = question.lower()

        amount = self._find_amount(q)
        if amount is None:
            return None

        codes = self._find_currency_codes(q)
        if len(codes) >= 2:
            # Tenemos al menos 2 monedas explícitas, primera = origen, segunda = destino
            return amount, codes[0], codes[1]

        # Si solo hay una moneda explícita, intentamos detectar dirección con patrones
        if len(codes) == 1:
            only = codes[0]

            # ¿Cuánto equivalen 500 EUR en COP?
            dest_pattern = r"(?:en|a)\s+(usd|aud|eur|gbp|ars|brl|clp|cop|mxn|pen)"
            m_dest = re.search(dest_pattern, q)
            if m_dest:
                to_code = m_dest.group(1).upper()
                if to_code == only:
                    # Solo detectamos una moneda distinta, no sabemos la otra
                    return None
                # asumimos que la moneda mencionada primero es origen
                return amount, only, to_code

        # Si llegamos aquí, no interpretamos la pregunta como conversión
        return None


@dataclass
class CurrencyAgent:
    provider: FrankfurterProvider
    parser: Parser

    def answer(self, question: str) -> str:
        parsed = self.parser.parse(question)

        # Si el parser entiende que es una conversión, llamamos a la "tool"
        if parsed:
            amount, from_code, to_code = parsed
            try:
                converted = self.provider.convert(amount, from_code, to_code)
            except Exception as e:
                return (
                    f"No pude obtener la tasa de cambio para {from_code}->{to_code}. "
                    f"Detalle técnico: {e}"
                )

            return (
                f"{amount:,.2f} {from_code} ≈ {converted:,.2f} {to_code} "
                f"(tasa de cambio en tiempo casi real del BCE)."
            )

        # Si no es conversión (Pregunta 3), respondemos de forma conceptual
        return (
            "La tasa de cambio es el precio de una moneda expresado en otra. "
            "Es clave en transacciones internacionales porque determina el valor "
            "real de pagos, inversiones y deudas cuando las partes operan en "
            "monedas diferentes; en energía y recursos ayuda a gestionar el "
            "riesgo de que los ingresos estén en moneda local mientras la deuda "
            "y los contratos de suministro estén en divisas fuertes como USD o EUR."
        )
