import sys
import grpc
import dservice_pb2
import dservice_pb2_grpc
import hservice_pb2
import hservice_pb2_grpc


def connect_insecure_channel(ip: str, port: int) -> dservice_pb2_grpc.DBStub:
    channel = grpc.insecure_channel(f'{ip}:{port}')
    return dservice_pb2_grpc.DBStub(channel)
    
def register_user_password(username: str, password: str, db_stub: dservice_pb2_grpc.DBStub):
    usrpwd = dservice_pb2.UserPass(username=username, password=password)
    res = db_stub.RegisterUser(usrpwd)
    if not res.success:
        print('Failed to register user and password')
        
def store_data(username: str, password: str, message: str, db_stub: dservice_pb2_grpc.DBStub):
    usrpwdmsg = dservice_pb2.StoreReq(username=username, password=password, msg=message)
    res = db_stub.StoreData(usrpwdmsg)
    if not res.success:
        print('Failed to store data')

def get_data(username: str, password: str, db_stub: dservice_pb2_grpc.DBStub) -> str:
    usrpwd = dservice_pb2.UserPass(username=username, password=password)
    msg = db_stub.GetData(usrpwd)
    if msg == '':
        print('Invalid credentials')
    return msg
    
def generate_passcode(username: str, password: str, db_stub: dservice_pb2_grpc.DBStub) -> str:
    usrpwd = dservice_pb2.UserPass(username=username, password=password)
    code = db_stub.GenPasscode(usrpwd)
    if code == '':
        print('Invalid credentials')
    return code
    
def get_authorized_data(passcode: dservice_pb2.Passcode, db_stub: dservice_pb2_grpc.DBStub):
    cd = dservice_pb2.Passcode(code=passcode)
    msg = db_stub.GetAuthData(cd)
    if msg.msg == '':
        print('Invalid passcode')
    return msg
    
   
if __name__ == '__main__':
    username = 'Leo'
    password = '1973'
    ip = "localhost"
    port = 50051
    db_stub = connect_insecure_channel(ip, port)
    register_user_password(username, password, db_stub) # fails after initial registration
    
    message_in = "Don't allow yourself to be trapped by your past experiences."
    store_data(username, password, message_in, db_stub)
    message_out = get_data(username, password, db_stub)
    #print(type(message_out))
    print("message_out: ", message_out.msg)
    
    passcode = generate_passcode(username, password, db_stub)
    print("passcode: ", passcode.code)
    #print(type(passcode))

    message_out_auth = get_authorized_data(passcode.code, db_stub)
    #print(type(message_out_auth))
    print("message_out_auth: ", message_out_auth.msg)