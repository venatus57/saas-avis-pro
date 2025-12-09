import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="NEXA - Reputation Intelligence",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 🎨 CSS PREMIUM & CORRECTION COULEURS ---
premium_css = """
<style>
    /* 1. LE FOND GLOBAL */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. LA CARTE CENTRALE */
    .main .block-container {
        background-color: #ffffff;
        padding: 3rem !important;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        max-width: 850px;
        margin-top: 50px !important;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 3. NETTOYAGE TOTAL */
    #MainMenu {visibility: hidden;} 
    header {visibility: hidden;} 
    [data-testid="stToolbar"] {visibility: hidden !important;} 
    .stDeployButton {display:none;}
    footer {visibility: hidden !important; display: none !important; height: 0px !important;}
    [data-testid="stFooter"] {display: none !important;}

    /* 4. TYPOGRAPHIE & STYLE */
    h1 {
        color: #222 !important;
        font-weight: 800 !important;
        text-align: left !important;
        font-size: 3rem !important;
        margin-bottom: 0rem !important;
        margin-top: 0rem !important;
        letter-spacing: -1px;
    }
    
    /* 5. CUSTOMISATION DES INPUTS (LA CORRECTION EST ICI 👇) */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: #f8f9fa !important; /* Fond gris très clair */
        padding: 15px !important;
        font-size: 16px !important;
        
        /* FORCE LE TEXTE EN NOIR */
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important; /* Vital pour Chrome/Safari */
        caret-color: #000000 !important; /* Le curseur qui clignote devient noir */
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
        background-color: #ffffff !important; /* Devient blanc pur quand on clique */
    }

    /* 6. STYLE DES BOUTONS RADIO */
    .stRadio > div {
        background-color: #fff;
        padding: 0px;
        color: #000 !important; /* Force le texte des options en noir */
    }
    .stRadio label {
        color: #333 !important; /* Texte des labels en gris foncé */
    }

    /* 7. LE BOUTON D'ACTION */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px 25px !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3) !important;
        margin-top: 20px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.5) !important;
    }

</style>
"""
st.markdown(premium_css, unsafe_allow_html=True)


# --- SÉCURITÉ ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"
query_params = st.query_params
user_token = query_params.get("token", "")

if user_token != SECRET_TOKEN:
    st.error("⛔ Session expirée.")
    st.info("Veuillez vous reconnecter via le portail principal.")
    st.link_button(
        "🔐 Se reconnecter au Portail", 
        "https://gen-lang-client-0236145808.web.app", 
        type="primary", 
        use_container_width=True
    )
    st.stop()


# --- CONFIG IA ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Clé API manquante.")
        st.stop()
except Exception:
    st.stop()


# --- INTERFACE ---

# 1. EN-TÊTE PRO
st.markdown("<h1>NEXA</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: left; color: #000000; font-size: 1.3rem; font-weight: 500; margin-bottom: 35px; margin-top: 5px;'>
    Solution Intelligente de Gestion des Avis Google
    </p>
    """, 
    unsafe_allow_html=True
)

# 2. ZONE DE TRAVAIL
st.markdown("### 1️⃣ L'avis à traiter")
avis_client = st.text_area(
    label="Avis",
    label_visibility="collapsed", 
    height=180, 
    placeholder="Copiez-collez l'avis du client ici..."
)

st.write("") 

# 3. OPTIONS
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Ton de réponse")
    genre = st.selectbox(
        "Ton",
        ["Professionnel & Concis", "Chaleureux & Empathique", "Commercial & Vendeur", "Excuses & Résolution"],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 📏 Longueur")
    taille = st.radio(
        "Longueur",
        ["Courte", "Moyenne", "Détaillée"],
        horizontal=True,
        label_visibility="collapsed"
    )

# 4. ACTION
if st.button("✨ GÉNÉRER LA RÉPONSE"):
    if not avis_client:
        st.warning("⚠️ L'avis est vide.")
    else:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Agis comme un expert relation client NEXA.
            Avis : "{avis_client}"
            Ton : {genre}
            Longueur : {taille}
            Règle d'or : Pas de guillemets, direct, professionnel.
            """
            
            with st.spinner("Analyse en cours..."):
                response = model.generate_content(prompt)
                
                st.success("✅ Réponse générée")
                st.text_area("Résultat :", value=response.text, height=250)
                
        except Exception as e:
            st.error(f"Erreur : {e}")
