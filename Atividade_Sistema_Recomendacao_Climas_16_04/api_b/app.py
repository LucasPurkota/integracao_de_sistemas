from flask import Flask, jsonify, request

app = Flask(__name__)

weather_data = {
    "curitiba": {"city": "Curitiba", "temp": 15, "unit": "Celsius"},
    "saojosedospinhais": {"city": "São José dos Pinhais", "temp": 28, "unit": "Celsius"},
    "araucaria": {"city": "Araucaria", "temp": 31, "unit": "Celsius"},
}

@app.route("/weather/<city>", methods=["GET"])
def get_weather(city):
  data = weather_data.get(city)
  if data:
    return jsonify(data)
  return jsonify({"error": "City not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)