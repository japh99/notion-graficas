import requests
import json
import os
from datetime import datetime
import pytz

NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

zona_horaria = pytz.timezone('America/Bogota')
hora_actual = datetime.now(zona_horaria).strftime("%d/%m/%Y %I:%M %p")

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

def extraer_datos_notion(db_id, nombre_db):
    if not db_id or len(db_id) < 10:
        print(f"⚠️  Saltando '{nombre_db}': ID no configurado")
        return []
    
    print(f"\n{'='*50}")
    print(f"📦 EXTRAYENDO: {nombre_db}")
    print(f"{'='*50}")
    
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    resultados = []
    next_cursor = None
    
    while True:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            resultados.extend(results)
            
            # 🔍 ANÁLISIS DE PRIMER REGISTRO (solo la primera vez)
            if results and len(resultados) <= len(results):
                print(f"✅ Conectado. Total registros: {data.get('total', len(results))}")
                print(f"\n🔍 ESTRUCTURA DE PROPIEDADES:")
                props = results[0].get('properties', {})
                for prop_name, prop_val in props.items():
                    tipo = prop_val.get('type', 'unknown')
                    print(f"   • {prop_name:<20} ({tipo})")
            
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print(f"📊 Registros extraídos: {len(resultados)}")
    return resultados

# Ejecución
print(f"\n🚀 INICIANDO EXTRACCIÓN JAPH 2026 - {hora_actual}\n")

datos_finales = {
    "metadata": {
        "ultima_actualizacion": hora_actual,
        "estado": "OK"
    },
    "datos": {}
}

for nombre, id_notion in dbs_config.items():
    datos_finales["datos"][nombre] = extraer_datos_notion(id_notion, nombre)

# Guardar
with open("datos.json", "w", encoding="utf-8") as f:
    json.dump(datos_finales, f, ensure_ascii=False, indent=2)

print(f"\n{'='*50}")
print(f"✅ COMPLETADO: {sum(len(v) for v in datos_finales['datos'].values())} registros totales")
print(f"{'='*50}")
