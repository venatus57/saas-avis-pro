import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Repond'Avis Pro", page_icon="💬")

# --- CHARGEMENT CLÉ ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Fichier .streamlit/secrets.toml introuvable.")
        st.stop()
except Exception:
    st.warning("⚠️ Clé introuvable.")
    st.stop()

# --- HEADER ---
st.title("💬 Repond'Avis Pro")
st.info("💡 Copiez l'avis, réglez, générez.")

# --- ZONE 1 : L'AVIS ---
st.subheader("1️⃣ L'avis reçu")
avis_client = st.text_area(
    "Collez le texte du client ici :", 
    height=100,
    placeholder="Exemple : Pizza froide..."
)

# --- ZONE 2 : RÉGLAGES ---
st.subheader("2️⃣ Vos préférences")
col1, col2 = st.columns(2)

with col1:
    genre = st.selectbox(
        "Ton :", 
        ["Professionnel & Courtois", "Chaleureux & Amical", "Commercial", "Excuses & Empathie"],
    )

with col2:
    taille = st.radio(
        "Longueur :",
        ["Court", "Moyen", "Long"],
        horizontal=True,
    )

# --- ACTION ---
st.write("---")
generate_btn = st.button("✨ GÉNÉRER LA RÉPONSE", type="primary", use_container_width=True)

if generate_btn:
    if not avis_client:
        st.warning("⚠️ Collez un avis d'abord !")
    else:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            Tâche : Réponds à cet avis Google.
            Avis : "{avis_client}"
            Ton : {genre}
            Longueur : {taille}
            Important : Fais des paragraphes clairs. Pas de guillemets.
            """
            
            with st.spinner("Rédaction..."):
                response = model.generate_content(prompt)
                
                # --- LE CHANGEMENT EST ICI ---
                st.success("✅ Réponse prête (Vous pouvez la modifier) :")
                
                # On utilise text_area au lieu de code. 
                # Ça gère les retours à la ligne et permet au client de corriger.
                st.text_area(
                    label="Résultat :",
                    value=response.text,
                    height=250, # Assez grand pour tout lire
                    label_visibility="collapsed"
                )
                
        except Exception as e:
            st.error(f"Erreur : {e}")
            