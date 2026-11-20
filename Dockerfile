
FROM php:8.2-apache

RUN apt-get update && apt-get install -y libcurl4-openssl-dev \
    && docker-php-ext-install curl mysqli pdo pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/Listen 80/Listen 10000/' /etc/apache2/ports.conf

RUN sed -i 's/<VirtualHost \*:80>/<VirtualHost *:10000>/' /etc/apache2/sites-available/000-default.conf

RUN a2enmod rewrite

COPY . /var/www/html/

EXPOSE 10000
