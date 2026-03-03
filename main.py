import requests
import json
import os
import time
from datetime import datetime
import pytz

# ==========================================
# ⚙️ CONFIGURACIÓN Y LLAVES
# ==========================================
NOTION_TOKEN = os.environ['NOTION_TOKEN']
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Configuración de Tiempo
zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m %I:%M %p")

# Orden cronológico para gráficas mensuales
MESES_ORDEN = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

print(f"🤖 INICIANDO CEREBRO MAESTRO v3.0 - {hora_actual}")

# ==========================================
# 🧠 GENERADOR DE APPS INTERACTIVAS
# ==========================================
def crear_app(nombre_archivo, titulo, labels, datos, colores, mensaje, tipo_default='doughnut', index_axis='x'):
    js_labels = json.dumps(labels)
    js_data = json.dumps(datos)
    js_colors = json.dumps(colores)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: -apple-system, sans-serif; background-color: transparent; color: #EBEBEB; display: flex; flex-direction: column; align-items: center; margin: 0; padding: 10px; }}
            h3 {{ margin: 0 0 10px 0; font-size: 16px; text-align: center; font-weight: 600; }}
            .controls {{ display: flex; gap: 6px; margin-bottom: 10px; }}
            button {{ background: #444; color: white; border: none; padding: 4px 10px; border-radius: 12px; cursor: pointer; font-size: 11px; transition: 0.3s; }}
            button:hover {{ background: #2ea043; }}
            .chart-box {{ width: 100%; max-width: 350px; height: 220px; position: relative; }}
            .insight-box {{ background-color: #262626; border-left: 4px solid {colores[0]}; padding: 12px; border-radius: 6px; margin-top: 15px; font-size: 13px; line-height: 1.4; width: 90%; max-width: 350px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .timestamp {{ font-size: 10px; color: #888; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h3>{titulo}</h3>
        <div class="controls">
            <button onclick="cambiarTipo('bar')">📊</button>
            <button onclick="cambiarTipo('doughnut')">🍩</button>
            <button onclick="cambiarTipo('line')">📈</button>
        </div>
        <div class="chart-box"><canvas id="miGrafica"></canvas></div>
        <div class="insight-box">{mensaje}</div>
        <div class="timestamp">🔄 Sincronizado: {hora_actual}</div>
        <script>
            let myChart;
            function renderChart(tipo) {{
                const ctx = document.getElementById('miGrafica').getContext('2d');
                if (myChart) myChart.destroy();
                myChart = new Chart(ctx, {{
                    type: tipo,
                    data: {{
                        labels: {js_labels},
                        datasets: [{{
                            label: 'Monto/Cantidad',
                            data: {js_data},
                            backgroundColor: {js_colors},
                            borderColor: {js_colors}[0],
                            borderWidth: tipo === 'line' ? 2 : 0,
                            tension: 0.4,
                            fill: tipo === 'line'
                        }}]
                    }},
                    options: {{
                        indexAxis: '{index_axis}',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: tipo === 'doughnut', position: 'bottom', labels: {{ color: '#ccc' }} }} }},
                        scales: {{
                            y: {{ display: tipo !== 'doughnut', ticks: {{ color: '#ccc' }} }},
                            x: {{ display: tipo !== 'doughnut', ticks: {{ color: '#ccc' }} }}
                        }}
                    }}
                }});
            }}
            function cambiarTipo(t) {{ renderChart(t); }}
            renderChart('{tipo_default}');
        </script>
    </body>
    </html>
    """
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        file.write(html)

# ==========================================
# 📊 MÓDULO: FINANZAS (HISTÓRICO Y CATEGORÍAS)
# ==========================================
try:
    print("📈 Procesando Finanzas...")
    db_egresos = os.environ['DB_EGRESOS']
    db_ingresos = os.environ['DB_INGRESOS']

    # --- EGRESOS ---
    r_eg = requests.post(f"https://api.notion.com/v1/databases/{db_egresos}/query", headers=headers).json().get("results",[])
    eg_mes = {m: 0 for m in MESES_ORDEN}
    eg_cat = {}
    total_eg = 0
    hormiga = 0
    
    for r in r_eg:
        p = r["properties"]
        monto = p["Monto"]["number"] or 0
        mes = p["Mes"]["select"]["name"] if p["Mes"]["select"] else None
        tipo_list = p["Tipo"]["multi_select"]
        cat = tipo_list[0]["name"] if tipo_list else "Otros"
        
        total_eg += monto
        if mes in eg_mes: eg_mes[mes] += monto
        eg_cat[cat] = eg_cat.get(cat, 0) + monto
        if monto <= 15000 and cat not in ["Suscripciones", "Arriendo"]: hormiga += monto

    crear_app("egresos_mes.html", "Gastos Mensuales", list(eg_mes.keys()), list(eg_mes.values()), ['#f85149'], f"Total Año: ${total_eg:,.0f}", 'bar')
    crear_app("egresos.html", "Gastos por Categoría", list(eg_cat.keys()), list(eg_cat.values()), ['#ff6384', '#36a2eb', '#cc65fe'], f"🐜 Gastos Hormiga: ${hormiga:,.0f}", 'doughnut')

    # --- INGRESOS ---
    r_in = requests.post(f"https://api.notion.com/v1/databases/{db_ingresos}/query", headers=headers).json().get("results",[])
    in_mes = {m: 0 for m in MESES_ORDEN}
    total_in = 0
    for r in r_in:
        p = r["properties"]
        monto = p["Monto"]["number"] or 0
        mes = p["Mes"]["select"]["name"] if p["Mes"]["select"] else None
        total_in += monto
        if mes in in_mes: in_mes[mes] += monto

    crear_app("ingresos_mes.html", "Ingresos Mensuales", list(in_mes.keys()), list(in_mes.values()), ['#2ea043'], f"Total Año: ${total_in:,.0f}", 'bar')
    crear_app("ingresos.html", "Balance General", ["Ingresos", "Egresos"], [total_in, total_eg], ['#2ea043', '#f85149'], f"Saldo Actual: ${total_in-total_eg:,.0f}", 'bar')

except Exception as e: print(f"Error Finanzas: {e}")

# ==========================================
# 🛒 MÓDULO: COMPRAS (WISHLIST)
# ==========================================
try:
    print("🛒 Procesando Compras...")
    db_c = os.environ['DB_COMPRAS']
    res = requests.post(f"https://api.notion.com/v1/databases/{db_c}/query", headers=headers).json().get("results",[])
    si, no, count_no = 0, 0, 0
    for r in res:
        p = r["properties"]
        val = p.get("Monto", p.get("Precio", {"number":0}))["number"] or 0
        done = False
        for k, v in p.items():
            if v["type"] == "checkbox" and v["checkbox"]: done = True
        if done: si += val
        else: 
            no += val
            count_no += 1
    crear_app("compras.html", "Presupuesto Wishlist", ["Comprado", "Pendiente"], [si, no], ['#2ea043', '#555555'], f"Faltan ${no:,.0f} para {count_no} items.", 'doughnut')
except Exception as e: print(f"Error Compras: {e}")

# ==========================================
# 💳 MÓDULO: SUSCRIPCIONES
# ==========================================
try:
    print("💳 Procesando Suscripciones...")
    db_s = os.environ['DB_SUBS']
    res = requests.post(f"https://api.notion.com/v1/databases/{db_s}/query", headers=headers).json().get("results",[])
    subs = {}
    for r in res:
        n = r["properties"]["Servicio"]["title"][0]["plain_text"]
        v = r["properties"]["Precio"]["number"] or 0
        subs[n] = v
    crear_app("suscripciones.html", "Suscripciones", list(subs.keys()), list(subs.values()), ['#ff9f40'], f"Gasto Mensual: ${sum(subs.values()):,.0f}", 'bar')
except Exception as e: print(f"Error Subs: {e}")

# ==========================================
# ✅ MÓDULO: TAREAS
# ==========================================
try:
    print("🚀 Procesando Tareas...")
    db_t = os.environ['DB_TAREAS']
    res = requests.post(f"https://api.notion.com/v1/databases/{db_t}/query", headers=headers).json().get("results",[])
    h, p = 0, 0
    for r in res:
        if r["properties"]["Hecho"]["checkbox"]: h += 1
        else: p += 1
    crear_app("tareas.html", "Productividad", ["Hecho", "Pendiente"], [h, p], ['#2ea043', '#f85149'], f"Tareas pendientes: {p}", 'doughnut')
except Exception as e: print(f"Error Tareas: {e}")

# ==========================================
# 🏆 MÓDULO: HÁBITOS
# ==========================================
try:
    print("🏆 Procesando Hábitos...")
    db_h = os.environ['DB_HABITOS']
    res = requests.post(f"https://api.notion.com/v1/databases/{db_h}/query", headers=headers).json().get("results",[])
    habs = {"Meditacion":0, "Leer":0, "Ejercicio":0, "Agua 2LT":0, "Agradecer":0}
    for r in res:
        for k in habs.keys():
            if r["properties"].get(k, {}).get("checkbox"): habs[k] += 1
    crear_app("habitos.html", "Consistencia de Hábitos", list(habs.keys()), list(habs.values()), ['#36a2eb'], "¡Mantén la racha!", 'bar')
except Exception as e: print(f"Error Hábitos: {e}")

# ==========================================
# 💀 MÓDULO: MEMENTO MORI
# ==========================================
try:
    vivido, esperanza = 26, 80 # Ajusta tu edad aquí
    crear_app("memento.html", "Progreso de Vida (Años)", ["Vivido", "Restante"], [vivido, esperanza-vivido], ['#333', '#eee'], f"Te quedan {(esperanza-vivido)*52} semanas.", 'bar', 'y')
except Exception as e: print(f"Error Memento: {e}")

# ==========================================
# 💤 MÓDULO: SUEÑO (ÚLTIMOS 7 DÍAS)
# ==========================================
try:
    print("💤 Procesando Sueño...")
    db_z = os.environ['DB_SUENO']
    payload = { "sorts": [ { "property": "Hora de despertar", "direction": "ascending" } ], "page_size": 7 }
    res = requests.post(f"https://api.notion.com/v1/databases/{db_z}/query", headers=headers, json=payload).json().get("results",[])
    d, v = [], []
    for r in res:
        mins = r["properties"]["Minutos totales de sueño"]["formula"]["number"] or 0
        fecha = r["properties"]["Hora de despertar"]["date"]["start"][5:10]
        d.append(fecha); v.append(round(mins/60, 1))
    crear_app("sueno.html", "Horas de Sueño", d, v, ['#36a2eb'], f"Promedio: {sum(v)/len(v) if v else 0:.1f}h", 'line')
except Exception as e: print(f"Error Sueño: {e}")

# ==========================================
# 🍅 MÓDULO: POMODORO
# ==========================================
try:
    print("🍅 Procesando Pomodoro...")
    db_p = os.environ['DB_POMODORO']
    res = requests.post(f"https://api.notion.com/v1/databases/{db_p}/query", headers=headers).json().get("results",[])
    poms = {}
    for r in res:
        t = r["properties"]["Tipo"]["select"]["name"]
        m = r["properties"]["Tiempo"]["number"] or 0
        poms[t] = poms.get(t, 0) + m
    crear_app("pomodoro.html", "Distribución Pomodoro", list(poms.keys()), list(poms.values()), ['#ff6384', '#36a2eb'], f"Total: {sum(poms.values())//60}h", 'doughnut')
except Exception as e: print(f"Error Pomodoro: {e}")

print("✅ Dashboard Centralizado Generado con Éxito.")
