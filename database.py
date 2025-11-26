import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Agora usamos apenas uma configuração, já que o banco foi unificado.
# Certifique-se de que no seu .env o DB_NAME seja o nome do novo banco unificado.
DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME") # Atualize seu .env para usar uma variável comum ou aponte as antigas para o mesmo nome
}

def get_db_connection():
    """Conecta ao banco de dados unificado do PasseBus."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return None

# Mantemos estes nomes por compatibilidade, mas ambos chamam a mesma função
def connect_app_db():
    return get_db_connection()

def connect_sim_db():
    return get_db_connection()