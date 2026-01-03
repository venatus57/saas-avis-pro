import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

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

# --- CONNEXION FIREBASE BLINDÉE ---
if not firebase_admin._apps:
    try:
        key_dict = dict(st.secrets["firebase"])
        if "private_key" in key_dict:
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Erreur critique de connexion Firebase : {e}")
        st.stop()

db = firestore.client()

# --- SÉCURITÉ ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"
query_params = st.query_params
token_recu = query_params.get("token", "")
user_email = query_params.get("email", "Utilisateur Test")

# Bloquage si pas de token (sauf pour le testeur)
if token_recu != SECRET_TOKEN and user_email == "Utilisateur Test":
    pass 
elif token_recu != SECRET_TOKEN:
     st.markdown("# 🔒 Accès Refusé")
     st.error("Accès interdit. Veuillez passer par le portail.")
     st.link_button("Aller au portail", "https://gen-lang-client-0236145808.web.app") 
     st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("💠 Nexa Pro")
    st.caption("Intelligence Artificielle")
    st.markdown("---")
    st.write(f"👤 **{user_email}**")
    st.success("🟢 En ligne")
    st.markdown("---")
    st.info("v1.3 - Historique Activé")

# --- CORPS PRINCIPAL ---
st.title("Gestionnaire d'E-Réputation")
st.markdown("#### *Transformez vos avis clients en opportunités.*")
st.markdown("---")

tab1, tab2 = st.tabs(["📝 Traitement des Avis", "📊 Historique Complet"])

# --- ONGLET 1 : TRAITEMENT ---
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
                # Modèle Gemini PRO
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
                        "date": firestore.SERVER_TIMESTAMP,
                        "ton": genre
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

# --- ONGLET 2 : HISTORIQUE (C'est ici que ça change !) ---
with tab2:
    st.header("📂 Vos Archives")
    
    # Bouton pour rafraîchir manuellement
    if st.button("🔄 Actualiser la liste"):
        st.rerun()

    try:
        # On récupère tous les avis de la base de données
        # Note : Pour filtrer par utilisateur, il faudrait créer un index dans Firebase.
        # Pour l'instant, on affiche tout pour éviter les bugs d'index.
        docs = db.collection("historique_avis").stream()
        
        # On convertit en liste
        liste_avis = []
        for doc in docs:
            avis_data = doc.to_dict()
            avis_data['id'] = doc.id
            liste_avis.append(avis_data)
        
        # S'il n'y a rien
        if not liste_avis:
            st.info("📭 Aucun historique trouvé. Commencez par traiter un avis !")
        else:
            # On affiche du plus récent au plus vieux (astuce Python simple)
            liste_avis.reverse()
            
            for avis in liste_avis:
                # Titre de l'accordéon (Date + Sentiment)
                # On gère la date proprement
                date_display = "Date inconnue"
                if avis.get('date'):
                    date_display = avis.get('date').strftime("%d/%m/%Y à %H:%M")
                
                titre = f"{date_display} - {avis.get('sentiment', 'Analyse')}"
                
                with st.expander(titre):
                    st.caption(f"Client : {avis.get('email_client', 'Inconnu')}")
                    st.markdown(f"**🗣️ Avis Original :**")
                    st.info(avis.get('avis_original', ''))
                    
                    st.markdown(f"**✍️ Réponse Générée :**")
                    st.code(avis.get('reponse_generee', ''), language=None)
                    
                    st.markdown(f"**💡 Conseil donné :** {avis.get('conseil', '')}")

    except Exception as e:
        st.warning(f"Impossible de charger l'historique pour le moment : {e}")
