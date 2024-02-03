import json
import logging
from core.db_connection import Database, CurserFromConnectionFromPool

def GetAllCurrentWallet(tele_id, serialize=False):
    with CurserFromConnectionFromPool() as cursor:
        query = "SELECT * FROM wallet WHERE tele_id = %s"
        cursor.execute(query, (str(tele_id),))
        wallets = cursor.fetchall()
        if wallets is None:
            return None
        else:
            if serialize is not True:
                return wallets
            else:
                # Extract field names from the cursor description
                field_names = [desc[0] for desc in cursor.description]

                # Convert fetched data into a list of dictionaries
                wallet_list = [dict(zip(field_names, wallet)) for wallet in wallets]

                # Serialize the list to JSON
                json_data = json.dumps(wallet_list, indent=2)
                return json_data

def GetCurrentWallet(tele_id, primary=True):
    with CurserFromConnectionFromPool() as cursor:
        query = "SELECT * FROM wallet WHERE tele_id = %s AND \"default\" = %s"
        cursor.execute(query, (str(tele_id), primary))
        wallet = cursor.fetchone()
        print(f'Wallet data for tele_id {tele_id}')
        print(f'Wallet data for wallet {wallet}')
        if wallet is None:
            return None
        else:
            return wallet

def NewWalletUser(payload):
    with CurserFromConnectionFromPool() as cursor:
        print(f'PAYLOAD DATA {payload}')
        try:
            query = "INSERT INTO wallet (tele_id, public_key, private_key, is_connected, \"default\", balance) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (payload['tele_id'], payload['public_key'], payload['private_key'], payload['is_connected'], payload['default'], payload['balance']))
        except Exception as e:
            logging.error(e)

def GetWalletByPrivate(private_key):
    print(f"private key: {private_key}")
    private_key=str(private_key)
    with CurserFromConnectionFromPool() as cursor:
        query = "SELECT * FROM wallet WHERE private_key = %s"
        cursor.execute(query, (private_key,))
        wallet = cursor.fetchone()
        if wallet:
            return wallet
        else:
            return None

def UpdateConnectionWallet(id):
    with CurserFromConnectionFromPool() as cursor:
        query = "UPDATE wallet SET is_connected = %s WHERE id = %s"
        cursor.execute(query, (True, id))

def UpdateWallet(id, column_values):
    with CurserFromConnectionFromPool() as cursor:
        # Generate SET part of the query dynamically
        set_clause = ", ".join(f"{column} = %s" for column in column_values.keys())

        query = f"""
            UPDATE wallet
            SET {set_clause}
            WHERE id = %s
        """

        # Prepare values for the query
        values = list(column_values.values())
        values.append(id)

        cursor.execute(query, tuple(values))

def CountSnipe(tele_id):
    with CurserFromConnectionFromPool() as cursor:
        query = "SELECT count(*) FROM wallet WHERE tele_id = %s AND is_connected = %s AND is_snipe = %s"
        cursor.execute(query, (tele_id, True, True))
        snipe_wallet = cursor.fetchone()
        if snipe_wallet is None:
            return None
        else:
            return snipe_wallet[0]