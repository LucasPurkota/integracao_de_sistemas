from flask import Flask, jsonify, request
import pika
import requests
import redis
import json
import threading
from time import sleep
from datetime import datetime

app = Flask(__name__)

# Configurações
API_NODE = "http://localhost:3000/alert"
CACHE_TIME = 30
EVENTS_CACHE_TIME = 60
RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'logistica_urgente'
EVENTS_LIST_KEY = 'sensor_events'

cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
@app.route("/event", methods=["POST"])
def post_event():
    try:
        data = request.get_json()
        
        if not data or 'temperatura' not in data or 'pressao' not in data:
            return jsonify({
                "error": "Parâmetros 'temperatura' e 'pressao' são obrigatórios",
            }), 400
        
        temperatura = data['temperatura']
        pressao = data['pressao']
        
        cache_key = f"sensor:{temperatura}:{pressao}"
        
        cached_data = cache.get(cache_key)
        if cached_data:
            print("Dados buscados usando dados do cache Redis")
            return jsonify({
                "data": json.loads(cached_data),
            })
        
        response = requests.post(
            API_NODE,
            json={
                "temperatura": temperatura,
                "pressao": pressao
            }
        )
        
        if response.status_code != 200:
            return jsonify({
                "error": "Erro ao conectar com a API Node",
            }), response.status_code
        
        alert_data = response.json()
        
        cache.setex(cache_key, CACHE_TIME, json.dumps(alert_data))
        
        print("Dados buscados da API Node")
        return jsonify({
            "data": alert_data,
        })
    except Exception as e:
        return jsonify({
            "error": "Erro interno no servidor: " + str(e),
        }), 500
        
        
def rabbitmq_consumer():
    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body)
            
            # Adiciona timestamp à mensagem
            msg['timestamp'] = datetime.now().isoformat()
            
            cache.lpush(EVENTS_LIST_KEY, json.dumps(msg))
            
            cache.ltrim(EVENTS_LIST_KEY, 0, 99)
            
            cache.expire(EVENTS_LIST_KEY, EVENTS_CACHE_TIME)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=callback,
                auto_ack=False
            )
            channel.start_consuming()
        except Exception as e:
            print(f"Erro no consumidor: {e}")
            sleep(5)

@app.route("/events", methods=["GET"])
def get_events():
    try:
        events = cache.lrange(EVENTS_LIST_KEY, 0, -1)
        
        parsed_events = [json.loads(event) for event in events]
        
        return jsonify({
            "messages": parsed_events,
        })
    except Exception as e:
        return jsonify({
            "error": "Erro ao obter mensagens",
        }), 500

if __name__ == "__main__":
    cache.delete(EVENTS_LIST_KEY)
    
    consumer_thread = threading.Thread(target=rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    
    app.run(port=3001, debug=True)