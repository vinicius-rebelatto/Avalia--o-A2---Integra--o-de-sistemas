from flask import Flask, request, jsonify
import redis
import pika
import json
import os

app = Flask(__name__)

# Configuração do Redis
redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)

# Lista em memória para armazenar eventos (alternativa ao Redis)
events = []

# Configuração do RabbitMQ
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_QUEUE = 'critical_events'

def setup_rabbitmq():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )  # Parêntese fechado aqui
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        return channel
    except Exception as e:
        print(f"Erro ao conectar ao RabbitMQ: {e}")
        return None

# Endpoint 1: POST /event
@app.route('/event', methods=['POST'])
def receive_event():
    try:
        event_data = request.json
        
        # Validação básica
        if not event_data or 'message' not in event_data:
            return jsonify({"error": "Dados do evento inválidos"}), 400
        
        # Adiciona timestamp se não existir
        if 'timestamp' not in event_data:
            event_data['timestamp'] = datetime.datetime.now().isoformat()
        
        # Armazena no Redis
        redis_key = f"event:{len(events) + 1}"
        redis_client.setex(redis_key, 3600, json.dumps(event_data))  # Expira em 1 hora
        
        # Armazena em memória
        events.append(event_data)
        
        return jsonify({"status": "Event received", "event": event_data}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 2: GET /events
@app.route('/events', methods=['GET'])
def get_events():
    try:
        # Tenta obter do cache Redis primeiro
        cached_events = []
        for key in redis_client.keys('event:*'):
            event = redis_client.get(key)
            if event:
                cached_events.append(json.loads(event))
        
        # Se não houver no Redis, retorna da memória
        if not cached_events and events:
            return jsonify(events)
        
        return jsonify(cached_events)
    
    except Exception as e:
        # Fallback para memória se Redis falhar
        return jsonify(events)

# Consumidor RabbitMQ em segundo plano
def start_rabbitmq_consumer():
    def callback(ch, method, properties, body):
        try:
            event = json.loads(body)
            print(f" [x] Received via RabbitMQ: {event}")
            
            # Processa o evento igual ao endpoint HTTP
            redis_key = f"rabbitmq_event:{len(events) + 1}"
            redis_client.setex(redis_key, 3600, json.dumps(event))
            events.append(event)
            
        except Exception as e:
            print(f"Error processing RabbitMQ message: {e}")

    try:
        channel = setup_rabbitmq()
        if channel:
            channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=callback,
                auto_ack=True)
            
            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
    except Exception as e:
        print(f"RabbitMQ consumer error: {e}")

if __name__ == '__main__':
    # Inicia o consumidor RabbitMQ em uma thread separada
    import threading
    rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer)
    rabbitmq_thread.daemon = True
    rabbitmq_thread.start()
    
    # Inicia o servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)