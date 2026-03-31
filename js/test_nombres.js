fetch('../data/datos.json')
            .then(r => r.json())
            .then(data => {
                let html = '';
                const datos = data.datos || data;
                
                for (const [nombre, registros] of Object.entries(datos)) {
                    if (!Array.isArray(registros)) continue;
                    
                    html += `<div class="db">`;
                    html += `<h2>📁 ${nombre.toUpperCase()} (${registros.length} registros)</h2>`;
                    
                    if (registros.length === 0) {
                        html += `<div class="error">Sin registros para analizar</div>`;
                        html += `</div>`;
                        continue;
                    }
                    
                    // Analizar primer registro
                    const props = registros[0].properties || {};
                    
                    for (const [propName, propVal] of Object.entries(props)) {
                        const tipo = propVal.type || 'unknown';
                        html += `<div class="prop">• ${propName} <span class="type">(${tipo})</span></div>`;
                        
                        // Muestra valor según tipo
                        let muestra = '';
                        try {
                            switch(tipo) {
                                case 'title':
                                    muestra = propVal.title?.[0]?.plain_text || 'vacío';
                                    break;
                                case 'number':
                                    muestra = propVal.number;
                                    break;
                                case 'select':
                                    muestra = propVal.select?.name || 'null';
                                    break;
                                case 'multi_select':
                                    muestra = JSON.stringify(propVal.multi_select?.map(o => o.name) || []);
                                    break;
                                case 'checkbox':
                                    muestra = propVal.checkbox;
                                    break;
                                case 'date':
                                    muestra = propVal.date?.start || 'null';
                                    break;
                                case 'formula':
                                    muestra = propVal.formula?.number || propVal.formula?.string || 'formula';
                                    break;
                                case 'rollup':
                                    muestra = propVal.rollup?.number || 'rollup';
                                    break;
                                default:
                                    muestra = '[ver JSON]';
                            }
                        } catch(e) {
                            muestra = 'Error: ' + e.message;
                        }
                        
                        html += `<div class="sample">→ ${muestra}</div>`;
                    }
                    
                    html += `</div>`;
                }
                
                document.getElementById('output').innerHTML = html;
            })
            .catch(err => {
                document.getElementById('output').innerHTML = 
                    `<div class="error">Error cargando datos.json: ${err.message}</div>`;
            });