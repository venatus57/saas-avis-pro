import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION DE LA PAGE (Doit être la première commande Streamlit) ---
st.set_page_config(
    page_title="NEXA - Reputation Intelligence",
    page_icon="💎",
    layout="centered", # Important pour le look "carte centrale"
    initial_sidebar_state="collapsed"
)

# --- 🎨 CSS PREMIUM : C'EST ICI QUE LA MAGIE OPÈRE ---
# On injecte du CSS pour forcer Streamlit à ressembler à notre page de login
premium_css = """
<style>
    /* 1. LE FOND GLOBAL (Le même dégradé que le login) */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 2. LA "CARTE" CENTRALE */
    /* On cible le conteneur principal de Streamlit pour en faire une carte */
    .main .block-container {
        background-color: #ffffff;
        padding: 3rem !important; /* Plus d'espace à l'intérieur */
        border-radius: 20px; /* Bords très ronds */
        box-shadow: 0 20px 40px rgba(0,0,0,0.2); /* Belle ombre portée */
        max-width: 800px; /* Largeur max pour faire pro */
        margin-top: 50px !important; /* Un peu d'espace en haut */
        border: 1px solid rgba(255,255,255,0.2); /* Petit bord subtil */
    }

    /* 3. TYPOGRAPHIE & COULEURS */
    h1 {
        color: #333 !important;
        font-weight: 800 !important;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    h3 {
        color: #555 !important;
        font-weight: 600 !important;
    }
    p, label, .stSelectbox label, .stRadio label {
        color: #444 !important;
        font-size: 1rem !important;
    }

    /* 4. CUSTOMISATION DES INPUTS (Zones de texte, menus) */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #eee !important;
        background-color: #f9f9f9 !important;
        padding: 15px !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    /* Les menus déroulants */
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid #eee !important;
        background-color: #f9f9f9 !important;
    }

    /* 5. LE BOUTON PREMIUM (Remplacement du rouge par le dégradé) */
    .stButton > button {
        width: 100%; /* Pleine largeur */
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px 25px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    /* Effet au survol du bouton */
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6) !important;
    }
    .stButton > button:active {
        transform: translateY(1px);
    }

    /* Cacher des éléments parasites de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Petits ajustements d'espacement */
    .st-emotion-cache-16txtl3 { padding-top: 1rem; } /* Espace avant les colonnes */
    hr { margin: 2rem 0; border-color: #eee; }

</style>
"""
# Injection du CSS
st.markdown(premium_css, unsafe_allow_html=True)


# --- SÉCURITÉ (LE BRACELET VIP) ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"
query_params = st.query_params
user_token = query_params.get("token", "")

if user_token != SECRET_TOKEN:
    # On stylise même le message d'erreur pour qu'il soit propre
    st.error("⛔ Accès refusé. Session expirée ou invalide.")
    # Le lien de redirection vers ton site Firebase
    st.markdown(
        """<a href="https://gen-lang-client-0236145808.web.app" target="_parent" 
        style="display: block; text-align: center; background: #dc3545; color: white; 
        padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px;">
        Se reconnecter au portail NEXA</a>""", 
        unsafe_allow_html=True
    )
    st.stop()


# --- CONFIGURATION IA ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Clé API Google introuvable.")
        st.stop()
except Exception as e:
    st.warning(f"⚠️ Erreur de configuration IA : {e}")
    st.stop()


# --- L'INTERFACE UTILISATEUR (Dans la carte blanche) ---

# Titre Principal avec le nouveau nom
st.markdown("<h1>💎 NEXA<br><span style='font-size: 1.2rem; font-weight:400; color:#666;'>Reputation Intelligence</span></h1>", unsafe_allow_html=True)

# Petit message de bienvenue discret
st.toast("✅ Connecté à l'espace sécurisé.", icon="🔒")

st.subheader("1️⃣ L'avis client reçu")
avis_client = st.text_area(
    "Collez le texte de l'avis ici :", 
    height=120, 
    placeholder="Exemple : 'Service impeccable et plats délicieux, mais un peu bruyant samedi soir...'"
)

st.write("") # Petit espace

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox(
        "Ton de la réponse :", 
        ["Professionnel & Concis", "Chaleureux & Empathique", "Commercial & Engageant", "Excuses Sincères & Résolution"]
    )
with col2:
    # J'ai changé le radio en selectbox pour que ce soit plus propre visuellement dans la carte
    taille = st.selectbox("Longueur souhaitée :", ["Courte (1-2 phrases)", "Moyenne (3-4 phrases)", "Détaillée (5+ phrases)"])

st.markdown("---") # Ligne de séparation subtile

# --- GÉNÉRATION ---
# Le bouton sera automatiquement stylisé par le CSS ci-dessus
if st.button("✨ GÉNÉRER LA RÉPONSE PREMIUM"):
    if not avis_client:
        st.warning("⚠️ Veuillez coller un avis d'abord.")
    else:
        try:
            # Modèle performant
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prompt optimisé pour un résultat pro
            prompt = f"""
            Agis comme un expert en communication de crise et relation client pour une marque premium.
            Rédige une réponse à cet avis Google.

            Avis du client : "{avis_client}"
            Ton à adopter : {genre}
            Longueur : {taille}

            Directives importantes :
            - Ne mets JAMAIS de guillemets au début ou à la fin de la réponse.
            - Sois direct, pertinent et professionnel.
            - Si l'avis est négatif, remercie pour le retour et propose une solution sans être sur la défensive.
            - Si l'avis est positif, remercie chaleureusement et invite à revenir.
            """
            
            # Spinner personnalisé
            with st.spinner("🧠 L'IA NEXA analyse l'avis et rédige la réponse..."):
                response = model.generate_content(prompt)
                
                st.success("✅ Réponse générée avec succès !")
                st.subheader("Votre réponse prête à l'emploi :")
                st.text_area(
                    "Cliquez dedans puis Ctrl+A / Ctrl+C pour copier :", 
                    value=response.text, 
                    height=250
                )
                
        except Exception as e:
            st.error(f"Une erreur technique est survenue : {e}")
