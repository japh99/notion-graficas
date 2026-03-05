import requests
import json
import os
from datetime import datetime
import pytz

# ==========================================
# ⚙️ CONFIGURACIÓN DE SEGURIDAD
# ==========================================
# Extraemos el Token de los Secrets de GitHub
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Configuración de hora para el reporte
zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m/%Y %I:%M %p")

# Diccionario con todos tus IDs de Notion (Vinculados a tus Secrets)
dbs_config = {
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

# Estructura inicial del archivo de datos
datos_finales = {
    "metadata": {
        "ultima_actualizacion": hora_actual,
        "estado": "OK"
    }
}

# ==========================================
# 🚜 FUNCIÓN EXTRACTORA (EL TRACTOR)
# ==========================================
def extraer_datos_notion(db_id, nombre_db):
    if not db_id or len(db_id) < 10:
        print(f"⚠️ Saltando '{nombre_db}': ID no configurado o inválido.")
        return []
    
    print(f"📦 Extrayendo datos de: {nombre_db}...")
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    
    try:
        # Hacemos la petición a la API de Notion
        response = requests.post(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            print(f"✅ {nombre_db}: {len(results)} filas encontradas.")
            return results
        else:
            print(f"❌ Error en {nombre_db}: Status {response.status_code}")
            print(f"Detalle: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error crítico en {nombre_db}: {str(e)}")
        return []

# ==========================================
# 🚀 EJECUCIÓN MAESTRA
# ==========================================
print(f"--- INICIANDO EXTRACCIÓN GLOBAL ({hora_actual}) ---")

for nombre, id_notion in dbs_config.items():
    datos_finales[nombre] = extraer_datos_notion(id_notion, nombre)

# Guardar el resultado en el archivo datos.json
try:
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(datos_finales, f, ensure_ascii=False, indent=4)
    print("\n🚀 ¡PROCESO COMPLETADO! El archivo 'datos.json' ha sido actualizado.")
except Exception as e:
    print(f"\n❌ ERROR al guardar el archivo JSON: {str(e)}")
