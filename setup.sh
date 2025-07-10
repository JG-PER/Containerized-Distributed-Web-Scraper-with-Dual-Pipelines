#!/bin/bash

# This script initializes the docker-compose.yml file for the project.

echo "Creating docker-compose.yml file..."

cat << EOF > docker-compose.yml
# Docker Compose file for the Distributed Web Scraper Project
# Defines the services, networks, and volumes for the application.

version: '3.8'

services:
  # Phase 2, Step 3: Task Queue Service
  # This service will manage and distribute scraping tasks.
  rabbitmq:
    image: "rabbitmq:3.13-management"
    container_name: rabbitmq
    ports:
      - "5672:5672"  # Port for AMQP protocol
      - "15672:15672" # Port for the management UI
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_running"]
      interval: 30s
      timeout: 30s
      retries: 3

  # Phase 2, Step 4: Database Service
  # This service will store the processed data. [cite_start]InfluxDB is also a good choice[cite: 21].
  db:
    image: "postgres:16"
    container_name: postgres-db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: scraper_data
    ports:
      - "5432:5432"
    volumes:
      - [cite_start]postgres-data:/var/lib/postgresql/data # Using a volume to persist database data[cite: 36].
    networks:
      - app-network
    healthcheck:
        test: ["CMD-SHELL", "pg_isready -U user -d scraper_data"]
        interval: 10s
        timeout: 5s
        retries: 5

# [cite_start]Define the custom bridge network for services to communicate[cite: 33].
networks:
  app-network:
    driver: bridge

# Define the named volume for persistent database storage.
volumes:
  postgres-data:
    driver: local

EOF

echo "docker-compose.yml has been created successfully."
echo "The file includes services for RabbitMQ and PostgreSQL, and a custom network named 'app-network'."