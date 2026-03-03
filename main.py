import requests
import json
import os
import time
from datetime import datetime
import pytz # Para la hora exacta

NOTION_TOKEN = os.environ['NOTION_TOKEN']
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Obtenemos la fecha y hora actual (ajusta 'America/Bogota' a tu zona horaria si quieres)
zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m %I:%M %p")

# ==========================================
# 🧠 FUNCIÓN GENERADORA DE APP INTERACTIVA
# ==========================================
def crear_app_interactiva(nombre_archivo, titulo, labels, datos, colores, mensaje):
    # Aquí inyectamos los datos de Python dentro del JavaScript
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: transparent; color: #EBEBEB; display: flex; flex-direction: column; align-items: center; margin: 0; padding: 10px; }}
            
            h3 {{ margin: 0 0 10px 0; font-size: 16px; text-align: center; }}
            
            .controls {{ display: flex; gap: 10px; margin-bottom: 10px; }}
            
            button {{
                background: #444; color: white; border: none; padding: 5px 12px;
                border-radius: 15px; cursor: pointer; font-size: 12px; transition: 0.3s;
            }}
            button:hover {{ background: #2ea043; }}
            button.active {{ background: #2ea043; font-weight: bold; }}

            .chart-box {{ width: 100%; max-width: 350px; position: relative; height: 250px; }}
            
            .insight-box {{ 
                background-color: #262626; border-left: 4px solid {colores[0]}; 
                padding: 12px; border-radius: 6px; margin-top: 15px; 
                font-size: 13px; line-height: 1.4; width: 90%; max-width: 350px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            .timestamp {{ font-size: 10px; color: #888; margin-top: 10px; }}
        </style>
    </head>
    <body>

        <h3>{titulo}</h3>

        <!-- BOTONES PARA CAMBIAR EL TIPO DE GRÁFICA -->
        <div class="controls">
            <button onclick="cambiarTipo('doughnut')" id="btn-dona">🍩 Dona</button>
            <button onclick="cambiarTipo('bar')" id="btn-barras">📊 Barras</button>
            <button onclick="cambiarTipo('pie')" id="btn-pastel">🥧 Pastel</button>
        </div>

        <div class="chart-box">
            <canvas id="miGrafica"></canvas>
        </div>

        <div class="insight-box">{mensaje}</div>
        <div class="timestamp">🔄 Última actualización: {hora_actual}</div>

        <script>
            // RECIBIMOS LOS DATOS DE PYTHON
            const labels = {json.dumps(labels)};
            const dataValues = {json.dumps(datos)};
            const backgroundColors = {json.dumps(colores)};

            let myChart; // Variable global para la gráfica

            function renderChart(tipo) {
                const ctx = document.getElementById('miGrafica').getContext('2d');
                
                // Si ya existe una gráfica, la destruimos para crear la nueva
                if (myChart) myChart.destroy();

                // Configuración especial si es Barras (para que no se vea gigante)
                const options = {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ 
                        legend: {{ display: tipo !== 'bar', position: 'bottom', labels: {{ color: '#ccc' }} }} 
                    }},
                    scales: {{
                        y: {{ display: tipo === 'bar', ticks: {{ color: '#ccc' }} }},
                        x: {{ display: tipo === 'bar', ticks: {{ color: '#ccc' }} }}
                    }}
                }};

                myChart = new Chart(ctx, {{
                    type: tipo,
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: 'Valor',
                            data: dataValues,
                            backgroundColor: backgroundColors,
                            borderWidth: 0,
                            borderRadius: 4
                        }}]
                    }},
                    options: options
                }});
            }

            // Función para los botones
            function cambiarTipo(nuevoTipo) {{
                renderChart(nuevoTipo);
                // Actualizar estilo de botones
                document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                if(nuevoTipo === 'doughnut') document.getElementById('btn-dona').classList.add('active');
                if(nuevoTipo === 'bar') document.getElementById('btn-barras').classList.add('active');
                if(nuevoTipo === 'pie') document.getElementById('btn-pastel').classList.add('active');
            }}

            // Iniciar con Dona por defecto
            cambiarTipo('doughnut');
        </script>
    </body>
    </html>
    """
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        file.write(html)


print("🤖 INICIANDO CEREBRO MAESTRO 2.0 (INTERACTIVO)...")

# ==========================================
# 📊 MÓDULO FINANZAS
# ==========================================
DB_EGRESOS = os.environ['DB_EGRESOS']
DB_INGRESOS = os.environ['DB_INGRESOS']

# Egresos
res = requests.post(f"https://api.notion.com/v1/databases/{DB_EGRESOS}/query", headers=headers).json().get("results",[])
cats = {}
total_out = 0
for r in res:
    try:
        m = r["properties"]["Monto"]["number"]
        if m:
            t = r["properties"]["Tipo"]["multi_select"]
            c = t[0]["name"] if t else "Otros"
            cats[c] = cats.get(c, 0) + m
            total_out += m
    except: pass

msg_out = f"💸 Total Gastado: <b>${total_out:,.0f}</b>"
# Generamos la app interactiva para Egresos
crear_app_interactiva("egresos.html", "Mis Gastos", list(cats.keys()), list(cats.values()), 
                      ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'], msg_out)

time.sleep(1)

# Ingresos
res_in = requests.post(f"https://api.notion.com/v1/databases/{DB_INGRESOS}/query", headers=headers).json().get("results",[])
total_in = sum([r["properties"]["Monto"]["number"] for r in res_in if r["properties"]["Monto"]["number"] is not None])
balance = total_in - total_out
msg_in = f"💰 Ingresos: ${total_in:,.0f}<br>⚖️ Balance: <b>${balance:,.0f}</b>"
crear_app_interactiva("ingresos.html", "Flujo de Caja", ["Ingresos", "Egresos"], [total_in, total_out], 
                      ['#2ea043', '#f85149'], msg_in)

# ==========================================
# 📊 MÓDULO TAREAS
# ==========================================
try:
    DB_TAREAS = os.environ['DB_TAREAS']
    res_t = requests.post(f"https://api.notion.com/v1/databases/{DB_TAREAS}/query", headers=headers).json().get("results",[])
    hechas = sum(1 for r in res_t if r["properties"]["Hecho"]["checkbox"])
    pendientes = len(res_t) - hechas
    msg_t = f"🚀 Completadas: {hechas}<br>⚠️ Pendientes: {pendientes}"
    crear_app_interactiva("tareas.html", "Progreso Tareas", ["Hecho", "Pendiente"], [hechas, pendientes], 
                          ['#2ea043', '#555'], msg_t)
except: pass

# ==========================================
# 📊 MÓDULO HÁBITOS
# ==========================================
try:
    DB_HABITOS = os.environ['DB_HABITOS']
    res_h = requests.post(f"https://api.notion.com/v1/databases/{DB_HABITOS}/query", headers=headers).json().get("results",[])
    habs = {"Meditacion":0, "Leer":0, "Ejercicio":0} # Agrega aquí tus hábitos reales
    for r in res_h:
        for k in habs.keys():
            if r["properties"].get(k, {}).get("checkbox"): habs[k] += 1
    
    msg_h = "Mantén la racha 🔥"
    crear_app_interactiva("habitos.html", "Mis Hábitos", list(habs.keys()), list(habs.values()), 
                          ['#36a2eb', '#ffce56', '#4bc0c0'], msg_h)
except: pass

print("✅ ¡Gráficas Interactivas Generadas!")
