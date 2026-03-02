import requests
import json
import os
import time

NOTION_TOKEN = os.environ['NOTION_TOKEN']
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Función para crear los paneles interactivos
def crear_html(nombre_archivo, titulo, tipo_grafico, labels, datos, colores, mensaje):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display:flex; flex-direction:column; align-items:center; color: #EBEBEB; background-color: transparent; margin: 0; padding: 10px; }}
            .chart-container {{ width: 100%; max-width: 320px; margin-top: 10px; }}
            .insight-box {{ background-color: #2F2F2F; border-left: 5px solid {colores[0]}; padding: 15px; border-radius: 8px; max-width: 400px; margin-top: 20px; font-size: 14px; line-height: 1.5; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #EBEBEB; }}
            h3 {{ margin-bottom: 0; color: #ffffff; font-weight: 600; text-align: center; }}
            b {{ color: #ffffff; }}
        </style>
    </head>
    <body>
        <h3>{titulo}</h3>
        <div class="chart-container"><canvas id="miGrafica"></canvas></div>
        <div class="insight-box">{mensaje}</div>
        <script>
            Chart.defaults.color = '#A0A0A0';
            new Chart(document.getElementById('miGrafica'), {{
                type: '{tipo_grafico}',
                data: {{ labels: {json.dumps(labels)}, datasets:[{{ data: {json.dumps(datos)}, backgroundColor: {json.dumps(colores)}, borderWidth: 0 }}] }},
                options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});
        </script>
    </body>
    </html>
    """
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        file.write(html)

print("Iniciando creación del Dashboard Central...")

# ==========================================
# 📊 MÓDULO 1: FINANZAS
# ==========================================
DB_INGRESOS = os.environ['DB_INGRESOS']
DB_EGRESOS = os.environ['DB_EGRESOS']

# Egresos
res_egresos = requests.post(f"https://api.notion.com/v1/databases/{DB_EGRESOS}/query", headers=headers).json().get("results",[])
gastos_cat = {}
total_gastado = 0

for row in res_egresos:
    try:
        monto = row["properties"]["Monto"]["number"]
        if monto is None: continue
        etiquetas = row["properties"]["Tipo"]["multi_select"]
        cat = etiquetas[0]["name"] if etiquetas else "Otros"
        total_gastado += monto
        gastos_cat[cat] = gastos_cat.get(cat, 0) + monto
    except: pass

cat_max = max(gastos_cat, key=gastos_cat.get) if gastos_cat else "Ninguna"
msg_egresos = f"💸 <b>Egresos:</b> Total gastado: <b>${total_gastado:,.0f} COP</b>.<br>Mayor fuga: <b>{cat_max}</b>."
crear_html("egresos.html", "Distribución de Gastos", "doughnut", list(gastos_cat.keys()), list(gastos_cat.values()),['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'], msg_egresos)

time.sleep(1) # Pausa de 1 segundo para no saturar Notion

# Ingresos
res_ingresos = requests.post(f"https://api.notion.com/v1/databases/{DB_INGRESOS}/query", headers=headers).json().get("results",[])
total_ingresos = sum([r["properties"]["Monto"]["number"] for r in res_ingresos if r["properties"]["Monto"]["number"] is not None])

balance = total_ingresos - total_gastado
msg_ingresos = f"💰 <b>Ingresos:</b> ${total_ingresos:,.0f} COP.<br>⚖️ <b>Balance:</b> ${balance:,.0f} COP disponibles."
crear_html("ingresos.html", "Flujo de Caja", "bar",["Ingresos", "Egresos"], [total_ingresos, total_gastado],['#2ea043', '#f85149'], msg_ingresos)

print("✅ Módulo Finanzas listo.")
time.sleep(1)

# ==========================================
# 📊 MÓDULO 2: TAREAS
# ==========================================
try:
    DB_TAREAS = os.environ['DB_TAREAS']
    res_tareas = requests.post(f"https://api.notion.com/v1/databases/{DB_TAREAS}/query", headers=headers).json().get("results",[])
    
    hechas = 0
    pendientes = 0
    for row in res_tareas:
        if row["properties"]["Hecho"]["checkbox"]: hechas += 1
        else: pendientes += 1
        
    msg_tareas = f"✅ Has completado <b>{hechas}</b> tareas.<br>🚀 Tienes <b>{pendientes}</b> tareas pendientes. ¡A trabajar!"
    crear_html("tareas.html", "Progreso de Tareas", "doughnut", ["Completadas", "Pendientes"], [hechas, pendientes],['#2ea043', '#f85149'], msg_tareas)
    print("✅ Módulo Tareas listo.")
except Exception as e:
    print("Módulo Tareas saltado (Asegúrate de poner DB_TAREAS en GitHub).")

time.sleep(1)

# ==========================================
# 📊 MÓDULO 3: HÁBITOS (Habit Tracker)
# ==========================================
try:
    DB_HABITOS = os.environ['DB_HABITOS']
    res_habitos = requests.post(f"https://api.notion.com/v1/databases/{DB_HABITOS}/query", headers=headers).json().get("results",[])
    
    habitos_cuenta = {"Meditacion":0, "Leer":0, "Ejercicio":0, "Agua 2LT":0, "Agradecer":0}
    
    for row in res_habitos:
        for hab in habitos_cuenta.keys():
            if row["properties"].get(hab, {}).get("checkbox") == True:
                habitos_cuenta[hab] += 1
                
    mejor_hab = max(habitos_cuenta, key=habitos_cuenta.get)
    peor_hab = min(habitos_cuenta, key=habitos_cuenta.get)
    
    msg_habitos = f"🏆 Tu hábito más fuerte es <b>{mejor_hab}</b>.<br>⚠️ No descuides <b>{peor_hab}</b>, lo has cumplido menos veces."
    crear_html("habitos.html", "Consistencia de Hábitos", "bar", list(habitos_cuenta.keys()), list(habitos_cuenta.values()), ['#36a2eb'], msg_habitos)
    print("✅ Módulo Hábitos listo.")
except Exception as e:
    print("Módulo Hábitos saltado.")

print("🚀 ¡Todas las gráficas generadas y listas para Notion!")
