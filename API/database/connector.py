from pymongo import MongoClient
import socket

client = MongoClient('localhost', 27017)

# Send a ping to confirm a successful connection
try:

    ping_result = client.admin.command('ping')
    database_list = client.list_database_names()
     # Comando ping devuelve {'ok': 1.0} si funciona
    print(f"Respuesta del ping: {ping_result}")
    print(f"Bases de datos disponibles: {database_list[:4]}...")
    print("✅ ¡Conexión exitosa a MongoDB local!")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
finally:
# Siempre cerrar la conexión
    if 'client' in locals():
        client.close()
    print("Conexión cerrada")