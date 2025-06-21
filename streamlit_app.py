import streamlit as st
import json
import random
import os

# ------------------------------
# Cargar o crear base de datos
# ------------------------------
DATA_FILE = "usuarios.json"

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
# Lógica de inversión
# ------------------------------
def invertir(usuario, tipo, usuarios):
    saldo = usuarios[usuario]['saldo']
    historial = usuarios[usuario]['historial']

    if tipo == "Segura":
        monto = 5
        if saldo < monto:
            return "Saldo insuficiente"
        usuarios[usuario]['saldo'] -= monto
        resultado = random.choices([1, 0], weights=[80, 20])[0]
        ganancia = 1 if resultado == 1 else 0

    elif tipo == "Media":
        monto = 10
        if saldo < monto:
            return "Saldo insuficiente"
        usuarios[usuario]['saldo'] -= monto
        resultado = random.choices(["ganar", "perder"], weights=[60, 40])[0]
        ganancia = 5 if resultado == "ganar" else -2

    elif tipo == "Arriesgada":
        monto = 15
        if saldo < monto:
            return "Saldo insuficiente"
        usuarios[usuario]['saldo'] -= monto
        resultado = random.choices(["ganar", "perder"], weights=[30, 70])[0]
        ganancia = 10 if resultado == "ganar" else -5

    usuarios[usuario]['saldo'] += max(ganancia, 0)
    historial.append({
        "tipo": tipo,
        "monto": monto,
        "ganancia": ganancia,
        "saldo_resultante": usuarios[usuario]['saldo']
    })

    guardar_usuarios(usuarios)

    return f"Inversión {tipo}: {'Ganaste' if ganancia >= 0 else 'Perdiste'} ${abs(ganancia)}"

# ------------------------------
# Interfaz Streamlit
# ------------------------------
st.title("💰 Simulador de Inversión Económica")

usuarios = cargar_usuarios()

opcion = st.sidebar.selectbox("Opciones", ["Crear cuenta", "Iniciar sesión"])

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
            st.success("Cuenta creada exitosamente. ¡Comienzas con $100!")

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
            st.write(f"💵 Tu saldo: **${usuarios[usuario]['saldo']}**")

            st.write("### 📈 Invertir tu dinero")
            tipo = st.selectbox("Selecciona tipo de inversión", ["Segura", "Media", "Arriesgada"])
            if st.button("Invertir"):
                resultado = invertir(usuario, tipo, usuarios)
                st.info(resultado)
                st.write(f"Saldo actualizado: **${usuarios[usuario]['saldo']}**")

            st.write("### 📜 Historial de inversiones")
            for h in usuarios[usuario]['historial']:
                st.write(f"- Tipo: {h['tipo']} | Inversión: ${h['monto']} | Resultado: ${h['ganancia']} | Saldo tras inversión: ${h['saldo_resultante']}")
