from flask import Flask, render_template, request

from src.fx_provider import FrankfurterProvider
from src.currency_agent import CurrencyAgent, Parser

app = Flask(__name__)

agent = CurrencyAgent(provider=FrankfurterProvider(), parser=Parser())


PRESETS = {
    "p1": "¿Cuál es el valor de 10000 COP en USD hoy?",
    "p2": "¿Cuánto equivalen 500 EUR en COP con la tasa actual?",
    "p3": "¿Qué significa tasa de cambio y por qué es importante en transacciones internacionales?",
}


@app.route("/", methods=["GET", "POST"])
def index():
    question = ""
    answer = ""
    used_tool = False
    fx_info = None

    if request.method == "POST":
        preset = request.form.get("preset")
        if preset in PRESETS:
            question = PRESETS[preset]
        else:
            question = request.form.get("question", "")

        if question.strip():
            answer_text, used_tool, fx_info = agent.answer(question)
            answer = answer_text
        else:
            used_tool = False
            fx_info = None

    return render_template(
        "index.html",
        question=question,
        answer=answer,
        used_tool=used_tool,
        fx_info=fx_info,
    )



if __name__ == "__main__":
    app.run(debug=True)
