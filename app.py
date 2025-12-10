import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION STRICTE ---
st.set_page_config(
    page_title="NEXA Intelligence",
    page_icon="🟦", # Icône sobre (carré bleu) ou rien
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 🎨 CSS CORPORATE (Le Nettoyage) ---
corporate_css = """
<style>
    /* 1. FOND SOBRE ET PRO */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); /* Gris-Bleu Entreprise (plus neutre que le violet) */
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* 2. CARTE CENTRALE (Style "Logiciel Bancaire") */
    .main .block-container {
        background-color: #ffffff;
        padding: 40px !important;
        border-radius: 8px; /* Bords moins ronds, plus sérieux */
        box-shadow: 0 4px 20px rgba(0,0,0,0.1); /* Ombre plus discrète */
        max-width: 900px;
        margin-top: 40px !important;
        border: 1px solid #e1e4e8;
    }

    /* 3. SUPPRESSION TOTALE DU BRANDING STREAMLIT */
    #MainMenu {visibility: hidden;} 
    header {visibility: hidden;} 
    [data-testid="stToolbar"] {visibility: hidden !important;} 
    .stDeployButton {display:none;}
    
    /* Cacher le footer et le bouton fullscreen buggé */
    footer {visibility: hidden !important; display: none !important; height: 0px !important;}
    [data-testid="stFooter"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}

    /* 4. TYPOGRAPHIE SÉRIEUSE */
    h1 {
        color: #1a202c !important; /* Noir Encre */
        font-weight: 700 !important;
        text-align: left !important;
        font-size: 2.2rem !important;
        margin-bottom: 0px !important;
        letter-spacing: -0.5px;
    }
    p {
        color: #4a5568 !important; /* Gris foncé professionnel */
    }
    h3 {
        color: #2d3748 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
    }
    
    /* 5. INPUTS PROPRES (Style Bootstrap/SaaS) */
    .stTextArea textarea {
        border-radius: 6px !important;
        border: 1px solid #cbd5e0 !important;
        background-color: #ffffff !important;
        padding: 12px !important;
        font-size: 15px !important;
        color: #1a202c !important;
        -webkit-text-fill-color: #1a202c !important;
        caret-color: #1a202c !important;
    }
    .stTextArea textarea:focus {
        border-color: #3182ce !important; /* Bleu corporatif */
        box-shadow: 0 0 0 1px #3182ce !important;
    }

    /* 6. BOUTONS RADIO (Style Pilules) */
    .stRadio > div {
        background-color: transparent;
    }
    .stRadio label {
        color: #2d3748 !important;
        font-weight: 500;
    }

    /* 7. BOUTON D'ACTION (Style "Valider") */
    .stButton > button {
        width: 100%;
        background-color: #2b6cb0 !important; /* Bleu foncé sérieux */
        background-image: none !important; /* Pas de dégradé fantaisie */
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 14px 24px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-transform: none !important; /* Pas de majuscules agressives */
        transition: background-color 0.2s;
        margin-top: 25px;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        background-color: #2c5282 !important; /* Bleu encore plus foncé */
    }

</style>
"""
st.markdown(corporate_css, unsafe_allow_html=True)


# --- SÉCURITÉ ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"
query_params = st.query_params
user_token = query_params.get("token", "")

if user_token != SECRET_TOKEN:
    st.error("Session expirée.")
    st.link_button(
        "Connexion Portail", 
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
        st.error("Erreur de configuration système (API Key).")
        st.stop()
except Exception:
    st.stop()


# --- INTERFACE ---

# 1. EN-TÊTE (Très sobre)
st.markdown("<h1>NEXA</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: left; font-size: 1.1rem; margin-bottom: 30px; margin-top: 5px; color: #718096;'>
    Gestionnaire de Réputation Client
    </p>
    """, 
    unsafe_allow_html=True
)

# 2. ZONE DE TRAVAIL (Sans emoji)
st.markdown("<h3>Avis Client</h3>", unsafe_allow_html=True)
avis_client = st.text_area(
    label="Avis",
    label_visibility="collapsed", 
    height=150, 
    placeholder="Collez le texte de l'avis ici..."
)

# 3. OPTIONS
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3>Ton de réponse</h3>", unsafe_allow_html=True)
    genre = st.selectbox(
        "Ton",
        ["Professionnel", "Empathique", "Commercial", "Résolution de problème"],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<h3>Longueur</h3>", unsafe_allow_html=True)
    taille = st.radio(
        "Longueur",
        ["Courte", "Standard", "Détaillée"],
        horizontal=True,
        label_visibility="collapsed"
    )

# 4. ACTION
if st.button("Générer la réponse"):
    if not avis_client:
        st.warning("Veuillez saisir un avis.")
    else:
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Agis en tant que service client professionnel.
            Avis client : "{avis_client}"
            Ton : {genre}
            Longueur : {taille}
            Instruction : Réponse directe, sans guillemets, format professionnel.
            """
            
            with st.spinner("Traitement en cours..."):
                response = model.generate_content(prompt)
                
                st.success("Réponse générée")
                st.text_area("Copier le texte ci-dessous :", value=response.text, height=200)
                
        except Exception as e:
            st.error(f"Erreur technique : {e}")


