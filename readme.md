# Prova de Integração de sistemas – A2

Para começar a rodar as aplicações, é possível usar o comando:
```docker-compose up -d --build```

## O que cada API faz e como executá-la.
### api-node
A api node teem por objetivo simula sensores instalados nos poços de petróleo.

#### Seguem os endpoints da aplicação:
Rota Get ```http://localhost:3000/sensor-data```
Resposta da requisição:
``` json
{
    "temperature": "32.98",
    "pressure": "18.56",
    "timestamp": "2025-05-30T23:17:27.349Z"
}
```

Rota Post ```http://localhost:3000/alert```
Corpo de para envio da requisição:
``` json
{
  "message": "Temperatura crítica acima de 100°C detectada no poço BR-42",
  "severity": "high"  // (opcional: high/medium/low)
}
```

Resposta da requisição:
``` json
{
    "status": "Alert sent",
    "pythonResponse": {
        "event": {
            "message": "Temperatura crítica acima de 100°C detectada no poço BR-42",
            "severity": "high",
            "source": "node-sensor",
            "timestamp": "2025-05-30T23:17:24.115Z"
        },
        "status": "Event received"
    }
}
```


### api-python
A api python teem por objetivo gerenciar os alertas e conectar eles com o rabitmq para menssageria.


#### Seguem os endpoints da aplicação:
Rota Get ```http://localhost:5000/events```
Resposta da requisição(Ele aumenta conforme o número de eventos registrados):
``` json
[
    {
        "message": "Falha na válvula de segurança do tanque T-100",
        "severity": "critical",
        "source": "postman-test",
        "timestamp": "2025-05-30T22:05:00.000Z"
    },
    {
        "message": "Temperatura crítica acima de 100°C detectada no poço BR-42",
        "severity": "high",
        "source": "node-sensor",
        "timestamp": "2025-05-30T23:17:24.115Z"
    },
    {
        "message": "Falha na válvula de segurança do tanque T-100",
        "severity": "critical",
        "source": "postman-test",
        "timestamp": "2025-05-30T22:05:00.000Z"
    },
    {
        "message": "Falha na válvula de segurança do tanque T-100",
        "severity": "critical",
        "source": "postman-test",
        "timestamp": "2025-05-30T22:05:00.000Z"
    }
]
```

Rota Post ```http://localhost:5000/event```
Corpo de para envio da requisição:
``` json
{
  "source": "postman-test",
  "message": "Falha na válvula de segurança do tanque T-100",
  "severity": "critical",  // (opcional)
  "timestamp": "2025-05-30T22:05:00.000Z"  // (opcional - se omitido, a API gera automaticamente)
}
```

Resposta da requisição:
``` json
{
    "event": {
        "message": "Falha na válvula de segurança do tanque T-100",
        "severity": "critical",
        "source": "postman-test",
        "timestamp": "2025-05-30T22:05:00.000Z"
    },
    "status": "Event received"
}
```

## Como elas se comunicam.


## Onde o cache Redis foi usado.


## Como a fila RabbitMQ entra no fluxo.
