
import aiomysql


async def get_db_connection():
    try:
        # Establece los parámetros de conexión
        conn = await aiomysql.connect(
            host="mysql.railway.internal",
            port=3306,
            user="root",
            password="eVDyoCODzXXFVditKVWwmjITDfwijYoS",
            db="admtaller",
            autocommit=True
        )
        # Realiza cualquier otra configuración necesaria
        return conn
    except aiomysql.Error as e:
        # Maneja la excepción y muestra un mensaje de error personalizado
        print(f"Error al conectar a la base de datos: {e}")
        return None
