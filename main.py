import requests
import json
import os

# SOLO NECESITAMOS LA LLAVE MAESTRA. ¡El robot buscará el resto!
NOTION_TOKEN = os.environ['NOTION_TOKEN']

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

print("==========================================================")
print(" 🕵️ INICIANDO EL SÚPER ESCÁNER DE NOTION... ")
print("==========================================================\n")

# Le pedimos a Notion que nos devuelva TODAS las bases de datos conectadas
url_search = "https://api.notion.com/v1/search"
payload = {
    "filter": {
        "value": "database",
        "property": "object"
    }
}

response = requests.post(url_search, headers=headers, json=payload)

if response.status_code == 200:
    bases_de_datos = response.json().get("results",[])
    
    if not bases_de_datos:
        print("⚠️ No encontré ninguna base de datos.")
        print("Asegúrate de haber ido a Notion > Tres puntitos > Conexiones > y agregar 'Graficas Automáticas' a tus tablas.")
    else:
        print(f"✅ ¡Encontré {len(bases_de_datos)} bases de datos conectadas!\n")
        
        for db in bases_de_datos:
            # Extraer el nombre de la tabla
            try:
                nombre_db = db["title"][0]["plain_text"]
            except:
                nombre_db = "Base de datos sin título"
            
            db_id = db["id"]
            
            print(f"📁 NOMBRE: {nombre_db}")
            print(f"🔑 ID A COPIAR: {db_id}")
            print(f"📋 COLUMNAS QUE TIENE:")
            
            # Mostrar todas las columnas y qué tipo de datos guardan
            for nombre_columna, info in db["properties"].items():
                print(f"   👉 '{nombre_columna}' (Tipo: {info['type']})")
                
            print("-" * 50)
else:
    print(f"❌ Error de conexión: {response.text}")

print("\n🚀 ESCANEO TERMINADO. Pásale este texto completo a la IA.")
