import streamlit as st
import json
import os
import random
from datetime import datetime

DB_FILE = "banco_virtual.json"

# Cargar base de datos
def cargar_datos():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Guardar base de datos
def guardar_datos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Crear cuenta
def crear_cuenta(data, usuario, contraseña):
    if usuario in data:
        return "❌ Usuario ya existe."
    data[usuario] = {
        "contraseña": contraseña,
        "saldo": 100,
        "ahorro": 0,
        "prestamo": 0,
        "historial": []
    }
    guardar_datos(data)
    return "✅ Cuenta creada con $100 de saldo inicial."

# Verificar usuario
def login(data, usuario, contraseña):
    if usuario in data and data[usuario]["contraseña"] == contraseña:
        return True
    return False

# Agregar al historial
def agregar_historial(data, usuario, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    data[usuario]["historial"].append(f"[{timestamp}] {mensaje}")
    guardar_datos(data)

# Invertir
def invertir(data, usuario, tipo, monto):
    saldo = data[usuario]["saldo"]
    if monto > saldo:
        return "❌ No tienes suficiente saldo."
    tipos = {
        "segura": (5, 0.8, 1, 0),
        "media": (10, 0.6, 5, -2),
        "arriesgada": (15, 0.3, 10, -5)
    }
    minimo, prob, ganancia, perdida = tipos[tipo]
    if monto < minimo:
        return f"❌ Inversión mínima: ${minimo}"

    data[usuario]["saldo"] -= monto
    if random.random() < prob:
        resultado = monto + ganancia
        data[usuario]["saldo"] += resultado
        agregar_historial(data, usuario, f"Inversión {tipo}: +${ganancia}")
        return f"🎉 Ganaste ${ganancia}. Nuevo saldo: ${data[usuario]['saldo']}"
    else:
        resultado = monto + perdida
        data[usuario]["saldo"] += resultado
        agregar_historial(data, usuario, f"Inversión {tipo}: ${perdida}")
        return f"😢 Mala suerte. Recuperaste ${resultado}. Saldo actual: ${data[usuario]['saldo']}"

# Ahorro semanal con interés
def aplicar_interes(data, usuario, tasa=0.02):
    ahorro = data[usuario]["ahorro"]
    ganancia = round(ahorro * tasa, 2)
    data[usuario]["ahorro"] += ganancia
    agregar_historial(data, usuario, f"Interés ganado en ahorro: +${ganancia}")
    guardar_datos(data)

# Comprar en tienda
def comprar(data, usuario, producto, precio):
    if data[usuario]["saldo"] >= precio:
        data[usuario]["saldo"] -= precio
        agregar_historial(data, usuario, f"Compró {producto} por ${precio}")
        guardar_datos(data)
        return f"✅ Compraste {producto}. Saldo restante: ${data[usuario]['saldo']}"
    return "❌ No tienes suficiente dinero."

# Pedir préstamo
def pedir_prestamo(data, usuario, monto, tasa=0.1):
    interes = round(monto * tasa, 2)
    total = monto + interes
    data[usuario]["saldo"] += monto
    data[usuario]["prestamo"] += total
    agregar_historial(data, usuario, f"Préstamo de ${monto}. Deberás pagar ${total}")
    guardar_datos(data)
    return f"✅ Recibiste ${monto}. Deuda total: ${total}"

# Pagar préstamo
def pagar_prestamo(data, usuario, pago):
    deuda = data[usuario]["prestamo"]
    if deuda == 0:
        return "🎉 No tienes deudas."
    if pago > data[usuario]["saldo"]:
        return "❌ No tienes suficiente saldo."
    pago_real = min(pago, deuda)
    data[usuario]["saldo"] -= pago_real
    data[usuario]["prestamo"] -= pago_real
    agregar_historial(data, usuario, f"Pagó préstamo: -${pago_real}")
    guardar_datos(data)
    return f"✅ Pagaste ${pago_real}. Deuda restante: ${data[usuario]['prestamo']}"

# App Streamlit
st.set_page_config(page_title="Banco Educativo", page_icon="🏦")
st.title("🏦 Banco Virtual Educativo")
data = cargar_datos()

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    tab1, tab2 = st.tabs(["🔐 Iniciar sesión", "🆕 Crear cuenta"])
    with tab1:
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if login(data, user, password):
                st.session_state.usuario = user
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

    with tab2:
        new_user = st.text_input("Nuevo usuario")
        new_pass = st.text_input("Nueva contraseña", type="password")
        if st.button("Crear cuenta"):
            msg = crear_cuenta(data, new_user, new_pass)
            st.success(msg)

else:
    st.success(f"Bienvenido, {st.session_state.usuario}")
    usuario = st.session_state.usuario
    saldo = data[usuario]["saldo"]
    ahorro = data[usuario]["ahorro"]
    prestamo = data[usuario]["prestamo"]

    st.subheader("💼 Tu información")
    st.write(f"**Saldo:** ${saldo}")
    st.write(f"**Ahorro:** ${ahorro}")
    st.write(f"**Deuda:** ${prestamo}")

    with st.expander("📥 Depositar al ahorro"):
        monto = st.number_input("¿Cuánto quieres mover de tu saldo al ahorro?", min_value=0.0)
        if st.button("Guardar"):
            if monto <= saldo:
                data[usuario]["saldo"] -= monto
                data[usuario]["ahorro"] += monto
                agregar_historial(data, usuario, f"Depositó ${monto} al ahorro")
                st.success("✅ Movimiento realizado.")
                st.experimental_rerun()
            else:
                st.error("❌ No tienes suficiente saldo.")

    with st.expander("📈 Invertir dinero"):
        tipo = st.selectbox("Tipo de inversión", ["segura", "media", "arriesgada"])
        monto = st.number_input("¿Cuánto invertir?", min_value=0.0)
        if st.button("Invertir"):
            resultado = invertir(data, usuario, tipo, monto)
            st.info(resultado)

    with st.expander("🛍️ Comprar en tienda"):
        productos = {"Juguete": 10, "Dulces": 5, "Pase especial": 15}
        prod = st.selectbox("Producto", list(productos.keys()))
        if st.button("Comprar"):
            msg = comprar(data, usuario, prod, productos[prod])
            st.info(msg)

    with st.expander("💳 Préstamo"):
        monto = st.number_input("¿Cuánto quieres pedir prestado?", min_value=0.0)
        if st.button("Solicitar préstamo"):
            msg = pedir_prestamo(data, usuario, monto)
            st.success(msg)

    with st.expander("💸 Pagar deuda"):
        pago = st.number_input("¿Cuánto pagar?", min_value=0.0)
        if st.button("Pagar préstamo"):
            msg = pagar_prestamo(data, usuario, pago)
            st.info(msg)

    with st.expander("📅 Aplicar interés a ahorro"):
        if st.button("Aplicar interés"):
            aplicar_interes(data, usuario)
            st.success("✅ Interés aplicado.")
            st.experimental_rerun()

    with st.expander("📜 Historial de transacciones"):
        historial = data[usuario]["historial"]
        for h in reversed(historial[-20:]):
            st.write(h)

    if st.button("🚪 Cerrar sesión"):
        st.session_state.usuario = None
        st.experimental_rerun()
