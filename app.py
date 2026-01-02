import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="NEXA - Intelligence Artificielle",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS & HACKS ---
corporate_css = """
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .main .block-container { background-color: #ffffff; padding: 40px !important; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 900px; margin-top: 40px !important; border: 1px solid #e1e4e8; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    h1 { color: #1a202c !important; font-weight: 700; font-size: 2.2rem; letter-spacing: -1px; }
    .sentiment-box { padding: 12px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; text-align: center; font-size: 1.1rem; }
    .positif { background-color: #d1fae5; color: #065f46; border: 1px solid #34d399; }
    .negatif { background-color: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
    .neutre { background-color: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
    .conseil-box { background-color: #ebf8ff; border-left: 5px solid #4299e1; color: #2b6cb0; padding: 15px; margin-bottom: 25px; }
</style>
"""
st.markdown(corporate_css, unsafe_allow_html=True)

# --- SÉCURITÉ & IDENTIFICATION ---
# --- SÉCURITÉ (Le "Videur") ---
# 1. On définit le mot de passe secret (le même que dans index.html)
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"

# 2. On récupère les infos de l'URL
query_params = st.query_params
token_recu = query_params.get("token", "")
user_email = query_params.get("email", "Inconnu")

# 3. VERIFICATION : Si le token n'est pas bon, on BLOQUE tout.
if token_recu != SECRET_TOKEN:
    st.error("⛔ Accès refusé. Vous devez passer par le portail de connexion.")
    # On ajoute un bouton pour retourner au login (remplace par ton lien Firebase)
    st.link_button("Aller à la connexion", "https://gen-lang-client-0236145808.web.app") 
    st.stop() # Arrête le chargement de la page ici

# 4. Si on est passé, on affiche l'utilisateur
st.sidebar.success(f"👤 Connecté : {user_email}")
# --- FIREBASE ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Erreur Base de Données : {e}")
        st.stop()

db = firestore.client()

# --- IA GOOGLE ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass

# --- INTERFACE ---
st.markdown("<h1>NEXA</h1>", unsafe_allow_html=True)
st.markdown("<p style='margin-bottom: 30px; color: #718096;'>Intelligence Artificielle de Réputation</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡ Analyse & Réponse", "📊 Mon Historique"])

# --- ONGLET 1 : GÉNÉRATEUR ---
with tab1:
    st.markdown("<h3>1️⃣ L'avis à traiter</h3>", unsafe_allow_html=True)
    avis_client = st.text_area("Avis", label_visibility="collapsed", height=150, placeholder="Collez l'avis du client ici...")

    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox("Ton", ["Professionnel", "Chaleureux", "Commercial", "Ferme"], label_visibility="collapsed")
    with col2:
        taille = st.radio("Longueur", ["Courte", "Standard", "Détaillée"], horizontal=True, label_visibility="collapsed")

    st.write("") 

    if st.button("✨ ANALYSER & RÉPONDRE"):
        if not avis_client:
            st.warning("⚠️ L'avis est vide.")
        else:
            try:
                # 1. IA
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Agis comme un expert. Avis : "{avis_client}". Ton : {genre}.
                Format : SENTIMENT: ... CONSEIL: ... REPONSE: ...
                """
                
                with st.spinner("🧠 Analyse en cours..."):
                    response = model.generate_content(prompt)
                    text = response.text
                    try:
                        sentiment = text.split("SENTIMENT:")[1].split("CONSEIL:")[0].strip()
                        conseil = text.split("CONSEIL:")[1].split("REPONSE:")[0].strip()
                        reponse_finale = text.split("REPONSE:")[1].strip()
                    except:
                        sentiment = "Neutre"; conseil = "Voir ci-dessous"; reponse_finale = text

                    # 2. SAUVEGARDE SÉCURISÉE (Avec l'email !)
                    db.collection("historique_avis").add({
                        "email_client": user_email,  # <--- C'est ici que la magie opère
                        "avis_original": avis_client,
                        "reponse_generee": reponse_finale,
                        "sentiment": sentiment,
                        "conseil": conseil,
                        "date": firestore.SERVER_TIMESTAMP,
                        "ton": genre
                    })

                # AFFICHAGE
                st.markdown("---")
                if "POSITIF" in sentiment.upper(): st.markdown(f'<div class="sentiment-box positif">😊 {sentiment}</div>', unsafe_allow_html=True)
                elif "NÉGATIF" in sentiment.upper(): st.markdown(f'<div class="sentiment-box negatif">😡 {sentiment}</div>', unsafe_allow_html=True)
                else: st.markdown(f'<div class="sentiment-box neutre">😐 {sentiment}</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="conseil-box">💡 <b>Conseil :</b> {conseil}</div>', unsafe_allow_html=True)
                st.subheader("✍️ Réponse :")
                st.text_area("Résultat", value=reponse_finale, height=200)
                st.success("✅ Sauvegardé dans VOTRE espace personnel.")

            except Exception as e:
                st.error(f"Erreur : {e}")

# --- ONGLET 2 : HISTORIQUE FILTRÉ ---
with tab2:
    st.header(f"💾 Historique de : {user_email}")
    
    if st.button("🔄 Rafraîchir"):
        st.rerun()

    try:
        # 1. On récupère TOUS les avis de cet utilisateur spécifique
        # (On filtre côté Python pour éviter les erreurs d'index Firebase complexes pour l'instant)
        docs = db.collection("historique_avis").where("email_client", "==", user_email).stream()
        
        # 2. On les transforme en liste pour pouvoir les trier
        liste_avis = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            liste_avis.append(data)
            
        # 3. On trie par date (du plus récent au plus vieux)
        # (Astuce : on le fait ici en Python, c'est plus simple que de configurer Firebase)
        liste_avis.sort(key=lambda x: x.get('date', 0) if x.get('date') else 0, reverse=True)
        
        # 4. Affichage
        if not liste_avis:
            st.info("Aucun historique pour ce compte.")
        else:
            for data in liste_avis:
                titre = f"📅 {data.get('sentiment', 'Avis')} - {data.get('avis_original', '')[:40]}..."
                with st.expander(titre):
                    st.markdown(f"**Avis Client :** {data.get('avis_original')}")
                    st.info(data.get('reponse_generee'))
                    st.caption(f"Conseil : {data.get('conseil')}")
            
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
