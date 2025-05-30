const express = require('express');
const redis = require('redis');
const axios = require('axios');

const app = express();
app.use(express.json());

// Configuração do Redis para Docker
const redisClient = redis.createClient({
    url: 'redis://redis:6379'  // Nome do serviço no docker-compose
});

redisClient.on('error', (err) => console.log('Redis Client Error', err));
redisClient.connect();

// Simulação de dados de sensor
function generateSensorData() {
    return {
        temperature: (Math.random() * 100).toFixed(2),
        pressure: (Math.random() * 50).toFixed(2),
        timestamp: new Date().toISOString()
    };
}

// Endpoint 1: GET /sensor-data
app.get('/sensor-data', async (req, res) => {
    try {
        const cacheKey = 'sensor-data';
        const cachedData = await redisClient.get(cacheKey);

        if (cachedData) {
            console.log('Retornando dados do cache');
            return res.json(JSON.parse(cachedData));
        }

        const sensorData = generateSensorData();
        // Cache por 30 segundos
        await redisClient.setEx(cacheKey, 30, JSON.stringify(sensorData));
        
        console.log('Retornando dados frescos');
        res.json(sensorData);
    } catch (error) {
        console.error(error);
        res.status(500).send('Erro ao obter dados do sensor');
    }
});

// Endpoint 2: POST /alert
app.post('/alert', async (req, res) => {
    try {
        const { message } = req.body;
        
        if (!message) {
            return res.status(400).send('Mensagem de alerta é obrigatória');
        }

        // Envia o alerta para a API Python (nome do serviço no docker-compose)
        const response = await axios.post('http://api-python:5000/event', {
            source: 'node-sensor',
            message: message,
            severity: 'high',
            timestamp: new Date().toISOString()
        });

        res.json({ status: 'Alert sent', pythonResponse: response.data });
    } catch (error) {
        console.error('Erro ao enviar alerta:', error.message);
        res.status(502).json({ 
            error: 'Erro ao enviar alerta',
            details: error.message
        });
    }
});

// Configuração do servidor
const PORT = 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`API Node.js rodando na porta ${PORT}`);
});