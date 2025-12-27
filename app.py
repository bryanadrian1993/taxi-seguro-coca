import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
import time

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y MARCA
# ---------------------------------------------------------
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚕", layout="centered")

# Estilos CSS Profesionales (Amarillo/Negro/Rojo)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* Encabezados */
    h1 { color: #D32F2F; font-family: 'Arial Black', sans-serif; text-align: center; text-transform: uppercase; margin-bottom: 0px;}
    h3 { color: #333; text-align: center; font-size: 16px; margin-top: 5px; font-weight: bold;}
    
    /* Botones Principales (Amarillo Taxi) */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        font-weight: bold;
        background-color: #FFD700; 
        color: black; 
        border: 2px solid #000;
        font-size: 16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #FFEA00;
        border-color: #D32F2F;
    }

    /* Botón PayPhone (Naranja Vibrante) */
    .payphone-btn { 
        background-color: #FF6D00; 
        color: white !important; 
        padding: 18px; 
        border-radius: 12px; 
        text-align: center; 
        display: block; 
        text-decoration: none; 
        font-weight: bold; 
        font-size: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
                  
    /* Botón WhatsApp (Verde Oficial) */
    .wa-btn { 
        background-color: #25D366; 
        color: white !important; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        display: block; 
        text-decoration: none; 
        font-weight: bold; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #128C7E;
    }

    /* Alertas y Cajas */
    .caja-alerta {
        background-color: #FFEBEE;
        color: #B71C1C;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #D32F2F;
        text-align: center;
        margin-bottom: 20px;
    }
    .caja-exito {
        background-color: #E8F5E9;
        color: #1B5E20;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXIÓN A GOOGLE SHEETS
# ---------------------------------------------------------
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Intenta leer desde los Secretos de Streamlit Cloud
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            # IMPORTANTE: La hoja debe llamarse EXACTAMENTE así en tu Drive
            return client.open("Base_Datos_Coca").sheet1 
        else:
            return None
    except Exception as e:
        return None

# ---------------------------------------------------------
# INTERFAZ DE USUARIO
# ---------------------------------------------------------

# Logo / Título
st.markdown("<h1>🚕 TAXI SEGURO - COCA</h1>", unsafe_allow_html=True)
st.markdown("<h3>📍 Francisco de Orellana | Servicio 24/7</h3>", unsafe_allow_html=True)
st.divider()

# Menú Principal
menu = st.selectbox("SELECCIONA UNA OPCIÓN:", ["👤 PASAJERO (PEDIR UNIDAD)", "🚕 CONDUCTOR (ACTIVAR PAGO)"])

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MÓDULO 1: PASAJERO
# ==========================================
if menu == "👤 PASAJERO (PEDIR UNIDAD)":
    st.info("👇 Presiona para enviar tu ubicación exacta al conductor")
    
    # 1. Geolocalización
    loc = get_geolocation()
    
    ubicacion_txt = "Pendiente..."
    mapa_link = ""

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        ubicacion_txt = f"{lat}, {lon}"
        mapa_link = f"http://googleusercontent.com/maps.google.com/maps?q={lat},{lon}"
        st.markdown(f'<div class="caja-exito">✅ Ubicación detectada en El Coca</div>', unsafe_allow_html=True)
    
    # 2. Formulario
    with st.form("formulario_pedido"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Tu Nombre:")
        with col2:
            celular = st.text_input("Tu WhatsApp:")
            
        referencia = st.text_input("Referencia / Destino:", placeholder="Ej: Barrio Central, frente a la Farmacia...")
        tipo_servicio = st.radio("¿Qué necesitas?", ["Taxi Ejecutivo 🚕", "Camioneta 🛻", "Moto Envío 📦"], horizontal=True)
        
        enviar = st.form_submit_button("SOLICITAR UNIDAD AHORA")

        if enviar:
            if not loc:
                st.error("⚠️ PRIMERO debemos detectar tu ubicación (GPS).")
            elif not nombre:
                st.warning("⚠️ Escribe tu nombre.")
            else:
                # Guardar en Base de Datos
                hoja = conectar_google_sheets()
                if hoja:
                    try:
                        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                        hoja.append_row([fecha, nombre, celular, tipo_servicio, referencia, ubicacion_txt, mapa_link, "PENDIENTE"])
                        st.success("¡Solicitud registrada!")
                        
                        # Generar Link de WhatsApp
                        mensaje_wa = f"👋 Hola, soy *{nombre}*.\nNecesito un *{tipo_servicio}* en El Coca.\n📍 *GPS:* {mapa_link}\n🏠 *Ref:* {referencia}"
                        link_wa = f"https://wa.me/593962362257?text={mensaje_wa}" # CAMBIA ESTE NÚMERO POR EL TUYO
                        
                        st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 CONFIRMAR POR WHATSAPP</a>', unsafe_allow_html=True)
                    except:
                        st.error("Error al conectar con la base de datos.")
                else:
                    st.error("Error de configuración (Secrets).")

# ==========================================
# MÓDULO 2: CONDUCTOR
# ==========================================
elif menu == "🚕 CONDUCTOR (ACTIVAR PAGO)":
    st.markdown("### 🚦 Control de Suscripción Diaria")
    st.write("Ingresa tu número para verificar tu estado:")
    
    conductor_id = st.text_input("Celular (+593):", placeholder="099...")
    
    # AQUÍ IRÍA LA LÓGICA DE VERIFICACIÓN AUTOMÁTICA
    # Por ahora simulamos que NO ha pagado para mostrar el botón
    
    if conductor_id:
        st.markdown("""
        <div class="caja-alerta">
            <b>⛔ ACCESO BLOQUEADO</b><br>
            Tu suscripción del día ha vencido.
            <br>Cancela <b>$1.00 USD</b> para recibir carreras hoy.
        </div>
        """, unsafe_allow_html=True)
        
        # Enlace de Cobro PayPhone (CÁMBIALO POR EL TUYO REAL)
        link_pago_payphone = "https://pay.payphonetodoesposible.com/" 
        
        st.write("👇 **OPCIÓN 1: ACTIVACIÓN AUTOMÁTICA (Recomendado)**")
        st.markdown(f'<a href="{link_pago_payphone}" class="payphone-btn" target="_blank">💳 PAGAR $1.00 CON PAYPHONE</a>', unsafe_allow_html=True)

        st.write("👇 **OPCIÓN 2: MANUAL (Deuna / Banco)**")
        st.info("**Banco Pichincha** | Cta: 220XXXXXX | CI: 17XXXXXXX")
        
        msg_pago = f"Adjunto pago de $1 para activar el numero {conductor_id}"
        st.markdown(f'<a href="https://wa.me/593962362257?text={msg_pago}" class="wa-btn" target="_blank">ENVIAR COMPROBANTE</a>', unsafe_allow_html=True)
