# ----- SESIÓN INICIADA -----
if 'usuario_logueado' not in st.session_state:
    st.session_state['usuario_logueado'] = None

elif st.session_state['usuario_logueado']:
    usuario = st.session_state['usuario_logueado']
    st.success(f"Bienvenido nuevamente, {usuario}")
    st.write(f"💵 Saldo: **${usuarios[usuario]['saldo']:.2f}**")

    # Inversión
    st.write("### 📈 Inversión")
    tipo = st.selectbox("Tipo", ["Segura", "Media", "Arriesgada"])
    monto = st.number_input("¿Cuánto quieres invertir?", min_value=1.0, step=1.0)
    if st.button("Hacer inversión"):
        resultado = invertir(usuario, tipo, monto, usuarios)
        st.info(resultado)
        st.write(f"Nuevo saldo: **${usuarios[usuario]['saldo']:.2f}**")

    # Depósito
    st.write("### ➕ Depositar dinero (clave de padres)")
    monto_dep = st.number_input("Cantidad a depositar", min_value=1, step=1, key="dep")
    clave_dep = st.text_input("Clave de padres para depósito", type="password", key="clave_dep")
    if st.button("Depositar"):
        resultado = depositar(usuario, monto_dep, clave_dep, usuarios)
        st.info(resultado)

    # Retiro
    st.write("### ➖ Retirar dinero (clave de padres)")
    monto_ret = st.number_input("Cantidad a retirar", min_value=1, step=1, key="ret")
    clave_ret = st.text_input("Clave de padres para retiro", type="password", key="clave_ret")
    if st.button("Retirar"):
        resultado = retirar(usuario, monto_ret, clave_ret, usuarios)
        st.info(resultado)

    # Historial
    st.write("### 📜 Historial")
    for mov in reversed(usuarios[usuario]['historial']):
        st.write(f"- [{mov['tipo']}] {mov['detalle']} | Monto: ${mov['monto']} | Resultado: {mov['resultado']} | Saldo: ${mov['saldo_resultante']:.2f}")

    if st.button("🔓 Cerrar sesión"):
        st.session_state['usuario_logueado'] = None
        st.experimental_rerun()

# ----- INICIAR SESIÓN -----
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
