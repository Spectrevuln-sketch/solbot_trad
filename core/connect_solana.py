import os
from threading import Event
import json
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from dotenv import load_dotenv
load_dotenv()

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)

class SolanaCrypt():
    __connect__ = None
    __thred__ = None

    @classmethod
    def initialise(cls, **kwargs):
        cls.__connect__ = Client(os.getenv('SOLANA_URL'),commitment=Commitment(
    "confirmed"), timeout=30, blockhash_cache=True)
        cls.__thred__ = Event()

    @classmethod
    def get_connect(cls):
        if cls.__connect__ is None:
            cls.initialise()
        return cls.__connect__.is_connected()

    @classmethod
    def close_connection(cls):
        if cls.__connect__ is not None:
            print(f'Connection close')


class CruserSolana():
    def __init__(self):
        self.connection = None
        self.client = None

    def __enter__(self):
        self.connection = SolanaCrypt.get_connect()
        self.client = SolanaCrypt.__connect__
        return self.client

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value is not None:
            SolanaCrypt.close_connection()
        else:
            SolanaCrypt.initialise()

class SolThrad():
    def __init__(self):
        self.connection = None
        self.thred = None

    def __enter__(self):
        self.connection = SolanaCrypt.get_connect()
        self.thred = SolanaCrypt.__thred__
        return self.thred

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value is not None:
            SolanaCrypt.close_connection()
        else:
            SolanaCrypt.initialise()






