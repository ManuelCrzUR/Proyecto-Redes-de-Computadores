// Configurar IP del servidor — cambiar según la IP local del escritorio
const SERVER = "http://127.0.0.1:8000";

// Cargar datos al iniciar
loadRules();
loadNodes();
loadEvents();

// Polling cada 5 segundos
setInterval(loadRules, 5000);
setInterval(loadNodes, 5000);
setInterval(loadEvents, 5000);
setInterval(checkServerStatus, 10000);

// Verificar estado del servidor
checkServerStatus();

async function checkServerStatus() {
    try {
        const res = await fetch(`${SERVER}/nodes`, { method: "GET" });
        document.getElementById("serverStatus").textContent = `✅ Conectado (${SERVER})`;
        document.getElementById("serverStatus").style.color = "#27ae60";
    } catch (e) {
        document.getElementById("serverStatus").textContent = `❌ Desconectado`;
        document.getElementById("serverStatus").style.color = "#e74c3c";
    }
}

async function loadRules() {
    try {
        const res = await fetch(`${SERVER}/rules`);
        const rules = await res.json();
        const tbody = document.querySelector("#rulesTable tbody");
        tbody.innerHTML = "";

        rules.forEach(rule => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${rule.id || "—"}</td>
                <td>${rule.src_ip || "—"}</td>
                <td>${rule.dst_ip || "—"}</td>
                <td>${rule.protocol || "—"}</td>
                <td>${rule.dst_port || "—"}</td>
                <td><span class="${rule.action}">${rule.action}</span></td>
                <td>${rule.priority}</td>
                <td>${rule.description || "—"}</td>
                <td><button class="delete" onclick="deleteRule('${rule.id}')">Eliminar</button></td>
            `;
        });
    } catch (e) {
        console.error("Error cargando reglas:", e);
    }
}

async function loadNodes() {
    try {
        const res = await fetch(`${SERVER}/nodes`);
        const nodes = await res.json();
        const tbody = document.querySelector("#nodesTable tbody");
        tbody.innerHTML = "";

        nodes.forEach(node => {
            const row = tbody.insertRow();
            const lastSeen = node.last_seen ? new Date(node.last_seen).toLocaleTimeString() : "—";
            row.innerHTML = `
                <td><strong>${node.name}</strong></td>
                <td>${node.ip}</td>
                <td>${node.listen_port}</td>
                <td>${lastSeen}</td>
            `;
        });

        if (nodes.length === 0) {
            const row = tbody.insertRow();
            row.innerHTML = `<td colspan="4" style="text-align: center; color: #999;">Sin nodos registrados</td>`;
        }
    } catch (e) {
        console.error("Error cargando nodos:", e);
    }
}

async function loadEvents() {
    try {
        const res = await fetch(`${SERVER}/events`);
        const events = await res.json();
        const tbody = document.querySelector("#eventsTable tbody");
        tbody.innerHTML = "";

        events.reverse().forEach(event => {
            const row = tbody.insertRow();
            const timestamp = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : "—";
            row.innerHTML = `
                <td>${timestamp}</td>
                <td>${event.node_name}</td>
                <td>${event.src_ip}</td>
                <td>${event.protocol}</td>
                <td>${event.port}</td>
                <td><span class="${event.action}">${event.action}</span></td>
            `;
        });

        if (events.length === 0) {
            const row = tbody.insertRow();
            row.innerHTML = `<td colspan="6" style="text-align: center; color: #999;">Sin eventos registrados</td>`;
        }
    } catch (e) {
        console.error("Error cargando eventos:", e);
    }
}

async function addRule() {
    const rule = {
        src_ip: document.getElementById("ruleSrc").value || null,
        dst_ip: document.getElementById("ruleDst").value || null,
        protocol: document.getElementById("ruleProto").value || null,
        src_port: null,
        dst_port: parseInt(document.getElementById("ruleDstPort").value) || null,
        action: document.getElementById("ruleAction").value,
        priority: parseInt(document.getElementById("rulePriority").value),
        description: document.getElementById("ruleDesc").value,
    };

    try {
        const res = await fetch(`${SERVER}/rules`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(rule),
        });

        if (res.ok) {
            alert("✅ Regla creada");
            document.getElementById("ruleSrc").value = "";
            document.getElementById("ruleDst").value = "";
            document.getElementById("ruleProto").value = "";
            document.getElementById("ruleDstPort").value = "";
            document.getElementById("ruleAction").value = "allow";
            document.getElementById("rulePriority").value = "10";
            document.getElementById("ruleDesc").value = "";
            loadRules();
        } else {
            alert("❌ Error creando regla");
        }
    } catch (e) {
        console.error("Error:", e);
        alert("❌ Error conectando al servidor");
    }
}

async function deleteRule(ruleId) {
    if (!confirm("¿Eliminar esta regla?")) return;

    try {
        const res = await fetch(`${SERVER}/rules/${ruleId}`, { method: "DELETE" });

        if (res.ok) {
            alert("✅ Regla eliminada");
            loadRules();
        } else {
            alert("❌ Error eliminando regla");
        }
    } catch (e) {
        console.error("Error:", e);
        alert("❌ Error conectando al servidor");
    }
}

async function clearEvents() {
    if (!confirm("¿Limpiar todos los eventos?")) return;

    try {
        // Nota: Este endpoint no existe en el servidor, pero puede agregarse si es necesario
        alert("Función de limpiar eventos no implementada en el servidor");
    } catch (e) {
        console.error("Error:", e);
    }
}
