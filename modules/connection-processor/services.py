from typing import Dict

from app import db
from models import Location
from geoalchemy2.functions import ST_AsText, ST_Point


class LocationService:
    @staticmethod
    def create(location: Dict) -> Location:
        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
        db.session.add(new_location)
        db.session.commit()

        return new_location