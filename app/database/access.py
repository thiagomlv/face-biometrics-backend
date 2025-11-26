from app.database.connection import get_connection

class DBAccess:
    """Data base access layer"""

    # =========================================
    #     Simple access methods
    # =========================================
        
    @staticmethod
    def execute(query: str, params: tuple = ()):
        try:
            # Connect to DB
            conn = get_connection()
            cur = conn.cursor()

            # Execute query
            cur.execute(query, params)
            conn.commit()

            # Close connection
            cur.close()
            conn.close()

        except Exception as e:
            raise RuntimeError(f"Database error: {e}")


    @staticmethod
    def fetch(query: str, params: tuple = (), commit: bool = False):
        try:
            # Connect to DB
            conn = get_connection()
            cur = conn.cursor()

            # Execute query
            cur.execute(query, params)

            # Save results
            result = cur.fetchall()

            # Commit if needed
            if commit:
                conn.commit()

            # Close connection
            cur.close()
            conn.close()
            
            return result
        
        except Exception as e:
            raise RuntimeError(f"Database error: {e}")
    
        
        
    
    @staticmethod
    def fetch_one(query: str, params: tuple = ()):
        try: 
            # Connect to DB
            conn = get_connection()
            cur = conn.cursor()

            # Execute query
            cur.execute(query, params)
            
            # Save result
            result = cur.fetchone()

            # Close connection
            cur.close()
            conn.close()

            return result

        except Exception as e:
            raise RuntimeError(f"Database error: {e}")
        

        
