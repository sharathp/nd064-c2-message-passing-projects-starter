import logging
import grpc
import person_pb2
import person_pb2_grpc

from datetime import datetime, timedelta
from typing import Dict, List

from app import db, kafka_producer   # noqa
from app.udaconnect.models import Connection, Location, Person
from app.udaconnect.schemas import LocationSchema
from sqlalchemy.sql import text


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-person-api")

TOPIC_KAFKA_LOCATIONS = "locations"
BASE_URL_PERSON_API = "http://udaconnect-person-api:5000/api"

channel = grpc.insecure_channel("udaconnect-person-grpc:5000")
person_stub = person_pb2_grpc.PersonServiceStub(channel)

class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        locations: List = db.session.query(Location).filter(
            Location.person_id == person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()

        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in PersonService.retrieve_all()}

        # Prepare arguments for queries
        data = []
        for location in locations:
            data.append(
                {
                    "person_id": person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )

        query = text(
            """
        SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
        FROM    location
        WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
        AND     person_id != :person_id
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
        """
        )
        result: List[Connection] = []
        for line in tuple(data):
            for (
                exposed_person_id,
                location_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in db.engine.execute(query, **line):
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)

                result.append(
                    Connection(
                        person=person_map[exposed_person_id], location=location,
                    )
                )

        return result


class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        # pass the location to be created into kafka topic
        kafka_producer.send(TOPIC_KAFKA_LOCATIONS, location)
        return location


class PersonService:

    # Retrieve from person-grpc
    @staticmethod
    def retrieve_all() -> List[Person]:
        response = person_stub.Get(person_pb2.Empty())
        person_list = [Person(id=item.id,
                              first_name=item.first_name,
                              last_name=item.last_name,
                              company_name=item.company_name) for item in response.items]
        return person_list
