# filename: webContent_processor/processor.py

import pika
import time
import os
import json
from weasyprint import HTML
import hashlib

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
OUTPUT_DIR = '/output'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f" [o] PDF Processor: Output directory '{OUTPUT_DIR}' is ready.")

    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            print(" [o] PDF Processor: Successfully connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(" [!] PDF Processor: Connection to RabbitMQ failed. Retrying...")
            time.sleep(5)

    channel.queue_declare(queue='pdf_content_queue', durable=True)

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            url = data['url']
            html_content = data['html_content']
            print(f" [x] PDF Processor: Received content for {url}. Generating PDF...")

            filename = f"{hashlib.sha256(url.encode()).hexdigest()[:12]}.pdf"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            HTML(string=html_content, base_url=url).write_pdf(filepath)
            print(f" [o] PDF Processor: Successfully created PDF: {filename}")

        except Exception as e:
            print(f" [!] PDF Processor: Failed to process message. Error: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='pdf_content_queue', on_message_callback=callback)

    print(' [*] PDF Processor: Waiting for data on queue "pdf_content_queue".')
    channel.start_consuming()

if __name__ == '__main__':
    main()