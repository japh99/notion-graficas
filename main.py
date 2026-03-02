import requests
import json
import os

NOTION_TOKEN = os.environ['NOTION_TOKEN']
DB_INGRESOS = os.environ['DB_INGRESOS']
DB_EGRESOS = os.environ['DB_EGRESOS']

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ==========================================
# 📊 1. ANÁLISIS DE EGRESOS (Gastos)
# ==========================================
res_egresos = requests.post(f"https://api.notion.com/v1/databases/{DB_EGRESOS}/query", headers=headers)
datos_egresos = res_egresos.json().get("results",[])

gastos_por_categoria = {}
total_gastado = 0
gastos_hormiga = 0
cantidad_hormiga = 0

for row in datos_egresos:
    try:
        monto = row["properties"]["Monto"]["number"]
        if monto is None: continue
        
        # Como "Tipo" es multi-select, extraemos la primera etiqueta que le hayas puesto
        etiquetas_tipo = row["properties"]["Tipo"]["multi_select"]
        if etiquetas_tipo:
            categoria = etiquetas_tipo[0]["name"]
        else:
            categoria = "Sin categoría"

        total_gastado += monto
        gastos_por_categoria[categoria] = gastos_por_categoria.get(categoria, 0) + monto

        # DETECTAR GASTO HORMIGA (Menor a 15,000 COP)
        if monto <= 15000 and categoria not in["Suscripciones", "Arriendo", "Deuda"]:
            gastos_hormiga += monto
            cantidad_hormiga += 1
    except Exception:
        pass 

cat_max = max(gastos_por_categoria, key=gastos_por_categoria.get) if gastos_por_categoria else "Ninguna"

mensaje_egresos = f"💸 <b>Resumen Egresos:</b> Has gastado un total de <b>${total_gastado:,.0f} COP</b>. "
if gastos_por_categoria:
    mensaje_egresos += f"Tu mayor gasto es en <b>{cat_max}</b> (${gastos_por_categoria.get(cat_max, 0):,.0f} COP). "

if cantidad_hormiga > 3:
    mensaje_egresos += f"<br><br>⚠️ <b>¡Alerta Gasto Hormiga!</b> Has hecho {cantidad_hormiga} compras pequeñas que suman <b>${gastos_hormiga:,.0f} COP</b>. ¡Esas pequeñas fugas suman rápido!"
else:
    mensaje_egresos += "<br><br>✅ Tus gastos pequeños están bajo control."

# ==========================================
# 📊 2. ANÁLISIS DE INGRESOS Y BALANCE
# ==========================================
res_ingresos = requests.post(f"https://api.notion.com/v1/databases/{DB_INGRESOS}/query", headers=headers)
datos_ingresos = res_ingresos.json().get("results",[])

total_ingresos = 0

for row in datos_ingresos:
    try:
        monto_in = row["properties"]["Monto"]["number"]
        if monto_in is not None:
            total_ingresos += monto_in
    except Exception:
        pass

balance_real = total_ingresos - total_gastado
mensaje_ingresos = f"💰 <b>Resumen Ingresos:</b> Han entrado <b>${total_ingresos:,.0f} COP</b>."
mensaje_ingresos += f"<br><br>⚖️ <b>Balance Real:</b> Te quedan <b>${balance_real:,.0f} COP</b> disponibles."


# ==========================================
# 🎨 3. GENERAR LOS PANELES WEB INTERACTIVOS
# ==========================================
def crear_html(nombre_archivo, titulo, tipo_grafico, labels, datos, colores, mensaje):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display:flex; flex-direction:column; align-items:center; color: #EBEBEB; background-color: transparent; margin: 0; padding: 10px; }}
            .chart-container {{ width: 100%; max-width: 320px; margin-top: 10px; }}
            .insight-box {{ background-color: #2F2F2F; border-left: 5px solid #2ea043; padding: 15px; border-radius: 8px; max-width: 400px; margin-top: 20px; font-size: 14px; line-height: 1.5; box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: #EBEBEB; }}
            h3 {{ margin-bottom: 0; color: #ffffff; font-weight: 600; }}
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
                data: {{
                    labels: {json.dumps(labels)},
                    datasets:[{{ data: {json.dumps(datos)}, backgroundColor: {json.dumps(colores)}, borderWidth: 0 }}]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});
        </script>
    </body>
    </html>
    """
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        file.write(html)

# Dibujar Panel de Egresos
colores_egresos =['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0', '#f7797d', '#b19cd9']
crear_html("egresos.html", "Distribución de Gastos", "doughnut", list(gastos_por_categoria.keys()), list(gastos_por_categoria.values()), colores_egresos, mensaje_egresos)

# Dibujar Panel de Ingresos (Cambiamos la línea roja a la caja de insights para Egresos)
html = open("egresos.html", "r", encoding="utf-8").read().replace("#2ea043", "#f85149")
open("egresos.html", "w", encoding="utf-8").write(html)

# Dibujar Panel de Ingresos vs Egresos
crear_html("ingresos.html", "Flujo de Caja", "bar", ["Ingresos 🟢", "Egresos 🔴"], [total_ingresos, total_gastado],['#2ea043', '#f85149'], mensaje_ingresos)

print("¡Paneles financieros creados con éxito!")
