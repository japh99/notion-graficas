async function loadData() {
            try {
                const response = await fetch('datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                // NOMBRES EXACTOS: Name (title), Tiempo (number), Tipo (select: "Enfoque" o "Descanso")
                const pomodoros = data.datos?.pomodoro || data.pomodoro || [];
                processPomodoros(pomodoros);
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<div style="color: var(--accent);">Error: ${error.message}</div>`;
            }
        }

        function processPomodoros(pomodoros) {
            const processed = pomodoros.map(p => {
                const props = p.properties || {};
                return {
                    // NOMBRES EXACTOS:
                    nombre: props.Name?.title?.[0]?.plain_text || 'Sesión',
                    tiempo: props.Tiempo?.number || 25,
                    tipo: props.Tipo?.select?.name || 'Enfoque' // "Enfoque" o "Descanso"
                };
            });

            const totalSesiones = processed.length;
            const tiempoTotal = processed.reduce((s, p) => s + p.tiempo, 0);
            const enfoque = processed.filter(p => p.tipo === 'Enfoque');
            const descanso = processed.filter(p => p.tipo === 'Descanso');
            const tiempoEnfoque = enfoque.reduce((s, p) => s + p.tiempo, 0);
            const tiempoDescanso = descanso.reduce((s, p) => s + p.tiempo, 0);

            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${totalSesiones}</div>
                    <div class="stat-label">Sesiones Totales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(tiempoTotal / 60).toFixed(1)}h</div>
                    <div class="stat-label">Tiempo Total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--accent);">${enfoque.length}</div>
                    <div class="stat-label">Enfoque</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--success);">${descanso.length}</div>
                    <div class="stat-label">Descanso</div>
                </div>
            `;

            renderCharts(processed, tiempoEnfoque, tiempoDescanso);
        }

        function renderCharts(pomodoros, tiempoEnfoque, tiempoDescanso) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';

            // Gráfico de tipos
            new Chart(document.getElementById('typeChart'), {
                type: 'pie',
                data: {
                    labels: ['Enfoque', 'Descanso'],
                    datasets: [{
                        data: [tiempoEnfoque, tiempoDescanso],
                        backgroundColor: ['#ef4444', '#10b981']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { color: textColor } } }
                }
            });

            // Gráfico de tiempo por sesión
            new Chart(document.getElementById('timeChart'), {
                type: 'bar',
                data: {
                    labels: pomodoros.slice(-10).map((p, i) => `#${i + 1}`),
                    datasets: [{
                        label: 'Minutos',
                        data: pomodoros.slice(-10).map(p => p.tiempo),
                        backgroundColor: pomodoros.slice(-10).map(p => p.tipo === 'Enfoque' ? '#ef4444' : '#10b981'),
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: isDark ? '#2f2f2f' : '#e0e0e0' }, ticks: { color: textColor } },
                        x: { grid: { display: false }, ticks: { color: textColor } }
                    }
                }
            });
        }

        loadData();