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
        if estado in["Done", "Hecho", "Completado"]:
            completadas += 1
        else:
            pendientes += 1
    except Exception as e:
        pass 

# 3. Crear la gráfica y pedir un enlace corto y limpio
chart_config = {
  "type": "doughnut",
  "data": {
    "labels":["Completadas", "Pendientes"],
    "datasets": [{
        "data":[completadas, pendientes],
        "backgroundColor":["#2e7d32", "#d32f2f"]
    }]
  }
}

# Aquí le pedimos el enlace corto a QuickChart
qc_response = requests.post("https://quickchart.io/chart/create", json={"chart": chart_config})
chart_url = qc_response.json()["url"]
print("Enlace limpio generado:", chart_url)

# 4. Actualizar Notion con el enlace limpio
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
