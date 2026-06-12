<?php

header('Content-Type: application/json');

// načtení JSON těla
$raw = file_get_contents('php://input');

$data = json_decode($raw, true);

// jednoduchý log pro kontrolu
file_put_contents(
    __DIR__ . '/api_log.txt',
    date('Y-m-d H:i:s') . ' ' .
    $raw . PHP_EOL,
    FILE_APPEND
);

// kontrola API klíče (volitelné)
$apiKey = $_SERVER['HTTP_X_API_KEY'] ?? '';

if ($apiKey !== '12345678')
{
    http_response_code(401);

    echo json_encode([
        'ok' => false,
        'error' => 'Invalid API key'
    ]);

    exit;
}

// kontrola dat
if (
    !isset($data['id']) ||
    !isset($data['time']) ||
    !isset($data['timestamp'])
)
{
    http_response_code(400);

    echo json_encode([
        'ok' => false,
        'error' => 'Missing data'
    ]);

    exit;
}

// odpověď pro RoboCounter
echo json_encode([
    'ok' => true,
    'message' => 'Data accepted',
    'received' => $data
]);

// příklad dat na serveru v souboru: 2026-06-12 10:25:23 {"gate_id": 2, "team_id": 2, "id": 6, "time": 16.0, "timestamp": "2026-06-12 10:25:23"}