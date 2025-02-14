import datetime
import bcrypt
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from grpc import insecure_channel
import jwt
from sqlalchemy.orm import Session
from auth_pb2_grpc import AuthServiceStub
import models, schemas

SECRET_KEY = "this-is-the-super-key"
ALGORITHM = "HS256"
grpc_channel = insecure_channel('localhost:50051')
auth_stub = AuthServiceStub(grpc_channel)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)
def create_user(db: Session, user: schemas.UserCreate, role: str):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = models.User(
        username=user.username,
        password=hashed_password.decode('utf-8'),
        role=role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, user_username: str):
    return db.query(models.User).filter(models.User.username == user_username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.uid == user_id).first()

def get_current_user_role(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")

        if datetime.datetime.fromtimestamp(payload['exp']) < datetime.datetime.now():
            print("Token is expired.")
            return False

        return payload['role']
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return False
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return False
def update_user(db: Session, user_id: int, user_update: schemas.UserCreate, role: str):
    hashed_password = bcrypt.hashpw(user_update.password.encode('utf-8'), bcrypt.gensalt())
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()

    db_user.username = user_update.username
    db_user.password = hashed_password.decode('utf-8')
    db_user.role = role

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()
    db.delete(db_user)
    db.commit()

def update_user_password(db: Session, user_id: int, new_password: str):
    db_user = db.query(models.User).filter(models.User.uid == user_id).first()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    if db_user:
        db_user.password = hashed_password.decode('utf-8')  
        db.commit()  
        db.refresh(db_user)
        return db_user
    return None

def get_user_id_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        sub = payload.get("sub")  
        if sub:
            user_id = sub.split(":")[1]
            return int(user_id)
        raise HTTPException(status_code=401, detail="Invalid token: sub not found")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
