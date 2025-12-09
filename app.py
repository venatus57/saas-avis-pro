import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Repond'Avis Pro", page_icon="💬")

# --- 2. SÉCURITÉ (LE BRACELET VIP) ---
# Doit être EXACTEMENT le même que dans ton index.html sur Firebase
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"

# Récupération du token dans l'URL
query_params = st.query_params
user_token = query_params.get("token", "")

# Si le token est faux ou absent -> On bloque tout
if user_token != SECRET_TOKEN:
    st.error("⛔ Accès refusé. Vous devez passer par le portail sécurisé.")
    # Remplace ce lien par TON lien Firebase final (.web.app)
    st.link_button("Se connecter au Portail", "https://gen-lang-client-0236145808.web.app")
    st.stop() # Arrête le script ici, personne ne voit la suite

# --- 3. CONFIGURATION GEMINI (IA) ---
try:
    # On cherche la clé dans les secrets Streamlit
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Clé API Google introuvable dans les secrets Streamlit.")
        st.stop()
except Exception as e:
    st.warning(f"⚠️ Erreur de configuration IA : {e}")
    st.stop()

# --- 4. L'INTERFACE DE TON SAAS ---
st.title("💬 Repond'Avis Pro")
st.success(f"✅ Connecté via le portail sécurisé.")

st.subheader("1️⃣ L'avis reçu")
avis_client = st.text_area("Copiez l'avis client ici :", height=100, placeholder="Exemple : Pizza froide et service lent...")

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox("Ton de la réponse :", ["Professionnel & Poli", "Chaleureux & Empathique", "Commercial & Vendeur", "Excuses Sincères"])
with col2:
    taille = st.radio("Longueur :", ["Court", "Moyen", "Long"], horizontal=True)

st.write("---")

# --- 5. GÉNÉRATION DE LA RÉPONSE ---
if st.button("✨ GÉNÉRER LA RÉPONSE", type="primary", use_container_width=True):
    if not avis_client:
        st.warning("⚠️ Merci de coller un avis d'abord !")
    else:
        try:
            # Utilisation du modèle Gemini
            model = genai.GenerativeModel('gemini-1.5-flash') # J'ai mis 1.5-flash car c'est le plus stable et rapide
            
            prompt = f"""
            Agis comme un expert en relation client. Rédige une réponse à cet avis Google.
            Avis du client : "{avis_client}"
            Ton à adopter : {genre}
            Longueur souhaitée : {taille}
            Directives : Ne mets pas de guillemets au début ou à la fin. Sois pertinent.
            """
            
            with st.spinner("L'IA rédige votre réponse..."):
                response = model.generate_content(prompt)
                
                st.subheader("✅ Voici votre réponse :")
                st.text_area("À copier-coller :", value=response.text, height=250)
                
        except Exception as e:
            st.error(f"Une erreur est survenue avec l'IA : {e}")
