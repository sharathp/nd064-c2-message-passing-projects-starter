import os
import logging
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("udaconnect-connection-processor")

logger.info(os.environ)

TOPIC_NAME = 'locations'
consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=os.environ['KAFKA_SERVICE_SERVICE_HOST'])

logger.info(f"Metrics")
logger.info(f"{consumer.metrics()}")

for message in consumer:
    logger.info(f"{message}")

