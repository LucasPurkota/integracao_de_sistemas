from flask import Flask, jsonify
import requests

app = Flask(__name__)

API_B_URL = "http://localhost:5000/weather/{}"

@app.route("/recommendation/<city>", methods=["GET"])
def get_recommendation(city):
    try:
        response = requests.get(API_B_URL.format(city))
        if response.status_code == 200:
            data = response.json()
            temp = data["temp"]

            if temp > 30:
                recommendation = "Está muito quente! Beba bastante água e use protetor solar."
            elif temp > 15:
                recommendation = "O clima está agradável, aproveite o dia!"
            else:
                recommendation = "Está frio! Não se esqueça do casaco."

            return jsonify({
                "city": data["city"],
                "temp": temp,
                "unit": data["unit"],
                "recommendation": recommendation
            })
        else:
            return jsonify({"error": "Cidade não encontrada na API B"}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Erro ao se conectar à API B", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
