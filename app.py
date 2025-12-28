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
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #FFD700 !important; color: black !important; border: 2px solid #000; }
    .wa-btn { background-color: #25D366 !important; color: white !important; padding: 15px; border-radius: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; border: 1px solid #128C7E; margin-top: 10px; }
    .caja-gps { background-color: #F0F2F6; padding: 15px; border-radius: 10px; text-align: center; border: 1px dashed #ccc; margin-bottom: 15px; }
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
# 4. INTERFAZ DE USUARIO
# ---------------------------------------------------------
st.markdown("<h1>🚕 TAXI SEGURO - COCA</h1>", unsafe_allow_html=True)
st.markdown("<h3>📍 Servicio 24/7 | El Coca</h3>", unsafe_allow_html=True)
st.divider()

menu = st.selectbox("MENÚ:", ["👤 PASAJERO", "🚕 CONDUCTOR"])

if menu == "👤 PASAJERO":
    st.markdown('<div class="caja-gps">', unsafe_allow_html=True)
    st.write("🛰️ **Paso 1: Activa tu GPS**")
    # Botón específico para disparar el permiso de ubicación
    loc = get_geolocation()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("form_pedido"):
        nombre = st.text_input("Tu Nombre:")
        celular_cliente = st.text_input("Tu WhatsApp (Para registro):")
        referencia = st.text_input("📍 Referencia (Ej: Junto al Parque):")
        tipo_servicio = st.selectbox("Vehículo:", ["Taxi Ejecutivo 🚕", "Camioneta 🛻", "Moto Envío 📦"])
        
        enviar = st.form_submit_button("REGISTRAR PEDIDO")

    if enviar:
        if not nombre or not celular_cliente:
            st.error("⚠️ Nombre y WhatsApp son obligatorios")
        else:
            # Procesar Ubicación
            if loc and 'coords' in loc:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                # ENLACE OFICIAL DE GOOGLE MAPS
                mapa_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                coords_txt = f"{lat}, {lon}"
                st.success("📍 Ubicación GPS obtenida con éxito")
            else:
                mapa_link = "SIN GPS (Ubicación Manual)"
                coords_txt = "Manual"
                st.warning("⚠️ No se detectó GPS. Se enviará solo la referencia.")

            # Guardar en Google Sheets
            hoja = conectar_google_sheets()
            if hoja:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                hoja.append_row([fecha, nombre, celular_cliente, tipo_servicio, referencia, coords_txt, mapa_link, "PENDIENTE"])

            # -----------------------------------------------------------
            # CORRECCIÓN DE MENSAJE: CONSTRUCCIÓN DEL TEXTO PARA TI
            # -----------------------------------------------------------
            mensaje_wa = (
                f"👋 *NUEVO PEDIDO DE TAXI*\n\n"
                f"👤 *Cliente:* {nombre}\n"
                f"📱 *Celular:* {celular_cliente}\n"
                f"🚕 *Servicio:* {tipo_servicio}\n"
                f"🏠 *Ref:* {referencia}\n\n"
                f"📍 *MAPA:* {mapa_link}"
            )
            
            mensaje_codificado = urllib.parse.quote(mensaje_wa)
            # TU NÚMERO (Propietario)
            link_final = f"https://wa.me/593962384356?text={mensaje_codificado}"
            
            st.info("✅ Pedido registrado en el sistema.")
            st.markdown(f'<a href="{link_final}" class="wa-btn" target="_blank">📲 ENVIAR A CENTRAL (WHATSAPP)</a>', unsafe_allow_html=True)

elif menu == "🚕 CONDUCTOR":
    st.write("Sección de conductores...")
