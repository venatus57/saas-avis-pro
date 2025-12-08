import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Repond'Avis Pro", page_icon="🔒")

# --- SÉCURITÉ : LE DIGICODE ---
def check_password():
    """Retourne True si le mot de passe est bon."""
    # On cherche le mot de passe dans les secrets
    if "MOT_DE_PASSE" not in st.secrets:
        st.error("⚠️ Erreur de configuration : Mot de passe non défini dans les secrets.")
        return False

    # On demande le mot de passe à l'utilisateur
    password_input = st.sidebar.text_input("🔒 Mot de passe client :", type="password")
    
    if password_input == st.secrets["MOT_DE_PASSE"]:
        return True
    elif password_input == "":
        st.warning("Veuillez entrer votre code d'accès personnel.")
        return False
    else:
        st.error("❌ Mot de passe incorrect.")
        return False

# Si le mot de passe n'est pas bon, on arrête tout ici.
if not check_password():
    st.stop()

# =========================================================
# SI ON ARRIVE ICI, C'EST QUE LE CLIENT A PAYÉ ET A LE CODE
# =========================================================

# --- CHARGEMENT CLÉ API ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Clé API introuvable.")
        st.stop()
except Exception:
    st.warning("⚠️ Erreur technique (Clé).")
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
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"Réponds à cet avis Google : '{avis_client}'. Ton: {genre}. Taille: {taille}. Pas de guillemets."
            
            with st.spinner("Rédaction..."):
                response = model.generate_content(prompt)
                st.success("✅ Réponse prête :")
                st.text_area("Résultat :", value=response.text, height=200)
                
        except Exception as e:
            st.error(f"Erreur : {e}")
            
