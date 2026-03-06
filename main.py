import requests
import json
import os
from datetime import datetime
import pytz

# ==========================================
# ⚙️ CONFIGURACIÓN DE NOTION
# ==========================================
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Configuración de Hora (Colombia)
zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m/%Y %I:%M %p")

# ==========================================
# 📂 MAPEO DE BASES DE DATOS (IDs)
# ==========================================
# Se leen de los Secrets que configuraste en GitHub
dbs_config = {
    "ingresos": os.environ.get('DB_INGRESOS'),
    "egresos": os.environ.get('DB_EGRESOS'),
    "tareas": os.environ.get('DB_TAREAS'),
    "habitos": os.environ.get('DB_HABITOS'),
    "pomodoro": os.environ.get('DB_POMODORO'),
    "memento": os.environ.get('DB_MEMENTO'),
    "suscripciones": os.environ.get('DB_SUBS'),
    "sueno": os.environ.get('DB_SUENO'),           # Noches (Bd)
    "sueno_detalles": os.environ.get('DB_SUENO_DETALLES'), # Sueño (Bd)
    "resumenes": os.environ.get('DB_SUENO_RESUMEN'),       # Resúmenes (Bd)
    "compras": os.environ.get('DB_COMPRAS')
}

datos_finales = {
    "metadata": {
        "ultima_actualizacion": hora_actual,
        "estado": "Sincronizado"
    }
}

# ==========================================
# 🚜 FUNCIÓN EXTRACTORA
# ==========================================
def obtener_datos(db_id, nombre):
    if not db_id:
        print(f"⚠️ Saltando '{nombre}': No se encontró el ID en Secrets.")
        return []
    
    print(f"📦 Extrayendo: {nombre}...")
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    
    try:
        response = requests.post(url, headers=headers, timeout=20)
        if response.status_code == 200:
            registros = response.json().get("results", [])
            print(f"✅ {nombre}: {len(registros)} registros extraídos.")
            return registros
        else:
            print(f"❌ Error en {nombre} (Status {response.status_code}): {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error crítico extrayendo {nombre}: {e}")
        return []

# ==========================================
# 🚀 EJECUCIÓN
# ==========================================
print(f"--- INICIO DE EXTRACCIÓN: {hora_actual} ---")

for nombre_clave, id_notion in dbs_config.items():
    datos_finales[nombre_clave] = obtener_datos(id_notion, nombre_clave)

# Guardar el archivo central datos.json
try:
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(datos_finales, f, ensure_ascii=False, indent=4)
    print("\n🚀 ¡ÉXITO! El archivo 'datos.json' ha sido actualizado y guardado.")
except Exception as e:
    print(f"\n❌ ERROR FATAL al guardar el JSON: {e}")
