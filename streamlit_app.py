import streamlit as st
import json
import random
import os

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
DATA_FILE = "usuarios.json"
CLAVE_PADRES = "admin123"

# ------------------------------
# CARGAR / GUARDAR USUARIOS
# ------------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def cargar_usuarios():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(DATA_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

# ------------------------------
# FUNCIONES ECONÓMICAS
# ------------------------------
def invertir(usuario, tipo, monto, usuarios):
    saldo = usuarios[usuario]['saldo']
    historial = usuarios[usuario]['historial']

    if tipo == "Segura":
        comision = 0.5
        prob = 80
        ganancia_fija = 0.2 * monto
    elif tipo == "Media":
        comision = 1
        prob = 60
        ganancia_fija = 0.5 * monto
    elif tipo == "Arriesgada":
        comision = 1.5
        prob = 30
        ganancia_fija = monto
    else:
        return "Tipo de inversión inválido"

    total_coste = monto + comision
    if saldo < total_coste:
        return "Saldo insuficiente para cubrir inversión y comisión"

    resultado = random.randint(1, 100)
    usuarios[usuario]['saldo'] -= total_coste

    if resultado <= prob:
        ganancia = ganancia_fija
        usuarios[usuario]['saldo'] += monto + ganancia
        resultado_texto = f"Ganaste ${ganancia:.2f}"
    else:
        ganancia = -monto
        resultado_texto = f"Perdiste tu inversión de ${monto}"

    historial.append({
        "tipo": "Inversión",
        "detalle": f"{tipo} (Comisión: ${comision})",
        "monto": monto,
        "resultado": resultado_texto,
        "saldo_resultante": usuarios[usuario]['saldo']
    })

    guardar_usuarios(usuarios)
    return resultado_texto

def depositar(usuario, monto, clave_padre, usuarios):
    if clave_padre != CLAVE_PADRES:
        return "Clave de padres incorrecta"
    usuarios[usuario]['saldo'] += monto
    usuarios[usuario]['historial'].append({
        "tipo": "Depósito",
        "detalle": "Padres",
        "monto": monto,
        "resultado": f"+${monto}",
        "saldo_resultante": usuarios[usuario]['saldo']
    })
    guardar_usuarios(usuarios)
    return f"Depósito exitoso de ${monto}"

def retirar(usuario, monto, clave_padre, usuarios):
    if clave_padre != CLAVE_PADRES:
        return "Clave de padres incorrecta"
    if usuarios[usuario]['saldo'] < monto:
        return "Saldo insuficiente"
    usuarios[usuario]['saldo'] -= monto
    usuarios[usuario]['historial'].append({
        "tipo": "Retiro",
        "detalle": "Padres",
        "monto": monto,
        "resultado": f"-${monto}",
        "saldo_resultante": usuarios[usuario]['saldo']
    })
    guardar_usuarios(usuarios)
    return f"Retiro exitoso de ${monto}"

def eliminar_cuenta(usuario_borrar, clave_padre, usuarios):
    if clave_padre != CLAVE_PADRES:
        return "Clave de padres incorrecta"
    if usuario_borrar not in usuarios:
        return "Usuario no encontrado"
    del usuarios[usuario_borrar]
    guardar_usuarios(usuarios)
    return f"Cuenta '{usuario_borrar}' eliminada con éxito"

# ------------------------------
# INICIO STREAMLIT
# ------------------------------
st.set_page_config(page_title="Simulador Económico", page_icon="💰")
st.title("💰 Simulador Económico Interactivo")

usuarios = cargar_usuarios()

# ------------------------------
# SESIÓN
# ------------------------------
if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

# ------------------------------
# OPCIONES INICIALES
# ------------------------------
opcion = st.sidebar.selectbox("Opciones", ["Crear cuenta", "Iniciar sesión", "Eliminar cuenta"])

# ------------------------------
# CREAR CUENTA
# ------------------------------
if opcion == "Crear cuenta":
    st.subheader("📝 Crear cuenta")
    nuevo_usuario = st.text_input("Nombre de usuario")
    nueva_clave = st.text_input("Contraseña", type="password")
    if st.button("Crear"):
        if nuevo_usuario in usuarios:
            st.error("Ese usuario ya existe.")
        else:
            usuarios[nuevo_usuario] = {
                "clave": nueva_clave,
                "saldo": 100,
                "historial": []
            }
            guardar_usuarios(usuarios)
            st.success("¡Cuenta creada! Tienes $100 iniciales.")

# ------------------------------
# ELIMINAR CUENTA
# ------------------------------
elif opcion == "Eliminar cuenta":
    st.subheader("🗑️ Eliminar cuenta")
    usuario_borrar = st.text_input("Nombre de la cuenta")
    clave_admin = st.text_input("Clave de padres", type="password")
    if st.button("Eliminar cuenta"):
        resultado = eliminar_cuenta(usuario_borrar, clave_admin, usuarios)
        st.info(resultado)

# ------------------------------
# INICIAR SESIÓN
# ------------------------------
elif opcion == "Iniciar sesión" and not st.session_state['usuario_logueado']:
    st.subheader("🔐 Iniciar sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if usuario not in usuarios:
            st.error("Usuario no encontrado.")
        elif usuarios[usuario]['clave'] != clave:
            st.error("Contraseña incorrecta.")
        else:
            st.session_state['usuario_logueado'] = usuario
            st.experimental_rerun()

# ------------------------------
# SESIÓN INICIADA
# ------------------------------
elif st.session_state['usuario_logueado']:
    usuario = st.session_state['usuario_logueado']
    st.success(f"Bienvenido, {usuario}")
    st.write(f"💵 Saldo actual: **${usuarios[usuario]['saldo']:.2f}**")

    # --- Inversión ---
    st.write("### 📈 Inversión")
    tipo = st.selectbox("Tipo de inversión", ["Segura", "Media", "Arriesgada"])
    monto = st.number_input("¿Cuánto deseas invertir?", min_value=1.0, step=1.0)
    if st.button("Hacer inversión"):
        resultado = invertir(usuario, tipo, monto, usuarios)
        st.info(resultado)
        st.write(f"Saldo después: **${usuarios[usuario]['saldo']:.2f}**")

    # --- Depósito ---
    st.write("### ➕ Depósito (requiere clave de padres)")
    monto_dep = st.number_input("Cantidad a depositar", min_value=1, step=1, key="dep")
    clave_dep = st.text_input("Clave de padres para depósito", type="password", key="clave_dep")
    if st.button("Depositar"):
        resultado = depositar(usuario, monto_dep, clave_dep, usuarios)
        st.info(resultado)

    # --- Retiro ---
    st.write("### ➖ Retiro (requiere clave de padres)")
    monto_ret = st.number_input("Cantidad a retirar", min_value=1, step=1, key="ret")
    clave_ret = st.text_input("Clave de padres para retiro", type="password", key="clave_ret")
    if st.button("Retirar"):
        resultado = retirar(usuario, monto_ret, clave_ret, usuarios)
        st.info(resultado)

    # --- Historial ---
    st.write("### 📜 Historial de movimientos")
    for mov in reversed(usuarios[usuario]['historial']):
        st.write(f"- [{mov['tipo']}] {mov['detalle']} | Monto: ${mov['monto']} | Resultado: {mov['resultado']} | Saldo: ${mov['saldo_resultante']:.2f}")

    # --- Cerrar sesión ---
    if st.button("🔓 Cerrar sesión"):
        st.session_state['usuario_logueado'] = None
        st.experimental_rerun()
