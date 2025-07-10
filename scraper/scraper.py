import pika
import time
import os

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

def main():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            print("Scraper: Successfully connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            print("Scraper: Connection to RabbitMQ failed. Retrying...")
            time.sleep(5)

    # Declare the queue we receive tasks from
    channel.queue_declare(queue='task_queue', durable=True)
    # Declare the queue we send results to
    channel.queue_declare(queue='data_queue', durable=True)

    def callback(ch, method, properties, body):
        task_url = body.decode()
        print(f" [x] Scraper: Received task: {task_url}")
        
        # Simulate scraping and generating a result
        result_data = f"Scraped data from: {task_url}"
        
        # Publish the result to the data_queue for the processor
        channel.basic_publish(
            exchange='',
            routing_key='data_queue',
            body=result_data,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(f" [x] Scraper: Sent result to data_queue.")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    print(' [*] Scraper: Waiting for tasks.')
    channel.start_consuming()

if __name__ == '__main__':
    main()