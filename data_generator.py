import time
import json
import random
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOPIC = 'cloud_metrics'
RESOURCES = ['ec2-web-server', 'lambda-auth', 'rds-main-db', 'ec2-worker-node']

def generate_metric(spike: bool = False) -> Dict[str, Any]:
    if spike:
        resource_id = 'ec2-worker-node'
        cpu_usage = random.uniform(800.0, 1000.0)
    else:
        resource_id = random.choice(RESOURCES)
        cpu_usage = random.uniform(10.0, 40.0)

    return {
        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        'resource_id': resource_id,
        'cpu_usage': round(cpu_usage, 2)
    }

def main() -> None:
    max_retries = 30
    producer = None
    
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            logging.info("Connected to Confluent Kafka!")
            break
        except NoBrokersAvailable:
            logging.warning(f"Waiting for Kafka to start... (Attempt {attempt+1}/{max_retries})")
            time.sleep(2)
            
    if not producer:
        logging.error("Could not connect to Kafka. Exiting.")
        return

    logging.info(f"Starting data generator for topic '{TOPIC}'...")

    try:
        counter = 0
        while True:
            spike = (counter > 0 and counter % 30 == 0)
            
            metric = generate_metric(spike)
                
            future = producer.send(TOPIC, value=metric)
            future.get(timeout=10) # Block until sent successfully
            
            if spike:
                logging.warning(f"🚨 ANOMALY INJECTED: {metric}")
            else:
                logging.info(f"Sent: {metric}")
                
            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping generator...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        producer.flush()
        producer.close()

if __name__ == '__main__':
    main()
