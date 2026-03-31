let allTasks = [];
        let showAll = false;

        async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                const tareas = data.datos?.tareas || [];
                processTareas(tareas);
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<div style="color: #ef4444;">Error: ${error.message}</div>`;
            }
        }

        function processTareas(tareas) {
            // ESTRUCTURA REAL:
            // • Fecha (date) → "2025-06-08T23:30:00.000-05:00"
            // • Planificada para días pasados (formula) → "⏰[PENDIENTE]"
            // • Proyectos (relation)
            // • En espera (checkbox) → false
            // • Hecho (checkbox) → true
            // • Nombre (title) → "Lavar los Dientes"
            
            allTasks = tareas.map(t => {
                const p = t.properties || {};
                return {
                    nombre: p.Nombre?.title?.[0]?.plain_text || 'Sin nombre',
                    hecho: p.Hecho?.checkbox === true,
                    enEspera: p['En espera']?.checkbox === true,
                    fecha: p.Fecha?.date?.start,
                    planificacion: p['Planificada para días pasados']?.formula?.string || ''
                };
            });

            const hechas = allTasks.filter(t => t.hecho).length;
            const enEspera = allTasks.filter(t => t.enEspera && !t.hecho).length;
            const pendientes = allTasks.length - hechas - enEspera;
            const progreso = allTasks.length ? (hechas / allTasks.length) * 100 : 0;

            document.getElementById('progressValue').textContent = progreso.toFixed(0) + '%';
            
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${allTasks.length}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value pending">${pendientes + enEspera}</div>
                    <div class="stat-label">Pendientes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value done">${hechas}</div>
                    <div class="stat-label">Completadas</div>
                </div>
            `;

            renderRing(progreso);
            renderList();
        }

        function renderRing(progreso) {
            const ctx = document.getElementById('progressChart').getContext('2d');
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Completado', 'Pendiente'],
                    datasets: [{
                        data: [progreso, 100 - progreso],
                        backgroundColor: ['#3b82f6', isDark ? '#2f2f2f' : '#e0e0e0'],
                        borderWidth: 0,
                        cutout: '85%'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: { enabled: false } }
                }
            });
        }

        function renderList() {
            const tasksToShow = showAll ? allTasks : allTasks.slice(0, 20);
            
            document.getElementById('taskList').innerHTML = tasksToShow.map(t => {
                let checkboxClass = 'pending';
                let checkContent = '';
                if (t.hecho) {
                    checkboxClass = 'done';
                    checkContent = '✓';
                } else if (t.enEspera) {
                    checkboxClass = 'waiting';
                }
                
                const dateStr = t.fecha ? new Date(t.fecha).toLocaleDateString('es') : '';
                
                return `
                    <div class="task-item">
                        <div class="task-checkbox ${checkboxClass}">${checkContent}</div>
                        <div class="task-name ${t.hecho ? 'done' : ''}">${t.nombre}</div>
                        <div class="task-date">${dateStr}</div>
                    </div>
                `;
            }).join('');
        }

        function toggleFilter() {
            showAll = !showAll;
            document.querySelector('.filter-btn').textContent = showAll ? 'Ver menos' : 'Ver todas';
            renderList();
        }

        loadData();