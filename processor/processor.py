import pika
import time
import os
import psycopg2

# --- Database and RabbitMQ connection details from environment variables ---
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('POSTGRES_DB', 'scraper_data')
DB_USER = os.getenv('POSTGRES_USER', 'user')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

def get_db_connection():
    """Establishes a connection to the database, retrying if necessary."""
    while True:
        try:
            conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
            return conn
        except psycopg2.OperationalError as e:
            print(f" [!] Processor: Could not connect to database: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def setup_database(conn):
    """Ensures the required table exists in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scraped_data (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.commit()
    print(" [o] Processor: Database table verified/created.")

def main():
    # --- RabbitMQ Connection ---
    while True:
        try:
            mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = mq_connection.channel()
            print(" [o] Processor: Successfully connected to RabbitMQ.")
            break
        except pika.exceptions.AMQPConnectionError:
            print(" [!] Processor: Connection to RabbitMQ failed. Retrying...")
            time.sleep(5)

    channel.queue_declare(queue='data_queue', durable=True)
    db_conn = get_db_connection()
    setup_database(db_conn)

    def callback(ch, method, properties, body):
        nonlocal db_conn  # Moved to the top of the function to fix the SyntaxError
        data = body.decode()
        print(f" [x] Processor: Received data: '{data}'")
        try:
            with db_conn.cursor() as cur:
                cur.execute("INSERT INTO scraped_data (content) VALUES (%s);", (data,))
                db_conn.commit()
                print(f" [o] Processor: Successfully inserted data into database.")
        except (psycopg2.InterfaceError, psycopg2.OperationalError):
            print(" [!] Processor: Database connection lost. Reconnecting...")
            db_conn = get_db_connection() # Re-assign the connection directly
            with db_conn.cursor() as cur:
                 cur.execute("INSERT INTO scraped_data (content) VALUES (%s);", (data,))
                 db_conn.commit()
                 print(f" [o] Processor: Reconnected and inserted data.")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='data_queue', on_message_callback=callback)
    print(' [*] Processor: Waiting for data.')
    channel.start_consuming()

if __name__ == '__main__':
    main()