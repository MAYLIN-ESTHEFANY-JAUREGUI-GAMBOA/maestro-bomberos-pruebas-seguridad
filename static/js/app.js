const formulario = document.getElementById("formBombero");
const mensaje = document.getElementById("mensaje");
const lista = document.getElementById("listaBomberos");
const busqueda = document.getElementById("busqueda");
const filtroEstado = document.getElementById("filtroEstado");
const btnGuardar = document.getElementById("btnGuardar");

let bomberos = [];
let idEnEdicion = null;

function mostrarMensaje(texto, tipo = "success") {
    mensaje.textContent = texto;
    mensaje.className = `notice notice-${tipo}`;
}

async function solicitar(url, opciones = {}) {
    const respuesta = await fetch(url, {
        ...opciones,
        headers: { ...(opciones.body ? { "Content-Type": "application/json" } : {}), ...opciones.headers },
    });
    const resultado = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok) {
        throw new Error(resultado.mensaje || "No fue posible completar la solicitud.");
    }
    return resultado;
}

function actualizarResumen() {
    const activos = bomberos.filter((bombero) => bombero.estado).length;
    document.getElementById("totalBomberos").textContent = bomberos.length;
    document.getElementById("activosBomberos").textContent = activos;
    document.getElementById("inactivosBomberos").textContent = bomberos.length - activos;
}

function crearCelda(texto, clase) {
    const celda = document.createElement("td");
    if (clase) celda.className = clase;
    celda.textContent = texto;
    return celda;
}

function crearBoton(etiqueta, icono, clase, accion) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = `icon-button ${clase || ""}`.trim();
    boton.setAttribute("aria-label", etiqueta);
    boton.title = etiqueta;
    boton.textContent = icono;
    boton.addEventListener("click", accion);
    return boton;
}

function renderizarLista() {
    const texto = busqueda.value.trim().toLocaleLowerCase("es");
    const estadoSeleccionado = filtroEstado.value;
    const filtrados = bomberos.filter((bombero) => {
        const coincideTexto = `${bombero.nombres} ${bombero.apellidos} ${bombero.dni}`.toLocaleLowerCase("es").includes(texto);
        const coincideEstado = estadoSeleccionado === "todos"
            || (estadoSeleccionado === "activo" && bombero.estado)
            || (estadoSeleccionado === "inactivo" && !bombero.estado);
        return coincideTexto && coincideEstado;
    });

    lista.replaceChildren();
    document.getElementById("contadorRegistros").textContent = `${filtrados.length} ${filtrados.length === 1 ? "registro" : "registros"}`;
    document.getElementById("resultadoBusqueda").textContent = filtrados.length === bomberos.length
        ? `Mostrando ${filtrados.length} registros`
        : `${filtrados.length} de ${bomberos.length} registros`;

    if (!filtrados.length) {
        const fila = document.createElement("tr");
        const celda = crearCelda(
            bomberos.length ? "No hay resultados para esta búsqueda." : "Aún no hay bomberos registrados.",
            "table-message",
        );
        celda.colSpan = 5;
        fila.appendChild(celda);
        lista.appendChild(fila);
        return;
    }

    filtrados.forEach((bombero) => {
        const fila = document.createElement("tr");
        const personal = document.createElement("td");
        const personCell = document.createElement("div");
        personCell.className = "person-cell";
        const avatar = document.createElement("span");
        avatar.className = "avatar";
        avatar.setAttribute("aria-hidden", "true");
        avatar.textContent = `${bombero.nombres[0] || ""}${bombero.apellidos[0] || ""}`.toLocaleUpperCase("es");
        const identidad = document.createElement("span");
        const nombre = document.createElement("span");
        nombre.className = "person-name";
        nombre.textContent = `${bombero.nombres} ${bombero.apellidos}`;
        const subtitulo = document.createElement("span");
        subtitulo.className = "person-label";
        subtitulo.textContent = "Personal operativo";
        identidad.append(nombre, subtitulo);
        personCell.append(avatar, identidad);
        personal.appendChild(personCell);

        const estado = document.createElement("span");
        estado.className = `status-tag ${bombero.estado ? "status-active" : "status-inactive"}`;
        estado.textContent = bombero.estado ? "Activo" : "Inactivo";
        const estadoCelda = document.createElement("td");
        estadoCelda.appendChild(estado);
        const acciones = document.createElement("td");
        const botones = document.createElement("div");
        botones.className = "actions";
        botones.append(
            crearBoton("Editar registro", "✎", "", () => iniciarEdicion(bombero)),
            crearBoton(
                bombero.estado ? "Desactivar bombero" : "Activar bombero",
                bombero.estado ? "◌" : "✓",
                "",
                () => cambiarEstado(bombero),
            ),
            crearBoton("Eliminar registro", "×", "danger", () => eliminarBombero(bombero)),
        );
        acciones.appendChild(botones);
        fila.append(
            personal,
            crearCelda(bombero.dni),
            (() => {
                const celda = document.createElement("td");
                const etiqueta = document.createElement("span");
                etiqueta.className = "specialty-tag";
                etiqueta.textContent = bombero.especialidad;
                celda.appendChild(etiqueta);
                return celda;
            })(),
            estadoCelda,
            acciones,
        );
        lista.appendChild(fila);
    });
}

async function cargarBomberos() {
    lista.replaceChildren();
    const fila = document.createElement("tr");
    const celda = crearCelda("Cargando directorio…", "table-message");
    celda.colSpan = 5;
    fila.appendChild(celda);
    lista.appendChild(fila);
    try {
        bomberos = await solicitar("/api/bomberos");
        actualizarResumen();
        renderizarLista();
    } catch (error) {
        const errorRow = document.createElement("tr");
        const errorCell = crearCelda(error.message, "table-message");
        errorCell.colSpan = 5;
        errorRow.appendChild(errorCell);
        lista.replaceChildren(errorRow);
        mostrarMensaje("No se pudo cargar el directorio. Verifica la conexión con el servidor.", "error");
    }
}

function iniciarEdicion(bombero) {
    idEnEdicion = bombero.id;
    document.getElementById("dni").value = bombero.dni;
    document.getElementById("nombres").value = bombero.nombres;
    document.getElementById("apellidos").value = bombero.apellidos;
    document.getElementById("especialidad").value = bombero.especialidad;
    document.getElementById("tituloFormulario").textContent = "Editar bombero";
    document.getElementById("textoBoton").textContent = "Guardar cambios";
    document.getElementById("btnCancelar").classList.remove("hidden");
    mensaje.className = "notice hidden";
    document.getElementById("dni").focus();
    document.querySelector(".form-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function cancelarEdicion() {
    idEnEdicion = null;
    formulario.reset();
    document.getElementById("tituloFormulario").textContent = "Registrar bombero";
    document.getElementById("textoBoton").textContent = "Registrar bombero";
    document.getElementById("btnCancelar").classList.add("hidden");
    mensaje.className = "notice hidden";
}

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (!formulario.reportValidity()) return;

    const datos = {
        dni: document.getElementById("dni").value.trim(),
        nombres: document.getElementById("nombres").value.trim(),
        apellidos: document.getElementById("apellidos").value.trim(),
        especialidad: document.getElementById("especialidad").value,
    };
    btnGuardar.disabled = true;
    try {
        const id = idEnEdicion;
        const resultado = await solicitar(id ? `/api/bomberos/${id}` : "/api/bomberos", {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(datos),
        });
        cancelarEdicion();
        mostrarMensaje(resultado.mensaje);
        await cargarBomberos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    } finally {
        btnGuardar.disabled = false;
    }
});

async function cambiarEstado(bombero) {
    try {
        const resultado = await solicitar(`/api/bomberos/${bombero.id}/estado`, {
            method: "PATCH",
            body: JSON.stringify({ estado: !bombero.estado }),
        });
        mostrarMensaje(resultado.mensaje);
        await cargarBomberos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function eliminarBombero(bombero) {
    if (!window.confirm(`¿Eliminar el registro de ${bombero.nombres} ${bombero.apellidos}? Esta acción no se puede deshacer.`)) return;
    try {
        const resultado = await solicitar(`/api/bomberos/${bombero.id}`, { method: "DELETE" });
        if (idEnEdicion === bombero.id) cancelarEdicion();
        mostrarMensaje(resultado.mensaje);
        await cargarBomberos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

busqueda.addEventListener("input", renderizarLista);
filtroEstado.addEventListener("change", renderizarLista);
document.getElementById("btnCancelar").addEventListener("click", cancelarEdicion);
document.getElementById("btnActualizar").addEventListener("click", cargarBomberos);
cargarBomberos();
