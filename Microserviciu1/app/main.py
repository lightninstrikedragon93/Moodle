from logging import Logger
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
import grpc
import httpx
from sqlalchemy.orm import Session
import crud as crud
from auth_middleware import AuthMiddleware
from auth_pb2_grpc import AuthServiceStub
from database import SessionLocal, engine
import models as models
import schemas as schemas
import uvicorn
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from auth_pb2 import TokenRequest

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Moodle",
    description= "API pentru gestionarea entitatilor academice: profesori, studenti si discipline",
    version="1.0.0"

)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()


def generate_links(entity_type: str, method_type: str, entity_id: Optional[int] = None, entity_code: Optional[str] = None, evaluation_type: Optional[str] = None, title: Optional[str] = None) -> dict:
    base_url = "/api/academia"
    
    links = {
        "self": None,
        "parent": None,
        "update": None,
        "delete": None
    }
    
    if entity_type == "cadru_didactic" and entity_id is not None:
        links["self"] = {
            "href": f"{base_url}/professors/{entity_id}",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/professors/",
            "method": "GET"
        }
        links["lectures"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures",
            "method": "GET"
        }
        links["update"] = {
            "href": f"{base_url}/professors/{entity_id}",
            "method": "PUT"
        }
        links["delete"] = {
            "href": f"{base_url}/professors/{entity_id}",
            "method": "DELETE"
        }
        
    elif entity_type == "disciplina" and entity_code is not None:
        links["self"] = {
            "href": f"{base_url}/lectures/{entity_code}",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/lectures/",
            "method": "GET"
        }
        
        links["update"] = {
            "href": f"{base_url}/lectures/{entity_code}",
            "method": "PUT"
        }
        links["delete"] = {
            "href": f"{base_url}/lectures/{entity_code}",
            "method": "DELETE"
        }
        
    elif entity_type == "student" and entity_id is not None:
        links["self"] = {
            "href": f"{base_url}/students/{entity_id}",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/students/",
            "method": "GET"
        }
        links["lectures"] = {
            "href": f"{base_url}/students/{entity_id}/lectures",
            "method": "GET"
        }
        links["lectures"] = {
            "href": f"{base_url}/students/{entity_id}/lectures",
            "method": "POST"
        }
        links["update"] = {
            "href": f"{base_url}/students/{entity_id}",
            "method": "PUT"
        }
        links["delete"] = {
            "href": f"{base_url}/students/{entity_id}",
            "method": "DELETE"
        }

    elif entity_type == "join_ds" and entity_id is not None:
        links["self"] = {
            "href": f"{base_url}/students/{entity_id}/lectures",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/students/{entity_id}",
            "method": "GET"
        }

        links["update"] = {
            "href": f"{base_url}/students/{entity_id}",
            "method": "PUT"
        }
        links["delete"] = {
            "href": f"{base_url}/students/{entity_id}/lectures/{entity_code}",
            "method": "DELETE"
        }
    elif entity_type == "evaluare" and entity_id and entity_code is not None:
        links["self"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/evaluare",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures",
            "method": "GET"
        }
        links["delete"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/evaluare/{evaluation_type}",
            "method": "DELETE"
        }

    elif entity_type == "materiale_laborator" and entity_id and entity_code is not None:
        links["self"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/materiale_laborator",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}",
            "method": "GET"
        }

        links["update"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/materiale_laborator/{title}",
            "method": "PUT"
        }
        links["delete"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/materiale_laborator/{title}",
            "method": "DELETE"
        }
    
    elif entity_type == "materiale_curs" and entity_id and entity_code is not None:
        links["self"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/materiale_curs",
            "method": f"{method_type}"
        }
        links["parent"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}",
            "method": "GET"
        }

        links["update"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/materiale_curs/{title}",
            "method": "PUT"
        }
        links["delete"] = {
            "href": f"{base_url}/professors/{entity_id}/lectures/{entity_code}/materiale_curs/{title}",
            "method": "DELETE"
        }
    
    return links

MATERIALE_SERVICE = "http://materiale:8001"
SECRET_KEY = "this-is-the-super-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)

origins = ["http://localhost:3000"]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)
#cadre didactice
#creare cadru didactic
@app.post("/api/academia/professors/", response_model=schemas.Cadre_Didactice_Create, status_code=201)
def create_cadru_didactic(
    cadru_didactic: schemas.Cadre_Didactice_Create,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_cadru_didactic = crud.get_cadru_didactic_by_email(db, cadru_didactic_email=cadru_didactic.email)
    if existing_cadru_didactic:
        raise HTTPException(status_code=409, detail="Cadru didactic already exists")
    
    if not cadru_didactic.email or not crud.is_valid_email(cadru_didactic.email):
        raise HTTPException(status_code=422, detail="Invalid Email format. Must contain @ and .")
    
    new_cadru_didactic= crud.create_cadru_didactic(db=db, cadru_didactic=cadru_didactic)
    
    links = generate_links("cadru_didactic", "POST", new_cadru_didactic.id)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")

    response = schemas.Cadre_Didactice(
        **new_cadru_didactic.__dict__,
        links=links
    )

    return JSONResponse(content=response.dict(), status_code=201)

# afisare cadru didactic
@app.get("/api/academia/professors/{email}", response_model=schemas.Cadre_Didactice, status_code=200)
def get_cadru_didactic(
    email: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    db_cadru_didactic = crud.get_cadru_didactic_by_email(db, cadru_didactic_email=email)

    if db_cadru_didactic is None:
        raise HTTPException(status_code=404, detail="Cadru didactic not found")
    
    if role == "student" or (role == "profesor" and db_cadru_didactic.email != username):
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    links = generate_links("cadru_didactic", "GET", db_cadru_didactic.id)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")

    response = schemas.Cadre_Didactice(
        **db_cadru_didactic.__dict__,
        links=links
    )

    return JSONResponse(content=response.dict(), status_code=200)

@app.get("/api/academia/professors/", response_model=List[schemas.Cadre_Didactice], status_code=200)
def get_cadre_didactice(
    skip: int = Query(0),
    limit: int = Query(10),
    acad_rank: Optional[str] = Query(None, alias="acad_rank"),
    affiliation: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    if not any([acad_rank, affiliation, name]):
        professors = crud.get_cadre_didactice(db, skip=skip, limit=limit)
    else:
        professors = crud.get_filtered_professors(db, acad_rank=acad_rank, affiliation=affiliation, name=name)

    if not professors:
        raise HTTPException(status_code=404, detail="Cadre Didactice not found")
    
    response = []
    for professor in professors:
        links = generate_links("cadru_didactic", "GET", entity_id=professor.id)
        professor_with_links = schemas.Cadre_Didactice(
            **professor.__dict__,
            links=links
        )
        response.append(professor_with_links.dict())
    
    return JSONResponse(content=response, status_code=200)


#stergere cadru didactic
@app.delete("/api/academia/professors/{id}", status_code=204)
def delete_cadru_didactic(
    id: int,
    current_user: str = Depends(oauth2_scheme),
    db:Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_cadru_didactic = crud.get_cadru_didactic(db, cadru_didactic_id=id)
    if not existing_cadru_didactic:
        raise HTTPException(status_code=404, detail="Cadru didactic not found")
    
    crud.delete_cadru_didactic(db, id)
    return Response(status_code=204)

#update cadru didactic
@app.put("/api/academia/professors/{id}", response_model=schemas.Cadre_Didactice_Create, status_code=200)
def update_cadru_didactic(
    id: int, 
    cadru_didactic_update: schemas.Cadre_Didactice_Create,
    current_user: str = Depends(oauth2_scheme),
    db: Session=Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_cadru_didactic = crud.get_cadru_didactic(db, cadru_didactic_id=id)
    if not existing_cadru_didactic:
        raise HTTPException(status_code=404, detail="Cadru didactic not found")
    
    existing_cadru_didactic_email = crud.get_cadru_didactic_by_email(db, cadru_didactic_update.email)

    if existing_cadru_didactic_email and existing_cadru_didactic_email.id != existing_cadru_didactic.id:
        raise HTTPException(status_code=409, detail="Conflict: Another Cadru Didactic has this email")
    
    if not cadru_didactic_update.email or not crud.is_valid_email(cadru_didactic_update.email):
        raise HTTPException(status_code=422, detail="Invalid Email format. Must contain @ and .")
    
    updated_cadru_didactic = crud.update_cadru_didactic(db, cadru_didactic_id=id, cadru_didactic_update=cadru_didactic_update)

    links = generate_links("cadru_didactic", "PUT", updated_cadru_didactic.id)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")
    
    response = schemas.Cadre_Didactice(
        **updated_cadru_didactic.__dict__,
        links=links
    )
    return JSONResponse(content=response.dict(), status_code=200)

# discipline
# creare disciplina
@app.post("/api/academia/lectures/", response_model=schemas.Discipline_De_Studiu, status_code=201)
def create_disciplina(
    disciplina: schemas.Discipline_De_Studiu_Create,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_disciplina = crud.get_disciplina(db, cod=disciplina.cod)
    if existing_disciplina:
        raise HTTPException(status_code=409, detail="Disciplina already exists")
    
    cadru_didactic = crud.get_cadru_didactic(db, disciplina.id_titular)
    if not cadru_didactic:
        raise HTTPException(status_code=404, detail="Cadru didactic not found")
    
    rank = "titular"
    cadru_didactic_rank = crud.get_cadru_didactic_by_rank(db, disciplina.id_titular, rank)
    if not cadru_didactic_rank:
        raise HTTPException(status_code=422, detail="Cadru didactic must be titular")
    
    if not crud.is_name_valid(disciplina.nume_disciplina):
        raise HTTPException(status_code=422, detail="Invalid Name format. Must contain only characters.")
    
    new_disciplina= crud.create_disciplina(db=db, disciplina=disciplina)

    links = generate_links("disciplina", "POST", entity_code=new_disciplina.cod)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")

    response = schemas.Discipline_De_Studiu(
        **new_disciplina.__dict__,
        links=links
    )

    return JSONResponse(content=response.dict(), status_code=201)

# afisare disciplina
@app.get("/api/academia/lectures/{cod}", response_model=schemas.Discipline_De_Studiu, status_code=200)
def read_disciplina(
    cod: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "profesor" and role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    db_disciplina = crud.get_disciplina(db, cod=cod)
    if db_disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    links = generate_links("disciplina", "GET", entity_code=db_disciplina.cod)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")

    response = schemas.Discipline_De_Studiu(
        **db_disciplina.__dict__,
        links=links
    )

    return JSONResponse(content=response.dict(), status_code=200)

# toate disciplinele cu paginare
@app.get("/api/academia/lectures/", response_model=list[schemas.Discipline_De_Studiu], status_code=200)
def read_discipline(
    skip: int = 0, 
    limit: int = 10,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "profesor" and role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    db_discipline = crud.get_discipline(db, skip=skip, limit=limit)
    if not db_discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    response = []
    for disciplina in db_discipline:
        links = generate_links("disciplina", "GET", entity_code=disciplina.cod)
        disciplina_with_links = schemas.Discipline_De_Studiu(
            **disciplina.__dict__,
            links=links
        )
        response.append(disciplina_with_links.dict())

    return JSONResponse(content=response, status_code=200)

# disciplinele asociate unui profesor
@app.get("/api/academia/professors/{id}/lectures", response_model=List[schemas.Discipline_De_Studiu], status_code=200)
def read_cadru_didactic_by_discipline(
    id: int,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)
    
    cadru_didactic = crud.get_cadru_didactic(db, id)
    if cadru_didactic is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    if role != "profesor" and cadru_didactic.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    discipline_de_studiu = crud.get_disciplina_by_cadru_didactic(db, id)
    if not discipline_de_studiu :
        raise HTTPException(status_code=404, detail="No discipline was found for this cadru didactic")
    
    response = [] 
    for disciplina in discipline_de_studiu:
        links = generate_links("disciplina", "GET", entity_code=disciplina.cod)
        disciplina_with_links = schemas.Discipline_De_Studiu(
            **disciplina.__dict__,
            links=links
        )
        response.append(disciplina_with_links.dict())

    return JSONResponse(content=response, status_code=200)
    
# disciplinele asociate unui student
@app.get("/api/academia/students/{id}/lectures", response_model=List[schemas.Discipline_De_Studiu], status_code=200)
def read_student_By_lectures(
    id: int,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)
    student = crud.get_student(db, id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if role != "student" and student.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    discipline_de_studiu = crud.get_disciplina_by_student(db, id)

    if not discipline_de_studiu:
        raise HTTPException(status_code=404, detail="No discipline was found for this student")
    
    response = [] 
    for disciplina in discipline_de_studiu:
        links = generate_links("disciplina", "GET", entity_code=disciplina.cod)
        disciplina_with_links = schemas.Discipline_De_Studiu(
            **disciplina.__dict__,
            links=links
        )
    response.append(disciplina_with_links.dict())

    return JSONResponse(content=response, status_code=200)

#steregere disciplina
@app.delete("/api/academia/lectures/{cod}", status_code=204)
def delete_disciplina(
    cod: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session=Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    existing_disciplina = crud.get_disciplina(db, cod=cod )
    if not existing_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina de Studiu not found")

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    crud.delete_disciplina(db, cod)
    return Response(status_code=204)

#update disciplina
@app.put("/api/academia/lectures/{cod}", status_code=200)
def update_disciplina(
    cod: str, 
    disciplina_update: schemas.Discipline_De_Studiu_Create,
    current_user: str =Depends(oauth2_scheme),
    db: Session=Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    cadru_didactic = crud.get_cadru_didactic(db, disciplina_update.id_titular)
    if not cadru_didactic:
        raise HTTPException(status_code=404, detail="Cadru didactic not found")
    
    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_disciplina = crud.get_disciplina(db, cod=cod)
    if not existing_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    rank = "titular"
    cadru_didactic_rank = crud.get_cadru_didactic_by_rank(db, disciplina_update.id_titular, rank)
    if not cadru_didactic_rank:
        raise HTTPException(status_code=422, detail="Cadru didactic must be titular")
    
    if not crud.is_name_valid(disciplina_update.nume_disciplina):
        raise HTTPException(status_code=422, detail="Invalid Name format. Must contain only characters.")
    
    update_disciplina = crud.update_disciplina(db, discipline_cod=cod, discipline_update=disciplina_update)
    
    links = generate_links("disciplina", "PUT", entity_code=update_disciplina.cod)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")
    
    response = schemas.Discipline_De_Studiu(
        **update_disciplina.__dict__,
        links=links
    )
    return JSONResponse(content=response.dict(), status_code=200)

# afisare student dupa email
@app.get("/api/academia/students/{email}", response_model=schemas.Studenti, status_code=200)
def read_student(
    email: str, 
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)
    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    db_studenti = crud.get_student_by_email(db, student_email=email)
    if db_studenti is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if role == "profesor" or (role == "student" and db_studenti.email != username):
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")

    links = generate_links("student", "GET", db_studenti.id)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")

    response = schemas.Studenti(
        **db_studenti.__dict__,
        links=links
    )
    return JSONResponse(content=response.dict(), status_code=200)

#creare student
@app.post("/api/academia/students/", response_model=schemas.Studenti, status_code=201)
def create_studenti(
    student: schemas.Studenti_Create,
    current_user: str = Depends (oauth2_scheme), 
    db: Session = Depends(get_db)):
    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_student = crud.get_student_by_email(db, student_email=student.email)
    if existing_student:
        raise HTTPException(status_code=409, detail="Student already exists")
    if not student.email:
        raise HTTPException(status_code=422, detail="Invalid data")
    new_student= crud.create_student(db=db, student=student)
    
    links = generate_links("student", "POST", new_student.id)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")
    
    response = schemas.Studenti(
        **new_student.__dict__,
        links=links
    )

    return JSONResponse(content=response.dict(), status_code=201)

# asociere disciplina la student
@app.post("/api/academia/students/{id}/lectures", response_model=schemas.Join_DS, status_code=201)
def add_disciplina_to_student(
    id: int, 
    cod: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    db_student = crud.get_student(db, id=id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_discipline = crud.get_disciplina(db, cod)
    if db_discipline is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    existing_entry = db.query(models.Join_DS).filter(
        models.Join_DS.student_id == id, 
        models.Join_DS.discipline_id == cod
    ).first()

    if existing_entry:
        raise HTTPException(
            status_code=409, 
            detail="The student is already assigned to this discipline."
        )

    if not db_student.an_studii == db_discipline.an_studiu: 
        raise HTTPException(
            status_code=422,
            detail=f"Student cannot be assigned to disciplina. "
                   f"Student's year of study: {db_student.an_studii}, "
                   f"Discipline's year of study: {db_discipline.an_studiu}"
        )
    
    join_ds_entry = crud.add_disciplina_to_student(db, id_student=id, cod_disciplina=cod)

    links = generate_links("join_ds", "POST", db_student.id)
    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")
    
    response = schemas.Join_DS(
        student_id=join_ds_entry.student_id,
        disciplina_id=join_ds_entry.discipline_id,
        links=links
    )

    return JSONResponse(content=response.dict(), status_code=201)

#sterge disciplina la care este asociat un student
@app.delete("/api/academia/students/{id}/lectures/{cod}", status_code=204)
def delete_disciplina_from_student(
    id: int, 
    cod: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_student = crud.get_student(db, id)
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")
    existing_disciplina = crud.get_disciplina(db, cod)
    if existing_disciplina is None:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    crud.delete_disciplina_from_student(db, id_student=id, cod_disciplina=cod)
    return Response(status_code=204)

#stergere student
@app.delete("/api/academia/students/{id}", status_code=204)
def delete_student(
    id: int,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_student = crud.get_student(db, id=id)
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    crud.delete_student(db, id)
    return Response(status_code=204)

#update student
@app.put("/api/academia/students/{id}", status_code=200)
def update_student(
    id: int, 
    student_update: schemas.Studenti_Create,
    current_user: str = Depends(oauth2_scheme),
    db: Session=Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    existing_student = crud.get_student(db, id=id)
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_student_email = crud.get_student_by_email(db, student_update.email)
    if existing_student_email and existing_student_email.id != existing_student.id:
        raise HTTPException(status_code=409, detail="Conflict: Another Student has this email")
    
    if not student_update.email or not crud.is_valid_email(student_update.email):
        raise HTTPException(status_code=422, detail="Invalid Email format. Must contain @ and .")
    
    update_student = crud.update_student(db,student_id=id, student_update=student_update)

    links = generate_links("student", "PUT", update_student.id)

    if not links:
        raise HTTPException(status_code=500, detail="Links generation failed")
    
    response = schemas.Studenti(
        **update_student.__dict__,
        links=links
    )
    return JSONResponse(content=response.dict(), status_code=200)

#adaugare evaluare la disciplina
@app.post("/api/academia/professors/{id_cadru_didactic}/lectures/{cod_disciplina}/evaluare", status_code=201)
async def add_evaluare(
    id_cadru_didactic: int, 
    cod_disciplina: str, 
    evaluare: dict,
    current_user: str = Depends(oauth2_scheme),
    db: Session=Depends(get_db)):

    print(f"Received data: {evaluare}", flush=True)
    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)
        
    cadru_didactic = crud.get_cadru_didactic(db, id_cadru_didactic)
    if not cadru_didactic:
        raise HTTPException(status_code=404, detail="Cadru didactic not found")
    
    if role != "profesor" and cadru_didactic.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_cadru_didactic:
        raise HTTPException(status_code=409, detail="Cadru didactic is not the titular of this discipline")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.post(
                f"{MATERIALE_SERVICE}/evaluare/{cod_disciplina }",
                headers=headers,
                json={
                    "tip": evaluare.get("tip")  ,
                    "pondere": evaluare.get("pondere"),
                }
            )
            if response.status_code == 201:
                links = generate_links("evaluare", "POST", id_cadru_didactic, cod_disciplina, evaluare.get("tip"))

                response = response.json()

                response['links'] = links

                return JSONResponse(content=response, status_code=201)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error creating evaluare")
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

#stergere evaluare
@app.delete("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/evaluare/{tip_evaluare}", status_code=204)
async def delete_evaluare(
    id_profesor: int, 
    cod_disciplina: str,
    tip_evaluare: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")

    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.delete(
                f"{MATERIALE_SERVICE}/evaluare/{cod_disciplina}/{tip_evaluare}",
                headers=headers
            )
            if response.status_code == 204:
                return Response(status_code=204)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error deleting evaluare"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# afisare evaluari
@app.get("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/evaluare", status_code=200)
async def get_evaluari(
    id_profesor: int, 
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role == "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.get(
                f"{MATERIALE_SERVICE}/evaluare/{cod_disciplina}",
                headers=headers
            )
            response.raise_for_status()
            if response.status_code == 200:
                evaluari = response.json()

                response_with_links = []
                for evaluare in evaluari:
                    links = generate_links(
                        "evaluare",
                        "GET",
                        id_profesor,
                        cod_disciplina,
                        evaluation_type=evaluare.get('tip')
                    )
                    evaluare_with_links = {
                        **evaluare,
                        "links": links
                    }
                    response_with_links.append(evaluare_with_links)

                return JSONResponse(content=response_with_links, status_code=200)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Evaluari not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error retrieving evaluari"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Evaluari not found")
            raise HTTPException(status_code=500, detail="Error retrieving evaluari from external service")

# adaugare material laborator
@app.post("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator", status_code=201)
async def add_materiale_laborator(
    id_profesor: int, 
    cod_disciplina: str, 
    material: dict,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            material_data = {
                "titlu": material.get("titlu")  ,
                "continut": material.get("continut"),
                "capitol": material.get("capitol"),
                "saptamana": material.get("saptamana")
            }
            
            response = await client.post(
                f"{MATERIALE_SERVICE}/materiale_laborator/{cod_disciplina}",
                headers=headers,
                json=material_data
            )
            if response.status_code == 201:
                response = response.json()

                links = generate_links("materiale_laborator", "POST", id_profesor, cod_disciplina, title=material.get("titlu"))

                response['links'] = links

                return JSONResponse(content=response, status_code=201)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error creating material laborator"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# afisare material laborator
@app.get("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator", status_code=200)
async def get_materiale_laborator(
    id_profesor: int, 
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role == "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.get(
                f"{MATERIALE_SERVICE}/materiale_laborator/{cod_disciplina}",
                headers=headers
            )
            if response.status_code == 200:
                materiale = response.json()

                response_with_links = []
                for material in materiale:
                    links = generate_links(
                        "materiale_laborator",
                        "GET",
                        id_profesor,
                        cod_disciplina,
                       title=material.get('titlu')
                    )
                    material_with_links = {
                        **material,
                        "links": links
                    }
                    response_with_links.append(material_with_links)

                return JSONResponse(content=response_with_links, status_code=200)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Material not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error retrieving material laborator"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# Update material laborator
@app.put("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator/{titlu}", status_code=200)
async def update_materiale_laborator(
    id_profesor: int, 
    cod_disciplina: str, 
    titlu: str, 
    material: dict,
    current_user: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            material_data = {
                "titlu": material.get("titlu")  ,
                "continut": material.get("continut"),
                "capitol": material.get("capitol"),
                "saptamana": material.get("saptamana")
            }
            
            response = await client.put(
                f"{MATERIALE_SERVICE}/materiale_laborator/{cod_disciplina}/{titlu}",
                headers=headers,
                json=material_data
            )
            if response.status_code == 200:
                material_response = response.json()

                updated_title = material_response.get("titlu", titlu)
                links = {
                    "self": {
                        "href": f"/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator/{updated_title}",
                        "method": "PUT"
                    },
                    "parent": {
                        "href": f"/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator",
                        "method": "GET"
                    },
                    "delete": {
                        "href": f"/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator/{updated_title}",
                        "method": "DELETE"
                    }
                }
                
                material_response["links"] = links
                return JSONResponse(content=material_response, status_code=200)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error updating material laborator"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# stergere material laborator
@app.delete("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_laborator/{titlu}", status_code=204)
async def delete_materiale_laborator(
    id_profesor: int, 
    cod_disciplina: str, 
    titlu: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.delete(
                f"{MATERIALE_SERVICE}/materiale_laborator/{cod_disciplina}/{titlu}",
                headers=headers
            )
            if response.status_code == 204:
                return  Response(status_code=204)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error deleting material laborator"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# adaugare material curs
@app.post("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_curs", status_code=201)
async def add_materiale_curs(
    id_profesor: int, 
    cod_disciplina: str, 
    material: dict,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            material_data = {
                "titlu": material.get("titlu")  ,
                "continut": material.get("continut"),
                "capitol": material.get("capitol"),
                "saptamana": material.get("saptamana")
            }
            
            response = await client.post(
                f"{MATERIALE_SERVICE}/materiale_curs/{cod_disciplina}",
                headers=headers,
                json=material_data
            )
            if response.status_code == 201:
                response = response.json()

                links = generate_links("materiale_curs", "POST", id_profesor, cod_disciplina, title=material.get("titlu"))

                response['links'] = links

                return JSONResponse(content=response, status_code=201)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error creating material curs"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# afisare material curs
@app.get("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_curs", status_code=200)
async def get_materiale_curs(
    id_profesor: int, 
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)

    if role == "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.get(
                f"{MATERIALE_SERVICE}/materiale_curs/{cod_disciplina}",
                headers=headers
            )
            if response.status_code == 200:
                materiale = response.json()

                response_with_links = []
                for material in materiale:
                    links = generate_links(
                        "materiale_curs",
                        "GET",
                        id_profesor,
                        cod_disciplina,
                        title=material.get('titlu')
                    )
                    material_with_links = {
                        **material,
                        "links": links
                    }
                    response_with_links.append(material_with_links)

                return JSONResponse(content=response_with_links, status_code=200)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Material not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error retrieving material curs"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# Update material curs
@app.put("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_curs/{titlu}", status_code=200)
async def update_materiale_curs(
    id_profesor: int, 
    cod_disciplina: str, 
    titlu: str, 
    material: dict,
    current_user: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            material_data = {
                "titlu": material.get("titlu")  ,
                "continut": material.get("continut"),
                "capitol": material.get("capitol"),
                "saptamana": material.get("saptamana")
            }
            
            response = await client.put(
                f"{MATERIALE_SERVICE}/materiale_curs/{cod_disciplina}/{titlu}",
                headers=headers,
                json=material_data
            )
            if response.status_code == 200:
                material_response = response.json()

                updated_title = material_response.get("titlu", titlu)
                links = {
                    "self": {
                        "href": f"/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_curs/{updated_title}",
                        "method": "PUT"
                    },
                    "parent": {
                        "href": f"/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_lcurs",
                        "method": "GET"
                    },
                    "delete": {
                        "href": f"/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_curs/{updated_title}",
                        "method": "DELETE"
                    }
                }
                
                material_response["links"] = links
                return JSONResponse(content=material_response, status_code=200)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error updating material curs"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

# stergere material curs
@app.delete("/api/academia/professors/{id_profesor}/lectures/{cod_disciplina}/materiale_curs/{titlu}", status_code=204)
async def delete_materiale_curs(
    id_profesor: int, 
    cod_disciplina: str, 
    titlu: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)

    is_valid, token_response = auth_service.validate_token(current_user)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    role = auth_service.get_role(current_user)
    username = auth_service.get_username(current_user)

    if role != "profesor" and profesor.email != username:
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    profesor = crud.get_cadru_didactic(db, id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor not found")
    
    disciplina = crud.get_disciplina(db, cod_disciplina)
    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina not found")
    
    if disciplina.id_titular != id_profesor:
        raise HTTPException(status_code=403, detail="Cadru didactic is not the titular of this discipline")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {current_user}"}
            response = await client.delete(
                f"{MATERIALE_SERVICE}/materiale_curs/{cod_disciplina}/{titlu}",
                headers=headers
            )
            if response.status_code == 200:
                return response.json(), Response(status_code=204)
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error deleting material curs"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/academia/all_students/", response_model=list[schemas.Studenti], status_code=200)
def get_students(
    skip: int, 
    limit: int,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):
        
    auth_service = AuthMiddleware(app)
    is_valid, token_response = auth_service.validate_token(current_user)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")
    role = auth_service.get_role(current_user)
    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    db_students = crud.get_students(db, skip=skip, limit=limit)
    if not db_students:
        raise HTTPException(status_code=404, detail="Students not found")
    
    response = []
    for student in db_students:
        links = generate_links("student", "GET", entity_id=student.id)
        student_with_links = schemas.Studenti(
            **student.__dict__,
            links=links
        )
        response.append(student_with_links.dict())
    return JSONResponse(content=response, status_code=200)

#verificare daca un student este inmatriculat la o anumita disciplina
@app.get("/api/academia/students/{id}/lectures/{cod}/check", status_code=200)
def check_disciplina_association(
    id: int, 
    cod: str,
    current_user: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    auth_service = AuthMiddleware(app)
    is_valid, token_response = auth_service.validate_token(current_user)

    role = auth_service.get_role(current_user)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Token")

    if role != "admin":
        response = auth_service.distroy_token(current_user)
        raise HTTPException(status_code=403, detail="Operation not permitted")
    


    association = crud.check_disciplina_association(db, id=id, cod=cod)
    return {"associated": association is not None} 
    
    


