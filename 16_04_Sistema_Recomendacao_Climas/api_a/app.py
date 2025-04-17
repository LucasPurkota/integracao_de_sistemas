from flask import Flask, jsonify
import requests
import redis
import json

app = Flask(__name__)

API_B_URL = "http://localhost:5000/weather/{}"

cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route("/recommendation/<city>", methods=["GET"])
def get_recommendation(city):
    cache_key = f"weather:{city.lower()}"

    cached_data = cache.get(cache_key)
    if cached_data:
        data = json.loads(cached_data)
        print("Dados busacados usando dados do cache Redis")
    else:
        try:
            response = requests.get(API_B_URL.format(city))
            if response.status_code != 200:
                return jsonify({"error": "Cidade não encontrada na API B"}), 404

            data = response.json()

            cache.setex(cache_key, 60, json.dumps(data))
            print("Dados buscados da API B")
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Erro ao se conectar à API B", "details": str(e)}), 500

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

if __name__ == "__main__":
    app.run(port=5001, debug=True)
