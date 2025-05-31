# Prova de Integração de sistemas – A2

Para começar a rodar as aplicações, é possível usar o comando:
```docker-compose up -d --build```

## O que cada API faz e como executá-la.
### api-node
A api node teem por objetivo simula sensores instalados nos poços de petróleo.

#### Seguem os endpoints da aplicação:
Rota Get ```http://localhost:3000/sensor-data```
##### Resposta da requisição:
``` json
{
    "temperature": "32.98",
    "pressure": "18.56",
    "timestamp": "2025-05-30T23:17:27.349Z"
}
```

Rota Post ```http://localhost:3000/alert```
##### Corpo de para envio da requisição:
``` json
{
  "message": "Temperatura crítica acima de 100°C detectada no poço BR-42",
  "severity": "high"  // (opcional: high/medium/low)
}
```

##### Resposta da requisição:
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

##### Resposta da requisição(Ele aumenta conforme o número de eventos registrados):
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
##### Corpo de para envio da requisição:
``` json
{
  "source": "postman-test",
  "message": "Falha na válvula de segurança do tanque T-100",
  "severity": "critical",  // (opcional)
  "timestamp": "2025-05-30T22:05:00.000Z"  // (opcional - se omitido, a API gera automaticamente)
}
```

##### Resposta da requisição:
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





### api-php
A api python teem por objetivo gerenciar transporte de equipamentos e comunicar quando acontecer alguma urgência.


#### Seguem os endpoints da aplicação:
Rota Get ```http://localhost:8000/equipments```

##### Resposta da requisição(Retorna uma lista simulada dos equipamentos, é somente uma lista criada localmente):
``` json
[
    {
        "id": 1,
        "name": "Bomba Centrífuga",
        "status": "operacional"
    },
    {
        "id": 2,
        "name": "Válvula de Segurança",
        "status": "manutenção"
    },
    {
        "id": 3,
        "name": "Sensor de Pressão",
        "status": "operacional"
    }
]
```

Rota Post ```http://localhost:8000/dispatch```
##### Corpo de para envio da requisição:
``` json
{
  "message": "Falha na bomba principal - urgente!"
}
```

##### Resposta da requisição:
``` json
{"status":"Mensagem enviada para a fila"}
```

### O RabitMQ está dockerizado e pode ser acessado em:
Ele permite ver a fila dos eventos críticos registrados na api python
 ```http://localhost:15672```
 usuário e senha: ```guest/guest```


## Como elas se comunicam.
Todas as 3 apis se comunicam, tendo a api-python no centro. A api-python é responsável por receber requisições de alerta das outras apis, armazenar o dados em cache com o redis e listar todos os eventos realizados.

A Api node ela envia alertas para a api-python, como sitado anteriomente.

Do outro lado a api-php se comunica com a api-python enviando mensagens na fila critical_events para a api-python, e de acordo com a fila a api-python vai consumindo essas mensagens em segundo plano.

## Onde o cache Redis foi usado.
### Na rota get ```http://localhost:3000/sensor-data```, é armazenado os dados simulados pelo usuário.
### Na rota get ```http://localhost:5000/event```, é armazenado os dados recebidos pela api-node e os dados recebidos na fila do rabitMQ, o qual é enviada pela api-php

## Como a fila RabbitMQ entra no fluxo.
A Fila do RabitMQ está entre as apis pyhton e php. A api-php possui a rota post ```http://localhost:8000/dispatch``` que está conectada ao RabitMQ como sender, enviando mensagens na fila quando ocorre um evento crítico, e do outro lado está a api-python como receiver, recebendo essas mensagens e as consumindo em segundo plano.