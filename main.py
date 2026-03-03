import requests
import json
import os
import time
from datetime import datetime
import pytz

# ==========================================
# ⚙️ CONFIGURACIÓN INICIAL
# ==========================================
NOTION_TOKEN = os.environ['NOTION_TOKEN']
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Configura tu zona horaria (Ej: America/Bogota, America/Mexico_City, Europe/Madrid)
zona_horaria = pytz.timezone('America/Bogota') 
hora_actual = datetime.now(zona_horaria).strftime("%d/%m %I:%M %p")

print("🤖 INICIANDO CEREBRO MAESTRO 3.0 (ALL-IN-ONE)...")

# ==========================================
# 🧠 GENERADOR DE APPS INTERACTIVAS
# ==========================================
def crear_app(nombre_archivo, titulo, labels, datos, colores, mensaje, tipo_default='doughnut', index_axis='x'):
    # Preparamos los datos para JavaScript
    js_labels = json.dumps(labels)
    js_data = json.dumps(datos)
    js_colors = json.dumps(colores)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: transparent; color: #EBEBEB; display: flex; flex-direction: column; align-items: center; margin: 0; padding: 10px; }}
            h3 {{ margin: 0 0 10px 0; font-size: 16px; text-align: center; font-weight: 600; }}
            .controls {{ display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; justify-content: center; }}
            button {{ background: #444; color: white; border: none; padding: 4px 10px; border-radius: 12px; cursor: pointer; font-size: 11px; transition: 0.3s; }}
            button:hover {{ background: #2ea043; }}
            button.active {{ background: #2ea043; font-weight: bold; }}
            .chart-box {{ width: 100%; max-width: 350px; position: relative; height: 220px; }}
            .insight-box {{ background-color: #262626; border-left: 4px solid {colores[0]}; padding: 12px; border-radius: 6px; margin-top: 15px; font-size: 13px; line-height: 1.4; width: 90%; max-width: 350px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .timestamp {{ font-size: 10px; color: #888; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h3>{titulo}</h3>
        <div class="controls">
            <button onclick="cambiarTipo('doughnut')" id="btn-doughnut">🍩</button>
            <button onclick="cambiarTipo('bar')" id="btn-bar">📊</button>
            <button onclick="cambiarTipo('line')" id="btn-line">📈</button>
            <button onclick="cambiarTipo('pie')" id="btn-pie">🥧</button>
        </div>
        <div class="chart-box"><canvas id="miGrafica"></canvas></div>
        <div class="insight-box">{mensaje}</div>
        <div class="timestamp">🔄 Actualizado: {hora_actual}</div>

        <script>
            const labels = {js_labels};
            const dataValues = {js_data};
            const backgroundColors = {js_colors};
            let myChart;

            function renderChart(tipo) {{
                const ctx = document.getElementById('miGrafica').getContext('2d');
                if (myChart) myChart.destroy();

                const idxAxis = '{index_axis}'; // Para barras horizontales
                
                const options = {{
                    indexAxis: idxAxis,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: tipo === 'doughnut' || tipo === 'pie', position: 'bottom', labels: {{ color: '#ccc' }} }} }},
                    scales: {{
                        y: {{ display: tipo === 'bar' || tipo === 'line', ticks: {{ color: '#ccc' }} }},
                        x: {{ display: tipo === 'bar' || tipo === 'line', ticks: {{ color: '#ccc' }} }}
                    }}
                }};

                myChart = new Chart(ctx, {{
                    type: tipo,
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: 'Datos',
                            data: dataValues,
                            backgroundColor: backgroundColors,
                            borderColor: backgroundColors[0],
                            borderWidth: tipo === 'line' ? 2 : 0,
                            borderRadius: 4,
                            tension: 0.4,
                            fill: tipo === 'line'
                        }}]
                    }},
                    options: options
                }});
            }}
            
            function cambiarTipo(t) {{
                renderChart(t);
                document.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                const btn = document.getElementById('btn-'+t);
                if(btn) btn.classList.add('active');
            }}
            
            cambiarTipo('{tipo_default}');
        </script>
    </body>
    </html>
    """
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        file.write(html)

# ==========================================
# 💸 1. FINANZAS (Ingresos y Egresos)
# ==========================================
try:
    print("💸 Analizando Finanzas...")
    DB_EGRESOS = os.environ['DB_EGRESOS']
    DB_INGRESOS = os.environ['DB_INGRESOS']

    # Egresos
    res_out = requests.post(f"https://api.notion.com/v1/databases/{DB_EGRESOS}/query", headers=headers).json().get("results",[])
    cats = {}
    total_out = 0
    hormiga = 0
    
    for r in res_out:
        try:
            m = r["properties"]["Monto"]["number"]
            if m:
                t = r["properties"]["Tipo"]["multi_select"]
                c = t[0]["name"] if t else "Otros"
                cats[c] = cats.get(c, 0) + m
                total_out += m
                if m <= 15000 and c not in ["Suscripciones", "Arriendo"]: hormiga += m
        except: pass

    msg_out = f"💸 Gastos Totales: <b>${total_out:,.0f}</b><br>🐜 Gastos Hormiga: <b>${hormiga:,.0f}</b>"
    crear_app("egresos.html", "Mis Gastos", list(cats.keys()), list(cats.values()), 
              ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'], msg_out, 'doughnut')

    # Ingresos
    res_in = requests.post(f"https://api.notion.com/v1/databases/{DB_INGRESOS}/query", headers=headers).json().get("results",[])
    total_in = sum([r["properties"]["Monto"]["number"] for r in res_in if r["properties"]["Monto"]["number"]])
    balance = total_in - total_out
    
    msg_in = f"💰 Ingresos: ${total_in:,.0f}<br>⚖️ Balance: <b>${balance:,.0f}</b>"
    crear_app("ingresos.html", "Flujo de Caja", ["Ingresos", "Egresos"], [total_in, total_out], 
              ['#2ea043', '#f85149'], msg_in, 'bar')

except Exception as e: print("Error Finanzas:", e)
time.sleep(1)

# ==========================================
# 🚀 2. TAREAS (Productividad)
# ==========================================
try:
    print("🚀 Analizando Tareas...")
    DB_TAREAS = os.environ['DB_TAREAS']
    res = requests.post(f"https://api.notion.com/v1/databases/{DB_TAREAS}/query", headers=headers).json().get("results",[])
    hechas = 0
    pendientes = 0
    for r in res:
        if r["properties"]["Hecho"]["checkbox"]: hechas += 1
        else: pendientes += 1
        
    msg_t = f"🚀 Completadas: <b>{hechas}</b><br>⚠️ Pendientes: <b>{pendientes}</b>"
    crear_app("tareas.html", "Progreso Tareas", ["Completadas", "Pendientes"], [hechas, pendientes], 
              ['#2ea043', '#555555'], msg_t, 'doughnut')
except Exception as e: print("Error Tareas:", e)
time.sleep(1)

# ==========================================
# 🏆 3. HÁBITOS
# ==========================================
try:
    print("🏆 Analizando Hábitos...")
    DB_HABITOS = os.environ['DB_HABITOS']
    res = requests.post(f"https://api.notion.com/v1/databases/{DB_HABITOS}/query", headers=headers).json().get("results",[])
    habs = {}
    lista_habitos = ["Meditacion", "Leer", "Ejercicio", "Agua 2LT", "Agradecer"] # Tus columnas
    
    for h in lista_habitos: habs[h] = 0
    for r in res:
        for h in lista_habitos:
            if r["properties"].get(h, {}).get("checkbox"): habs[h] += 1
            
    msg_h = "La constancia es la clave. 🔥"
    crear_app("habitos.html", "Racha de Hábitos", list(habs.keys()), list(habs.values()), 
              ['#36a2eb', '#ffce56', '#4bc0c0', '#ff6384', '#9966ff'], msg_h, 'bar')
except Exception as e: print("Error Hábitos:", e)

# ==========================================
# 🍅 4. POMODORO
# ==========================================
try:
    print("🍅 Analizando Pomodoro...")
    DB_POM = os.environ['DB_POMODORO']
    res = requests.post(f"https://api.notion.com/v1/databases/{DB_POM}/query", headers=headers).json().get("results",[])
    tiempos = {}
    for r in res:
        t = r["properties"]["Tipo"]["select"]["name"]
        minutos = r["properties"]["Tiempo"]["number"]
        if minutos: tiempos[t] = tiempos.get(t, 0) + minutos
    
    horas = sum(tiempos.values()) // 60
    msg_pom = f"⏱️ Total Enfoque: <b>{horas} horas</b>."
    crear_app("pomodoro.html", "Sesiones Pomodoro", list(tiempos.keys()), list(tiempos.values()), 
              ['#ff6384', '#36a2eb', '#ffce56'], msg_pom, 'pie')
except Exception as e: print("Error Pomodoro:", e)

# ==========================================
# 💀 5. MEMENTO MORI
# ==========================================
try:
    print("💀 Analizando Vida...")
    # EDAD MANUAL (Cámbiala por tu edad real aquí)
    edad = 26 
    esperanza = 80
    vivido = edad
    restante = esperanza - edad
    
    msg_mem = f"Has vivido <b>{edad} años</b>.<br>Te quedan aprox. <b>{restante} inviernos</b>. ¡Vive!"
    crear_app("memento.html", "Mi Vida en Años", ["Vivido", "Restante"], [vivido, restante], 
              ['#333333', '#EBEBEB'], msg_mem, 'bar', 'y') # 'y' para horizontal
except Exception as e: print("Error Memento:", e)

# ==========================================
# 🛒 6. COMPRAS (Wishlist / Presupuesto)
# ==========================================
try:
    print("🛒 Analizando Compras...")
    DB_COMPRAS = os.environ['DB_COMPRAS']
    res = requests.post(f"https://api.notion.com/v1/databases/{DB_COMPRAS}/query", headers=headers).json().get("results",[])
    
    comprado_val = 0
    pendiente_val = 0
    items_falta = 0
    
    for r in res:
        try:
            # Lógica para encontrar Precio
            props = r["properties"]
            precio = 0
            if "Precio" in props: precio = props["Precio"]["number"]
            elif "Monto" in props: precio = props["Monto"]["number"]
            elif "Costo" in props: precio = props["Costo"]["number"]
            if precio is None: precio = 0

            # Lógica para encontrar el Checkbox
            check = False
            if "Comprado" in props: check = props["Comprado"]["checkbox"]
            elif "Hecho" in props: check = props["Hecho"]["checkbox"]
            elif "Check" in props: check = props["Check"]["checkbox"]
            
            if check: comprado_val += precio
            else: 
                pendiente_val += precio
                items_falta += 1
        except: pass
            
    progreso = (comprado_val / (comprado_val + pendiente_val) * 100) if (comprado_val + pendiente_val) > 0 else 0
    msg_comp = f"Has completado el <b>{progreso:.0f}%</b> de tu lista.<br>Te faltan <b>${pendiente_val:,.0f}</b> para los {items_falta} deseos restantes."
    
    crear_app("compras.html", "Presupuesto de Deseos", ["Ya tengo ✅", "Me falta 💰"], [comprado_val, pendiente_val], 
              ['#2ea043', '#555555'], msg_comp, 'doughnut')
except Exception as e: print("Error Compras:", e)

# ==========================================
# 💳 7. SUSCRIPCIONES
# ==========================================
try:
    print("💳 Analizando Suscripciones...")
    DB_SUBS = os.environ['DB_SUBS']
    res = requests.post(f"https://api.notion.com/v1/databases/{DB_SUBS}/query", headers=headers).json().get("results",[])
    subs = {}
    for r in res:
        n = r["properties"]["Servicio"]["title"][0]["plain_text"]
        p = r["properties"]["Precio"]["number"]
        if p: subs[n] = p
    
    total_sub = sum(subs.values())
    msg_sub = f"Gasto fijo mensual: <b>${total_sub:,.0f}</b>"
    crear_app("suscripciones.html", "Suscripciones Mensuales", list(subs.keys()), list(subs.values()), 
              ['#ff9f40', '#ff6384', '#4bc0c0'], msg_sub, 'bar')
except Exception as e: print("Error Subs:", e)

# ==========================================
# 💤 8. SUEÑO
# ==========================================
try:
    print("💤 Analizando Sueño...")
    DB_SUENO = os.environ['DB_SUENO']
    payload = { "sorts": [ { "property": "Hora de despertar", "direction": "ascending" } ] }
    res = requests.post(f"https://api.notion.com/v1/databases/{DB_SUENO}/query", headers=headers, json=payload).json().get("results",[])
    
    dias = []
    horas_sueno = []
    for r in res:
        # Intenta obtener los minutos desde una fórmula o número
        mins = 0
        props = r["properties"]
        if "Minutos totales de sueño" in props: mins = props["Minutos totales de sueño"]["formula"]["number"]
        elif "Minutos" in props: mins = props["Minutos"]["number"]
        
        # Obtener fecha
        fecha = ""
        if "Hora de despertar" in props and props["Hora de despertar"]["date"]:
            fecha = props["Hora de despertar"]["date"]["start"][5:10] # MM-DD
        
        if mins and fecha:
            dias.append(fecha)
            horas_sueno.append(round(mins/60, 1))
            
    promedio = sum(horas_sueno)/len(horas_sueno) if horas_sueno else 0
    msg_sueno = f"😴 Promedio: <b>{promedio:.1f} horas</b>."
    crear_app("sueno.html", "Calidad de Sueño", dias[-7:], horas_sueno[-7:], 
              ['#36a2eb'], msg_sueno, 'line')
except Exception as e: print("Error Sueño:", e)

print("✅ ¡TODAS LAS GRÁFICAS GENERADAS CON ÉXITO!")
