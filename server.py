import grpc
import logging
import subprocess
from concurrent import futures
from proto import example_pb2, example_pb2_grpc
from proto import my_pb2, my_pb2_grpc
from grpc_reflection.v1alpha import reflection

class ExampleServicer(example_pb2_grpc.ExampleServiceServicer):
    def SayHello(self, request, context):
        name = request.name
        response_message = self.run_command(name)
        return example_pb2.HelloResponse(message=response_message)

class MyServicer(my_pb2_grpc.MyServiceServicer):
    def RunCommand(self, name,context):
        try:
            command = f"echo {name}"
            result = exec_linux_cmd(command)
            logging.info(result)
            return my_pb2.MyResponse(message="OK")
        except subprocess.CalledProcessError as e:
            return my_pb2.MyResponse(message="NG")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))

    example_pb2_grpc.add_ExampleServiceServicer_to_server(ExampleServicer(), server)
    my_pb2_grpc.add_MyServiceServicer_to_server(MyServicer(), server)

    SERVICES = (
        example_pb2.DESCRIPTOR.services_by_name['ExampleService'].full_name,
        my_pb2.DESCRIPTOR.services_by_name['MyService'].full_name,
        reflection.SERVICE_NAME,
    )

    reflection.enable_server_reflection(SERVICES, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server started. Listening on port 50051")
    server.wait_for_termination()


def exec_linux_cmd(cmd):
    logging.info("run: " + cmd)
    res = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = res.stdout
    return res.decode("utf-8")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
