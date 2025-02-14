from typing import Optional
from pydantic import BaseModel

class ProbeEvaluare(BaseModel):
    tip: str
    pondere: int
    links: Optional[dict] = None

class MaterialeCurs(BaseModel):
    titlu: str
    continut: str
    capitol: Optional[int] = None
    saptamana: Optional[int] = None
    links: Optional[dict] = None

class MaterialeLaborator(BaseModel):
    titlu: str
    continut: str
    capitol: Optional[int] = None
    saptamana: Optional[int] = None
    links: Optional[dict] = None
    