import json
import logging
import random
import time
from datetime import datetime, timezone
from typing import Any

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TOPIC = 'cloud_metrics'
RESOURCES = ['ec2-web-server', 'lambda-auth', 'rds-main-db', 'ec2-worker-node']

def generate_metric(spike: bool = False) -> dict[str, Any]:
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
            logger.info("Connected to Confluent Kafka!")
            break
        except NoBrokersAvailable:
            logger.warning(f"Waiting for Kafka to start... (Attempt {attempt+1}/{max_retries})")
            time.sleep(2)
            
    if not producer:
        logger.error("Could not connect to Kafka. Exiting.")
        return

    logger.info(f"Starting data generator for topic '{TOPIC}'...")

    try:
        counter = 0
        while True:
            spike = (counter > 0 and counter % 30 == 0)
            
            metric = generate_metric(spike)
                
            future = producer.send(TOPIC, value=metric)
            future.get(timeout=10) # Block until sent successfully
            
            if spike:
                logger.warning(f"🚨 ANOMALY INJECTED: {metric}")
            else:
                logger.info(f"Sent: {metric}")
                
            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping generator...")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Unexpected error: {e}")
    finally:
        producer.flush()
        producer.close()

if __name__ == '__main__':
    main()
