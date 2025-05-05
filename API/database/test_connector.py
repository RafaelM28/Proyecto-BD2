from connector import MongoDB


def test_connection():
    print("\n=== Iniciando prueba de conexión ===")
    
    try:
        mongo = MongoDB()
        db = mongo.get_db("bases2")
        print("✅ ¡Conexión exitosa!")
        print("Bases de datos:", db.client.list_database_names())
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()