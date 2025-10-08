import grpc
import hservice_pb2
import hservice_pb2_grpc
import dservice_pb2
import dservice_pb2_grpc

#library to create hash values
import hashlib

#used for synchronous communication
from concurrent.futures import ThreadPoolExecutor

#inherits from hservice .proto thing to make sure the format is rigt
class gRPCServerImplementationClass(hservice_pb2_grpc.HSServicer):
    def GetHash(self, request, something):
        #build a connection to localhost:50051
        target = f"{request.ip}:{request.port}"
        #close chanel if we are done in the chanel.
        with grpc.insecure_channel(target) as channel:
            #create a stub (client proxy = handles networking usw.) so we can use rpc's like normal methods in python
            d_stub = dservice_pb2_grpc.DBStub(channel)
            #here we benefit from the stub
            pdata = d_stub.GetAuthData(dservice_pb2.Passcode(code=request.passcode))
        #read message from pdata in a string format
        msg = getattr(pdata, "msg", "")
        #convert into utf-8 to formarat msg (format requirement of sha) and then return a hexadecimal string. 
        digest = hashlib.sha256(msg.encode("utf-8")).hexdigest()

        return hservice_pb2.Response(hash=digest)

def serve():
    #start a server with 10 Threads to grant multible requests
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    #tell the workers what to do (so they can access the hashgenerator)
    hservice_pb2_grpc.add_HSServicer_to_server(gRPCServerImplementationClass(), server)
    #tell the workers on which port to wait for customers
    server.add_insecure_port("[::]:50052")
    print("Hash server listening on :50052")
    server.start()
    #ensure that the server stays open by blocking furter executeion.
    server.wait_for_termination()

if __name__ == '__main__':
    serve()