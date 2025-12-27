import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_js_eval import get_geolocation
from datetime import datetime
import urllib.parse # <--- ESTO ES LO NUEVO PARA QUE WHATSAPP NO FALLE

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="TAXI SEGURO - COCA", page_icon="🚕", layout="centered")

# ---------------------------------------------------------
# 2. ESTILOS CSS BLINDADOS (FUERZA EL MODO CLARO)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* VARIABLES GLOBALES */
    :root {
        --primary-color: #FFD700;
        --background-color: #ffffff;
        --secondary-background-color: #f0f2f6;
        --text-color: #000000;
        --font: sans-serif;
    }
    
    /* FORZAR FONDO BLANCO Y TEXTO NEGRO EN TODA LA APP */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Títulos */
    h1 { 
        color: #D32F2F !important; 
        font-family: 'Arial Black', sans-serif; 
        text-align: center; 
        text-transform: uppercase; 
        margin-bottom: 0px;
    }
    h3 { 
        color: #333333 !important; 
        text-align: center; 
        font-size: 16px; 
        margin-top: 5px; 
        font-weight: bold;
    }
    p, label, div, span {
        color: #000000 !important;
    }
    
    /* Campos de Entrada (Inputs) - Fondo blanco obligado */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #cccccc;
    }

    /* Botones Principales (Amarillo Taxi) */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        font-weight: bold;
        background-color: #FFD700 !important; 
        color: black !important; 
        border: 2px solid #000;
        font-size: 16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #FFEA00 !important;
        border-color: #D32F2F !important;
    }

    /* Botón PayPhone (Naranja Vibrante) */
    .payphone-btn { 
        background-color: #FF6D00 !important; 
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
        background-color: #25D366 !important; 
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

    /* Cajas de Estado */
    .caja-exito {
        background-color: #E8F5E9 !important;
        color: #1B5E20 !important;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        text-align: center;
        margin-bottom: 20px;
    }
    .caja-alerta {
        background-color: #FFEBEE !important;
        color: #B71C1C !important;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #D32F2F;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. CONEXIÓN A GOOGLE SHEETS (CON AUTOREPARACIÓN)
# ---------------------------------------------------------
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" in st.secrets:
            # Creamos una copia del diccionario para no romper nada
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            # --- CORRECCIÓN AUTOMÁTICA DEL ERROR JWT ---
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            # Conecta a la hoja "Base_Datos_Coca" y toma la PRIMERA pestaña (índice 0)
            return client.open("Base_Datos_Coca").get_worksheet(0) 
        else:
            st.error("⚠️ Faltan los Secrets en Streamlit.")
            return None
            
    except Exception as e:
        # Muestra el error real si sigue fallando
        st.error(f"⚠️ ERROR DE CONEXIÓN: {e}") 
        return None

# ---------------------------------------------------------
# 4. INTERFAZ DE USUARIO (FRONTEND)
# ---------------------------------------------------------

# Encabezado con Logo
st.markdown("<h1>🚕 TAXI SEGURO - COCA</h1>", unsafe_allow_html=True)
st.markdown("<h3>📍 Francisco de Orellana | Servicio 24/7</h3>", unsafe_allow_html=True)
st.divider()

# Menú Principal
menu = st.selectbox("SELECCIONA UNA OPCIÓN:", ["👤 PASAJERO (PEDIR UNIDAD)", "🚕 CONDUCTOR (ACTIVAR PAGO)"])

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MÓDULO A: PASAJERO
# ==========================================
if menu == "👤 PASAJERO (PEDIR UNIDAD)":
    st.info("👇 Presiona abajo para permitir el acceso al GPS")
    
    # 1. Geolocalización
    loc = get_geolocation()
    
    ubicacion_txt = "Pendiente..."
    mapa_link = ""

    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        ubicacion_txt = f"{lat}, {lon}"
        # Generamos link directo a Google Maps
        mapa_link = f"http://googleusercontent.com/maps.google.com/maps?q={lat},{lon}"
        st.markdown(f'<div class="caja-exito">✅ Ubicación detectada en El Coca</div>', unsafe_allow_html=True)
    
    # 2. Formulario de Pedido
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
                st.error("⚠️ PRIMERO debemos detectar tu ubicación (GPS). Asegúrate de dar permiso.")
            elif not nombre:
                st.warning("⚠️ Escribe tu nombre para que el conductor sepa a quién buscar.")
            else:
                # Guardar en Base de Datos
                hoja = conectar_google_sheets()
                if hoja:
                    try:
                        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                        # Columnas: Fecha, Nombre, Celular, Tipo, Ref, Coordenadas, LinkMapa, Estado
                        hoja.append_row([fecha, nombre, celular, tipo_servicio, referencia, ubicacion_txt, mapa_link, "PENDIENTE"])
                        st.success("✅ ¡Solicitud registrada con éxito!")
                        
                        # --- GENERACIÓN DE LINK DE WHATSAPP MEJORADA ---
                        mensaje_wa = f"👋 Hola, soy *{nombre}*.\nNecesito un *{tipo_servicio}* en El Coca.\n📍 *GPS:* {mapa_link}\n🏠 *Ref:* {referencia}"
                        
                        # Codificamos el mensaje para que funcione bien en internet (convierte espacios en %20, etc.)
                        mensaje_codificado = urllib.parse.quote(mensaje_wa)
                        
                        # Usamos tu número detectado: 593960643638
                        link_wa = f"https://wa.me/593960643638?text={mensaje_codificado}" 
                        
                        st.markdown(f'<a href="{link_wa}" class="wa-btn" target="_blank">📲 CONFIRMAR POR WHATSAPP</a>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"⚠️ Error al guardar datos: {e}")
                else:
                    pass

# ==========================================
# MÓDULO B: CONDUCTOR
# ==========================================
elif menu == "🚕 CONDUCTOR (ACTIVAR PAGO)":
    st.markdown("### 🚦 Control de Suscripción Diaria")
    st.write("Ingresa tu número para verificar tu estado:")
    
    conductor_id = st.text_input("Celular (+593):", placeholder="099...")
    
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
        st.info("""
        🏦 **Banco Pichincha / Deuna**
        \nCuenta Ahorros: **220XXXXXXX**
        \nCI: **17XXXXXXX**
        \nNombre: **Tu Nombre**
        """)
        
        msg_pago = f"Hola Admin, adjunto pago de $1 para activar el numero {conductor_id} en Taxi Seguro Coca."
        st.markdown(f'<a href="https://wa.me/593960643638?text={msg_pago}" class="wa-btn" target="_blank">✅ ENVIAR COMPROBANTE</a>', unsafe_allow_html=True)
