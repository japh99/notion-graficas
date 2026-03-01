import requests
import json
import os
import urllib.parse

NOTION_TOKEN = os.environ['NOTION_TOKEN']
DATABASE_ID = os.environ['DATABASE_ID']
BLOCK_ID = os.environ['BLOCK_ID']

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 1. Leer datos de Notion
url_db = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
response = requests.post(url_db, headers=headers)
datos = response.json().get("results",[])

# 2. Contar tareas
completadas = 0
pendientes = 0

for row in datos:
    try:
        estado = row["properties"]["Estado"]["status"]["name"]
        if estado in ["Done", "Hecho", "Completado"]:
            completadas += 1
        else:
            pendientes += 1
    except Exception:
        pass 

# 3. Crear la gráfica
chart_config = {
  "type": "doughnut",
  "data": {
    "labels":["Completadas", "Pendientes"],
    "datasets":[{
        "data":[completadas, pendientes],
        "backgroundColor":["#2e7d32", "#d32f2f"]
    }]
  }
}

# Convertimos la gráfica a texto seguro
config_codificada = urllib.parse.quote(json.dumps(chart_config))

# ¡EL TRUCO PARA NOTION! 
# Usamos "chart.png" y agregamos "&ext=.png" al final para que Notion vea la extensión y lo acepte.
chart_url = f"https://quickchart.io/chart.png?c={config_codificada}&ext=.png"

# 4. Actualizar Notion
url_block = f"https://api.notion.com/v1/blocks/{BLOCK_ID}"
update_data = {
    "image": {
        "external": { "url": chart_url }
    }
}
res = requests.patch(url_block, headers=headers, json=update_data)

if res.status_code == 200:
    print("¡Gráfica actualizada con éxito en Notion!")
else:
    print("ERROR DE NOTION:", res.text)
    raise Exception("El script falló al intentar actualizar la imagen en Notion.")
