import logging
import time
import grpc
import person_pb2
import person_pb2_grpc

from app import app
from concurrent import futures
from services import PersonService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("udaconnect-person-grpc")


class PersonServer(person_pb2_grpc.PersonServiceServicer):
    def Create(self, request, context):
        request_person = {
            "id": request.id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "company_name": request.company_name,
        }

        logger.info(f"Received Create message: {request_person}")
        with app.app_context():
            PersonService.create(request_person)
            return person_pb2.PersonMessage(**request_person)

    def GetById(self, request, context):
        person_id = request.id
        logger.info(f"Received GetById message: {person_id}")
        with app.app_context():
            person = PersonService.retrieve(person_id)
            dict_person = {
                "id": person.id,
                "first_name": person.first_name,
                "last_name": person.last_name,
                "company_name": person.company_name
            }
            return person_pb2.PersonMessage(**dict_person)

    def Get(self, request, context):
        logger.info(f"Received Get message")
        with app.app_context():
            person_model_list = PersonService.retrieve_all()
            person_list = [person_pb2.PersonMessage(
                                id=person_model.id,
                                first_name=person_model.first_name,
                                last_name=person_model.last_name,
                                company_name=person_model.company_name) for person_model in person_model_list]
            result = person_pb2.PersonMessageList()
            result.items.extend(person_list)
            return result


# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
person_pb2_grpc.add_PersonServiceServicer_to_server(PersonServer(), server)


print("Server starting on port 5000...")
server.add_insecure_port("[::]:5000")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)



