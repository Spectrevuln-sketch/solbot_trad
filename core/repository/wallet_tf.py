from core.db_connection import CurserFromConnectionFromPool
from core.utils.serializer import serializeDB


class WalletTF():
  __table_name__ = 'wallet_tf'
  _cursor = CurserFromConnectionFromPool()

  @classmethod
  def PrepareTF(cls, walletData):
    query = f"SELECT * FROM {cls.__table_name__} WHERE walletPub = '%s'"
    cls._cursor.execute(query, (walletData['public_key'],))
    res = cls._cursor.fetchone()
    if res is not None:
      return {
        'status': '99',
        'message': 'already prepared transaction'
      }
    else:
      query = f"INSERT INTO {cls.__table_name__} (walletPub, walletPriv) ('%s', '%s')"
      cls._cursor.execute(query, (walletData['public_key'], walletData['private_key']))
      res = cls._cursor.rowcount
      if res == 0:
        return {
          'status': '99',
          'message': 'Filed to insert prepared transaction'
        }
      else:
        return {
          'status': '00',
          'message': 'Succeeded to insert prepared transaction'
        }
