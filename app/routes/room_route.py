from fastapi import APIRouter, HTTPException, Query
from app.database.access import DBAccess
from app.models.room import Room


# ======================================================
#     Router setup
# ======================================================
router = APIRouter(
    prefix="/room",
    tags=["Room"]
)


# ======================================================
#     POST /room/
# ======================================================
@router.post("/", response_model=dict)
def create_room(room: Room):
    """
    Create a new room for a user, ensuring no duplicates
    (same name and location for the same user).
    """
    try:
        # Check if a room with same name/location/user already exists
        existing_room = DBAccess.fetch_one(
            """
            SELECT id FROM room
            WHERE name = %s AND location = %s AND user_id = %s;
            """,
            (room.name, room.location, room.user_id)
        )

        if existing_room:
            raise HTTPException(
                status_code=400,
                detail="Room already exists for this user."
            )

        # Insert the new room and return the created record
        result = DBAccess.fetch(
            """
            INSERT INTO room (name, location, user_id)
            VALUES (%s, %s, %s)
            RETURNING id, name, location, user_id;
            """,
            (room.name, room.location, room.user_id),
            commit=True
        )

        return result[0]

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
#     GET /room/
# ======================================================
@router.get("/", response_model=list[Room])
def get_rooms(user_id: int = Query(...)):
    """
    Get all rooms that belong to a specific user.
    """
    try:
        result = DBAccess.fetch(
            """
            SELECT id, name, location, user_id
            FROM room
            WHERE user_id = %s;
            """,
            (user_id,)
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
