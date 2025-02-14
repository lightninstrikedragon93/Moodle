from fastapi import Request, HTTPException, Response
from grpc import insecure_channel
import jwt
from auth_pb2_grpc import AuthServiceStub
from auth_pb2 import TokenRequest

SECRET_KEY= "this-is-the-super-key"
ALGORITHM = "HS256"
class AuthMiddleware:
    def __init__(self, app):
        self.app = app
        self.channel = insecure_channel('auth_service:50051')
        self.stub = AuthServiceStub(self.channel)

    async def __call__(self, scope, receive, send):
        
        request = Request(scope, receive)

        if request.method == "OPTIONS":
            headers = {
                "Access-Control-Allow-Origin": "http://localhost:3000",  
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
            }
            response = Response(status_code=200, headers=headers)
            await response(scope, receive, send)
            return
        
        token = self.get_token_from_request(request)
        if not token:
            raise HTTPException(status_code=401, detail="Token missing")

        user = self.validate_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        request.state.current_user = user

        await self.app(scope, receive, send)

    def get_token_from_request(self, request: Request):
        auth_header = request.headers.get("Authorization")
        print(auth_header)
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[len("Bearer "):]
        return None

    def validate_token(self, token: str):
        stub = self.get_auth_service_stub()
        try:
            response = stub.ValidateToken(TokenRequest(token=token))
            if response.valid:
                return True, ""
            return False, response.message
        except Exception as e:
            return False, str(e)
        
    def distroy_token(self, token: str):
        stub = self.get_auth_service_stub()
        try:
            response = stub.DestroyToken(TokenRequest(token=token))
            if response.valid:
                return True, ""
            return False, response.message
        except Exception as e:
            return False, str(e)
        
    def get_role(self, token:str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")  
            if role is None:
                raise HTTPException(status_code=403, detail="Role not found in token")
            return role
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    def get_username(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload.get("sub")
            if sub is None:
                raise HTTPException(status_code=403, detail="Sub not found in token")
            
            username, _ = sub.split(':')
            return username
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_uid(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload.get("sub")
            if sub is None:
                raise HTTPException(status_code=403, detail="Sub not found in token")
            
            _, uid = sub.split(':')
            return uid
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_auth_service_stub(self):
        channel = insecure_channel('auth_service:50051')
        return AuthServiceStub(channel)