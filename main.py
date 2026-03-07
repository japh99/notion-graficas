import requests
import json
import os
from datetime import datetime
import pytz

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m/%Y %I:%M %p")

# ==========================================
# 📂 MAPEO DE BASES DE DATOS
# ==========================================
dbs_config = {
    # Finanzas
    "ingresos": os.environ.get('DB_INGRESOS'),
    "egresos": os.environ.get('DB_EGRESOS'),
    "suscripciones": os.environ.get('DB_SUBS'),
    "compras": os.environ.get('DB_COMPRAS'),
    
    # Productividad (Aquí está la magia nueva)
    "tareas": os.environ.get('DB_TAREAS'),
    "pomodoro": os.environ.get('DB_POMODORO'),   # Sesiones (Tiempos)
    "proyectos": os.environ.get('DB_PROYECTOS'), # Categorías (Trabajo/Personal)
    
    # Salud y Vida
    "habitos": os.environ.get('DB_HABITOS'),
    "sueno": os.environ.get('DB_SUENO'),           # Noches
    "sueno_detalles": os.environ.get('DB_SUENO_DETALLES'), # Detalles
    "resumenes": os.environ.get('DB_SUENO_RESUMEN'),       # Resúmenes
    "memento": os.environ.get('DB_MEMENTO')
}

datos_finales = {
    "metadata": {
        "ultima_actualizacion": hora_actual,
        "estado": "Sincronizado"
    }
}

# ==========================================
# 🚜 FUNCIÓN EXTRACTORA (CON PAGINACIÓN)
# ==========================================
def obtener_datos(db_id, nombre):
    if not db_id:
        print(f"⚠️ Saltando '{nombre}': Falta el ID en Secrets.")
        return []
    
    print(f"📦 Extrayendo: {nombre}...")
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    results = []
    has_more = True
    start_cursor = None
    
    try:
        while has_more:
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor
                
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                results.extend(data.get("results", []))
                has_more = data.get("has_more", False)
                start_cursor = data.get("next_cursor")
            else:
                print(f"❌ Error en {nombre}: {response.status_code} - {response.text}")
                has_more = False
        
        print(f"✅ {nombre}: {len(results)} registros totales.")
        return results

    except Exception as e:
        print(f"❌ Error crítico en {nombre}: {e}")
        return []

# ==========================================
# 🚀 EJECUCIÓN
# ==========================================
print(f"--- INICIO DE EXTRACCIÓN: {hora_actual} ---")

for nombre_clave, id_notion in dbs_config.items():
    datos_finales[nombre_clave] = obtener_datos(id_notion, nombre_clave)

# Guardar
try:
    with open("datos.json", "w", encoding="utf-8") as f:
        json.dump(datos_finales, f, ensure_ascii=False, indent=4)
    print("\n🚀 ¡ÉXITO! Base de datos centralizada actualizada.")
except Exception as e:
    print(f"\n❌ Error guardando JSON: {e}")
