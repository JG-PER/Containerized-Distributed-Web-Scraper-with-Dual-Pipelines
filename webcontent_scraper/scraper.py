# filename: webcontent_scraper/scraper.py

import pika
import time
import os
import requests
from bs4 import BeautifulSoup
import json
import random

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

REALISTIC_HEADERS_LIST = [
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    },
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.5',
        'Sec-Ch-Ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    },
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    }
]

def main():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=600))
            channel = connection.channel()
            print("PDF Scraper: Successfully connected to RabbitMQ.")
            
            channel.queue_declare(queue='pdf_task_queue', durable=True)
            channel.queue_declare(queue='pdf_content_queue', durable=True)

            def callback(ch, method, properties, body):
                task_url = body.decode()
                print(f" [x] PDF Scraper: Received task: {task_url}")
                
                max_retries = 3
                for i in range(max_retries):
                    try:
                        headers = random.choice(REALISTIC_HEADERS_LIST)
                        headers['Referer'] = 'https://www.google.com/'
                        print(f" [i] Attempt {i+1}/{max_retries} with User-Agent: {headers['User-Agent']}")

                        response = requests.get(task_url, headers=headers, timeout=20)
                        response.raise_for_status()

                        soup = BeautifulSoup(response.text, 'html.parser')
                        full_html_content = str(soup)

                        if full_html_content:
                            message_data = {"url": task_url, "html_content": full_html_content}
                            message_body = json.dumps(message_data)
                            channel.basic_publish(exchange='', routing_key='pdf_content_queue', body=message_body)
                            print(f" [o] SUCCESS: Sent full HTML from {task_url} to queue.")
                        else:
                            print(f" [!] WARNING: No content found in response from {task_url}")
                        
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                        # --- DELAY REMOVED ---
                        
                        return # Exit callback function, task is done

                    except requests.exceptions.RequestException as e:
                        print(f" [!] FAILED attempt {i+1}: {e}")
                        # --- RETRY DELAY REMOVED ---
                        if i >= max_retries - 1:
                            print(f" [!] All {max_retries} retries failed for {task_url}. Discarding message.")
                            ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue='pdf_task_queue', on_message_callback=callback)
            print(' [*] PDF Scraper: Waiting for tasks on queue "pdf_task_queue".')
            
            channel.start_consuming()

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
            print(f" [!] Connection error or stream lost: {e}. Reconnecting...")
            # --- RECONNECTION DELAY REMOVED ---
        except KeyboardInterrupt:
            print("Exiting.")
            break

if __name__ == '__main__':
    main()