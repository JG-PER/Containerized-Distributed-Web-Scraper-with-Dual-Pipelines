# Distributed Web Scraper with Dual Pipelines

This project demonstrates a full-stack, distributed application built with a microservices architecture using Docker and Docker Compose. It features two independent, parallel data processing pipelines that run simultaneously. This project also includes advanced anti-blocking techniques, such as realistic browser headers and rate-limiting, and provides a selectable backend for the PDF pipeline (a fast `requests`-based scraper or a powerful `Selenium`-based headless browser).

1.  A **Real-Time Dashboard Pipeline** that processes simple tasks and visualizes the results on a web interface.
2.  A **PDF Generation Pipeline** that scrapes live web content from a list of URLs and saves the content as PDF files.

The entire application stack is containerized and orchestrated through Docker Compose files, showcasing a robust and scalable design.

---

## Architecture Overview

The application is split into two distinct workflows, each triggered by sending a task to a different message queue.

### Pipeline A: Real-Time Dashboard

This pipeline is designed for lightweight data processing and visualization.

**Data Flow:**
`[Scheduler]` -> `(task_queue)` -> `[Scraper]` -> `(data_queue)` -> `[Processor]` -> `[Database]` -> `[Backend API]` -> `[Frontend]`

### Pipeline B: PDF Generation

This pipeline can be run with one of two scraper backends: a fast, lightweight `requests` implementation (default) or a robust `Selenium` implementation for JavaScript-heavy sites.

**Data Flow:**
`[Scheduler]` -> `(pdf_task_queue)` -> `[PDF Scraper Backend]` -> `(pdf_content_queue)` -> `[WebContent Processor]` -> `(PDF Files)`

---

## Core Components

* **Scheduler (`scheduler.py`)**: A Python script run on the host machine to publish URLs from a text file to the desired pipeline's starting queue.
* **Task Queue (`rabbitmq`)**: A shared RabbitMQ message broker that routes tasks to the correct pipeline.
* **Selenium (`selenium`)**: A standalone Selenium service running a headless Chromium browser, used by the advanced scraper to render JavaScript and bypass sophisticated anti-bot measures.

### Dashboard Pipeline Services

* **`scraper`**: A simple Python worker that consumes tasks from `task_queue` and passes a simulated result to `data_queue`.
* **`processor`**: A Python worker that consumes from `data_queue` and stores the simple string data in the database.
* **`db`**: A PostgreSQL database for storing data from the dashboard pipeline.
* **`backend_api`**: A Python Flask API that serves data from the database.
* **`frontend`**: An Nginx web server that displays the data from the API on a simple webpage.

### PDF Pipeline Services

* **`webcontentprocessor`**: A Python worker that consumes HTML content from `pdf_content_queue`, converts it to a PDF using WeasyPrint, and saves the file to a persistent volume.
* **Selectable Scraper Backends**:
    * **`webcontentscraper` (Default)**: An advanced Python worker using the `requests` library with realistic, rotating headers and intelligent retries.
    * **`selenium_scraper` (Override)**: A Python worker that controls the `selenium` service to scrape dynamic, JavaScript-heavy websites.

---

## Technology Stack

* **Containerization**: Docker & Docker Compose
* **Backend**: Python (Flask, Pika, Psycopg2, Requests, BeautifulSoup4, WeasyPrint, Brotli, Selenium)
* **Message Queue**: RabbitMQ
* **Database**: PostgreSQL
* **Browser Automation**: Selenium
* **Web Servers**: Nginx

---

## Getting Started

### Prerequisites

* Docker & Docker Compose
* Python 3 and `pip` installed on your host machine (for the scheduler script).

### Setup & Installation

1.  **Install Python Dependency**: The scheduler script requires the `pika` library. Install it on your computer by running:
    ```sh
    pip install pika
    ```
2.  **Verify Project Structure**: Ensure all service directories (`scraper`, `processor`, `backend_api`, `frontend`, `webcontent_scraper`, `selenium_scraper`) and configuration files (`docker-compose.yml`, `docker-compose.selenium.yml`) are correctly named and located in the project root.

---

## Launching the Application

The application has two launch modes for the PDF Generation Pipeline with commands and details in the commands text file. 
This file also contains most basic details for running the program. 
