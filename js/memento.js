async function loadData() {
            try {
                const response = await fetch('datos.json');
                const data = await response.json();
                
                const memento = data.datos?.memento || [];
                processMemento(memento);
            } catch (error) {
                document.getElementById('stats').innerHTML = `<div style="color: var(--accent); grid-column: 1/-1;">Error: ${error.message}</div>`;
            }
        }

        function processMemento(memento) {
            // ESTRUCTURA REAL:
            // • Nov (checkbox) → false
            // • Sep (checkbox) → false
            // • Año (number) → 80
            // • Mar (checkbox) → false
            // • % Avance Vida (formula) → 0.8
            // • Feb (checkbox) → false
            // • Progreso (formula)
            // • Total años (relation)
            // • Cuenta Regresiva (formula) → 20
            // • Abr (checkbox) → false
            // • Jul (checkbox) → false
            // • Oct (checkbox) → false
            // • Ene (checkbox) → false
            // • Dic (checkbox) → false
            // • May (checkbox) → false
            // • Ago (checkbox) → false
            // • Edad Actual (rollup) → 32
            // • Jun (checkbox) → false
            // • Años (title) → "80"

            if (memento.length === 0) {
                renderDefault();
                return;
            }

            // Buscar el registro del año actual (donde Año = 80 o el que corresponda)
            const registro = memento.find(m => {
                const props = m.properties || {};
                return props['Edad Actual']?.rollup?.number !== undefined;
            }) || memento[0];

            const p = registro.properties || {};
            
            const edadActual = p['Edad Actual']?.rollup?.number || 32;
            const añoEsperanza = p.Año?.number || 80;
            const cuentaRegresiva = p['Cuenta Regresiva']?.formula?.number || (añoEsperanza - edadActual);
            const porcentajeAvance = p['% Avance Vida']?.formula?.number || (edadActual / añoEsperanza);
            
            const añosRestantes = añoEsperanza - edadActual;
            const porcentaje = porcentajeAvance * 100;

            // Actualizar UI
            document.getElementById('lifeProgress').style.width = porcentaje + '%';
            document.getElementById('lifeProgress').textContent = porcentaje.toFixed(1) + '%';
            
            document.getElementById('edadActual').textContent = edadActual;
            document.getElementById('añosRestantes').textContent = añosRestantes;
            document.getElementById('cuentaRegresiva').textContent = cuentaRegresiva;

            // Renderizar meses vividos (checkboxes de meses)
            renderMonths(p);
            
            // Quote aleatorio
            const frases = [
                "El problema no es que la vida sea corta, sino que la desperdiciamos.",
                "No cuentes los años, sino las horas.",
                "Vive como si fueras a morir mañana. Aprende como si fueras a vivir para siempre.",
                "El tiempo es el único capital que los humanos tienen, y solo pueden perderlo.",
                "Memento mori: Recuerda que vas a morir."
            ];
            document.getElementById('quote').textContent = frases[Math.floor(Math.random() * frases.length)];
        }

        function renderMonths(props) {
            const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
            const hoy = new Date();
            const mesActual = hoy.getMonth(); // 0-11
            
            const html = meses.map((mes, idx) => {
                const checkbox = props[mes]?.checkbox;
                let clase = 'month-box';
                if (checkbox) clase += ' month-lived';
                if (idx === mesActual) clase += ' month-current';
                return `<div class="${clase}" title="${mes}"></div>`;
            }).join('');
            
            document.getElementById('monthsGrid').innerHTML = html;
        }

        function renderDefault() {
            document.getElementById('lifeProgress').style.width = '40%';
            document.getElementById('lifeProgress').textContent = '40%';
            document.getElementById('edadActual').textContent = '32';
            document.getElementById('añosRestantes').textContent = '48';
            document.getElementById('cuentaRegresiva').textContent = '20';
            document.getElementById('quote').textContent = 'Configura tu base de datos Memento Mori para datos precisos.';
        }

        loadData();