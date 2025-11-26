from fastapi import APIRouter, HTTPException
from app.database.access import DBAccess


# ======================================================
#     Router setup
# ======================================================
router = APIRouter(
    prefix="/access-log",
    tags=["Access Log"]
)



# ======================================================
#     GET /access-log/
# ======================================================
@router.get("/")
def get_access_logs():
    """
    Retrieve all access log entries from the database.
    """
    try:
        result = DBAccess.fetch(
            "SELECT person_name, room_name, authorized, access_time FROM access_log;"
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
