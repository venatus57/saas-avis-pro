import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nexa | E-Réputation Pro",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONNALISÉ (DESIGN PRO) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; color: #FFFFFF !important; }
    .sentiment-box { padding: 15px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; text-align: center; color: black; }
    .positif { background-color: #d4edda; border: 1px solid #c3e6cb;}
    .negatif { background-color: #f8d7da; border: 1px solid #f5c6cb;}
    .neutre { background-color: #e2e3e5; border: 1px solid #d6d8db;}
    .conseil-box { background-color: #262730; color: #FFFFFF; padding: 20px; border-radius: 8px; border-left: 5px solid #4CAF50; margin: 20px 0; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #FF4B4B; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #FF2B2B; }
</style>
""", unsafe_allow_html=True)

# --- CONNEXION FIREBASE (CORRECTIF BLINDÉ) ---
if not firebase_admin._apps:
    try:
        # 1. On force la conversion en vrai dictionnaire (pour éviter l'erreur ValueError)
        key_dict = dict(st.secrets["firebase"])
        
        # 2. On répare la clé privée si elle contient des retours à la ligne cassés
        # (C'est souvent ça qui plante sur le Cloud)
        if "private_key" in key_dict:
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")

        # 3. On se connecte
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Erreur critique de connexion Firebase : {e}")
        st.stop()

# On récupère le client Database
db = firestore.client()

# --- SÉCURITÉ ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"
query_params = st.query_params
token_recu = query_params.get("token", "")
user_email = query_params.get("email", "Utilisateur Test")

# En prod, on bloque si pas de token (sauf si c'est toi qui teste)
if token_recu != SECRET_TOKEN and user_email == "Utilisateur Test":
    pass 
elif token_recu != SECRET_TOKEN:
     st.markdown("# 🔒 Accès Sécurisé Nécessaire")
     st.error("Veuillez passer par le portail de connexion.")
     st.link_button("Aller au portail", "https://saas-avis-login.web.app") 
     st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("💠 Nexa Pro")
    st.caption("Solution d'Intelligence Artificielle")
    st.markdown("---")
    st.write(f"👤 **{user_email}**")
    st.success("🟢 Connecté")
    st.markdown("---")
    st.info("Version Bêta 1.2")

# --- CORPS PRINCIPAL ---
st.title("Gestionnaire d'E-Réputation")
st.markdown("#### *Transformez vos avis clients en opportunités.*")
st.markdown("---")

tab1, tab2 = st.tabs(["📝 Traitement des Avis", "📊 Historique & Stats"])

with tab1:
    col_gauche, col_droite = st.columns([1, 1], gap="large")

    with col_gauche:
        st.subheader("1. Configuration")
        avis_client = st.text_area("Avis du client :", height=200, placeholder="Collez l'avis ici...")
        
        c1, c2 = st.columns(2)
        with c1:
             genre = st.selectbox("Ton :", ["Professionnel", "Commercial", "Direct"], index=0)
        with c2:
             taille = st.select_slider("Longueur :", options=["Courte", "Moyenne", "Longue"], value="Moyenne")

        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("✨ GÉNÉRER L'ANALYSE")

    with col_droite:
        st.subheader("2. Résultats Nexa")
        result_container = st.empty()
        
        if not analyze_button:
            result_container.info("👈 En attente d'analyse...")

        if analyze_button and avis_client:
            try:
                # Modèle Gemini PRO (Stable)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = f"""
                Rôle : Expert Service Client.
                Avis : "{avis_client}"
                Ton : {genre}
                Longueur : {taille}
                Consignes :
                1. SENTIMENT (1 mot: Positif/Négatif/Neutre)
                2. CONSEIL (Max 15 mots)
                3. REPONSE (Texte direct pour le client)
                Format :
                SENTIMENT: ...
                CONSEIL: ...
                REPONSE: ...
                """
                
                with st.spinner("🧠 Analyse en cours..."):
                    response = model.generate_content(prompt)
                    text = response.text
                    
                    try:
                        sentiment = text.split("SENTIMENT:")[1].split("CONSEIL:")[0].strip()
                        conseil = text.split("CONSEIL:")[1].split("REPONSE:")[0].strip()
                        reponse_finale = text.split("REPONSE:")[1].strip()
                    except:
                        sentiment = "Neutre"; conseil = "Vérifier manuellement"; reponse_finale = text

                    # Sauvegarde BDD
                    db.collection("historique_avis").add({
                        "email_client": user_email,
                        "avis_original": avis_client,
                        "reponse_generee": reponse_finale,
                        "sentiment": sentiment,
                        "conseil": conseil,
                        "date": firestore.SERVER_TIMESTAMP
                    })

                # Affichage
                result_container.empty()
                st.markdown("##### 🔍 Sentiment")
                if "POSITIF" in sentiment.upper(): st.markdown(f'<div class="sentiment-box positif">😊 {sentiment}</div>', unsafe_allow_html=True)
                elif "NÉGATIF" in sentiment.upper(): st.markdown(f'<div class="sentiment-box negatif">😡 {sentiment}</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="sentiment-box neutre">😐 {sentiment}</div>', unsafe_allow_html=True)

                st.markdown("##### 💡 Conseil")
                st.markdown(f'<div class="conseil-box">{conseil}</div>', unsafe_allow_html=True)
                
                st.markdown("##### ✍️ Réponse")
                st.text_area("À copier :", value=reponse_finale, height=200)
                st.success("✅ Sauvegardé.")

            except Exception as e:
                st.error(f"Erreur : {e}")

with tab2:
    st.write("Historique à venir...")
