# filename: scheduler.py

import pika
import sys

def send_tasks(filepath, queue_name):
    """
    Reads URLs from a file and sends them as tasks to a specified RabbitMQ queue.
    
    Usage: python3 scheduler.py <filepath> <queue_name>
    Example: python3 scheduler.py urls_for_pdf.txt pdf_task_queue
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        with open(filepath, 'r') as f:
            for url in f:
                url = url.strip()
                if url:
                    channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=url,
                        properties=pika.BasicProperties(
                            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                        ))
                    print(f" [x] Sent '{url}' to queue '{queue_name}'")
        connection.close()
        print("\nAll tasks sent successfully.")
    
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 scheduler.py <filepath> <queue_name>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    queue = sys.argv[2]
    send_tasks(file_path, queue)