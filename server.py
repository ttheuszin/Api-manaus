from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Dia 1 OK! Termux + Python funcionando."

@app.route("/hora")
def hora():
    agora = datetime.now().strftime("%H:%M:%S")
    return jsonify({
        "cidade": "Manaus",
        "hora": agora,
        "dia": 3,
        "status": "Consultando APIs"
    })

@app.route("/cep/<numero>")
def buscar_cep(numero):
    try:
        url = f"https://viacep.com.br/ws/{numero}/json/"
        r = requests.get(url, timeout=5)
        dados = r.json()
        if "erro" in dados:
            return jsonify({"erro": "CEP não encontrado"}), 404
        return jsonify({
            "cep": dados["cep"],
            "logradouro": dados["logradouro"],
            "bairro": dados["bairro"],
            "cidade": dados["localidade"],
            "uf": dados["uf"],
            "ddd": dados["ddd"],
            "dev": "Tu",
            "consultado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
    except:
        return jsonify({"erro": "Falha na consulta"}), 500

@app.route("/clima")
def clima_manaus():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-3.1&longitude=-60.0&current_weather=true"
        r = requests.get(url, timeout=5)
        temp = r.json()["current_weather"]["temperature"]
        return jsonify({
            "cidade": "Manaus",
            "temperatura": f"{temp}°C",
            "status": "Calor que só",
            "hora_consulta": datetime.now().strftime("%H:%M")
        })
    except:
        return jsonify({"erro": "Sem clima"}), 500

if __name__ == "__main__":
    print("Acessa no Chrome: http://127.0.0.1:5000")
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
