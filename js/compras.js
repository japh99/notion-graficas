async function loadData() {
            try {
                const response = await fetch('../data/datos.json');
                const data = await response.json();
                document.getElementById('lastUpdate').textContent = data.metadata?.ultima_actualizacion || 'Desconocida';
                
                // NOMBRES EXACTOS: Monto/Precio (number), Comprado/Hecho (checkbox)
                const compras = data.datos?.compras || data.compras || [];
                processPurchases(compras);
            } catch (error) {
                document.getElementById('statsGrid').innerHTML = `<div style="color: var(--accent);">Error: ${error.message}</div>`;
            }
        }

        function processPurchases(compras) {
            const processed = compras.map(c => {
                const props = c.properties || {};
                
                // Detectar nombre de columna (Precio o Monto)
                const monto = props.Precio?.number || props.Monto?.number || 0;
                // Detectar checkbox (Comprado o Hecho)
                const comprado = props.Comprado?.checkbox === true || props.Hecho?.checkbox === true;
                
                return {
                    nombre: props.Nombre?.title?.[0]?.plain_text || props.Items?.title?.[0]?.plain_text || 'Sin nombre',
                    monto: monto,
                    comprado: comprado
                };
            });

            const total = processed.reduce((s, c) => s + c.monto, 0);
            const comprados = processed.filter(c => c.comprado);
            const pendientes = processed.filter(c => !c.comprado);
            const totalComprado = comprados.reduce((s, c) => s + c.monto, 0);
            const totalPendiente = pendientes.reduce((s, c) => s + c.monto, 0);
            const progreso = total > 0 ? (totalComprado / total) * 100 : 0;

            // Actualizar termómetro
            document.getElementById('thermoFill').style.width = progreso + '%';
            document.getElementById('progressText').textContent = progreso.toFixed(1) + '%';
            document.getElementById('remainingText').textContent = '$' + (totalPendiente / 1000).toFixed(0) + 'K';

            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${processed.length}</div>
                    <div class="stat-label">Items Totales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--success);">${comprados.length}</div>
                    <div class="stat-label">Comprados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--accent);">${pendientes.length}</div>
                    <div class="stat-label">Pendientes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$${(total / 1000000).toFixed(2)}M</div>
                    <div class="stat-label">Valor Total</div>
                </div>
            `;

            renderLists(comprados, pendientes);
        }

        function renderLists(comprados, pendientes) {
            document.getElementById('compradosList').innerHTML = comprados.length ? comprados.map(c => `
                <div class="item">
                    <span class="item-name">${c.nombre}</span>
                    <span class="item-price item-comprado">$${c.monto.toLocaleString()}</span>
                </div>
            `).join('') : '<div style="color: var(--text-secondary); text-align: center;">Ninguno comprado aún</div>';

            document.getElementById('pendientesList').innerHTML = pendientes.length ? pendientes.map(c => `
                <div class="item">
                    <span class="item-name">${c.nombre}</span>
                    <span class="item-price item-pendiente">$${c.monto.toLocaleString()}</span>
                </div>
            `).join('') : '<div style="color: var(--text-secondary); text-align: center;">¡Todo comprado!</div>';
        }

        loadData();