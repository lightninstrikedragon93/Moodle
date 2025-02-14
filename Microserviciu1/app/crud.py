import re
from typing import Optional
from sqlalchemy.orm import Session
import models as models, schemas as schemas
from auth_pb2 import TokenRequest

#cadru didactic
def create_cadru_didactic(db: Session, cadru_didactic: schemas.Cadre_Didactice_Create):
    db_cadru_didactic = models.Cadre_Didactice(
        nume=cadru_didactic.nume,
        prenume=cadru_didactic.prenume,
        email=cadru_didactic.email,
        grad_didactic=cadru_didactic.grad_didactic,
        tip_asociere=cadru_didactic.tip_asociere,
        afiliere=cadru_didactic.afiliere,
    )
    db.add(db_cadru_didactic)
    db.commit()
    db.refresh(db_cadru_didactic)
    return db_cadru_didactic

def get_cadru_didactic(db: Session, cadru_didactic_id: int):
    return db.query(models.Cadre_Didactice).filter(models.Cadre_Didactice.id == cadru_didactic_id).first()

def get_cadre_didactice(db: Session, skip: int, limit: int):
    return db.query(models.Cadre_Didactice).offset(skip).limit(limit).all()

def get_cadru_didactic_by_email(db: Session, cadru_didactic_email: str):
    return db.query(models.Cadre_Didactice).filter(models.Cadre_Didactice.email == cadru_didactic_email).first()

def get_cadru_didactic_by_rank(db: Session, id_cadru_didactic: int, rank_cadru_didactic: str):
    cadru_didactic = get_cadru_didactic(db, id_cadru_didactic)
    if cadru_didactic:
        return cadru_didactic.tip_asociere == rank_cadru_didactic
    return False

def delete_cadru_didactic(db: Session, cadru_didactic_id: int):
    db_cadru_didactic = db.query(models.Cadre_Didactice).filter(models.Cadre_Didactice.id==cadru_didactic_id).first()

    db.delete(db_cadru_didactic)
    db.commit()

    return {"message": "Professor deleted successfully"}

def update_cadru_didactic(db: Session, cadru_didactic_id: int, cadru_didactic_update: schemas.Cadre_Didactice_Create):
    db_cadru_didactic = db.query(models.Cadre_Didactice).filter(models.Cadre_Didactice.id == cadru_didactic_id).first()

    db_cadru_didactic.nume = cadru_didactic_update.nume
    db_cadru_didactic.prenume = cadru_didactic_update.prenume
    db_cadru_didactic.email = cadru_didactic_update.email
    db_cadru_didactic.grad_didactic = cadru_didactic_update.grad_didactic 
    db_cadru_didactic.tip_asociere = cadru_didactic_update.tip_asociere
    db_cadru_didactic.afiliere = cadru_didactic_update.afiliere

    db.commit()
    db.refresh(db_cadru_didactic)
    return db_cadru_didactic
    
#discipline
def create_disciplina(db: Session, disciplina: schemas.Discipline_De_Studiu_Create):
    db_disciplina = models.Discipline_De_Studiu(
        cod=disciplina.cod,
        id_titular=disciplina.id_titular,
        nume_disciplina=disciplina.nume_disciplina,
        an_studiu=disciplina.an_studiu,
        tip_disciplina=disciplina.tip_disciplina,
        categorie_disciplina=disciplina.categorie_disciplina,
        tip_examinare=disciplina.tip_examinare,
    )
    db.add(db_disciplina)
    db.commit()
    db.refresh(db_disciplina)
    return db_disciplina

def get_disciplina(db: Session, cod: str):
    return db.query(models.Discipline_De_Studiu).filter(models.Discipline_De_Studiu.cod == cod).first()

def get_discipline(db: Session, skip: int, limit: int):
    return db.query(models.Discipline_De_Studiu).offset(skip).limit(limit).all()

def update_disciplina(db: Session, discipline_cod: str, discipline_update: schemas.Discipline_De_Studiu_Create):
    db_discipline = db.query(models.Discipline_De_Studiu).filter(models.Discipline_De_Studiu.cod == discipline_cod).first()

    db_discipline.cod = discipline_update.cod
    db_discipline.id_titular = discipline_update.id_titular
    db_discipline.nume_disciplina = discipline_update.nume_disciplina
    db_discipline.an_studiu = discipline_update.an_studiu
    db_discipline.tip_disciplina = discipline_update.tip_disciplina
    db_discipline.categorie_disciplina = discipline_update.categorie_disciplina
    db_discipline.tip_examinare = discipline_update.tip_examinare

    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def delete_disciplina(db: Session, discipline_cod: str):
    db_discipline = db.query(models.Discipline_De_Studiu).filter(models.Discipline_De_Studiu.cod == discipline_cod).first()

    db.delete(db_discipline)
    db.commit()

    return {"message": "Discipline deleted successfully"}

def get_disciplina_by_cadru_didactic(db: Session, id_profesor: int):
    professor = get_cadru_didactic(db, id_profesor)
    if not professor:
        return None
    discipline = (db.query(models.Discipline_De_Studiu)
        .filter(models.Discipline_De_Studiu.id_titular == id_profesor)
        .all()
    )

    return discipline

def get_disciplina_by_student(db: Session, id_student: int):
    student = get_student(db, id_student)
    if not student:
        return None
    discipline = (
        db.query(models.Discipline_De_Studiu)
        .join(models.Join_DS, models.Discipline_De_Studiu.cod == models.Join_DS.discipline_id)
        .filter(models.Join_DS.student_id == id_student)
        .all()
    )
    return discipline

# studenti
def get_student(db:Session, id: int):
    return db.query(models.Studenti).filter(models.Studenti.id == id).first()

def get_student_by_email(db: Session, student_email: str):
    return db.query(models.Studenti).filter(models.Studenti.email == student_email).first()

def create_student(db: Session, student: schemas.Studenti_Create):
    db_studenti = models.Studenti(
        nume = student.nume,
        prenume = student.prenume,
        email = student.email,
        ciclu_studii = student.ciclu_studii,
        an_studii = student.an_studii,
        grupa = student.grupa,
    )

    db.add(db_studenti)
    db.commit()
    db.refresh(db_studenti)
    return db_studenti

def update_student(db: Session, student_id: int, student_update: schemas.Studenti_Create):
    db_student = db.query(models.Studenti).filter(models.Studenti.id == student_id).first()

    db_student.nume = student_update.nume
    db_student.prenume = student_update.prenume
    db_student.email = student_update.email
    db_student.ciclu_studii = student_update.ciclu_studii
    db_student.an_studii = student_update.an_studii
    db_student.grupa = student_update.grupa

    db.commit()
    db.refresh(db_student)
    
    return db_student
def delete_student(db: Session, student_id: int):
    db_student = db.query(models.Studenti).filter(models.Studenti.id == student_id).first()

    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}

def get_students(db: Session, skip: int, limit: int):
    return db.query(models.Studenti).offset(skip).limit(limit).all()

def get_filtered_professors(db: Session, acad_rank: Optional[str], affiliation: Optional[str], name: Optional[str]):
    query = db.query(models.Cadre_Didactice)
    if acad_rank:
        query = query.filter(models.Cadre_Didactice.grad_didactic == acad_rank)
    if affiliation:
        query = query.filter(models.Cadre_Didactice.afiliere.ilike(f"%{affiliation}%"))
    if name:
        query = query.filter((models.Cadre_Didactice.nume.ilike(f"%{name}%")) |
                             (models.Cadre_Didactice.prenume.ilike(f"%{name}%")))

    return query.all()

def add_disciplina_to_student(db: Session, id_student: int, cod_disciplina: str):
    db_join_ds = models.Join_DS(
        student_id = id_student,
        discipline_id = cod_disciplina
    )

    db.add(db_join_ds)
    db.commit()
    db.refresh(db_join_ds)
    return db_join_ds

def delete_disciplina_from_student(db: Session, id_student: int, cod_disciplina: str):
    db_join_ds = db.query(models.Join_DS).filter(
        models.Join_DS.student_id == id_student,
        models.Join_DS.discipline_id == cod_disciplina
    ).first()

    db.delete(db_join_ds)
    db.commit()
    return {"message": "Disciplina deleted successfully from student"}

def get_studenti_and_discipline(db: Session):
    return db.query(models.Join_DS).all()

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email

def is_name_valid(name: str) -> bool:
    return bool(re.match("^[A-Za-z ]", name))

def check_disciplina_association(db: Session, id: int, cod: str):
    return db.query(models.Join_DS).filter(
        models.Join_DS.student_id == id,
        models.Join_DS.discipline_id == cod
    ).first()