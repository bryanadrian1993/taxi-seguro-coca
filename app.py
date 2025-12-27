import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse 

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚕", layout="centered")

# ---------------------------------------------------------
# 2. ESTILOS CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    :root { --primary-color: #FFD700; --background-color: #ffffff; --text-color: #000000; }
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    h1 { color: #D32F2F !important; font-family: 'Arial Black', sans-serif; text-align: center; text-transform: uppercase; margin-bottom: 0px; }
    h3 { color: #333333 !important; text-align: center; font-size: 16px; margin-top: 5px; font-weight: bold; }
    p, label, div, span { color: #000000 !important; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div { color: #000000 !important; background-color: #ffffff !important; border: 1px solid #cccccc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: bold; background-color: #FFD700 !important; color: black !important; border: 2px solid #000; font-size: 16px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); }
    .stButton>button:hover { background-color: #FFEA00 !important; border-color: #D32F2F !important; }
    .payphone-btn { background-color: #FF6D00 !important; color: white !important; padding: 18px; border-radius: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 18px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    .wa-btn { background-color: #25D366 !important; color: white !important; padding: 15px; border-radius: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #128C7E; }
    .caja-exito { background-color: #E8F5E9 !important; color: #1B5E20 !important; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32; text-align: center; margin-bottom: 20px; }
    .caja-alerta { background-color: #FFEBEE !important; color: #B71C1C !important; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. CONEXIÓN A GOOGLE SHEETS
# ---------------------------------------------------------
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client.open("Base_Datos_Coca").get_worksheet(0) 
        else:
            st.error("⚠️ Faltan los Secrets en Streamlit.")
            return None
    except Exception as e:
        st.error(f"⚠️ ERROR DE CONEXIÓN: {e}") 
        return None

# ---------------------------------------------------------
# 4. INTERFAZ DE USUARIO (FRONTEND)
# ---------------------------------------------------------
st.markdown("<h1>🚕 TAXI SEGURO - COCA</h1>", unsafe_allow_html=True)
st.markdown("<h3>📍 Francisco de Orellana | Servicio 24/7</h3>", unsafe_allow_html=True)
st.divider()

menu = st.selectbox("SELECCIONA UNA OPCIÓN:", ["👤 PASAJERO (PEDIR UNIDAD)", "🚕 CONDUCTOR (ACTIVAR PAGO)"])
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MÓDULO A: PASAJERO (MODO HÍBRIDO)
# ==========================================
if menu == "👤 PASAJERO (PEDIR UNIDAD)":
    
    # Intentamos obtener GPS
    try:
        loc = get_geolocation()
    except:
        loc = None
    
    ubicacion_detectada = False
    mapa_link = "No detectado"
    coords_txt = "Manual"

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        coords_txt = f"{lat}, {lon}"
        
        # >>>>> ESTE ES EL ENLACE UNIVERSAL QUE FUNCIONA EN PC Y MÓVIL <<<<<
        mapa_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        
        ubicacion_detectada = True
        st.markdown(f'<div class="caja-exito">✅ GPS Detectado automáticamente</div>', unsafe_allow_html=True)
    else:
        st.info("ℹ️ No detectamos tu GPS. Por favor escribe tu dirección abajo.")
    
    with st.form("formulario_pedido"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Tu Nombre:")
        with col2:
            celular = st.text_input("Tu WhatsApp:")
            
        referencia = st.text_input("📍 ¿Dónde te recogemos? (Barrio / Calles / Referencia):", placeholder="Ej: Barrio Central, frente al Tía")
        tipo_servicio = st.radio("¿Qué necesitas?", ["Taxi Ejecutivo 🚕", "Camioneta 🛻", "Moto Envío 📦"], horizontal=True)
        
        enviar = st.form_submit_button("SOLICITAR UNIDAD AHORA")

        if enviar:
            if not nombre:
                st.warning("⚠️ Por favor escribe tu nombre.")
            elif not ubicacion_detectada and len(referencia) < 3:
                st.error("⚠️ Como no tenemos tu GPS, debes escribir una referencia de dónde estás.")
            else:
                hoja = conectar_google_sheets()
                if hoja:
                    try:
                        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                        hoja.append_row([fecha, nombre, celular, tipo_servicio, referencia, coords_txt, mapa_link, "PENDIENTE"])
                        st.success("✅ ¡Solicitud lista!")
                        
                        # Armar mensaje 
                        if ubicacion_detectada:
                            texto_ubicacion = f"📍 *GPS:* {mapa_link}"
                        else:
                            texto_ubicacion = "📍 *Ubicación:* (Cliente envía ubicación manual)"

                        mensaje_wa = f"👋 Hola, soy *{nombre}*.\nNecesito un *{tipo_servicio}*.\n{texto_ubicacion}\n🏠 *Ref:* {referencia}"
                        
                        mensaje_codificado = urllib.parse.quote(mensaje_wa)
                        
                        # TU NÚMERO
                        link_wa = f"https://wa.me/593962384356?text={mensaje_codificado}" 
                        
                        st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"⚠️ Error: {e}")

# ==========================================
# MÓDULO B: CONDUCTOR
# ==========================================
elif menu == "🚕 CONDUCTOR (ACTIVAR PAGO)":
    st.markdown("### 🚦 Control de Suscripción Diaria")
    st.write("Ingresa tu número para verificar tu estado:")
    conductor_id = st.text_input("Celular (+593):", placeholder="099...")
    
    if conductor_id:
        st.markdown("""<div class="caja-alerta"><b>⛔ ACCESO BLOQUEADO</b><br>Suscripción vencida.</div>""", unsafe_allow_html=True)
        link_pago_payphone = "https://pay.payphonetodoesposible.com/" 
        st.markdown(f'<a href="{link_pago_payphone}" class="payphone-btn" target="_blank">💳 PAGAR $1.00 CON PAYPHONE</a>', unsafe_allow_html=True)
        
        st.info("O transferencia bancaria:")
        st.write("🏦 **Pichincha / Deuna**: 220XXXXXXX")
        
        msg_pago = f"Hola Admin, adjunto pago de $1 para activar el numero {conductor_id}."
        st.markdown(f'<a href="https://wa.me/593962384356?text={msg_pago}" class="wa-btn" target="_blank">✅ ENVIAR COMPROBANTE</a>', unsafe_allow_html=True)
