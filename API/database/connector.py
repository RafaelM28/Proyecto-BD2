from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse
from datetime import datetime

class MongoDBConnector:
    """
    Clase para manejar la conexión y operaciones con MongoDB Atlas.
    Proporciona métodos para interactuar con la base de datos.
    """
    
    def __init__(self): #Constructor
        # Configuración directa (solo para desarrollo)
        self.username = "pedrolp370"
        self.password = "LeaL030502"
        self.cluster_url = "gbdproject.ij90wxc.mongodb.net"
        self.db_name = "gbdproject"
        
        # Establecer conexión al inicializar
        self.client = self._connect_to_db()
        self.db = self.client[self.db_name]
    
    def _connect_to_db(self):
        """Método privado para establecer la conexión"""
        escaped_password = urllib.parse.quote_plus(self.password)
        uri = f"mongodb+srv://{self.username}:{escaped_password}@{self.cluster_url}/?retryWrites=true&w=majority&appName={self.db_name}"
        
        try:
            client = MongoClient(uri, server_api=ServerApi('1'))
            client.admin.command('ping')
            print("¡Conectado exitosamente a MongoDB Atlas!")
            return client
        except Exception as e:
            print(f"Error de conexión: {e}")
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