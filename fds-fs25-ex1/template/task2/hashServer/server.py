import grpc
import hservice_pb2
import hservice_pb2_grpc
import dservice_pb2
import dservice_pb2_grpc

import hashlib

from concurrent import futures

#https://codelabs.developers.google.com/grpc/getting-started-grpc-python#4
class MyHSServicer(hservice_pb2_grpc.HSServicer):

    def GetHash(self, request, context):
        channel = grpc.insecure_channel(f'{request.ip}:{request.port}')
        d_stub = dservice_pb2_grpc.DBStub(channel)
        data = d_stub.GetAuthData(dservice_pb2.Passcode(code=request.passcode))
        # https://realpython.com/ref/stdlib/hashlib/
        hashed_data = hashlib.sha256(data.msg.encode("utf-8")).hexdigest()
        return hservice_pb2.Response(hash=hashed_data)
 

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hservice_pb2_grpc.add_HSServicer_to_server(MyHSServicer(), server)
    server.add_insecure_port("[::]:50052")
    print("Hash server listening on port 50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
    