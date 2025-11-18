# database.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações lidas do .env
APP_DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME_APP")
}

SIM_DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME_SIM")
}

def connect_app_db():
    """Conecta ao banco de dados principal do aplicativo."""
    try:
        conn = mysql.connector.connect(**APP_DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Erro ao conectar ao APP DB: {e}")
    return None

def connect_sim_db():
    """Conecta ao banco de dados de simulação (SIM)."""
    try:
        conn = mysql.connector.connect(**SIM_DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Erro ao conectar ao SIM DB: {e}")
    return None