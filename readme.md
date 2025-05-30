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

## Como elas se comunicam.


## Onde o cache Redis foi usado.


## Como a fila RabbitMQ entra no fluxo.
