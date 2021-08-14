import os
import logging
from kafka import KafkaConsumer
import json
from app import app

from services import LocationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("udaconnect-connection-processor")

TOPIC_NAME = 'locations'
consumer = KafkaConsumer(TOPIC_NAME,
                         group_id='connection-processor-group',
                         bootstrap_servers=os.environ['KAFKA_SERVICE_SERVICE_HOST'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

logger.info("Processor ready to process locations")

for message in consumer:
    try:
        new_location = message.value
        logger.info(f"Received new location: {new_location}")
        with app.app_context():
            new_location = LocationService.create(new_location)
            logger.info(f"Successfully created new location: {new_location}")
    except Exception as e:
        logger.error(e)




