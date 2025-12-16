# src/currency_agent.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple, List

from .fx_provider import FrankfurterProvider
from .llm_client import ask_llm

SUPPORTED_CODES = [
    "USD", "AUD", "EUR", "GBP",
    "ARS", "BRL", "CLP", "COP",
    "MXN", "PEN",
]

NAME_TO_CODE = {
    "peso argentino": "ARS",
    "pesos argentinos": "ARS",
    "real brasileño": "BRL",
    "reales brasileños": "BRL",
    "peso chileno": "CLP",
    "pesos chilenos": "CLP",
    "peso colombiano": "COP",
    "pesos colombianos": "COP",
    "peso mexicano": "MXN",
    "pesos mexicanos": "MXN",
    "sol peruano": "PEN",
    "soles peruanos": "PEN",
    "dólar australiano": "AUD",
    "dólares australianos": "AUD",
    "libra esterlina": "GBP",
    "libras esterlinas": "GBP",
}


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
        codes: List[str] = []

        text_lower = text.lower()
        for name, code in NAME_TO_CODE.items():
            if name in text_lower and code not in codes:
                codes.append(code)

        up = text.upper()
        for code in SUPPORTED_CODES:
            if code in up:
                codes.append(code)

        # sin duplicados, preserva orden
        return list(dict.fromkeys(codes))

    def parse(self, question: str) -> Optional[Tuple[float, str, str]]:
        """
        Devuelve (amount, from_code, to_code) si es consulta de conversión.
        Si no puede interpretar la pregunta como conversión, devuelve None.
        """
        q = question.lower()

        amount = self._find_amount(q)
        codes = self._find_currency_codes(q)

        # Caso 1: hay monto explícito
        if amount is not None:
            # Intentamos primero patrón "en|a MONEDA" para fijar el destino:
            # ej. "¿Cuánto es 1000 COP en AUD?"
            dest_pattern = r"(?:en|a)\s+(usd|aud|eur|gbp|ars|brl|clp|cop|mxn|pen)"
            m_dest = re.search(dest_pattern, q)
            if m_dest:
                to_code = m_dest.group(1).upper()
                # origen = primera moneda distinta de destino
                from_code = None
                for c in codes:
                    if c != to_code:
                        from_code = c
                        break
                if from_code:
                    return amount, from_code, to_code

            # Si no hay patrón claro pero sí dos monedas, usamos la regla simple:
            if len(codes) >= 2:
                return amount, codes[0], codes[1]

            # No se pudo interpretar claramente
            return None

        # Caso 2: no hay monto, pero sí dos monedas: interpretamos 1 unidad
        if amount is None and len(codes) >= 2:
            return 1.0, codes[0], codes[1]

        # En cualquier otro caso, no se interpreta como conversión
        return None
@dataclass
class CurrencyAgent:
    provider: FrankfurterProvider
    parser: Parser

    def answer(self, question: str) -> Tuple[str, bool, Optional[Tuple[str, str, float]]]:
        """
        Devuelve:
        - texto de respuesta
        - used_tool: True si llamó a la tool de FX
        - fx_info: (from_code, to_code, rate_1_to_1) o None
        """
        parsed = self.parser.parse(question)

        # Si el parser entiende que es una conversión, llamamos a la "tool"
        if parsed:
            amount, from_code, to_code = parsed
            try:
                converted = self.provider.convert(amount, from_code, to_code)
            except Exception as e:
                msg = (
                    f"No pude obtener la tasa de cambio para {from_code}->{to_code}. "
                    f"Detalle técnico: {e}"
                )
                return msg, True, None

            # Formateo con separador de miles y coma decimal estilo ES
            def fmt(value: float) -> str:
                return (
                    f"{value:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

            # tasa 1 -> 1
            rate = converted / amount if amount != 0 else 0.0

            text = (
                f"{fmt(amount)} {from_code} equivalen aproximadamente a "
                f"{fmt(converted)} {to_code} "
                #f"(tasa de cambio diaria obtenida automáticamente; "
                #f"solo para fines educativos)."
            )

            return text, True, (from_code, to_code, rate)

        # Si no es conversión (Pregunta 3), delegamos la respuesta al LLM de Gorq
        try:
            msg = ask_llm(question)
        except Exception as e:
            # Fallback en caso de error con el LLM
            msg = (
                "La tasa de cambio es el precio de una moneda expresado en otra. "
                "Es clave en transacciones internacionales porque determina el valor "
                "real de pagos, inversiones y deudas cuando las partes operan en "
                "monedas diferentes; en energía y recursos ayuda a gestionar el "
                "riesgo de que los ingresos estén en moneda local mientras la deuda "
                "y los contratos de suministro estén en divisas fuertes como USD o EUR."
                f"(Nota técnica: no pude acceder al modelo de lenguaje para responder; {e})"
            )
        return msg, False, None
