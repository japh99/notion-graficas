import requests
import json
import os
from datetime import datetime
import pytz

# Configuración de Notion
NOTION_TOKEN = os.environ['NOTION_TOKEN']
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Obtener fecha de actualización
zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m %I:%M %p")

# Lista de tus bases de datos (usamos los nombres de tus secretos)
dbs_a_extraer = {
    "ingresos": os.environ.get('DB_INGRESOS'),
    "egresos": os.environ.get('DB_EGRESOS'),
    "tareas": os.environ.get('DB_TAREAS'),
    "habitos": os.environ.get('DB_HABITOS'),
    "pomodoro": os.environ.get('DB_POMODORO'),
    "memento": os.environ.get('DB_MEMENTO'),
    "suscripciones": os.environ.get('DB_SUBS'),
    "sueno": os.environ.get('DB_SUENO'),
    "compras": os.environ.get('DB_COMPRAS')
}

datos_finales = {
    "metadata": {
        "ultima_actualizacion": hora_actual
    }
}

def obtener_datos(db_id):
    if not db_id: return []
    try:
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        # Traemos los resultados (puedes añadir filtros aquí si quisieras)
        response = requests.post(url, headers=headers)
        return response.json().get("results", [])
    except Exception as e:
        print(f"Error extrayendo {db_id}: {e}")
        return []

# Proceso de extracción
for nombre, db_id in dbs_a_extraer.items():
    print(f"📦 Extrayendo datos de: {nombre}...")
    datos_finales[nombre] = obtener_datos(db_id)

# Guardar todo en el archivo central datos.json
with open("datos.json", "w", encoding="utf-8") as f:
    json.dump(datos_finales, f, ensure_ascii=False, indent=4)

print("🚀 ¡Archivo datos.json generado con éxito!")
