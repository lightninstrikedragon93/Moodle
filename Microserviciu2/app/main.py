from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
import schemas as schemas 
import uvicorn
from auth_middleware import AuthMiddleware

app = FastAPI(
    title="Materiale Didactice",
    description="Microserviciu pentru gestionarea materialelor si probelor asociate unei discipline.",
    version="1.0.0"
)
 
def get_db():
    client = MongoClient("mongodb://mongo:27017/")
    mongo_db = client["lectures"]
    return mongo_db

mongo_db = get_db()
discipline_collection = mongo_db["lectures"]

app.add_middleware(AuthMiddleware)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)

#creare materiale curs
@app.post("/materiale_curs/{cod_disciplina}", status_code=201, response_model=schemas.MaterialeCurs)
async def add_material(
    material: schemas.MaterialeCurs, 
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        disciplina = discipline_collection.find_one({"_id": cod_disciplina})
        if not disciplina:
            pass

        result = discipline_collection.update_one(
            {"_id": cod_disciplina},
            {
                "$push": {
                    "materiale_curs": {
                        "titlu": material.titlu,
                        "continut": material.continut,
                        "capitol": material.capitol,
                        "saptamana": material.saptamana
                    }
                }
            },
            upsert=True
        )
        
        return {
            "cod_disciplina": cod_disciplina,
            "titlu": material.titlu,
            "continut": material.continut,
            "capitol": material.capitol,
            "saptamana": material.saptamana
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")

#afisare materiale curs 
@app.get("/materiale_curs/{cod_disciplina}", response_model=List[schemas.MaterialeCurs])
async def get_all_materiale_curs(
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role == "admin":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        disciplina = discipline_collection.find_one({"_id": cod_disciplina})
        
        if not disciplina:
            raise HTTPException(
                status_code=404,
                detail=f"Disciplina {cod_disciplina} not found"
            )
            
        materiale_curs = disciplina.get("materiale_curs", [])
        
        if not materiale_curs:
            return []
            
        return materiale_curs
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

#update materiale curs
@app.put("/materiale_curs/{cod_disciplina}/{titlu}", status_code=200)
async def update_material(
    cod_disciplina: str, 
    titlu: str, 
    update_data: schemas.MaterialeCurs,
    current_user: str = Depends (oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        result = discipline_collection.update_one(
            {
                "_id": cod_disciplina,
                "materiale_curs.titlu": titlu
            },
            {
                "$set": {
                    "materiale_curs.$.titlu": update_data.titlu,
                    "materiale_curs.$.continut": update_data.continut,
                    "materiale_curs.$.capitol": update_data.capitol,
                    "materiale_curs.$.saptamana": update_data.saptamana
                }
            }
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Material not found")
        
        return {
            "titlu": update_data.titlu,
            "continut": update_data.continut,
            "capitol": update_data.capitol,
            "saptamana": update_data.saptamana
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")

#stergere materiale curs
@app.delete("/materiale_curs/{cod_disciplina}/{titlu}", status_code=200)
async def delete_materiale_curs(
    cod_disciplina: str, 
    titlu: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        result = discipline_collection.update_one(
            {"_id": cod_disciplina},
            {
                "$pull": {
                    "materiale_curs": {"titlu": titlu}
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Not found material with title {titlu} for disciplina {cod_disciplina}"
            )

        return {
            "message": f"Material {titlu} was deleted from disciplina {cod_disciplina}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#creare materiale laborator
@app.post("/materiale_laborator/{cod_disciplina}", status_code=201, response_model=schemas.MaterialeLaborator)
async def add_materiale_laborator(
    material: schemas.MaterialeLaborator, 
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        result = discipline_collection.update_one(
            {"_id": cod_disciplina},
            {
                "$push": {
                    "materiale_laborator": {
                        "titlu": material.titlu,
                        "continut": material.continut,
                        "capitol": material.capitol,
                        "saptamana": material.saptamana
                    }
                }
            },
            upsert=True
        )
        
        return {
            "cod_disciplina": cod_disciplina,
            "titlu": material.titlu,
            "continut": material.continut,
            "capitol": material.capitol,
            "saptamana": material.saptamana
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")

#afisare materiale laborator
@app.get("/materiale_laborator/{cod_disciplina}", response_model=List[schemas.MaterialeLaborator])
async def get_materiale_laborator(
    cod_disciplina: str,
    current_user: str = Depends (oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role == "admin":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        disciplina = discipline_collection.find_one({"_id": cod_disciplina})
        
        if not disciplina:
            raise HTTPException(
                status_code=404,
                detail=f"Disciplina {cod_disciplina} not found"
            )
            
        materiale_laborator = disciplina.get("materiale_laborator", [])
        
        if not materiale_laborator:
            return []
            
        return materiale_laborator
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

#update materiale laborator
@app.put("/materiale_laborator/{cod_disciplina}/{titlu}", status_code=200)
async def update_materiale_laborator(
    cod_disciplina: str, 
    titlu: str, 
    update_data: schemas.MaterialeLaborator,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        result = discipline_collection.update_one(
            {
                "_id": cod_disciplina,
                "materiale_laborator.titlu": titlu
            },
            {
                "$set": {
                    "materiale_laborator.$.titlu": update_data.titlu,
                    "materiale_laborator.$.continut": update_data.continut,
                    "materiale_laborator.$.capitol": update_data.capitol,
                    "materiale_laborator.$.saptamana": update_data.saptamana
                }
            }
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Material laborator not found")
        
        return {
            "titlu": update_data.titlu,
            "continut": update_data.continut,
            "capitol": update_data.capitol,
            "saptamana": update_data.saptamana
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")

#stergere materiale laborator
@app.delete("/materiale_laborator/{cod_disciplina}/{titlu}", status_code=200)
async def delete_materiale_laborator(
    cod_disciplina: str, 
    titlu: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        result = discipline_collection.update_one(
            {"_id": cod_disciplina},
            {
                "$pull": {
                    "materiale_laborator": {"titlu": titlu}
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Not found material laborator with title {titlu} for disciplina {cod_disciplina}"
            )

        return {
            "message": f"Material laborator {titlu} was deleted from disciplina {cod_disciplina}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#add evaluare
@app.post("/evaluare/{cod_disciplina}", status_code=201, response_model=schemas.ProbeEvaluare)
async def add_evaluare(
    evaluare: schemas.ProbeEvaluare, 
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        disciplina = discipline_collection.find_one({"_id": cod_disciplina})
        probe_existente  = disciplina.get("probe_evaluare", [])
        pondere_total = sum(probe["pondere"] for probe in probe_existente)
        if (pondere_total + evaluare.pondere) > 100:
            raise HTTPException(status_code=400, detail="Ponderea cannot be greater than 100%")

        result = discipline_collection.update_one(
            {"_id": cod_disciplina},  
            {
                "$push": {  
                    "probe_evaluare": {
                        "tip": evaluare.tip,
                        "pondere": evaluare.pondere
                    }
                }
            },
            upsert=True  
        )
        return {
            "cod_disciplina": cod_disciplina,
            "tip": evaluare.tip,
            "pondere": evaluare.pondere
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")

# stergere evaluare
@app.delete("/evaluare/{cod_disciplina}/{tip_evaluare}", status_code=200)
async def delete_evaluare(
    cod_disciplina: str, 
    tip_evaluare: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role != "profesor":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        result = discipline_collection.update_one(
            {"_id": cod_disciplina},
            {
                "$pull": {
                    "probe_evaluare": {"tip": tip_evaluare}
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Not found evaluarea {tip_evaluare} for disciplina {cod_disciplina}"
            )

        return {
            "message": f"Evaluare {tip_evaluare} was deleted from disciplina {cod_disciplina}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# afisare evaluari
@app.get("/evaluare/{cod_disciplina}", response_model=List[schemas.ProbeEvaluare])
async def get_evaluari(
    cod_disciplina: str,
    current_user: str = Depends(oauth2_scheme)):
    try:
        auth_service = AuthMiddleware(app)

        is_valid, token_response = auth_service.validate_token(current_user)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = auth_service.get_role(current_user)

        if role == "admin":
            response = auth_service.distroy_token(current_user)
            raise HTTPException(status_code=403, detail="Operation not permitted")
        
        disciplina = discipline_collection.find_one({"_id": cod_disciplina})
        
        if not disciplina:
            raise HTTPException(
                status_code=404,
                detail=f"Disciplina {cod_disciplina} not found"
            )
            
        evaluari = disciplina.get("probe_evaluare", [])
        
        if not evaluari:
            return []
            
        return evaluari
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

