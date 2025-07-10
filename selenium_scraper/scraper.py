# filename: webContent_scraper/scraper.py

import pika
import time
import os
from bs4 import BeautifulSoup
import json
import random  # <-- This line was missing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
SELENIUM_HOST = os.getenv('SELENIUM_HOST', 'selenium')
SELENIUM_URL = f"http://{SELENIUM_HOST}:4444/wd/hub"


def get_selenium_driver():
    """Initializes and returns a remote Selenium driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Keep trying to connect to Selenium until it's ready
    while True:
        try:
            driver = webdriver.Remote(command_executor=SELENIUM_URL, options=chrome_options)
            print(" [o] PDF Scraper: Successfully connected to Selenium.")
            return driver
        except Exception as e:
            print(f" [!] PDF Scraper: Selenium not ready, retrying in 5s... Error: {e}")
            time.sleep(5)


def main():
    driver = get_selenium_driver()
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            print("PDF Scraper: Successfully connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            print("PDF Scraper: Connection to RabbitMQ failed. Retrying...")
            time.sleep(5)

    channel.queue_declare(queue='pdf_task_queue', durable=True)
    channel.queue_declare(queue='pdf_content_queue', durable=True)

    def callback(ch, method, properties, body):
        task_url = body.decode()
        print(f" [x] PDF Scraper: Received task, navigating with Selenium: {task_url}")
        
        try:
            # Command the remote browser to get the URL
            driver.get(task_url)
            
            # Add a small wait for dynamic content to load
            time.sleep(3) 

            # Get the final page source after JavaScript has executed
            html_content = driver.page_source
            
            # --- The rest of the logic is the same ---
            soup = BeautifulSoup(html_content, 'html.parser')
            body_content = soup.find('body')
            
            if body_content:
                message_data = {"url": task_url, "html_content": str(body_content)}
                message_body = json.dumps(message_data)
                channel.basic_publish(exchange='', routing_key='pdf_content_queue', body=message_body)
                print(f" [o] SUCCESS: Sent content from {task_url} to queue.")
            else:
                print(f" [!] WARNING: No <body> tag found in {task_url}")

        except Exception as e:
            print(f" [!] FAILED to process {task_url} with Selenium. Error: {e}")

        # Acknowledge the message to remove it from the queue
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # Add a delay to be respectful to the server
        delay = random.uniform(2, 5)
        print(f" [i] Waiting for {delay:.2f} seconds...")
        time.sleep(delay)

    channel.basic_consume(queue='pdf_task_queue', on_message_callback=callback)
    print(' [*] PDF Scraper: Waiting for tasks on queue "pdf_task_queue".')
    channel.start_consuming()


if __name__ == '__main__':
    main()