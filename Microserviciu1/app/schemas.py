from typing import Dict, List
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class GradDidacticEnum(str, Enum):
    asist = "asistent"
    sef_lucr = "sef_lucrari"
    conf = "conferentiar"
    prof = "profesor"

class TipAsociereEnum(str, Enum):
    titular = "titular"
    asociere = "asociere"
    extern = "extern"

class CicluStudiiEnum(str, Enum):
    licenta = "licenta"
    master = "master"

class TipDisciplinaEnum(str, Enum):
    impusa = "impusa"
    optionala = "optinala"
    liber_aleasa = "liber_aleasa"

class CategorieDisciplinaEnum(str, Enum):
    domeniu = "domeniu"
    specialitate = "specialitate"
    adiacenta = "adiacenta"

class TipExaminareEnum(str, Enum):
    examen = "examen"
    colocviu = "colocviu"

class RolEnum(str, Enum):
    admin = "admin"
    profesor = "profesor"
    student = "student"

class Cadre_Didactice_Create(BaseModel):
    nume: str
    prenume: str
    email: EmailStr
    grad_didactic: Optional[GradDidacticEnum] = None
    tip_asociere: Optional[TipAsociereEnum] = None
    afiliere: Optional[str] = None

    class Config:
        from_attributes = True

class Cadre_Didactice(BaseModel):
    id: int
    nume: str
    prenume: str
    email: EmailStr
    grad_didactic: Optional[GradDidacticEnum] = None
    tip_asociere: Optional[TipAsociereEnum] = None
    afiliere: Optional[str] = None
    links: dict

    class Config:
        from_attributes = True

class Discipline_De_Studiu_Create(BaseModel):
    cod: str
    id_titular: int
    nume_disciplina: str
    an_studiu: int
    tip_disciplina:  Optional[TipDisciplinaEnum] = None
    categorie_disciplina:  Optional[CategorieDisciplinaEnum] = None
    tip_examinare:  Optional[TipExaminareEnum] = None

    class Config:
        from_attributes = True

class Discipline_De_Studiu(BaseModel):
    cod: str
    id_titular: int
    nume_disciplina: str
    an_studiu: int
    tip_disciplina: Optional[TipDisciplinaEnum] = None
    categorie_disciplina: Optional[CategorieDisciplinaEnum] = None
    tip_examinare: Optional[TipExaminareEnum] = None
    links: dict
    
    class Config:
        from_attributes = True

class Studenti_Create(BaseModel):
    nume: str
    prenume: str
    email: EmailStr
    ciclu_studii: Optional[CicluStudiiEnum] = None
    an_studii: int
    grupa: int

    class Config:
        from_attributes = True

class Studenti(BaseModel):
    id: int
    nume: str
    prenume: str
    email: EmailStr
    ciclu_studii: Optional[CicluStudiiEnum] = None
    an_studii: int
    grupa: int
    links: dict

    class Config:
        from_attributes = True

class Utilizatori_Create(BaseModel):
    id: int
    email: str
    parola: str
    rol: RolEnum

class Utilizatori(BaseModel):
    id: int
    email: str
    parola: str
    rol: RolEnum
    links: dict

    class Config:
        from_attributes = True

class Join_DS(BaseModel):
    student_id: int
    disciplina_id: str
    links: dict

    class Config:
        from_attributes = True

class Join_DS_Create(BaseModel):
    student_id: int
    discipline_id: str

    class Config:
        from_attributes = True

