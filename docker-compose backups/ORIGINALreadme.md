# Distributed Web Scraper with Real-Time Data Visualization

This project demonstrates a full-stack, distributed web scraping application built using a microservices architecture. Each component of the application runs in its own Docker container, and the entire stack is orchestrated using Docker Compose.

The application simulates a web scraping pipeline where tasks are queued, processed by scalable workers, stored in a database, and finally visualized on a real-time web dashboard.

---

## Architecture Overview

The application consists of six interconnected services that form a complete data pipeline. The flow of data is as follows:

**`[User]`** -> **`[RabbitMQ UI]`** -> `(task_queue)` -> **`[Scraper]`** -> `(data_queue)` -> **`[Processor]`** -> **`[PostgreSQL DB]`** <- **`[Backend API]`** <- **`[Frontend]`**

---

## Core Components

* **Scraper (`scraper/`)**: A Python worker that listens for tasks (URLs) on the `task_queue`, simulates scraping, and places the resulting data onto the `data_queue`.
* **Task Queue (`rabbitmq`)**: A RabbitMQ message broker that manages the distribution of tasks to the scraper workers and data to the processor workers.
* **Data Processor (`processor/`)**: A Python worker that listens for raw data on the `data_queue`, processes it, and stores it in the PostgreSQL database.
* **Database (`db`)**: A PostgreSQL database service for persistent storage of the scraped data. Data is stored in a `scraped_data` table.
* **Backend API (`backend_api/`)**: A Python Flask API that retrieves the processed data from the database and exposes it via a JSON endpoint.
* **Frontend (`frontend/`)**: A simple Nginx web server that serves a static HTML page. This page uses JavaScript to fetch data from the Backend API and display it to the user.

---

## Technology Stack

* **Containerization**: Docker & Docker Compose
* **Backend**: Python (Flask)
* **Message Queue**: RabbitMQ
* **Database**: PostgreSQL
* **Frontend**: HTML, CSS, JavaScript (served by Nginx)
* **Python Libraries**: `pika` (RabbitMQ), `psycopg2` (PostgreSQL), `Flask`

---

## Getting Started

### Prerequisites

* Docker
* Docker Compose

### Running the Application

1.  Ensure all the service directories (`scraper`, `processor`, `backend_api`, `frontend`) and the `docker-compose.yml` file are in the project root.
2.  Open a terminal in the project's root directory and run the following command to build and start all the services:

    ```sh
    docker-compose up --build -d
    ```

The application is now running.

---

## How to Use

1.  **Publish a Task**:
    * Navigate to the RabbitMQ management dashboard at **`http://localhost:15672`**.
    * Log in with `guest` / `guest`.
    * Go to the **Queues and Streams** tab, click on **`task_queue`**.
    * Expand the **Publish message** section, enter a URL (e.g., `https://example.com`) in the **Payload**, and click **Publish**.

2.  **View the Data**:
    * **Raw JSON Data**: You can see the API output by navigating to **`http://localhost:5001/api/data`**.
    * **Frontend Dashboard**: To see the final visualization, navigate to **`http://localhost:8080`**. The page will load and display all the data that has been scraped and processed.