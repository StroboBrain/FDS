import sys
import grpc
import dservice_pb2
import dservice_pb2_grpc
import hservice_pb2
import hservice_pb2_grpc


DATA_IP, DATA_PORT = "localhost", 50051
HASH_IP, HASH_PORT = "localhost", 50052
   
if __name__ == '__main__':
    username = 'ChMaKeNo'
    password = 'yourPassword'
    message = "message for hashing"

    with grpc.insecure_channel(f"{DATA_IP}:{DATA_PORT}") as ch:
        d = dservice_pb2_grpc.DBStub(ch)

        #register user
        reUser = d.RegisterUser(dservice_pb2.UserPass(username = username, password= password))
        #Store Data
        reUser = d.StoreData(dservice_pb2.StoreReq(username = username, password= password, msg = message))
        #generate (passkey/passcode)
        passkey = d.GenPasscode(dservice_pb2.UserPass(username = username, password= password)).code
        print("passkey: ", passkey)

    #talk to hash server
    with grpc.insecure_channel(f"{HASH_IP}:{HASH_PORT}") as ch:
        #hashservice stub (client stub to access the hashservice)
        hashservice = hservice_pb2_grpc.HSStub(ch)
        #make RPC to the HashServer
        res = hashservice.GetHash(hservice_pb2.Request(passcode= passkey, ip=DATA_IP, port=DATA_PORT))
        print("Hash:", res.hash)
