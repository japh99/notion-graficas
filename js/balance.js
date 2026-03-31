async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                
                document.getElementById('lastUpdate').textContent = 
                    data.metadata?.ultima_actualizacion || 'Desconocida';
                
                const ingresos = data.datos?.ingresos || data.ingresos || [];
                const egresos = data.datos?.egresos || data.egresos || [];
                
                processBalance(ingresos, egresos);
            } catch (error) {
                document.getElementById('metricsGrid').innerHTML = 
                    `<div style="color: var(--danger);">Error: ${error.message}</div>`;
            }
        }
        
        function processBalance(ingresos, egresos) {
            const ingresosProc = ingresos.map(i => ({
                monto: i.properties?.Monto?.number || 0,
                fecha: new Date(i.properties?.Fecha?.date?.start || i.created_time),
                categoria: i.properties?.Fuente?.select?.name || 'Otro'
            }));
            
            const egresosProc = egresos.map(e => ({
                monto: e.properties?.Monto?.number || 0,
                fecha: new Date(e.properties?.Fecha?.date?.start || e.created_time),
                categoria: e.properties?.Categoría?.select?.name || 'Otro',
                tipo: e.properties?.Tipo?.select?.name || 'Fijo'
            }));
            
            const totalIng = ingresosProc.reduce((s, i) => s + i.monto, 0);
            const totalEgr = egresosProc.reduce((s, e) => s + e.monto, 0);
            const balance = totalIng - totalEgr;
            
            document.getElementById('netBalance').textContent = 
                (balance >= 0 ? '+' : '') + '$' + (balance / 1000000).toFixed(2) + 'M';
            document.getElementById('netBalance').style.color = balance >= 0 ? '#34d399' : '#f87171';
            document.getElementById('totalIncome').textContent = '$' + (totalIng / 1000000).toFixed(2) + 'M';
            document.getElementById('totalExpense').textContent = '$' + (totalEgr / 1000000).toFixed(2) + 'M';
            
            renderMetrics(totalIng, totalEgr, balance, ingresosProc, egresosProc);
            renderCharts(ingresosProc, egresosProc);
            generateInsights(totalIng, totalEgr, egresosProc);
        }
        
        function renderMetrics(ing, egr, balance, ingresos, egresos) {
            const ratioAhorro = ing > 0 ? (balance / ing * 100) : 0;
            const gastoFijo = egresos.filter(e => e.tipo === 'Fijo').reduce((s, e) => s + e.monto, 0);
            const gastoVar = egr - gastoFijo;
            
            document.getElementById('metricsGrid').innerHTML = `
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">Ratio de Ahorro</span>
                        <span class="metric-trend ${ratioAhorro > 20 ? 'trend-up' : 'trend-down'}">
                            ${ratioAhorro > 20 ? 'Óptimo' : 'Bajo'}
                        </span>
                    </div>
                    <div class="metric-value ${ratioAhorro > 0 ? 'positive' : 'negative'}">
                        ${ratioAhorro.toFixed(1)}%
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">Gastos Fijos</span>
                        <span class="metric-trend trend-down">Mensual</span>
                    </div>
                    <div class="metric-value negative">
                        $${(gastoFijo / 1000000).toFixed(2)}M
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">Gastos Variables</span>
                        <span class="metric-trend trend-down">Controlable</span>
                    </div>
                    <div class="metric-value negative">
                        $${(gastoVar / 1000000).toFixed(2)}M
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-label">Runway (meses)</span>
                        <span class="metric-trend trend-up">Estimado</span>
                    </div>
                    <div class="metric-value positive">
                        ${balance > 0 ? Math.floor(balance / gastoFijo) : 0}
                    </div>
                </div>
            `;
        }
        
        function renderCharts(ingresos, egresos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            const gridColor = isDark ? '#2f2f2f' : '#e0e0e0';
            
            // Flujo de caja mensual
            const flujo = {};
            for (let i = 5; i >= 0; i--) {
                const fecha = new Date();
                fecha.setMonth(fecha.getMonth() - i);
                const key = fecha.toLocaleDateString('es', { month: 'short' });
                flujo[key] = { ingresos: 0, egresos: 0 };
            }
            
            ingresos.forEach(i => {
                const key = i.fecha.toLocaleDateString('es', { month: 'short' });
                if (flujo[key]) flujo[key].ingresos += i.monto;
            });
            
            egresos.forEach(e => {
                const key = e.fecha.toLocaleDateString('es', { month: 'short' });
                if (flujo[key]) flujo[key].egresos += e.monto;
            });
            
            new Chart(document.getElementById('cashflowChart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(flujo),
                    datasets: [{
                        label: 'Ingresos',
                        data: Object.values(flujo).map(f => f.ingresos),
                        backgroundColor: '#10b981',
                        borderRadius: 4
                    }, {
                        label: 'Egresos',
                        data: Object.values(flujo).map(f => f.egresos),
                        backgroundColor: '#ef4444',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: textColor } } },
                    scales: {
                        y: { 
                            grid: { color: gridColor }, 
                            ticks: { 
                                color: textColor,
                                callback: v => '$' + (v / 1000) + 'K'
                            } 
                        },
                        x: { grid: { display: false }, ticks: { color: textColor } }
                    }
                }
            });
            
            // Composición (donut)
            const totalIng = ingresos.reduce((s, i) => s + i.monto, 0);
            const totalEgr = egresos.reduce((s, e) => s + e.monto, 0);
            const ahorro = Math.max(0, totalIng - totalEgr);
            
            new Chart(document.getElementById('compositionChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Gastos', 'Ahorro/Inversión'],
                    datasets: [{
                        data: [totalEgr, ahorro],
                        backgroundColor: ['#ef4444', '#10b981'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: { position: 'bottom', labels: { color: textColor } }
                    }
                }
            });
        }
        
        function generateInsights(ing, egr, egresos) {
            const insights = [];
            const ratio = ing > 0 ? ((ing - egr) / ing * 100) : 0;
            
            if (ratio < 10) {
                insights.push('🚨 <strong>Alerta de ahorro:</strong> Tu ratio está por debajo del 10% recomendado. Revisa gastos no esenciales.');
            } else if (ratio > 30) {
                insights.push('🌟 <strong>Excelente disciplina:</strong> Estás ahorrando el ' + ratio.toFixed(0) + '% de tus ingresos.');
            }
            
            const gastoHormiga = egresos.filter(e => e.monto < 20000).reduce((s, e) => s + e.monto, 0);
            if (gastoHormiga > ing * 0.1) {
                insights.push('🐜 <strong>Gasto hormiga detectado:</strong> $' + (gastoHormiga / 1000).toFixed(0) + 'K en pequeñas compras (>10% de ingresos).');
            }
            
            const mayorCategoria = {};
            egresos.forEach(e => {
                mayorCategoria[e.categoria] = (mayorCategoria[e.categoria] || 0) + e.monto;
            });
            const catMayor = Object.entries(mayorCategoria).sort((a, b) => b[1] - a[1])[0];
            if (catMayor && catMayor[1] > egr * 0.4) {
                insights.push('📊 <strong>Concentración de gastos:</strong> ' + catMayor[0] + ' representa el ' + ((catMayor[1]/egr)*100).toFixed(0) + '% de tus egresos.');
            }
            
            if (insights.length === 0) {
                insights.push('✅ <strong>Balance saludable:</strong> Tus finanzas están en rango óptimo. Mantén el seguimiento.');
            }
            
            document.getElementById('insightsList').innerHTML = insights.map(i => 
                `<div class="insight-item">${i}</div>`
            ).join('');
        }
        
        loadData();