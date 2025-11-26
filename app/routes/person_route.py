import os
import uuid
import subprocess
import re
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body

# Database access layer
from app.database.access import DBAccess

# Data model
from app.models.person import Person


# Directory to save uploaded images
IMAGES_DIR = "/images"
os.makedirs(IMAGES_DIR, exist_ok=True)

GET_EMBEDDINGS_PATH = "/Backend/FaceRecognition/bin/get-embedding"


# ======================================================
#     Router setup
# ======================================================
router = APIRouter(
    prefix="/person",  # Route prefix
    tags=["Person"]    # Group for API documentation
)


# ======================================================
#     POST /person/
# ======================================================
@router.post("/", response_model=Person)
async def create_person(
    name: str = Form(...),
    email: str = Form(...),
    room_id: int = Form(...),
    user_id: int = Form(...),
    photo: UploadFile = File(...)
):
    """
    Create a new person in the database.

    - Checks if a person with the same email already exists in the given room.
    - Saves the uploaded photo to the server.
    - Initializes a 128-dimension facial vector with zeros.
    - Returns the new person data.
    """
    try:
        # Check if person already exists in the room
        existing = DBAccess.fetch(
            "SELECT id FROM person WHERE email=%s AND room_id=%s;",
            (email, room_id),
        )
        if existing:
            raise HTTPException(status_code=400, detail="Person already registered in this room")
        
        # Executa o programa e captura o output
        result = subprocess.run(
            [GET_EMBEDDINGS_PATH, "./resources/images/rosto01.png"],
            capture_output=True,
            text=True
        )

        # Generate unique filename for the uploaded photo
        file_ext = os.path.splitext(photo.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(IMAGES_DIR, unique_filename)

        # Save photo to disk
        with open(file_path, "wb") as f:
            f.write(await photo.read())

        # Executa o programa e captura o output
        result = subprocess.run(
            [GET_EMBEDDINGS_PATH, file_path],
            capture_output=True,
            text=True
        )

        # Captura apenas a linha que contém o vetor
        output = result.stdout.strip()

        # Extrai todos os números (positivos e negativos, com decimais)
        numbers = re.findall(r"-?\d+\.\d+", output)

        # Converte cada número de string para float
        embedding = [float(x) for x in numbers]

        # Insert new person into database
        result = DBAccess.fetch(
            """
            INSERT INTO person (name, facial_vector, photo_url, email, room_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (name, embedding, file_path, email, room_id),
            commit=True

        )

        new_id = result[0]['id']

        print(f"Person created! photo_url: {file_path}")

        # Return person data
        return {
            "id": new_id,
            "name": name,
            "facial_vector": embedding,
            "photo_url": file_path,
            "email": email,
            "room_id": room_id
        }

    except Exception as e:
        import traceback
        print("ERROR CREATING PERSON:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
#     GET /person/
# ======================================================
@router.get("/", response_model=list[Person])
def get_people(user_id: int):
    """
    Get all people that belong to rooms of a given user.
    """
    try:
        people = DBAccess.fetch(
            """
            SELECT 
                p.id,
                p.name,
                p.email,
                p.facial_vector,
                p.photo_url,
                p.room_id,
                r.name AS room_name,
                r.location AS room_location
            FROM person p
            JOIN room r ON p.room_id = r.id
            WHERE r.user_id = %s;
            """,
            (user_id,)
        )
        return people

    except Exception as e:
        import traceback
        print("ERROR FETCHING PEOPLE:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
#     DELETE /person/
# ======================================================
@router.delete("/")
async def delete_person(email: str = Body(...), room_id: int = Body(...)):
    """
    Remove a registered biometric (person) from the database and delete its photo.

    - Verifies if the person exists in the given room.
    - Deletes the corresponding photo from disk if present.
    - Removes the person record from the database.
    """
    try:
        # Check if person exists
        person = DBAccess.fetch(
            "SELECT id, photo_url FROM person WHERE email=%s AND room_id=%s;",
            (email, room_id)
        )
        if not person:
            raise HTTPException(status_code=404, detail="Biometria não encontrada")

        person = person[0]

        # Remove photo from disk
        if person["photo_url"] and os.path.exists(person["photo_url"]):
            os.remove(person["photo_url"])

        # Remove from database
        DBAccess.execute("DELETE FROM person WHERE id=%s;", (person["id"],))

        return {"detail": "Biometria removida com sucesso"}

    except Exception as e:
        import traceback
        print("ERRO AO REMOVER PESSOA:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
