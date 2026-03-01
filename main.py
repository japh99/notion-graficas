import requests
import json
import os

NOTION_TOKEN = os.environ['NOTION_TOKEN']
DATABASE_ID = os.environ['DATABASE_ID']
BLOCK_ID = os.environ['BLOCK_ID']

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 1. Leer los datos de la base de datos
url_db = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
response = requests.post(url_db, headers=headers)
datos = response.json().get("results",[])

# Contadores
completadas = 0
pendientes = 0

# 2. Contar tareas. 
# IMPORTANTE: Asume que tienes una columna tipo Estado/Select llamada "Estado"
for row in datos:
    try:
        # Cambia "Estado" si tu columna en Notion se llama diferente
        estado = row["properties"]["Estado"]["status"]["name"]
        if estado == "Done" or estado == "Hecho" or estado == "Completado":
            completadas += 1
        else:
            pendientes += 1
    except:
        pass # Ignora las filas vacías

# 3. Crear la gráfica (Tipo dona)
chart_config = {
  "type": "doughnut",
  "data": {
    "labels":["Completadas", "Pendientes"],
    "datasets": [{
        "data":[completadas, pendientes],
        "backgroundColor":["#2e7d32", "#d32f2f"] # Verde y Rojo
    }]
  }
}

chart_url = f"https://quickchart.io/chart?c={json.dumps(chart_config)}"

# 4. Actualizar Notion
url_block = f"https://api.notion.com/v1/blocks/{BLOCK_ID}"
update_data = {
    "image": {
        "type": "external",
        "external": { "url": chart_url }
    }
}
res = requests.patch(url_block, headers=headers, json=update_data)

if res.status_code == 200:
    print("¡Gráfica actualizada con éxito!")
else:
    print("Error:", res.text)
