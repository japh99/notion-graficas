async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                const habitos = data.datos?.habitos || [];
                processHabitos(habitos);
            } catch (error) {
                document.getElementById('habitsGrid').innerHTML = `<div style="color: var(--accent);">Error: ${error.message}</div>`;
            }
        }

        function processHabitos(habitos) {
            // ESTRUCTURA REAL (checkboxes):
            // • Meditacion (checkbox) → true
            // • Leer (checkbox) → true
            // • No Azúcar (checkbox) → true
            // • Fecha (date) → "2026-03-03"
            // • Dormí 7-8h (checkbox) → true
            // • Ejercicio (checkbox) → true
            // • Agradecer (checkbox) → true
            // • Agua 2LT (checkbox) → true
            // • Ducha Fría (checkbox) → false
            // • Diario (title) → "Prueba"
            
            if (habitos.length === 0) {
                document.getElementById('habitsGrid').innerHTML = '<div class="loading">No hay datos de hábitos</div>';
                return;
            }

            // Tomar el registro más reciente
            const ultimo = habitos[habitos.length - 1];
            const p = ultimo.properties || {};

            // Mapeo de hábitos con iconos
            const habitosMap = [
                { key: 'Meditacion', nombre: 'Meditación', icono: '🧘' },
                { key: 'Leer', nombre: 'Leer', icono: '📚' },
                { key: 'No Azúcar', nombre: 'No Azúcar', icono: '🚫🍬' },
                { key: 'Dormí 7-8h', nombre: 'Dormí 7-8h', icono: '😴' },
                { key: 'Ejercicio', nombre: 'Ejercicio', icono: '💪' },
                { key: 'Agradecer', nombre: 'Agradecer', icono: '🙏' },
                { key: 'Agua 2LT', nombre: 'Agua 2LT', icono: '💧' },
                { key: 'Ducha Fría', nombre: 'Ducha Fría', icono: '🚿' }
            ];

            const datosHabitos = habitosMap.map(h => ({
                ...h,
                hecho: p[h.key]?.checkbox === true
            }));

            const completados = datosHabitos.filter(h => h.hecho).length;
            const tasa = (completados / datosHabitos.length) * 100;

            document.getElementById('completionRate').textContent = tasa.toFixed(0) + '%';

            renderRadar(datosHabitos);
            renderHabits(datosHabitos);
        }

        function renderRadar(habitos) {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const textColor = isDark ? '#ffffff' : '#2c2c2c';
            const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

            // Para el radar, usamos 100% si está hecho, 0% si no
            const dataValues = habitos.map(h => h.hecho ? 100 : 0);

            new Chart(document.getElementById('radarChart'), {
                type: 'radar',
                data: {
                    labels: habitos.map(h => h.nombre),
                    datasets: [{
                        label: 'Hoy',
                        data: dataValues,
                        backgroundColor: 'rgba(6, 182, 212, 0.2)',
                        borderColor: '#06b6d4',
                        pointBackgroundColor: '#06b6d4',
                        pointBorderColor: '#fff',
                        borderWidth: 2
                    }, {
                        label: 'Objetivo',
                        data: habitos.map(() => 100),
                        backgroundColor: 'transparent',
                        borderColor: 'rgba(148, 163, 184, 0.5)',
                        borderDash: [5, 5],
                        pointRadius: 0,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: gridColor },
                            angleLines: { color: gridColor },
                            pointLabels: { color: textColor, font: { size: 11 } },
                            ticks: { display: false }
                        }
                    }
                }
            });
        }

        function renderHabits(habitos) {
            document.getElementById('habitsGrid').innerHTML = habitos.map(h => `
                <div class="habit-card">
                    <div class="habit-icon">${h.icono}</div>
                    <div class="habit-info">
                        <div class="habit-name">${h.nombre}</div>
                        <div class="habit-status ${h.hecho ? 'done' : ''}">${h.hecho ? '✅ Completado' : '⬜ Pendiente'}</div>
                    </div>
                </div>
            `).join('');
        }

        loadData();