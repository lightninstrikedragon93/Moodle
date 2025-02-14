from concurrent import futures
from contextlib import contextmanager
import datetime
import uuid
import bcrypt
import grpc
import jwt
import crud
import auth_pb2 as auth_pb2
import auth_pb2_grpc as auth_pb2_grpc
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from google.protobuf.json_format import MessageToDict

SECRET_KEY = "this-is-the-super-key"
ALGORITHM = "HS256"
BLACKLIST = set()

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        pass

    def Authenticate(self, request, context):
        with get_db_session() as db:
            try:
                user = crud.get_user_by_username(db, user_username=request.username)
                if user and bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
                    token = jwt.encode({
                        'iss': '[::]:50051',
                        'sub': f"{user.username}:{user.uid}",
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3),
                        'jti': str(uuid.uuid4()),
                        'role': user.role
                    }, SECRET_KEY, algorithm=ALGORITHM)
                    print(f'Authentication: {request.username} token: {token}')
                    return auth_pb2.AuthResponse(token=token)
                else:
                    context.set_details("Invalid username or password")
                    context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                    return auth_pb2.AuthResponse(token="")
            except Exception as e:
                context.set_details(f"Error during authentication: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return auth_pb2.AuthResponse(token="")


    def ValidateToken(self, request, context):
        if request.token in BLACKLIST:
            return auth_pb2.ValidationResponse(
                valid=False,
                message=f"Token is blacklisted {request.token}",
                sub="",
                role=""
            )

        try:
            print(f"Token to decode: {request.token}")
            payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"Decoded payload: {payload}")
            if 'exp' in payload and datetime.datetime.utcfromtimestamp(payload['exp']) < datetime.datetime.utcnow():
                BLACKLIST.add(request.token)
            return auth_pb2.ValidationResponse(
                valid=True,
                message="Token is valid",
                sub=str(payload['sub']),
                role=str(payload['role'])
            )
        except jwt.ExpiredSignatureError:
            BLACKLIST.add(request.token)
            return auth_pb2.ValidationResponse(
                valid=False,
                message="Token has expired",
                sub="",
                role=""
            )
        except jwt.InvalidTokenError as e:
            BLACKLIST.add(request.token)
            return auth_pb2.ValidationResponse(
                valid=False,
                message=f"Invalid token: {str(e)}",
                sub="",
                role=""
            )
        
    def DestroyToken(self, request, context):
        BLACKLIST.add(request.token)
        return auth_pb2.DestroyResponse(
            success=True,
            message="Token has been blacklisted"
        )
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at [::]:50051")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()