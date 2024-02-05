from core.db_connection import CurserFromConnectionFromPool
from core.utils.serializer import serializeDB


class SnipeTokenDB():
  __table_name__ = 'snipe_token'
  _cursor = CurserFromConnectionFromPool()

  @classmethod
  def CreateSnipe(cls, paylaod):
    query = f"SELECT * FROM {cls.__table_name__} WHERE token_pub = '%s' AND tele_id = '%s' AND payer_wallet = '%s'"
    cls._cursor.execute(query, (str(paylaod["token_target"]), str(paylaod["tele_id"]), str(paylaod["payer_wallet"])))
    snipe = cls._cursor.fetchone()
    if snipe is not None:
      query = f"INSERT INTO {cls.__table_name__} (payer_wallet, amount_buy, token_pub, tele_id) VALUES ('%s', '%s', '%s', '%s')"
      cls._cursor.execute(query, (str(paylaod["payer_wallet"]), str(paylaod["amount_buy"]), str(paylaod["token_target"]), str(paylaod["tele_id"])))
    else:
      return {
        "status": 400,
        "message": "Target Token Already Exists"
      }
  @classmethod
  def GetCurrentSnipe(cls, payload):
    query = f"SELECT * FROM {cls.__table_name__} WHERE token_pub = '%s' AND tele_id = '%s' AND payer_wallet = '%s'"
    cls._cursor.execute(query, (str(payload["token_target"]), str(payload["tele_id"]), str(payload["payer_wallet"])))
    snipe = cls._cursor.fatchone()
    if snipe is None:
      return {
        "status": 404,
        "message": "Target Token Not Found"
      }
    else:
      data = serializeDB(snipe, cls._cursor)
      return {
        "status": 200,
        "data": data
      }

  @classmethod
  def GetAllSnipeByTeleId(cls, tele_id):
    query = f"SELECT * FROM {cls.__table_name__} WHERE tele_id = '%s'"
    cls._cursor.execute(query, (str(tele_id)))
    snipe = cls._cursor.fetchall()
    if snipe is None:
      return {
        "status": 404,
        "message": "Target Token Not Found"
      }
    else:
      data = serializeDB(snipe, cls._cursor)
      return {
        "status": 200,
        "data": data
      }
  @classmethod
  def DeleteSnipe(cls, tele_id, token_target):
      findQuery = f"SELECT * FROM {cls._cursor} WHERE tele_id = {tele_id} AND token_target = {token_target}"
      cls._cursor.execute(findQuery)
      snipe = cls._cursor.fetchOne()
      if snipe is None:
          return {
          "status": 404,
          "message": "Target Token Not Found"
        }
      else:
        query = f"DELETE FROM {cls._cursor} WHERE tele_id = {tele_id} AND token_target = {token_target}"
        cls._cursor.execute(query)
