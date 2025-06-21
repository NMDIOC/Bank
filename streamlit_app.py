import streamlit as st
import json
import random
import os

# ------------------------------
# Configuración
# ------------------------------
DATA_FILE = "usuarios.json"
CLAVE_PADRES = "admin123"  # Cambia esta clave como quieras

# ------------------------------
# Base de datos
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
# Inversión con comisión
# ------------------------------
def invertir(usuario, tipo, usuarios):
    saldo = usuarios[usuario]['saldo']
    historial = usuarios[usuario]['historial']

    if tipo == "Segura":
        monto = 5
        comision = 0.5
        resultado = random.choices([1, 0], weights=[80, 20])[0]
        ganancia = 1 if resultado == 1 else 0
    elif tipo == "Media":
        monto = 10
        comision = 1
        resultado = random.choices(["ganar", "perder"], weights=[60, 40])[0]
        ganancia = 5 if resultado == "ganar" else -2
    elif tipo == "Arriesgada":
        monto = 15
        comision = 1.5
        resultado = random.choices(["ganar", "perder"], weights=[30, 70])[0]
        ganancia = 10 if resultado == "ganar" else -5
    else:
        return "Tipo de inversión inválido"

    total_coste = monto + comision
    if saldo < total_coste:
        return "Saldo insuficiente (se necesita cubrir comisión también)"

    usuarios[usuario]['saldo'] -= total_coste
    usuarios[usuario]['saldo'] += max(ganancia, 0)

    historial.append({
        "tipo": "Inversión",
        "detalle": f"{tipo} (Comisión: ${comision})",
        "monto": monto,
        "resultado": ganancia,
        "saldo_resultante": usuarios[usuario]['saldo']
    })

    guardar_usuarios(usuarios)

    return f"Inversión {tipo}: {'Ganaste' if ganancia >= 0 else 'Perdiste'} ${abs(ganancia)} (Comisión: ${comision})"

# ------------------------------
# Depósito y Retiro
# ------------------------------
def depositar(usuario, monto, clave_padre, usuarios):
    if clave_padre != CLAVE_PADRES:
        return "Contraseña de padres incorrecta"
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
        return "Contraseña de padres incorrecta"
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

# ------------------------------
# Eliminar cuenta
# ------------------------------
def eliminar_cuenta(usuario_a_borrar, clave_padre, usuarios):
    if clave_padre != CLAVE_PADRES:
        return "Contraseña de padres incorrecta"
    if usuario_a_borrar not in usuarios:
        return "Usuario no encontrado"
    del usuarios[usuario_a_borrar]
    guardar_usuarios(usuarios)
    return f"Cuenta '{usuario_a_borrar}' eliminada con éxito."

# ------------------------------
# Interfaz principal
# ------------------------------
st.title("💰 Simulador Económico Interactivo")

usuarios = cargar_usuarios()

opcion = st.sidebar.selectbox("Opciones", ["Crear cuenta", "Iniciar sesión", "Eliminar cuenta"])

if opcion == "Crear cuenta":
    st.subheader("📝 Crear nueva cuenta")
    nuevo_usuario = st.text_input("Nombre de usuario")
    nueva_clave = st.text_input("Contraseña", type="password")
    if st.button("Crear cuenta"):
        if nuevo_usuario in usuarios:
            st.error("Ese usuario ya existe.")
        else:
            usuarios[nuevo_usuario] = {
                "clave": nueva_clave,
                "saldo": 100,
                "historial": []
            }
            guardar_usuarios(usuarios)
            st.success("Cuenta creada. ¡Comienzas con $100!")

elif opcion == "Eliminar cuenta":
    st.subheader("🗑️ Eliminar cuenta")
    usuario_borrar = st.text_input("Nombre de cuenta a eliminar")
    clave_admin = st.text_input("Contraseña de padres", type="password")
    if st.button("Eliminar"):
        resultado = eliminar_cuenta(usuario_borrar, clave_admin, usuarios)
        if "éxito" in resultado:
            st.success(resultado)
        else:
            st.error(resultado)

elif opcion == "Iniciar sesión":
    st.subheader("🔐 Iniciar sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if usuario not in usuarios:
            st.error("Usuario no encontrado.")
        elif usuarios[usuario]['clave'] != clave:
            st.error("Contraseña incorrecta.")
        else:
            st.success(f"Bienvenido, {usuario}")
            st.write(f"💵 Tu saldo actual: **${usuarios[usuario]['saldo']}**")

            st.write("### 📈 Invertir dinero")
            tipo = st.selectbox("Tipo de inversión", ["Segura", "Media", "Arriesgada"])
            if st.button("Invertir"):
                resultado = invertir(usuario, tipo, usuarios)
                st.info(resultado)
                st.write(f"Saldo nuevo: **${usuarios[usuario]['saldo']}**")

            st.write("### ➕ Depósito (requiere clave de padres)")
            deposito = st.number_input("Cantidad a depositar", min_value=1, step=1)
            clave_dep = st.text_input("Clave de padres para depósito", type="password")
            if st.button("Depositar"):
                resultado = depositar(usuario, deposito, clave_dep, usuarios)
                st.info(resultado)

            st.write("### ➖ Retiro (requiere clave de padres)")
            retiro = st.number_input("Cantidad a retirar", min_value=1, step=1, key="retiro")
            clave_ret = st.text_input("Clave de padres para retiro", type="password")
            if st.button("Retirar"):
                resultado = retirar(usuario, retiro, clave_ret, usuarios)
                st.info(resultado)

            st.write("### 📜 Historial completo")
            historial = usuarios[usuario]['historial']
            if historial:
                for h in reversed(historial):
                    st.write(f"- [{h['tipo']}] {h['detalle']} | Monto: ${h['monto']} | Resultado: {h['resultado']} | Saldo: ${h['saldo_resultante']}")
            else:
                st.info("Aún no hay movimientos.")
