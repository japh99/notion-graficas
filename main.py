import requests
import json
import os
from datetime import datetime
import pytz

# Configuración
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Diccionario Maestro de Bases de Datos
# Agregamos las nuevas para el Sueño
dbs = {
    "ingresos": os.environ.get('DB_INGRESOS'),
    "egresos": os.environ.get('DB_EGRESOS'),
    "tareas": os.environ.get('DB_TAREAS'),
    "habitos": os.environ.get('DB_HABITOS'),
    "pomodoro": os.environ.get('DB_POMODORO'),
    "memento": os.environ.get('DB_MEMENTO'),
    "suscripciones": os.environ.get('DB_SUBS'),
    "sueno": os.environ.get('DB_SUENO'), # Noches (Bd)
    "sueno_detalles": os.environ.get('DB_SUENO_DETALLES'), # Sueño (Bd)
    "resumenes": os.environ.get('DB_SUENO_RESUMEN'), # Resúmenes (Bd)
    "compras": os.environ.get('DB_COMPRAS')
}

datos_finales = {
    "metadata": {
        "actualizacion": datetime.now(pytz.timezone('America/Bogota')).strftime("%d/%m %I:%M %p")
    }
}

def obtener_datos(db_id, nombre):
    if not db_id:
        print(f"⚠️ Saltando {nombre}: No hay ID.")
        return []
    try:
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            res = response.json().get("results", [])
            print(f"✅ {nombre} extraído ({len(res)} registros).")
            return res
        else:
            print(f"❌ Error en {nombre}: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error crítico en {nombre}: {e}")
        return []

# Ejecución
for nombre, db_id in dbs.items():
    datos_finales[nombre] = obtener_datos(db_id, nombre)

# Guardar datos.json
with open("datos.json", "w", encoding="utf-8") as f:
    json.dump(datos_finales, f, ensure_ascii=False, indent=4)

print("🚀 Proceso terminado. datos.json actualizado.")
