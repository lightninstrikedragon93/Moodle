import datetime
import logging
import time
from typing import Annotated
import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from grpc import insecure_channel
from jwt import PyJWTError
import jwt
import uvicorn
import models, crud, schemas
from auth_pb2_grpc import AuthServiceStub
from sqlalchemy.orm import Session
from auth_pb2 import AuthRequest, AuthResponse, TokenRequest
from auth_pb2_grpc import AuthServiceStub
from database import engine, SessionLocal
from google.protobuf.json_format import MessageToDict

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()

SECRET_KEY = "this-is-the-super-key"
ALGORITHM = "HS256"

time.sleep(3)
grpc_channel = insecure_channel('localhost:50051')
auth_stub = AuthServiceStub(grpc_channel)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)

def get_auth_service_stub():
    channel = insecure_channel('localhost:50051')
    return AuthServiceStub(channel)

@app.post("/token")
async def generate_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthServiceStub = Depends(get_auth_service_stub), db: Session = Depends(get_db)):
    credentials = HTTPException(
        status_code=401,
        detail="Credentiale invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_user = crud.get_user_by_username(db, form_data.username)
        if not db_user:
            raise credentials

        if not bcrypt.checkpw(form_data.password.encode('utf-8'), db_user.password.encode('utf-8')):
            raise credentials

        grpc_auth_request = AuthRequest(username=form_data.username, password=form_data.password)
        auth_response = auth_service.Authenticate(grpc_auth_request)

        if not auth_response.token:
            raise credentials

        validate_request = TokenRequest(token=auth_response.token)
        validate_response = auth_stub.ValidateToken(validate_request)

        validate_response_dict = MessageToDict(validate_response)

        return {"access_token": auth_response.token, "token_type": "bearer", "payload": validate_response_dict}
    except PyJWTError:
        raise credentials
    
@app.post("/api/academia_user", response_model=schemas.UserCreate, status_code=201)
async def create_user(
    user: schemas.UserCreate, 
    role: str, 
    db: Session = Depends(get_db), 
    current_user_role: str = Depends(crud.get_current_user_role)
):
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")

    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    new_user = crud.create_user(db=db, user=user, role=role)

    response = schemas.User(
        uid=new_user.uid,
        username=new_user.username,
        role=role,
        links={
            "self": {"href": f"/api/academia_user/{new_user.uid}", "method": "POST"},
            "parent": {"href": "/api/academia_user/", "method": "GET"},
            "update": {"href": f"/api/academia_user/{new_user.uid}", "method": "PUT"},
            "delete": {"href": f"/api/academia_user/{new_user.uid}", "method": "DELETE"}
        }
    )

    return JSONResponse(content=response.dict(), status_code=201)

@app.get("/api/academia_user", response_model=schemas.User, status_code=200)
async def get_user(
    user_id:int, 
    db: Session = Depends(get_db), 
    user_token: str = Depends(oauth2_scheme), 
    auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    grpc_token_request = TokenRequest(token=user_token)
    token_response = auth_service.ValidateToken(grpc_token_request)
    if not token_response.valid:
        raise HTTPException(status_code=401, detail="Inavild token")
    
    db_user = crud.get_user_by_id(db, user_id=user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    response = schemas.User(
        uid=db_user.uid,
        username=db_user.username,
        role=db_user.role,
        links={
            "self": {"href":"/api/academia_user/"+str(user_id), "method": "GET"},
            "parent": {"href":"/api/academia_user/", "method": "GET"},
            "update": {"href":"/api/academia_user/"+str(user_id), "method": "PUT"},
            "delete": {"href": f"/api/academia_user/{user_id}", "method": "DELETE"}
        }
    )

    return JSONResponse(content=response.dict(), status_code=200)

@app.put("/api/academia_user", response_model=schemas.UserCreate, status_code=200)
def update_user(
    user_id: int,
    role: str,
    user: schemas.UserCreate,
    db: Session = Depends(get_db), 
    current_user_role: str = Depends(crud.get_current_user_role)
    ):

    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")

    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user and existing_user.id != user_id:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    update_user = crud.update_user(db, user_id=user_id, user_update=user, role=role)

    response = schemas.UserCreate(
        **update_user.__dict__,
        links={
            "self": {"href":"/api/academia_user/"+str(user_id), "method": "PUT"},
            "parent": {"href":"/api/academia_user/", "method": "GET"},
            "update": {"href":"/api/academia_user/"+str(user_id), "method": "PUT"},
            "delte": {"href":"/api/academia_user/"+str(user_id), "method": "DELETE"},
        }
    )
    return JSONResponse(content=response.dict(), status_code=200)

@app.delete("/api/academia_user", status_code=204)
def delete_user(
    username: str, 
    db: Session = Depends(get_db), 
    current_user_role: str = Depends(crud.get_current_user_role)
):

    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")

    existing_user = crud.get_user_by_username(db, user_username=username)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    crud.delete_user(db, user_id=existing_user.uid)


@app.post("/api/logout", status_code=200)
def logout_user(
    response: Response,
    current_user: str = Depends(oauth2_scheme),
    auth_service: AuthServiceStub = Depends(get_auth_service_stub)
    ):

    grpc_token_request = TokenRequest(token=current_user)
    token_response = auth_service.ValidateToken(grpc_token_request)
    if not token_response.valid:
        raise HTTPException(status_code=401, detail="Invalid token")
    grpc_token_request = TokenRequest(token=current_user)
    token_response = auth_service.DestroyToken(grpc_token_request)

    response.status_code = 204

@app.put("/api/academia_user/change_password", status_code=200)
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user_token: str = Depends(oauth2_scheme),
    auth_service: AuthServiceStub = Depends(get_auth_service_stub)
):
    try:
        user_id = crud.get_user_id_from_token(current_user_token) 
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or user ID extraction failed")
    
    db_user = crud.get_user_by_id(db, user_id=user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(old_password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    if old_password == new_password:
        raise HTTPException(status_code=400, detail="New password must be different from old password")

    updated_user = crud.update_user_password(db, user_id=user_id, new_password=new_password)

    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update password")

    grpc_token_request = TokenRequest(token=current_user_token)
    token_response = auth_service.DestroyToken(grpc_token_request)
    if not token_response.success:
        raise HTTPException(status_code=500, detail="Failed to destroy token")

    return JSONResponse(
        content={"message": "Password changed successfully and logged out."},
        status_code=200
    )
