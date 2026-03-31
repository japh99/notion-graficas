async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                // NOMBRES EXACTOS: Minutos totales (formula/number), Hora de despertar (date)
                const suenos = data.datos?.sueno || data.sueno || [];
                processSleep(suenos);
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<div style="color: var(--accent);">Error: ${error.message}</div>`;
            }
        }

        function processSleep(suenos) {
            const processed = suenos.map(s => {
                const props = s.properties || {};
                
                // Buscar columna de minutos (puede ser formula o number)
                const minutos = props.Minutos_totales?.formula?.number || 
                               props.Minutos_totales?.number || 
                               props.Minutos?.number || 0;
                
                // Hora de despertar
                const horaDespertar = props.Hora_de_despertar?.date?.start || 
                                     props.Hora_despertar?.date?.start;
                
                return {
                    minutos: minutos,
                    horas: minutos / 60,
                    horaDespertar: horaDespertar ? new Date(horaDespertar) : null,
                    fecha: new Date(s.created_time)
                };
            }).slice(-7); // Últimos 7 días

            const promedioHoras = processed.reduce((s, r) => s + r.horas, 0) / processed.length || 0;
            const totalMinutos = processed.reduce((s, r) => s + r.minutos, 0);
            
            // Calcular calidad (8h = 100%)
            const calidad = Math.min((promedioHoras / 8) * 100, 100);

            document.getElementById('avgSleep').textContent = promedioHoras.toFixed(1) + 'h';
            
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${calidad.toFixed(0)}%</div>
                    <div class="stat-label">Calidad de Sueño</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${processed.length}</div>
                    <div class="stat-label">Noches Registradas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(totalMinutos / 60).toFixed(1)}h</div>
                    <div class="stat-label">Total Semanal</div>
                </div>
            `;

            renderChart(processed);
        }

        function renderChart(suenos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            const gridColor = isDark ? '#2f2f2f' : '#e0e0e0';

            new Chart(document.getElementById('sleepChart'), {
                type: 'line',
                data: {
                    labels: suenos.map(s => s.fecha.toLocaleDateString('es', { weekday: 'short' })),
                    datasets: [{
                        label: 'Minutos de sueño',
                        data: suenos.map(s => s.minutos),
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }, {
                        label: 'Meta (480min = 8h)',
                        data: suenos.map(() => 480),
                        borderColor: '#10b981',
                        borderDash: [5, 5],
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: textColor } } },
                    scales: {
                        y: { grid: { color: gridColor }, ticks: { color: textColor } },
                        x: { grid: { color: gridColor }, ticks: { color: textColor } }
                    }
                }
            });
        }

        loadData();