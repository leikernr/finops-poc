import time
import json
import random
from kafka import KafkaProducer
from datetime import datetime

# Initialize Kafka Producer
# Wait for broker to be available
while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        print("Connected to Kafka (Redpanda)!")
        break
    except Exception as e:
        print("Waiting for Kafka to start...")
        time.sleep(2)

TOPIC = 'cloud_metrics'

def generate_metric(spike=False):
    resources = ['ec2-web-server', 'lambda-auth', 'rds-main-db', 'ec2-worker-node']
    
    resource_id = random.choice(resources)
    base_cpu = random.uniform(10.0, 40.0)
    
    # We will measure cost based on cpu_usage units in our Flink job
    if spike and resource_id == 'ec2-worker-node':
        # Simulate a massive CPU/instance scale-out anomaly
        cpu_usage = random.uniform(800.0, 1000.0)
    else:
        cpu_usage = base_cpu

    # Round timestamp to seconds for easier windowing in PoC
    data = {
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'resource_id': resource_id,
        'cpu_usage': round(cpu_usage, 2)
    }
    return data

print(f"Starting data generator for topic '{TOPIC}'...")

try:
    counter = 0
    while True:
        # Inject an anomaly roughly every 30 seconds
        spike = (counter > 0 and counter % 30 == 0)
        
        # When spiking, ensure we pick the worker node
        metric = generate_metric(spike)
        if spike:
            metric['resource_id'] = 'ec2-worker-node'
            metric['cpu_usage'] = round(random.uniform(800.0, 1000.0), 2)
            
        producer.send(TOPIC, value=metric)
        
        if spike:
            print(f"🚨 ANOMALY INJECTED: {metric}")
        else:
            print(f"Sent: {metric}")
            
        counter += 1
        time.sleep(1) # Send 1 event per second
except KeyboardInterrupt:
    print("Stopping generator...")
finally:
    producer.flush()
    producer.close()
