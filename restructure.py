#!/usr/bin/env python3
"""
Script para reestructurar el proyecto:
1. Extraer CSS común a css/styles.css
2. Extraer JavaScript específico de cada página a js/
3. Actualizar los HTML para referenciar los archivos externos
4. Mover datos.json a data/
"""

import os
import re
from pathlib import Path

WORKSPACE = Path('/workspace')

def extract_js(html_file):
    """Extrae solo el JavaScript inline (no CDN) de un archivo HTML."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer JS inline (entre <script> y </script>, excluyendo CDN)
    js_matches = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
    # Filtrar scripts que no sean vacíos
    js_content = '\n'.join([js for js in js_matches if js.strip()])
    
    return js_content, content

def create_shared_css():
    """Crea un archivo CSS compartido con estilos comunes."""
    common_css = """:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f5;
    --text-primary: #2c2c2c;
    --text-secondary: #6b6b6b;
    --accent: #8b5cf6;
    --accent-light: #a78bfa;
    --border: #e0e0e0;
    --success: #10b981;
    --warning: #f59e0b;
    --card-bg: #ffffff;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #191919;
        --bg-secondary: #252525;
        --text-primary: #ffffff;
        --text-secondary: #a0a0a0;
        --accent: #a78bfa;
        --accent-light: #c4b5fd;
        --border: #2f2f2f;
        --success: #34d399;
        --warning: #fbbf24;
        --card-bg: #202020;
    }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    padding: 20px;
}

.container { max-width: 1200px; margin: 0 auto; }

h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 2rem; }

.summary-card {
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    border-radius: 16px;
    padding: 2rem;
    color: white;
    margin-bottom: 2rem;
    text-align: center;
}

.summary-label { font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem; }
.summary-value { font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem; }
.summary-sub { font-size: 0.9rem; opacity: 0.9; }

.funds-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.fund-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
}

.fund-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.fund-name { font-weight: 600; font-size: 1.1rem; }
.fund-type {
    font-size: 0.75rem;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    background: var(--bg-secondary);
    color: var(--text-secondary);
}

.fund-amount { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
.fund-progress { height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; margin-top: 1rem; }
.fund-progress-bar { height: 100%; background: var(--accent); border-radius: 3px; }
.fund-details { margin-top: 1rem; font-size: 0.85rem; color: var(--text-secondary); }

.actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn-primary {
    background: var(--accent);
    color: white;
}

.btn-primary:hover {
    background: var(--accent-light);
    transform: translateY(-2px);
}

.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.btn-secondary:hover {
    background: var(--border);
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.card-title {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.loading { text-align: center; padding: 3rem; color: var(--text-secondary); }

.chart-container {
    position: relative;
    height: 300px;
    margin-top: 1rem;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
}

th {
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

tr:hover { background: var(--bg-secondary); }

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-success { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.badge-warning { background: rgba(245, 158, 11, 0.1); color: var(--warning); }

input, select, textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 1rem;
    margin-bottom: 1rem;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 2rem;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
}

.form-group { margin-bottom: 1rem; }
.form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem; }

.nav-links {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.nav-links a {
    color: var(--text-secondary);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.2s;
}

.nav-links a:hover, .nav-links a.active {
    background: var(--bg-secondary);
    color: var(--accent);
}
"""
    
    css_path = WORKSPACE / 'css' / 'styles.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(common_css)
    print(f"✓ CSS común creado: {css_path}")
    return common_css

def update_html_file(html_file, has_specific_js=False):
    """Actualiza un archivo HTML para usar CSS y JS externos."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover bloque <style>...</style> completo si existe
    content = re.sub(r'\s*<style>.*?</style>\s*\n?', '', content, flags=re.DOTALL)
    
    # Añadir referencia al CSS externo si no existe
    if '<link rel="stylesheet" href="css/styles.css">' not in content:
        content = content.replace('</head>', '    <link rel="stylesheet" href="css/styles.css">\n</head>')
    
    # Si hay JS específico, actualizar referencia
    page_name = html_file.stem
    if has_specific_js:
        # Remover cualquier script inline existente (pero mantener CDN)
        content = re.sub(r'\s*<script>(?!.*cdn\.jsdelivr).*?</script>\s*\n?', '', content, flags=re.DOTALL)
        
        # Añadir referencia al JS específico antes de </body>
        js_ref = f'    <script src="js/{page_name}.js"></script>\n</body>'
        if '</body>' in content and f'src="js/{page_name}.js"' not in content:
            content = content.replace('</body>', js_ref)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ HTML actualizado: {html_file}")

def main():
    # Crear directorios
    (WORKSPACE / 'css').mkdir(exist_ok=True)
    (WORKSPACE / 'js').mkdir(exist_ok=True)
    (WORKSPACE / 'data').mkdir(exist_ok=True)
    
    # Mover datos.json si existe en root
    datos_old = WORKSPACE / 'datos.json'
    datos_new = WORKSPACE / 'data' / 'datos.json'
    if datos_old.exists() and not datos_new.exists():
        datos_old.rename(datos_new)
        print(f"✓ datos.json movido a data/")
    
    # Crear CSS compartido
    create_shared_css()
    
    # Procesar cada archivo HTML
    html_files = list(WORKSPACE.glob('*.html'))
    print(f"\nProcesando {len(html_files)} archivos HTML...")
    
    for html_file in html_files:
        page_name = html_file.stem
        
        # Extraer JS específico
        js_content, original_content = extract_js(html_file)
        
        # Guardar JS específico si existe
        has_specific_js = bool(js_content and js_content.strip())
        if has_specific_js:
            js_path = WORKSPACE / 'js' / f'{page_name}.js'
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content.strip())
            print(f"  → JS extraído: {page_name}.js ({len(js_content)} bytes)")
        
        # Actualizar HTML
        update_html_file(html_file, has_specific_js)
    
    print("\n✓ Reestructuración completada!")
    print("\nNueva estructura:")
    print("  /css/styles.css     - Estilos compartidos")
    print("  /js/*.js           - Scripts específicos por página")
    print("  /data/datos.json   - Datos JSON")
    print("  /*.html            - Páginas actualizadas")

if __name__ == '__main__':
    main()
