async function loadData() {
            try {
                const response = await fetch('datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                const egresos = data.datos?.egresos || [];
                processEgresos(egresos);
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<div style="color: var(--accent);">Error: ${error.message}</div>`;
            }
        }

        function processEgresos(egresos) {
            // ESTRUCTURA REAL:
            // • Balance (relation)
            // • Tipo (multi_select) → ["Vivienda"]
            // • Fecha (date) → "2026-03-03"
            // • Monto (number) → 500000
            // • Forty Box (select) → "Nequi"
            // • Mes (select) → "Marzo"
            // • Items (title) → "Arriendo Mes de Febrero"
            
            const processed = egresos.map(e => {
                const p = e.properties || {};
                return {
                    tipos: p.Tipo?.multi_select?.map(t => t.name) || ['Sin tipo'],
                    fecha: p.Fecha?.date?.start,
                    monto: p.Monto?.number || 0,
                    fortyBox: p['Forty Box']?.select?.name || 'Sin cuenta',
                    mes: p.Mes?.select?.name || 'Sin mes',
                    items: p.Items?.title?.[0]?.plain_text || 'Sin descripción'
                };
            });

            const total = processed.reduce((s, e) => s + e.monto, 0);
            const promedio = processed.length ? total / processed.length : 0;

            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">$${(total / 1000000).toFixed(2)}M</div>
                    <div class="stat-label">Total Egresos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$${Math.round(promedio / 1000)}K</div>
                    <div class="stat-label">Promedio</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${processed.length}</div>
                    <div class="stat-label">Transacciones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${new Set(processed.flatMap(e => e.tipos)).size}</div>
                    <div class="stat-label">Categorías</div>
                </div>
            `;

            renderPolarChart(processed);
            renderMesChart(processed);
            renderList(processed);
        }

        function renderPolarChart(egresos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';

            // Agrupar por tipo (multi_select puede tener varios)
            const porTipo = {};
            egresos.forEach(e => {
                e.tipos.forEach(tipo => {
                    porTipo[tipo] = (porTipo[tipo] || 0) + e.monto;
                });
            });

            const sorted = Object.entries(porTipo).sort((a, b) => b[1] - a[1]);
            const colors = [
                'rgba(239, 68, 68, 0.7)', 'rgba(245, 158, 11, 0.7)',
                'rgba(16, 185, 129, 0.7)', 'rgba(59, 130, 246, 0.7)',
                'rgba(139, 92, 246, 0.7)', 'rgba(236, 72, 153, 0.7)',
                'rgba(6, 182, 212, 0.7)', 'rgba(249, 115, 22, 0.7)'
            ];

            new Chart(document.getElementById('polarChart'), {
                type: 'polarArea',
                data: {
                    labels: sorted.map(s => s[0]),
                    datasets: [{
                        data: sorted.map(s => s[1]),
                        backgroundColor: colors.slice(0, sorted.length),
                        borderColor: isDark ? '#202020' : '#ffffff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: textColor }
                        }
                    },
                    scales: {
                        r: {
                            grid: { color: isDark ? '#2f2f2f' : '#e0e0e0' },
                            pointLabels: { color: textColor },
                            ticks: { color: textColor, backdropColor: 'transparent', callback: v => '$' + (v / 1000) + 'K' }
                        }
                    }
                }
            });
        }

        function renderMesChart(egresos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            const gridColor = isDark ? '#2f2f2f' : '#e0e0e0';

            const porMes = {};
            egresos.forEach(e => {
                porMes[e.mes] = (porMes[e.mes] || 0) + e.monto;
            });

            new Chart(document.getElementById('mesChart'), {
                type: 'line',
                data: {
                    labels: Object.keys(porMes),
                    datasets: [{
                        label: 'Gastos',
                        data: Object.values(porMes),
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: gridColor }, ticks: { color: textColor, callback: v => '$' + (v / 1000) + 'K' } },
                        x: { grid: { display: false }, ticks: { color: textColor } }
                    }
                }
            });
        }

        function renderList(egresos) {
            const recientes = egresos.slice(-5).reverse();
            document.getElementById('expenseList').innerHTML = recientes.map(e => `
                <div class="expense-item">
                    <div class="expense-info">
                        <div class="expense-name">${e.items}</div>
                        <div class="expense-meta">${e.tipos.join(', ')} • ${e.fortyBox} • ${e.mes}</div>
                    </div>
                    <div class="expense-amount">-$${e.monto.toLocaleString()}</div>
                </div>
            `).join('');
        }

        loadData();