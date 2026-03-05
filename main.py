import requests
import json
import os
from datetime import datetime, timedelta
import pytz
from collections import defaultdict

# ==========================================
# ⚙️ CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==========================================

NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise ValueError("❌ NOTION_TOKEN no está configurado en los secrets")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Configuración de zona horaria (Bogotá)
zona_horaria = pytz.timezone('America/Bogota')
hora_actual = datetime.now(zona_horaria).strftime("%d/%m/%Y %I:%M %p")

# Diccionario completo de bases de datos
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

# ==========================================
# 🚜 FUNCIÓN EXTRACTORA MEJORADA
# ==========================================

def extraer_datos_notion(db_id, nombre_db):
    """
    Extrae TODOS los registros de una base de datos Notion (maneja paginación)
    """
    if not db_id or len(db_id) < 10:
        print(f"⚠️  Saltando '{nombre_db}': ID no configurado o inválido")
        return []
    
    print(f"📦 Extrayendo datos de: {nombre_db}...")
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    
    todos_los_resultados = []
    next_cursor = None
    intentos = 0
    max_intentos = 3
    
    while intentos < max_intentos:
        try:
            payload = {}
            if next_cursor:
                payload["start_cursor"] = next_cursor
            
            # Notion tiene límite de 100 por página, así que paginamos
            payload["page_size"] = 100
            
            response = requests.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                todos_los_resultados.extend(results)
                
                # Verificar si hay más páginas
                next_cursor = data.get("next_cursor")
                if not next_cursor:
                    break  # No hay más datos
                
                print(f"   ↳ Página obtenida: {len(results)} registros (Total acumulado: {len(todos_los_resultados)})")
                
            elif response.status_code == 429:
                print(f"   ⏳ Rate limit alcanzado en {nombre_db}, esperando...")
                import time
                time.sleep(1)
                continue
            else:
                print(f"❌ Error en {nombre_db}: Status {response.status_code}")
                print(f"   Detalle: {response.text[:200]}")
                intentos += 1
                
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout en {nombre_db}, reintentando...")
            intentos += 1
        except Exception as e:
            print(f"❌ Error crítico en {nombre_db}: {str(e)}")
            intentos += 1
    
    print(f"✅ {nombre_db}: {len(todos_los_resultados)} filas totales extraídas")
    return todos_los_resultados

# ==========================================
# 🧠 ANÁLISIS INTELIGENTE (NUEVO)
# ==========================================

def generar_analitica(datos):
    """
    Genera insights automáticos basados en los datos recolectados
    """
    analitica = {
        "resumen_financiero": {},
        "productividad": {},
        "salud": {},
        "alertas": [],
        "recomendaciones": []
    }
    
    try:
        # Análisis Financiero
        ingresos = datos.get("ingresos", [])
        egresos = datos.get("egresos", [])
        
        if ingresos and egresos:
            total_ingresos = sum(
                extraer_numero(item.get("properties", {}).get("Monto")) 
                for item in ingresos
            )
            total_egresos = sum(
                extraer_numero(item.get("properties", {}).get("Monto")) 
                for item in egresos
            )
            
            balance = total_ingresos - total_egresos
            ratio_ahorro = (balance / total_ingresos * 100) if total_ingresos > 0 else 0
            
            analitica["resumen_financiero"] = {
                "total_ingresos_mes": total_ingresos,
                "total_egresos_mes": total_egresos,
                "balance_neto": balance,
                "ratio_ahorro_pct": round(ratio_ahorro, 2),
                "estado": "positivo" if balance > 0 else "negativo"
            }
            
            if ratio_ahorro < 10:
                analitica["alertas"].append("⚠️ Ratio de ahorro bajo (<10%). Considera revisar gastos hormiga.")
            elif ratio_ahorro > 30:
                analitica["recomendaciones"].append("🌟 Excelente ratio de ahorro. Podrías diversificar inversiones.")
        
        # Análisis de Productividad (Pomodoro)
        pomodoros = datos.get("pomodoro", [])
        if pomodoros:
            sesiones_completadas = len([
                p for p in pomodoros 
                if p.get("properties", {}).get("Estado", {}).get("select", {}).get("name") == "Completado"
            ])
            total_horas = sum(
                extraer_numero(p.get("properties", {}).get("Duración")) or 25 
                for p in pomodoros
            ) / 60
            
            # Detectar racha actual
            fechas_unicas = sorted(set([
                p.get("created_time", "")[:10] 
                for p in pomodoros 
                if p.get("created_time")
            ]), reverse=True)
            
            racha_actual = 0
            hoy = datetime.now(zona_horaria).strftime("%Y-%m-%d")
            
            for i, fecha in enumerate(fechas_unicas):
                fecha_esperada = (datetime.now(zona_horaria) - timedelta(days=i)).strftime("%Y-%m-%d")
                if fecha == fecha_esperada:
                    racha_actual += 1
                else:
                    break
            
            analitica["productividad"] = {
                "sesiones_totales": len(pomodoros),
                "sesiones_completadas": sesiones_completadas,
                "horas_foco_profundo": round(total_horas, 2),
                "racha_actual_dias": racha_actual,
                "eficiencia_pct": round(sesiones_completadas / len(pomodoros) * 100, 1) if pomodoros else 0
            }
            
            if racha_actual >= 7:
                analitica["recomendaciones"].append(f"🔥 Racha de productividad: {racha_actual} días. ¡Mantén el momentum!")
        
        # Análisis de Sueño
        suenos = datos.get("sueno", [])
        if suenos:
            duraciones = [
                extraer_numero(s.get("properties", {}).get("Duración")) 
                for s in suenos[-14:]  # Últimos 14 días
                if extraer_numero(s.get("properties", {}).get("Duración")) > 0
            ]
            
            if duraciones:
                promedio_sueno = sum(duraciones) / len(duraciones)
                analitica["salud"] = {
                    "promedio_sueno_horas": round(promedio_sueno, 2),
                    "dias_registrados": len(duraciones),
                    "calidad_promedio": calcular_calidad_sueno(suenos)
                }
                
                if promedio_sueno < 6:
                    analitica["alertas"].append("😴 Promedio de sueño crítico (<6h). Riesgo de burnout detectado.")
                elif promedio_sueno > 8.5:
                    analitica["recomendaciones"].append("✅ Buena higiene de sueño mantenida.")
        
        # Análisis de Hábitos
        habitos = datos.get("habitos", [])
        if habitos:
            completados_hoy = len([
                h for h in habitos 
                if h.get("properties", {}).get("Hoy", {}).get("checkbox") == True
            ])
            total_habitos = len(habitos)
            
            analitica["habitos"] = {
                "total_seguimiento": total_habitos,
                "completados_hoy": completados_hoy,
                "ratio_diario_pct": round(completados_hoy / total_habitos * 100, 1) if total_habitos else 0
            }
        
    except Exception as e:
        print(f"⚠️  Error en análisis inteligente: {e}")
        analitica["error"] = str(e)
    
    return analitica

def extraer_numero(prop):
    """Helper para extraer valores numéricos de propiedades de Notion"""
    if not prop:
        return 0
    if isinstance(prop, (int, float)):
        return prop
    if isinstance(prop, dict):
        if "number" in prop and prop["number"] is not None:
            return prop["number"]
        if "formula" in prop and "number" in prop["formula"]:
            return prop["formula"]["number"]
    return 0

def calcular_calidad_sueno(suenos):
    """Calcula calidad promedio de sueño basado en propiedades"""
    calidades = []
    for s in suenos[-14:]:
        prop_calidad = s.get("properties", {}).get("Calidad", {}).get("select", {}).get("name")
        if prop_calidad:
            mapping = {"Excelente": 5, "Buena": 4, "Regular": 3, "Mala": 2, "Pésima": 1}
            calidades.append(mapping.get(prop_calidad, 3))
    
    return round(sum(calidades) / len(calidades), 2) if calidades else 0

# ==========================================
# 🚀 EJECUCIÓN MAESTRA
# ==========================================

print(f"\n{'='*50}")
print(f"🚀 INICIANDO EXTRACCIÓN JAPH 2026")
print(f"📅 {hora_actual}")
print(f"{'='*50}\n")

# Extracción de todas las bases de datos
datos_crudos = {}
for nombre, id_notion in dbs_config.items():
    datos_crudos[nombre] = extraer_datos_notion(id_notion, nombre)
    print()  # Línea en blanco para legibilidad

# Generar análisis inteligente
print("🧠 Generando análisis inteligente...")
analitica = generar_analitica(datos_crudos)

# Estructura final del JSON
datos_finales = {
    "metadata": {
        "ultima_actualizacion": hora_actual,
        "estado": "OK",
        "version_sistema": "2.1.0",
        "total_registros": sum(len(v) for v in datos_crudos.values())
    },
    "analitica_inteligente": analitica,
    "datos": datos_crudos  # Datos crudos originales para los HTML
}

# Guardar archivo JSON con manejo de errores mejorado
try:
    output_path = "datos.json"
    
    # Verificar si existe backup previo
    if os.path.exists(output_path):
        backup_path = f"datos_backup_{datetime.now(zona_horaria).strftime('%Y%m%d_%H%M')}.json"
        os.rename(output_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
    
    # Guardar nuevo archivo
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(datos_finales, f, ensure_ascii=False, indent=2, default=str)
    
    # Verificar integridad
    file_size = os.path.getsize(output_path)
    print(f"\n{'='*50}")
    print(f"✅ ¡PROCESO COMPLETADO!")
    print(f"📁 Archivo: {output_path}")
    print(f"📊 Tamaño: {file_size:,} bytes")
    print(f"📈 Registros totales: {datos_finales['metadata']['total_registros']}")
    
    # Resumen por base de datos
    print(f"\n📋 RESUMEN DE BASES DE DATOS:")
    for nombre, datos in datos_crudos.items():
        status = "✅" if len(datos) > 0 else "⚠️"
        print(f"   {status} {nombre}: {len(datos)} registros")
    
    print(f"{'='*50}\n")
    
    # Generar reporte de alertas si existen
    if analitica.get("alertas"):
        print("🚨 ALERTAS DETECTADAS:")
        for alerta in analitica["alertas"]:
            print(f"   {alerta}")
        print()
    
    if analitica.get("recomendaciones"):
        print("💡 RECOMENDACIONES:")
        for rec in analitica["recomendaciones"]:
            print(f"   {rec}")
        print()

except Exception as e:
    print(f"\n❌ ERROR CRÍTICO al guardar datos.json: {str(e)}")
    # Intentar restaurar backup si existe
    if 'backup_path' in locals() and os.path.exists(backup_path):
        print(f"🔄 Restaurando backup: {backup_path}")
        os.rename(backup_path, output_path)
    raise
