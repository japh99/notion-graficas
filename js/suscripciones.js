async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                const subs = data.datos?.suscripciones || [];
                processSubs(subs);
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<div style="color: var(--accent);">Error: ${error.message}</div>`;
            }
        }

        function processSubs(subs) {
            // ESTRUCTURA REAL:
            // • Notas (rich_text)
            // • Precio (number) → 40000
            // • Etiqueta Costo Mensual (rich_text)
            // • Etiqueta Fecha Renocación (rich_text)
            // • Prox Renovación (formula)
            // • Días restantes (formula) → "0 days left"
            // • Costo Anual (formula) → 480000
            // • Costo Mensual (formula) → 40000
            // • Categoría (relation)
            // • Este Mes? (formula)
            // • Status (select) → "Activo"
            // • Cuenta (select) → "Mensual"
            // • Fecha Renovación (date) → null
            // • Servicio (title) → "Barbería"
            
            const processed = subs.map(s => {
                const p = s.properties || {};
                return {
                    servicio: p.Servicio?.title?.[0]?.plain_text || 'Sin nombre',
                    precio: p.Precio?.number || 0,
                    costoMensual: p['Costo Mensual']?.formula?.number || p.Precio?.number || 0,
                    costoAnual: p['Costo Anual']?.formula?.number || 0,
                    status: p.Status?.select?.name || 'Desconocido',
                    cuenta: p.Cuenta?.select?.name || 'Mensual',
                    diasRestantes: p['Días restantes']?.formula?.string || '',
                    proxRenovacion: p['Prox Renovación']?.formula?.date?.start || null
                };
            }).filter(s => s.status === 'Activo');

            const mensualTotal = processed.reduce((s, sub) => s + sub.costoMensual, 0);
            const anualTotal = processed.reduce((s, sub) => s + sub.costoAnual, 0);

            document.getElementById('burnRate').textContent = '$' + (mensualTotal / 1000).toFixed(0) + 'K';
            
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${processed.length}</div>
                    <div class="stat-label">Servicios Activos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$${(anualTotal / 1000000).toFixed(2)}M</div>
                    <div class="stat-label">Costo Anual</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$${Math.round(mensualTotal / processed.length / 1000)}K</div>
                    <div class="stat-label">Promedio/Mes</div>
                </div>
            `;

            renderChart(processed);
            renderList(processed);
        }

        function renderChart(subs) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';

            new Chart(document.getElementById('costChart'), {
                type: 'bar',
                data: {
                    labels: subs.map(s => s.servicio),
                    datasets: [{
                        label: 'Costo mensual ($)',
                        data: subs.map(s => s.costoMensual),
                        backgroundColor: '#ec4899',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { 
                            grid: { color: isDark ? '#2f2f2f' : '#e0e0e0' }, 
                            ticks: { color: textColor, callback: v => '$' + (v / 1000) + 'K' } 
                        },
                        x: { 
                            grid: { display: false }, 
                            ticks: { color: textColor, font: { size: 10 } } 
                        }
                    }
                }
            });
        }

        function renderList(subs) {
            document.getElementById('subList').innerHTML = subs.sort((a, b) => b.precio - a.precio).map(s => `
                <div class="sub-item">
                    <div class="sub-info">
                        <div class="sub-name">
                            ${s.servicio}
                            <span class="sub-status">${s.status}</span>
                        </div>
                        <div class="sub-meta">${s.cuenta} • ${s.diasRestantes}</div>
                    </div>
                    <div class="sub-price">$${s.costoMensual.toLocaleString()}</div>
                </div>
            `).join('');
        }

        loadData();