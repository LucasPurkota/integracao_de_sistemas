<?php
header("Content-Type: application/json");

// Configurações do RabbitMQ
define('RABBITMQ_HOST', 'rabbitmq');
define('RABBITMQ_PORT', 5672);
define('RABBITMQ_USER', 'guest');
define('RABBITMQ_PASS', 'guest');
define('RABBITMQ_QUEUE', 'logistica_urgente');

// Endpoint: Lista de equipamentos
if ($_SERVER['REQUEST_METHOD'] === 'GET' && parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) === '/equipments') {
    $equipments = [
        ['id' => 1, 'name' => 'Gerador 3000W', 'status' => 'disponível'],
        ['id' => 2, 'name' => 'Transformador 220V', 'status' => 'em manutenção'],
        ['id' => 3, 'name' => 'Painel Solar 150W', 'status' => 'disponível']
    ];
    
    echo json_encode($equipments);
    exit;
}

// Endpoint: Envio de mensagem para RabbitMQ
if ($_SERVER['REQUEST_METHOD'] === 'POST' && parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) === '/dispatch') {
    $data = json_decode(file_get_contents('php://input'), true);
    
    if (!$data || !isset($data['message'])) {
        http_response_code(400);
        echo json_encode(['error' => 'Campo "message" é obrigatório']);
        exit;
    }
    
    try {
        $connection = new AMQPConnection([
            'host' => RABBITMQ_HOST,
            'port' => RABBITMQ_PORT,
            'login' => RABBITMQ_USER,
            'password' => RABBITMQ_PASS
        ]);
        
        $connection->connect();
        $channel = new AMQPChannel($connection);
        
        // Cria uma exchange dedicada para evitar conflitos
        $exchange = new AMQPExchange($channel);
        $exchange->setName('logistica_exchange');
        $exchange->setType(AMQP_EX_TYPE_DIRECT);
        $exchange->setFlags(AMQP_DURABLE);
        $exchange->declareExchange();
        
        // Configura a fila
        $queue = new AMQPQueue($channel);
        $queue->setName(RABBITMQ_QUEUE);
        $queue->setFlags(AMQP_DURABLE);
        $queue->declareQueue();
        $queue->bind('logistica_exchange', RABBITMQ_QUEUE);
        
        // Publica a mensagem
        $exchange->publish(
            json_encode($data),
            RABBITMQ_QUEUE,
            AMQP_NOPARAM,
            ['delivery_mode' => AMQP_DURABLE]
        );
        
        echo json_encode(['status' => 'Mensagem enviada para RabbitMQ']);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode([
            'error' => 'Erro ao enviar mensagem',
            'details' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);
    }
    exit;
}

// Rota não encontrada
http_response_code(404);
echo json_encode(['error' => 'Endpoint não encontrado']);