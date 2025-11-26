from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import uuid
import subprocess
import re
import math
from app.database.access import DBAccess



# ======================================================
#     Path settings
# ======================================================
IMAGES_DIR = "/images"
os.makedirs(IMAGES_DIR, exist_ok=True)

GET_EMBEDDINGS_PATH = "/Backend/FaceRecognition/bin/get-embedding"


# ======================================================
#     Router setup
# ======================================================
router = APIRouter(
    prefix="/access-requisition",
    tags=["Access"]
)


# ======================================================
#     Get vector distance 
# ======================================================
def get_vector_distance(vec1: list[float], vec2: list[float]) -> float:
    """Calcula a distância Euclidiana entre dois vetores"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


# ======================================================
#     POST /access-requisition/
# ======================================================
@router.post("/")
async def access_requisition(photo: UploadFile = File(...), room_name: str = Form(...)):
    """
    Recebe uma imagem, calcula o embedding facial e verifica no banco
    se há algum vetor com distância < 0.6.
    Retorna True/False.
    """
    try:
        # Salvar a imagem temporariamente
        file_ext = os.path.splitext(photo.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(IMAGES_DIR, unique_filename)

        with open(file_path, "wb") as f:
            f.write(await photo.read())

        # Executa o programa que gera o embedding
        result = subprocess.run(
            [GET_EMBEDDINGS_PATH, file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Erro ao gerar embedding")

        # Extrai os números do output
        output = result.stdout.strip()
        numbers = re.findall(r"-?\d+\.\d+", output)
        embedding = [float(x) for x in numbers]

        if len(embedding) != 128:
            raise HTTPException(status_code=500, detail="Embedding inválido")

        # Buscar todos os embeddings no banco
        people = DBAccess.fetch("SELECT name, facial_vector FROM person;")
        vector = []
        authorized = "Não autorizado"

        # Verifica se algum vetor está próximo (distância < 0.6)
        for person in people:
            db_vector = person["facial_vector"]
            distance = get_vector_distance(embedding, db_vector)
            if distance < 0.6:
                vector = db_vector
                person_name = person["name"]
                authorized = "Autorizado"
                break

        DBAccess.execute(
            """
            INSERT INTO access_log (person_name, room_name, authorized) VALUES (%s, %s, %s)
            """,
            (person_name, room_name, authorized),
        )

        if len(vector) == 0:
            return False
        else:
            return True

    except Exception as e:
        import traceback
        print("ERROR ACCESS REQUISITION:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Remove a imagem temporária
        if os.path.exists(file_path):
            os.remove(file_path)
