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

# --- 🎨 CSS PREMIUM & NETTOYAGE ---
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

    /* 3. NETTOYAGE TOTAL (Adieu Streamlit branding) */
    #MainMenu {visibility: hidden;} /* Cache le menu 3 points */
    footer {visibility: hidden;} /* Cache "Built with Streamlit" */
    header {visibility: hidden;} /* Cache la barre colorée en haut */
    [data-testid="stToolbar"] {visibility: hidden !important;} /* Cache les outils dev */
    .stDeployButton {display:none;} /* Cache le bouton deploy */

    /* 4. TYPOGRAPHIE & STYLE */
    h1 {
        color: #333 !important;
        font-weight: 800 !important;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 5. CUSTOMISATION DES INPUTS */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #eee !important;
        background-color: #f8f9fa !important;
        padding: 15px !important;
        font-size: 16px !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }

    /* 6. STYLE DES BOUTONS RADIO (Plus jolis) */
    .stRadio > div {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eee;
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
    st.error("⛔ Session invalide.")
    st.markdown("""<a href="https://gen-lang-client-0236145808.web.app" target="_parent" style="display: block; text-align: center; background: #dc3545; color: white; padding: 10px; border-radius: 5px; text-decoration: none;">Se reconnecter</a>""", unsafe_allow_html=True)
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

# En-tête simplifié et centré
st.markdown("<h1>💎 NEXA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; margin-bottom: 30px;'>Intelligence Artificielle de Réputation</p>", unsafe_allow_html=True)

# Zone de l'avis (Plus grande pour combler le vide)
st.markdown("### 1️⃣ L'avis à traiter")
avis_client = st.text_area(
    label="Avis",
    label_visibility="collapsed", # On cache le label standard pour faire plus propre
    height=180, # Plus haut pour remplir l'espace
    placeholder="Copiez-collez l'avis du client ici..."
)

st.write("") # Espaceur

# Options en 2 colonnes
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
    # Changement ici : Radio horizontal au lieu de Selectbox
    taille = st.radio(
        "Longueur",
        ["Courte", "Moyenne", "Détaillée"],
        horizontal=True,
        label_visibility="collapsed"
    )

# Bouton d'action
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
