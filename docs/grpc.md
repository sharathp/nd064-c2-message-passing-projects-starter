# GRPC Implementation

* gRPC definition file - [person.proto](../modules/person-grpc/person.proto)
  * Generated `_pb2` and `*_pb2_grpc` files in the same directory as the above proto file using the following command: 
  `python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ person.proto`
* Server implementation - [server.py](../modules/person-grpc/server.py)
* Client implementation - [PersonService](../modules/connection-api/app/udaconnect/services.py)
