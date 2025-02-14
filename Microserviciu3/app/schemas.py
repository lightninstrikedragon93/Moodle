from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    uid: int
    username: str
    role: str
    links: dict

    class Config:
        from_attributes = True