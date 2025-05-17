from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

# Configuración de la conexión
username = "pedrolp370"
password = "LeaL030502"
cluster_url = "gbdproject.ij90wxc.mongodb.net"
db_name = "gbdproject"

# Escapar caracteres especiales en la contraseña
escaped_password = urllib.parse.quote_plus(password)

# Cadena de conexión
uri = f"mongodb+srv://{username}:{escaped_password}@{cluster_url}/?retryWrites=true&w=majority&appName={db_name}"

# Crear cliente y conectar
client = MongoClient(uri, server_api=ServerApi('1'))

# Probar la conexión
try:
    client.admin.command('ping')
    print("¡Conectado exitosamente a MongoDB Atlas!")
    # Después de tu conexión exitosa
    print("Bases de datos disponibles:")
    print(client.list_database_names())
except Exception as e:
    print(f"Error de conexión: {e}")