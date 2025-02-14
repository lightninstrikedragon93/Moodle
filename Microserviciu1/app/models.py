from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base
import enum

class GradDidacticEnum(str, enum.Enum):
    asist = "asistent"
    sef_lucr = "sef_lucrari"
    conf = "conferentiar"
    prof = "profesor"

class TipAsociereEnum(str, enum.Enum):
    titular = "titular"
    asociere = "asociere"
    extern = "extern"

class CicluStudiiEnum(str, enum.Enum):
    licenta = "licenta"
    master = "master"

class TipDisciplinaEnum(str, enum.Enum):
    impusa = "impusa"
    optionala = "optinala"
    liber_aleasa = "liber_aleasa"

class CategorieDisciplinaEnum(str, enum.Enum):
    domeniu = "domeniu"
    specialitate = "specialitate"
    adiacenta = "adiacenta"

class TipExaminareEnum(str, enum.Enum):
    examen = "examen"
    colocviu = "colocviu"

class RolEnum(str, enum.Enum):
    admin = "admin"
    profesor = "profesor"
    student = "student"

class Cadre_Didactice(Base):
    __tablename__ = "Cadre_Didactice"

    id = Column (Integer, primary_key=True, index=True, autoincrement=True)
    nume = Column (String, nullable=False)
    prenume = Column (String, nullable=False)
    email = Column (String, unique=True)
    grad_didactic = Column (Enum(GradDidacticEnum), nullable=True)
    tip_asociere = Column (Enum(TipAsociereEnum), nullable=False)
    afiliere = Column (String, nullable=True)

class Join_DS(Base):
    __tablename__ = 'Join_DS'

    student_id = Column(Integer, ForeignKey('Studenti.id'), primary_key=True)
    discipline_id = Column(String, ForeignKey('Discipline_De_Studiu.cod'), primary_key=True)

class Studenti(Base):
    __tablename__ = "Studenti"

    id = Column (Integer, primary_key=True, index=True, autoincrement=True)
    nume = Column (String, nullable=False)
    prenume = Column (String, nullable=False)
    email = Column (String, unique=True)
    ciclu_studii = Column (Enum(CicluStudiiEnum), nullable=False)
    an_studii = Column (Integer, nullable=False)
    grupa = Column (Integer, nullable=False)

    discipline = relationship(
        'Discipline_De_Studiu', 
        secondary=Join_DS.__tablename__,
        back_populates='studenti'
    )

class Discipline_De_Studiu(Base):
    __tablename__ = "Discipline_De_Studiu"

    cod = Column (String, primary_key=True, index=True)
    id_titular = Column (Integer, ForeignKey("Cadre_Didactice.id"), nullable=False)
    nume_disciplina = Column (String, nullable=False)
    an_studiu = Column (Integer, nullable=False)
    tip_disciplina = Column (Enum(TipDisciplinaEnum), nullable=False)
    categorie_disciplina = Column (Enum(CategorieDisciplinaEnum), nullable=False)
    tip_examinare = Column (Enum(TipExaminareEnum), nullable=False)

    studenti = relationship(
        'Studenti', 
        secondary=Join_DS.__tablename__,
        back_populates='discipline'
    )

class Utilizatori(Base):
    __tablename__ = "Utilizatori"

    id = Column (Integer, primary_key=True, autoincrement=True)
    email = Column (String, unique=True)
    parola = Column (String, nullable=False)
    rol = Column (Enum(RolEnum), nullable=False)





