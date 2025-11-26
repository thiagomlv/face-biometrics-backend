import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import extensions
from app.config.db_settings import settings


##############################################
#    Registration adapter for VECTOR type
##############################################
def cast_vector(value, cur):
    if value is None:
        return None
    try:
        return [float(x) for x in value.strip("[]").split(",")]
    except Exception:
        return value


##############################################
#    Connection
##############################################
def get_connection():
    """Create and return a new connection to PostgreSQL."""
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

    with conn.cursor() as cur:
        cur.execute("SELECT NULL::vector;")
        vector_oid = cur.description[0][1]

    VECTOR = extensions.new_type((vector_oid,), "VECTOR", cast_vector)
    extensions.register_type(VECTOR, conn)

    return conn
