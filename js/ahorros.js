async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                
                document.getElementById('lastUpdate').textContent = 
                    data.metadata?.ultima_actualizacion || 'Desconocida';
                
                // Intentar obtener de diferentes estructuras posibles
                const ahorros = data.datos?.ahorros || data.ahorros || [];
                const ingresos = data.datos?.ingresos || data.ingresos || [];
                
                // Si no hay ahorros específicos, simular desde ingresos con categoría "Ahorro"
                if (ahorros.length === 0 && ingresos.length > 0) {
                    const simulated = ingresos.filter(i => {
                        const cat = i.properties?.Categoría?.select?.name || '';
                        return cat.toLowerCase().includes('ahorro') || 
                               cat.toLowerCase().includes('inversión') ||
                               cat.toLowerCase().includes('fondo');
                    });
                    processSavings(simulated, true);
                } else {
                    processSavings(ahorros, false);
                }
            } catch (error) {
                document.getElementById('fundsGrid').innerHTML = 
                    `<div style="color: #ef4444;">Error: ${error.message}</div>`;
            }
        }
        
        function processSavings(ahorros, isSimulated) {
            const processed = ahorros.map(a => {
                const props = a.properties || {};
                return {
                    nombre: props.Nombre?.title?.[0]?.plain_text || 
                            props.Fuente?.select?.name || 'Fondo',
                    monto: props.Monto?.number || props.Cantidad?.number || 0,
                    meta: props.Meta?.number || props.Objetivo?.number || 0,
                    tipo: props.Tipo?.select?.name || 'General',
                    fecha: new Date(props.Fecha?.date?.start || a.created_time)
                };
            });
            
            // Agrupar por nombre si es necesario
            const agrupados = {};
            processed.forEach(p => {
                if (!agrupados[p.nombre]) {
                    agrupados[p.nombre] = { ...p, monto: 0 };
                }
                agrupados[p.nombre].monto += p.monto;
            });
            
            const fondos = Object.values(agrupados);
            renderSummary(fondos);
            renderAllocation(fondos);
            renderFunds(fondos);
            renderEvolution(processed);
        }
        
        function renderSummary(fondos) {
            const total = fondos.reduce((s, f) => s + f.monto, 0);
            document.getElementById('totalSavings').textContent = 
                '$' + (total / 1000000).toFixed(2) + 'M';
            document.getElementById('fundCount').textContent = fondos.length;
        }
        
        function renderAllocation(fondos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            
            const labels = fondos.map(f => f.nombre);
            const data = fondos.map(f => f.monto);
            const colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];
            
            new Chart(document.getElementById('allocationChart'), {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: isDark ? '#202020' : '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '60%',
                    plugins: {
                        legend: { 
                            position: 'right',
                            labels: { 
                                color: textColor,
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    return data.labels.map((label, i) => ({
                                        text: `${label}: ${((data.datasets[0].data[i] / total) * 100).toFixed(1)}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        hidden: false,
                                        index: i
                                    }));
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function renderFunds(fondos) {
            const colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];
            
            document.getElementById('fundsGrid').innerHTML = fondos.map((f, i) => {
                const pct = f.meta ? Math.min((f.monto / f.meta) * 100, 100) : 0;
                const color = colors[i % colors.length];
                
                return `
                    <div class="fund-card">
                        <div class="fund-header">
                            <div class="fund-name">${f.nombre}</div>
                            <div class="fund-type">${f.tipo}</div>
                        </div>
                        <div class="fund-amount">$${f.monto.toLocaleString()}</div>
                        ${f.meta ? `
                            <div class="fund-goal">Meta: $${f.meta.toLocaleString()}</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${pct}%; background: ${color};"></div>
                            </div>
                            <div class="progress-text">
                                <span>${pct.toFixed(1)}% completado</span>
                                <span>Restante: $${(f.meta - f.monto).toLocaleString()}</span>
                            </div>
                        ` : '<div class="fund-goal">Sin meta definida</div>'}
                    </div>
                `;
            }).join('');
        }
        
        function renderEvolution(ahorros) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            const gridColor = isDark ? '#2f2f2f' : '#e0e0e0';
            
            // Agrupar por mes
            const porMes = {};
            ahorros.sort((a, b) => a.fecha - b.fecha).forEach(a => {
                const key = a.fecha.toLocaleDateString('es', { month: 'short', year: '2-digit' });
                porMes[key] = (porMes[key] || 0) + a.monto;
            });
            
            // Calcular acumulado
            let acumulado = 0;
            const acumuladoData = Object.values(porMes).map(v => {
                acumulado += v;
                return acumulado;
            });
            
            new Chart(document.getElementById('evolutionChart'), {
                type: 'line',
                data: {
                    labels: Object.keys(porMes),
                    datasets: [{
                        label: 'Ahorro Acumulado',
                        data: acumuladoData,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        fill: true,
                        tension: 0.4
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
                        x: { grid: { color: gridColor }, ticks: { color: textColor } }
                    }
                }
            });
        }
        
        loadData();