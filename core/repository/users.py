from core.db_connection import CurserFromConnectionFromPool

def CreateUser(payload):
    with CurserFromConnectionFromPool() as cursor:
        query = "INSERT INTO users (first_name, last_name, type, tele_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (payload.first_name, payload.last_name, payload.type, payload.id))

def GetCurrentUser(tele_id):
    with CurserFromConnectionFromPool() as cursor:
        query = "SELECT * FROM users WHERE tele_id = %s"
        cursor.execute(query, (str(tele_id),))
        user = cursor.fetchone()
        if user:
            return user
        else:
            return None