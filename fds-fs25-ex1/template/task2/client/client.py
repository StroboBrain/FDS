import sys
import grpc
import dservice_pb2
import dservice_pb2_grpc
import hservice_pb2
import hservice_pb2_grpc


def connect_insecure_channel_data_server(ip: str, port: int) -> dservice_pb2_grpc.DBStub:
    channel = grpc.insecure_channel(f'{ip}:{port}')
    return dservice_pb2_grpc.DBStub(channel)
    
def connect_insecure_channel_hash_server(ip: str, port: int) -> hservice_pb2_grpc.HSStub:
    channel = grpc.insecure_channel(f'{ip}:{port}')
    return hservice_pb2_grpc.HSStub(channel)
    
def register_user_password(username: str, password: str, d_stub: dservice_pb2_grpc.DBStub):
    usrpwd = dservice_pb2.UserPass(username=username, password=password)
    return d_stub.RegisterUser(usrpwd)
        
def store_data(username: str, password: str, message: str, d_stub: dservice_pb2_grpc.DBStub):
    usrpwdmsg = dservice_pb2.StoreReq(username=username, password=password, msg=message)
    return d_stub.StoreData(usrpwdmsg)

def get_data(username: str, password: str, d_stub: dservice_pb2_grpc.DBStub) -> str:
    usrpwd = dservice_pb2.UserPass(username=username, password=password)
    return d_stub.GetData(usrpwd)
    
def generate_passcode(username: str, password: str, d_stub: dservice_pb2_grpc.DBStub) -> str:
    usrpwd = dservice_pb2.UserPass(username=username, password=password)
    return d_stub.GenPasscode(usrpwd)
    
def get_authorized_data_from_data_server(passcode: dservice_pb2.Passcode, d_stub: dservice_pb2_grpc.DBStub):
    cd = dservice_pb2.Passcode(code=passcode)
    return d_stub.GetAuthData(cd)
    
def get_authorized_data_from_hash_server(passcode: dservice_pb2.Passcode, d_stub: dservice_pb2_grpc.DBStub):
    pass
    
   
if __name__ == '__main__':
    username = 'Leo'
    password = '1973'
    passcode = ''
    message = ''
    ip_ds = "127.0.0.1"
    ip_hs = "127.0.0.1"
    port_ds = 50051
    port_hs = 50052
    d_stub = connect_insecure_channel_data_server(ip_ds, port_ds)
    h_stub = None
    
    while True:
        print("Enter 1 to register new user and password.")
        print("Enter 2 to store message on the data server.")
        print("Enter 3 to retrieve message from data server using username and password.")
        print("Enter 4 to generat one-time passcode.")
        print("Enter 5 to retrieve message from data server using one-time passcode.")
        print("Enter 6 to retrieve (hashed) message from hash sever using one-time passcode.") 
        print("Enter 7 to quit.")
        user_input = int(input())
        match user_input:
            case 1:
                username = input("Username: ")
                password = input("Password: ")
                res = register_user_password(username, password, d_stub)
                if not res.success:
                    print('Failed to register user and password')
                else:
                    print("User and password registered successfully.")
            case 2:
                username = input("Username: ")
                password = input("Password: ")
                massage = input("Message: ")
                res = store_data(username, password, massage, d_stub)
                if not res.success:
                    print("Failed to store data")
                else:
                    print("Data stored successfully.")
            case 3:
                username = input("Username: ")
                password = input("Password: ")
                message = get_data(username, password, d_stub)
                if message.msg == '':
                    print('Invalid credentials')
                else:
                    print("Message: ", message.msg)
            case 4:
                username = input("Username: ")
                password = input("Password: ")
                passcode = generate_passcode(username, password, d_stub)
                if passcode.code == '':
                    print('Invalid credentials')
                else:
                    print("Passcode: ", passcode.code)
            case 5:
                passcode = input("Passcode: ")
                #message = get_authorized_data_from_data_server(passcode.code, d_stub)
                message = get_authorized_data_from_data_server(passcode, d_stub)
                if message.msg == '':
                    print('Invalid passcode')
                else:
                    print("Message: ", message.msg)
            case 6:
                h_stub = connect_insecure_channel_hash_server(ip_hs, port_hs)
                passcode = input("Passcode: ")
                request = hservice_pb2.Request(passcode=passcode, ip=ip_ds, port=port_ds)
                hashed_data = h_stub.GetHash(request)
                print("Hashed data: ", hashed_data)
            case 7:
                print("Client terminated")
                break
            case _: # default
                print("Invalid input")

    