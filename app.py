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
# 2. ESTILOS CSS PERSONALIZADOS
# ---------------------------------------------------------
st.markdown("""
    <style>
    :root { --primary-color: #FFD700; }
    .stApp { background-color: #ffffff; color: #000000; }
    h1 { color: #D32F2F !important; text-align: center; font-family: 'Arial Black'; margin-bottom: 0px; }
    h3 { color: #333333 !important; text-align: center; font-size: 16px; margin-top: 5px; }
    
    /* Caja de instrucciones GPS */
    .instrucciones-gps {
        background-color: #FFF9C4;
        padding: 15px;
        border-radius: 10px;
        border: 2px dashed #FBC02D;
        text-align: center;
        margin-bottom: 20px;
        color: #000;
    }
    
    /* Botones */
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #FFD700 !important; color: black !important; border: 2px solid #000; }
    .wa-btn { background-color: #25D366 !important; color: white !important; padding: 18px; border-radius: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; font-size: 18px; border: 1px solid #128C7E; margin-top: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
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
        return None
    except:
        return None

# ---------------------------------------------------------
# 4. LÓGICA DE INTERFAZ
# ---------------------------------------------------------
st.markdown("<h1>🚕 TAXI SEGURO - COCA</h1>", unsafe_allow_html=True)
st.markdown("<h3>📍 Servicio 24/7 | Francisco de Orellana</h3>", unsafe_allow_html=True)
st.divider()

menu = st.selectbox("MENÚ PRINCIPAL:", ["👤 SOLICITAR TAXI", "🚕 CONDUCTORES"])

if menu == "👤 SOLICITAR TAXI":
    
    # --- INSTRUCCIÓN VISUAL PARA EL GPS ---
    st.markdown("""
        <div class="instrucciones-gps">
            <b>📢 IMPORTANTE:</b><br>
            Para enviarte la unidad rápido, por favor dale a <b>"PERMITIR"</b> 
            cuando tu celular te pida acceso a la ubicación (GPS). 🛰️
        </div>
    """, unsafe_allow_html=True)

    # Intentar obtener ubicación automáticamente
    loc = get_geolocation()

    with st.form("form_pedido"):
        nombre = st.text_input("👤 Tu Nombre:")
        celular_cliente = st.text_input("📱 Tu WhatsApp:")
        referencia = st.text_input("📍 Referencia (Casa, Local, Calles):")
        tipo_servicio = st.radio("¿Qué vehículo necesitas?", ["Taxi Ejecutivo 🚕", "Camioneta 🛻", "Moto Envío 📦"], horizontal=True)
        
        enviar = st.form_submit_button("✅ REGISTRAR MI PEDIDO")

    if enviar:
        if not nombre or not celular_cliente:
            st.error("⚠️ Por favor completa tu nombre y WhatsApp.")
        else:
            # Procesar Coordenadas
            if loc and 'coords' in loc:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                # ENLACE DE GOOGLE MAPS CORREGIDO (Formato Universal)
                mapa_link = f"https://www.google.com/maps?q={lat},{lon}"
                coords_txt = f"{lat}, {lon}"
                st.success("📍 ¡Ubicación GPS detectada correctamente!")
            else:
                mapa_link = "No proporcionado (GPS desactivado)"
                coords_txt = "Manual"
                st.warning("⚠️ No pudimos detectar tu GPS. Se enviará solo la referencia manual.")

            # 1. Guardar en la Base de Datos (Google Sheets)
            hoja = conectar_google_sheets()
            if hoja:
                try:
                    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Se guarda el celular del cliente para tu base de datos futura
                    hoja.append_row([fecha, nombre, celular_cliente, tipo_servicio, referencia, coords_txt, mapa_link, "PENDIENTE"])
                except:
                    pass

            # 2. Crear Mensaje para TI (El Propietario)
            # Usamos doble salto de línea para que sea fácil de leer en el chat
            mensaje_wa = (
                f"👋 *NUEVO PEDIDO DE UNIDAD*\n\n"
                f"👤 *Nombre:* {nombre}\n"
                f"📱 *WhatsApp Cliente:* {celular_cliente}\n"
                f"🚕 *Servicio:* {tipo_servicio}\n"
                f"🏠 *Referencia:* {referencia}\n\n"
                f"📍 *UBICACIÓN:* {mapa_link}"
            )
            
            # Codificar el texto para la URL de WhatsApp
            mensaje_codificado = urllib.parse.quote(mensaje_wa)
            
            # TU NÚMERO FIJO
            tu_numero = "593962384356"
            link_final = f"https://wa.me/{tu_numero}?text={mensaje_codificado}"
            
            # 3. Mostrar botón final
            st.info("✅ Datos registrados. Ahora presiona el botón de abajo para enviar el WhatsApp a la central.")
            st.markdown(f'<a href="{link_final}" class="wa-btn" target="_blank">📲 ENVIAR PEDIDO POR WHATSAPP</a>', unsafe_allow_html=True)

elif menu == "🚕 CONDUCTORES":
    st.info("Módulo de activación para conductores próximamente...")
