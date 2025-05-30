<?php
require_once __DIR__ . '/vendor/autoload.php';

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

// Dados simulados de equipamentos
$equipments = [
    ["id" => 1, "name" => "Bomba Centrífuga", "status" => "operacional"],
    ["id" => 2, "name" => "Válvula de Segurança", "status" => "manutenção"],
    ["id" => 3, "name" => "Sensor de Pressão", "status" => "operacional"]
];

// Endpoint 1: GET /equipments
if ($_SERVER['REQUEST_METHOD'] === 'GET' && $_SERVER['REQUEST_URI'] === '/equipments') {
    header('Content-Type: application/json');
    echo json_encode($equipments);
    exit;
}

// Endpoint 2: POST /dispatch
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_SERVER['REQUEST_URI'] === '/dispatch') {
    $input = json_decode(file_get_contents('php://input'), true);

    if (!isset($input['message'])) {
        http_response_code(400);
        echo json_encode(["error" => "Campo 'message' é obrigatório"]);
        exit;
    }

    // Publica mensagem no RabbitMQ
    try {
        $connection = new AMQPStreamConnection('rabbitmq', 5672, 'guest', 'guest');
        $channel = $connection->channel();
        $channel->queue_declare('critical_events', false, true, false, false);

        $message = new AMQPMessage(
            json_encode([
                'source' => 'php-logistics',
                'message' => $input['message'],
                'timestamp' => date('c')
            ]),
            ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
        );

        $channel->basic_publish($message, '', 'critical_events');
        $channel->close();
        $connection->close();

        echo json_encode(["status" => "Mensagem enviada para a fila"]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(["error" => "Erro ao enviar mensagem: " . $e->getMessage()]);
    }
    exit;
}

// Rota não encontrada
http_response_code(404);
echo json_encode(["error" => "Endpoint não encontrado"]);