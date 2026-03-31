async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                const ingresos = data.datos?.ingresos || [];
                processIngresos(ingresos);
            } catch (error) {
                document.getElementById('kpiGrid').innerHTML = `<div style="color: #ef4444;">Error: ${error.message}</div>`;
            }
        }

        function processIngresos(ingresos) {
            // ESTRUCTURA REAL:
            // • Fecha (date) → "2026-03-02"
            // • Motivo (select) → "Sueldo"
            // • Tipo (select) → "Nequi"
            // • Monto (number) → 510000
            // • Balance (relation)
            // • Mes (select) → "Febrero"
            // • Items (title) → "Nomina Hotel - Segunda Quin Feb"
            
            const processed = ingresos.map(i => {
                const p = i.properties || {};
                return {
                    fecha: p.Fecha?.date?.start,
                    motivo: p.Motivo?.select?.name || 'Sin motivo',
                    tipo: p.Tipo?.select?.name || 'Sin tipo',
                    monto: p.Monto?.number || 0,
                    mes: p.Mes?.select?.name || 'Sin mes',
                    items: p.Items?.title?.[0]?.plain_text || 'Sin descripción'
                };
            });

            const total = processed.reduce((s, i) => s + i.monto, 0);
            const promedio = processed.length ? total / processed.length : 0;
            const mesesUnicos = [...new Set(processed.map(i => i.mes))].length;

            document.getElementById('kpiGrid').innerHTML = `
                <div class="kpi-card">
                    <div class="kpi-value">$${(total / 1000000).toFixed(2)}M</div>
                    <div class="kpi-label">Total Ingresos</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">$${Math.round(promedio / 1000)}K</div>
                    <div class="kpi-label">Promedio</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${processed.length}</div>
                    <div class="kpi-label">Transacciones</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value">${mesesUnicos}</div>
                    <div class="kpi-label">Meses</div>
                </div>
            `;

            renderCharts(processed);
            renderList(processed);
        }

        function renderCharts(ingresos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            const gridColor = isDark ? '#2f2f2f' : '#e0e0e0';

            // Por Mes
            const porMes = {};
            ingresos.forEach(i => {
                porMes[i.mes] = (porMes[i.mes] || 0) + i.monto;
            });

            new Chart(document.getElementById('mesChart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(porMes),
                    datasets: [{
                        label: 'Ingresos ($)',
                        data: Object.values(porMes),
                        backgroundColor: '#10b981',
                        borderRadius: 6
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

            // Por Tipo (Nequi, etc.)
            const porTipo = {};
            ingresos.forEach(i => {
                porTipo[i.tipo] = (porTipo[i.tipo] || 0) + i.monto;
            });

            new Chart(document.getElementById('tipoChart'), {
                type: 'doughnut',
                data: {
                    labels: Object.keys(porTipo),
                    datasets: [{
                        data: Object.values(porTipo),
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'right', labels: { color: textColor } } }
                }
            });
        }

        function renderList(ingresos) {
            const recientes = ingresos.slice(-5).reverse();
            document.getElementById('recentList').innerHTML = recientes.map(i => `
                <div class="income-item">
                    <div class="income-info">
                        <div class="income-name">${i.items}</div>
                        <div class="income-meta">${i.motivo} • ${i.tipo} • ${i.mes}</div>
                    </div>
                    <div class="income-amount">+$${i.monto.toLocaleString()}</div>
                </div>
            `).join('');
        }

        loadData();