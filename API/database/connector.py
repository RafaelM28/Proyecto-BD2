from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse
from datetime import datetime

class MongoDBConnector:
    """
    Clase para manejar la conexión y operaciones con MongoDB local.
    """
    
    def __init__(self, db_name="gbdproject", host="localhost", port=27017):
        # Configuración para conexión local
        self.host = host
        self.port = port
        self.db_name = db_name
        
        # Establecer conexión al inicializar
        self.client = self._connect_to_db()
        self.db = self.client[self.db_name]

    def _connect_to_db(self):
        """Método privado para establecer la conexión local"""
        uri = f"mongodb://{self.host}:{self.port}/"
        
        try:
            client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000  # Timeout más corto para local
            )
            # Verificación simple para conexión local
            client.admin.command('ping')
            print("¡Conectado exitosamente a MongoDB local!")
            return client
        except Exception as e:
            print(f"Error de conexión local: {e}")
            raise
    
    def list_databases(self):
        """Lista todas las bases de datos disponibles"""
        return self.client.list_database_names()
    
    def insert_data(self, collection_name: str, data: dict):
        """
        Inserta un documento en la colección especificada
        :param collection_name: Nombre de la colección
        :param data: Diccionario con los datos a insertar
        :return: ID del documento insertado
        """
        try:
            collection = self.db[collection_name]
            data["created_at"] = datetime.now()  # Agrega timestamp automático
            result = collection.insert_one(data)
            print(f"Datos insertados en {collection_name} con ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"Error al insertar datos: {e}")
            raise
    
    def find_data(self, collection_name: str, query: dict = {}):
        """
        Busca documentos en una colección
        :param collection_name: Nombre de la colección
        :param query: Diccionario con el criterio de búsqueda
        :return: Lista de documentos encontrados
        """
        try:
            collection = self.db[collection_name]
            return list(collection.find(query))
        except Exception as e:
            print(f"Error al buscar datos: {e}")
            raise
    
    def close_connection(self):
        """Cierra la conexión con MongoDB"""
        self.client.close()
        print("Conexión cerrada")