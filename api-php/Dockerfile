FROM php:8.0-apache

WORKDIR /var/www/html

# Instala dependências para RabbitMQ e ferramentas necessárias
RUN apt-get update && apt-get install -y \
    librabbitmq-dev \
    git \
    unzip \
    && docker-php-ext-install sockets \
    && pecl install amqp \
    && docker-php-ext-enable amqp

# Instala Composer e dependências
COPY composer.json .
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && composer install --no-dev --optimize-autoloader

COPY . .

EXPOSE 8000

CMD ["php", "-S", "0.0.0.0:8000"]