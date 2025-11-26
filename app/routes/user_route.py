from fastapi import APIRouter, HTTPException, Query

# Database access layer
from app.database.access import DBAccess  

# Data model
from app.models.user import User


# ======================================================
#     Router setup
# ======================================================
router = APIRouter(
    prefix="/user",
    tags=["User"]
)


# ======================================================
#     POST /user/
# ======================================================
@router.post("/", response_model=User)
def create_user(user: User):
    """
    Create a new user in the database.
    """
    try:
        user.password_hash = str(user.password_hash)

        result = DBAccess.fetch(
            """
            INSERT INTO app_user (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, name, email, password_hash;
            """,
            (user.name, user.email, user.password_hash),
            commit=True
        )
        new_user = result[0]
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
#     GET /user/
# ======================================================
@router.get("/", response_model=list[User])
def get_users(id: int = Query(None), email: str = Query(None)):
    """
    Get users filtering by id or email.
    Returns all users if no filter is provided.
    """
    try:
        if id:
            result = DBAccess.fetch(
                "SELECT id, name, email, password_hash FROM app_user WHERE id=%s;",
                (id,)
            )
        elif email:
            result = DBAccess.fetch(
                "SELECT id, name, email, password_hash FROM app_user WHERE email=%s;",
                (email,)
            )
        else:
            result = DBAccess.fetch(
                "SELECT id, name, email, password_hash FROM app_user;"
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
