import base64
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Lola's Glam House - Area Admin",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Funzione per caricare e impostare lo sfondo in formato Base64
def set_background(png_file):
  try:
    with open(png_file, "rb") as f:
      encoded_string = base64.b64encode(f.read()).decode()
    css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Personalizzazione della card centrale */
        .login-container {{
            background-color: rgba(255, 255, 255, 0.90);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            max-width: 480px;
            margin: 2rem auto;
            color: #4a3b5c;
            font-family: sans-serif;
        }}
        .brand-title {{
            text-align: center;
            color: #4A2E6B;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 2px;
            letter-spacing: 0.5px;
        }}
        .title-text {{
            text-align: center;
            color: #5C4378;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .subtitle-text {{
            text-align: center;
            color: #7a688d;
            font-size: 13px;
            margin-bottom: 25px;
        }}
        .icon-header {{
            text-align: center;
            font-size: 30px;
            margin-bottom: 10px;
        }}
        /* Stile personalizzato per i pulsanti per richiamare il brand */
        div.stButton > button:first-child {{
            background-color: #8E44AD;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 600;
        }}
        div.stButton > button:first-child:hover {{
            background-color: #732D91;
            color: white;
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
  except FileNotFoundError:
    st.error(
        "Attenzione: Impossibile trovare il file 'background.png' nella"
        " cartella principale di GitHub."
    )


# Applica lo sfondo
set_background("background.png")

# Layout centrato (ottimizzato sia per PC che per mobile)
col1, col2, col3 = st.columns([1, 3.5, 1])

with col2:
  # Container visivo principale (stile card)
  st.markdown('<div class="login-container">', unsafe_allow_html=True)

  st.markdown('<div class="icon-header">✨</div>', unsafe_allow_html=True)
  st.markdown(
      '<div class="brand-title">Lola\'s Glam House</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="title-text">Area Admin</div>', unsafe_allow_html=True
  )
  st.markdown(
      '<div class="subtitle-text">Inserisci le tue credenziali per'
      " accedere</div>",
      unsafe_allow_html=True,
  )

  # Form di login
  with st.form("login_form"):
    nome = st.text_input("Nome", placeholder="Inserisci il tuo nome")
    cognome = st.text_input("Cognome", placeholder="Inserisci il tuo cognome")
    password = st.text_input(
        "Password", type="password", placeholder="Inserisci la tua password"
    )

    st.markdown(
        '<p style="font-size: 13px; text-align: left; margin-bottom:'
        ' 15px;">Non hai un account? <a href="#" target="_self"'
        ' style="color: #8E44AD; text-decoration: none; font-weight:'
        ' bold;">Registrati</a></p>',
        unsafe_allow_html=True,
    )

    # Pulsanti
    submit_btn = st.form_submit_button("Accedi", use_container_width=True)
    forgot_btn = st.form_submit_button(
        "Password dimenticata?", use_container_width=True
    )

    if submit_btn:
      # Logica di controllo (qui andrà integrato Supabase auth)
      if nome and cognome and password:
        st.success(f"Benvenuta in Lola's Glam House, {nome} {cognome}!")
      else:
        st.warning("Compila tutti i campi per procedere.")

    if forgot_btn:
      st.info("Funzione di recupero password in arrivo.")

  st.markdown("</div>", unsafe_allow_html=True)
