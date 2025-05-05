from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
            serverSelectionTimeoutMS=5000
        )
        try:
            self.client.admin.command('ping')
            print("✅ Conexión a MongoDB establecida")
        except ConnectionFailure as e:
            raise RuntimeError("Error al conectar a MongoDB") from e
    
    def get_db(self, db_name):
        return self.client[db_name]