import base64
import streamlit as st
from supabase import create_client

# Configurazione della pagina (sidebar espandibile/comprimibile di default)
st.set_page_config(
    page_title="Lola's Glam House - Area Admin",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)


# Funzione per impostare lo sfondo in formato Base64 e applicare lo stile personalizzato
def set_custom_theme(png_file):
  try:
    with open(png_file, "rb") as f:
      encoded_string = base64.b64encode(f.read()).decode()
    css = f"""
        <style>
        /* Sfondo generale con la galassia */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Rimozione header di Streamlit */
        header {{visibility: hidden;}}
        
        /* Card centrale in stile Glassmorphism */
        .login-card {{
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(12px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.5);
            max-width: 480px;
            margin: 1rem auto;
        }}

        /* Tipografia del Brand */
        .brand-title {{
            text-align: center;
            color: #4A2E6B;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 0px;
        }}
        .admin-subtitle {{
            text-align: center;
            color: #6C5B7B;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .desc-text {{
            text-align: center;
            color: #8E7B9D;
            font-size: 13px;
            margin-bottom: 20px;
        }}

        /* Personalizzazione dei campi di input (eliminato il nero spento) */
        .stTextInput input {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #3b2b4d !important;
            border-radius: 12px !important;
            border: 1px solid #D7BDE2 !important;
            padding: 10px 15px !important;
            font-size: 15px !important;
        }}
        .stTextInput input:focus {{
            border-color: #8E44AD !important;
            box-shadow: 0 0 8px rgba(142, 68, 173, 0.4) !important;
        }}
        .stTextInput label p {{
            color: #4A2E6B !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }}

        /* Pulsanti personalizzati coordinati */
        .stButton > button {{
            background: linear-gradient(135deg, #8E44AD 0%, #6C3483 100%);
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            box-shadow: 0 4px 15px rgba(142, 68, 173, 0.3);
            transition: all 0.3s ease;
            width: 100%;
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, #732D91 0%, #512E5F 100%);
            box-shadow: 0 6px 20px rgba(142, 68, 173, 0.5);
        }}

        /* Stile della tendina laterale (Sidebar) */
        [data-testid="stSidebar"] {{
            background-color: rgba(245, 238, 247, 0.92);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(142, 68, 173, 0.2);
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #4A2E6B !important;
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
  except FileNotFoundError:
    st.error(
        "Attenzione: file 'background.png' non trovato nella cartella principale"
        " di GitHub."
    )


# Applica lo sfondo e lo stile
set_custom_theme("background.png")

# Stato di sessione per il login
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

# --- TENDINA A SINISTRA (SIDEBAR) ---
with st.sidebar:
  st.markdown("### ✨ Lola's Glam House")
  st.markdown("---")

  if not st.session_state.logged_in:
    st.info(
        "🔒 Effettua l'accesso dall'area centrale per sbloccare la gestione del"
        " salone."
    )
  else:
    st.success("✅ Area Admin attiva")
    menu = st.radio(
        "Navigazione Gestione:",
        [
            "📅 Visualizza Prenotazioni",
            "➕ Nuova Prenotazione",
            "🛠️ Gestione Servizi",
        ],
    )
    st.markdown("---")
    if st.button("🚪 Esci (Logout)"):
      st.session_state.logged_in = False
      st.rerun()

# --- CORPO PRINCIPALE ---
if not st.session_state.logged_in:
  # Centriamo la card di login
  col1, col2, col3 = st.columns([1, 2.5, 1])

  with col2:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: center; font-size: 34px; margin-bottom:'
        ' 5px;">🔒</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand-title">Lola\'s Glam House</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="admin-subtitle">Area Admin</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="desc-text">Inserisci le credenziali per accedere alla'
        " gestione</div>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
      username_input = st.text_input("Nome Utente", placeholder="Es. Lola")
      password_input = st.text_input(
          "Password", type="password", placeholder="La tua password segreta"
      )

      submitted = st.form_submit_button("Accedi all'Area Admin")

      if submitted:
        # Recupero sicuro della password dai Secrets di Streamlit
        admin_password_secret = st.secrets.get("ADMIN_PASSWORD", "")

        if password_input == admin_password_secret and admin_password_secret:
          st.session_state.logged_in = True
          st.success("Accesso riuscito! Benvenuta.")
          st.rerun()
        else:
          st.error("Password errata o non configurata nei Secrets.")

    st.markdown("</div>", unsafe_allow_html=True)

else:
  # --- DASHBOARD DI GESTIONE PRENOTAZIONI CON SUPABASE ---
  st.markdown(
      """
    <div style="background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(10px); padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 1rem;">
        <h1 style="color: #4A2E6B; font-family: sans-serif;">Gestione Appuntamenti</h1>
        <p style="color: #6C5B7B;">Da qui puoi controllare gli appuntamenti delle tue clienti sincronizzati in tempo reale con Supabase.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Connessione a Supabase tramite i Secrets
  try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    st.markdown("### 📋 Elenco Prenotazioni")
    # Esempio di chiamata tabella 'prenotazioni' su Supabase
    response = supabase.table("prenotazioni").select("*").execute()
    data = response.data

    if data:
      st.dataframe(data, use_container_width=True)
    else:
      st.info(
          "Nessuna prenotazione trovata nel database Supabase (tabella"
          " 'prenotazioni')."
      )

  except Exception as e:
    st.warning(
        "⚠️ Configurazione Supabase non trovata o incompleta nei Secrets di"
        " Streamlit. Assicurati di aver inserito SUPABASE_URL e SUPABASE_KEY."
    )
