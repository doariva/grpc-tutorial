import grpc
import logging
from concurrent import futures
from proto import example_pb2, example_pb2_grpc
from grpc_reflection.v1alpha import reflection

class ExampleServicer(example_pb2_grpc.ExampleServiceServicer):
    def SayHello(self, request, context):
        return example_pb2.HelloResponse(message='Hello, %s!' % request.name)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    example_pb2_grpc.add_ExampleServiceServicer_to_server(ExampleServicer(), server)
    reflection.enable_server_reflection("example.ExampleService", server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server started. Listening on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
