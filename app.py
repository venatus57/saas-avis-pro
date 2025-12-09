import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Repond'Avis Pro", page_icon="🔒")

# --- SÉCURITÉ UNIQUE : LE TOKEN ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"

# Récupération du token dans l'URL
query_params = st.query_params
user_token = query_params.get("token", "")

# Si le token n'est pas bon, on bloque l'accès
if user_token != SECRET_TOKEN:
    st.error("⛔ Accès refusé. Vous devez passer par le portail de connexion.")
    st.link_button("Se connecter", "https://gen-lang-client-0236145808.web.app")
    st.stop()

# =========================================================
# SI ON ARRIVE ICI, C'EST QUE LE CLIENT EST AUTHENTIFIÉ
# =========================================================

# --- CHARGEMENT CLÉ API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Clé API introuvable.")
        st.stop()
except Exception as e:
    st.warning(f"⚠️ Erreur technique (Clé) : {e}")
    st.stop()

# --- LE VRAI SITE COMMENCE ICI ---
st.title("💬 Repond'Avis Pro")
st.success("✅ Accès autorisé. Bienvenue !")

# --- ZONE 1 : L'AVIS ---
st.subheader("1️⃣ L'avis reçu")
avis_client = st.text_area(
    "Collez le texte du client ici :", 
    height=100,
    placeholder="Exemple : Pizza froide..."
)

# --- ZONE 2 : RÉGLAGES ---
col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("Ton :", ["Professionnel", "Chaleureux", "Commercial", "Excuses"])
with col2:
    taille = st.radio("Longueur :", ["Court", "Moyen", "Long"], horizontal=True)

# --- ACTION ---
st.write("---")
if st.button("✨ GÉNÉRER LA RÉPONSE", type="primary", use_container_width=True):
    if not avis_client:
        st.warning("⚠️ Collez un avis d'abord !")
    else:
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            prompt = f"Réponds à cet avis Google : '{avis_client}'. Ton: {genre}. Taille: {taille}. Pas de guillemets."
            
            with st.spinner("Rédaction..."):
                response = model.generate_content(prompt)
                st.success("✅ Réponse prête :")
                st.text_area("Résultat :", value=response.text, height=200)
                
        except Exception as e:
            st.error(f"Erreur : {e}")
