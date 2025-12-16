# src/llm_client.py
from __future__ import annotations

import os
from groq import Groq  # pip install groq


_api_key = os.getenv("GROQ_API_KEY")
if not _api_key:
    raise RuntimeError(
        "Falta la variable de entorno GROQ_API_KEY para usar el LLM de Groq."
    )

_client = Groq(api_key=_api_key)


def ask_llm(question: str) -> str:
    """
    Envía la pregunta a un modelo de Groq y devuelve una respuesta breve en español
    con enfoque BFSI / energía.
    """
    resp = _client.chat.completions.create(
        model="llama-3.1-8b-instant",  # puedes cambiarlo si usas otro
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un analista financiero del sector energía y recursos,"
                    "trabajando en una empresa de consultoría para el sector BFSI."
                    "Respondes SIEMPRE en español, de forma clara y concisa, " 
                    "en 3 a 10 frases como máximo."
                    "Cuando expliques conceptos (como tasa de cambio o riesgo cambiario),"
                    "usa ejemplos de proyectos del sector energía o recursos."
                    "(por ejemplo parques eólicos, proyectos solares, minería, petróleo y gas) "
                    "y evita listas largas."
                ),
            },
            {"role": "user", "content": question},
        ],
        temperature=0.3,
        max_tokens=250,
    )
    return resp.choices[0].message.content.strip()
