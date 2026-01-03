import streamlit as st
import google.generativeai as genai
from firebase_admin import firestore

# --- CONFIGURATION DE LA PAGE (Doit être la 1ère commande Stramlit) ---
st.set_page_config(
    page_title="Nexa | E-Réputation Pro",
    page_icon="💠",  # Remplacé par un emoji pro pour l'instant
    layout="wide",    # Utilise toute la largeur de l'écran
    initial_sidebar_state="expanded"
)

# --- CSS PERSONNALISÉ POUR LE LOOK "PRO" ---
# C'est ici qu'on force le design sombre et propre pour régler tes problèmes de lisibilité
st.markdown("""
<style>
    /* Force le fond sombre pour la lisibilité */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Style des titres */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        color: #FFFFFF !important;
    }
    /* Style des boites de résultat */
    .sentiment-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: bold;
        text-align: center;
    }
    .positif { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;}
    .negatif { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;}
    .neutre { background-color: #e2e3e5; color: #383d41; border: 1px solid #d6d8db;}
    
    .conseil-box {
        background-color: #262730; /* Fond sombre pour le conseil */
        color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #4CAF50; /* Petite barre verte sur le côté */
        margin: 20px 0;
        font-size: 1.1em;
    }
    /* Amélioration des boutons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- CONNEXION (Ton code existant) ---
try:
    db = firestore.client()
except:
    st.error("Erreur de connexion à la base de données.")
    st.stop()

# --- SÉCURITÉ (Le "Videur") ---
SECRET_TOKEN = "AZERTY_SUPER_SECRET_123"
query_params = st.query_params
token_recu = query_params.get("token", "")
user_email = query_params.get("email", "Utilisateur Test")

if token_recu != SECRET_TOKEN and user_email != "Utilisateur Test":
     st.markdown("# 🔒 Accès Sécurisé Nécessaire")
     st.error("Veuillez passer par le portail de connexion pour accéder à Nexa.")
     st.link_button("Aller au portail", "https://saas-avis-login.web.app")
     st.stop()


# --- SIDEBAR (Barre latérale) ---
with st.sidebar:
    st.title("💠 Nexa Pro")
    st.write(f"Connecté en tant que : **{user_email}**")
    st.markdown("---")
    st.write("📌 **Menu**")
    # Tu pourras ajouter des pages ici plus tard (Paramètres, Facturation...)
    st.info("Version Bêta 1.2")


# --- CORPS PRINCIPAL DE LA PAGE ---

# Titre Principal Pro
st.title("Gestionnaire d'E-Réputation")
st.markdown("#### *Transformez vos avis clients en opportunités.*")
st.markdown("---")

# Création des onglets
tab1, tab2 = st.tabs(["📝 Traitement des Avis", "📊 Historique & Stats"])

with tab1:
    # --- NOUVEAU LAYOUT : 2 COLONNES ---
    col_gauche, col_droite = st.columns([1, 1.5], gap="large")

    # --- COLONNE DE GAUCHE : PANNEAU DE CONTRÔLE ---
    with col_gauche:
        st.subheader("Panneau de Contrôle")
        st.caption("Configurez votre réponse")
        
        avis_client = st.text_area("Collez l'avis du client ici :", height=200, placeholder="Ex: Très bon service, mais un peu d'attente...")

        col_options1, col_options2 = st.columns(2)
        with col_options1:
             genre = st.selectbox("Ton de la réponse :", ["Professionnel & Empathique", "Chaleureux & Commercial", "Direct & Concis"], index=0)
        with col_options2:
             taille = st.select_slider("Longueur souhaitée :", options=["Courte", "Moyenne", "Longue"], value="Moyenne")

        st.markdown("<br>", unsafe_allow_html=True) # Petit espace
        analyze_button = st.button("✨ GÉNÉRER L'ANALYSE & LA RÉPONSE")

    # --- COLONNE DE DROITE : TABLEAU DE BORD DE RÉSULTAT ---
    with col_droite:
        st.subheader("Tableau de Bord de l'Avis")
        
        # Placeholder : ce qu'on affiche avant qu'on clique sur le bouton
        result_container = st.empty()
        if not analyze_button:
            result_container.info("👈 Configurez l'avis à gauche et cliquez sur Générer pour voir les résultats ici.")

        if analyze_button:
            if not avis_client:
                 st.warning("⚠️ Veuillez coller un avis dans la zone de texte à gauche.")
            else:
                try:
                    # --- IA ---
                    # On utilise le modèle PRO stable
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = f"""
                    Rôle : Expert Service Client.
                    Avis client : "{avis_client}"
                    Ton à employer : {genre}
                    Longueur réponse : {taille}
                    
                    Tes Consignes STRICTES :
                    1. SENTIMENT : Réponds par UN SEUL MOT (Positif, Négatif ou Neutre).
                    2. CONSEIL : Une seule phrase très courte et actionnable (max 15 mots) pour le gérant.
                    3. REPONSE : Rédige uniquement la réponse destinée au client (sans guillemets, sans intro).
                    
                    Format de sortie OBLIGATOIRE :
                    SENTIMENT: ...
                    CONSEIL: ...
                    REPONSE: ...
                    """
                    
                    with st.spinner("🧠 Analyse Nexa en cours..."):
                        response = model.generate_content(prompt)
                        text = response.text
                        
                        # Parsing
                        try:
                            sentiment = text.split("SENTIMENT:")[1].split("CONSEIL:")[0].strip()
                            conseil = text.split("CONSEIL:")[1].split("REPONSE:")[0].strip()
                            reponse_finale = text.split("REPONSE:")[1].strip()
                        except:
                            sentiment = "Neutre"
                            conseil = "Analyse complexe, vérifiez la réponse."
                            reponse_finale = text

                        # SAUVEGARDE BDD
                        db.collection("historique_avis").add({
                            "email_client": user_email,
                            "avis_original": avis_client,
                            "reponse_generee": reponse_finale,
                            "sentiment": sentiment,
                            "conseil": conseil,
                            "date": firestore.SERVER_TIMESTAMP,
                            "ton": genre
                        })

                    # --- AFFICHAGE DES RÉSULTATS DANS LA COLONNE DE DROITE ---
                    # On vide le placeholder
                    result_container.empty()
                    
                    # 1. Le Sentiment
                    st.markdown("##### 1️⃣ Analyse du Sentiment")
                    if "POSITIF" in sentiment.upper(): 
                        st.markdown(f'<div class="sentiment-box positif">😊 {sentiment}</div>', unsafe_allow_html=True)
                    elif "NÉGATIF" in sentiment.upper(): 
                        st.markdown(f'<div class="sentiment-box negatif">😡 {sentiment}</div>', unsafe_allow_html=True)
                    else: 
                        st.markdown(f'<div class="sentiment-box neutre">😐 {sentiment}</div>', unsafe_allow_html=True)

                    # 2. Le Conseil Stratégique
                    st.markdown("##### 2️⃣ Conseil Stratégique Nexa")
                    st.markdown(f'<div class="conseil-box">💡 {conseil}</div>', unsafe_allow_html=True)
                    
                    # 3. La Réponse
                    st.markdown("##### 3️⃣ Proposition de Réponse")
                    st.text_area("Copiez-collez cette réponse :", value=reponse_finale, height=250)
                    st.success("✅ Analyse terminée et sauvegardée.")

                except Exception as e:
                    st.error(f"Une erreur technique est survenue : {e}")

with tab2:
    st.header("Historique de vos traitements")
    st.write("Bientôt disponible : retrouvez ici tous vos anciens avis traités.")
