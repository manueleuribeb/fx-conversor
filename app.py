
# app.py
from src.fx_provider import FrankfurterProvider
from src.currency_agent import CurrencyAgent, Parser

if __name__ == "__main__":
    agent = CurrencyAgent(provider=FrankfurterProvider(), parser=Parser())
    questions = [
        "¿Cuál es el valor de 10,000 COP en USD hoy?",
        "¿Cuánto equivalen 500 EUR en COP con la tasa actual?",
        "Convierte 1,000 pesos argentinos en soles peruanos",
        "Convierte 250 dólares australianos a euros",
        "Convierte 750 libras esterlinas a pesos mexicanos",
        "¿Cuánto equivalen 1200 reales brasileños en pesos chilenos?",
        "¿Qué significa tasa de cambio y por qué es importante en transacciones internacionales?"
    ]
    for q in questions:
        print("Q:", q)
        print(agent.answer(q))
