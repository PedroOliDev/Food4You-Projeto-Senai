import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def conectar():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )