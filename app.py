import base64
from datetime import datetime, time, timedelta
import hashlib
import os
import re
import secrets
import uuid
from zoneinfo import ZoneInfo
import pandas as pd
import psycopg2
import streamlit as st
from sqlalchemy import create_engine, text

# Configurazione Pagina
st.set_page_config(
    page_title="Lola's Glam House",
    page_icon="✨",
    layout="centered",
)


# Funzione per convertire l'immagine di sfondo in base64
def get_base64_image(image_path):
  if os.path.exists(image_path):
    with open(image_path, "rb") as f:
      data = f.read()
    return base64.b64encode(data).decode()
  return None


bg_base64 = None
for possible_bg in [
    "background.png",
    "background.jpg",
    "background.jpeg",
    "image.png",
]:
  bg_base64 = get_base64_image(possible_bg)
  if bg_base64:
    break

# Stile CSS Professionale: Sfondo statico di alta qualità, Sidebar coordinata e leggibilità perfetta
bg_css_style = (
    f"""
    .stApp {{
        background-image: linear-gradient(rgba(35, 12, 50, 0.45), rgba(20, 5, 35, 0.55)), url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }}
    """
    if bg_base64
    else """
    .stApp {
        background: linear-gradient(135deg, #2c163a 0%, #4a2858 100%);
        font-family: 'Inter', sans-serif;
    }
    """
)

st.markdown(
    f"""
    <style>
    {bg_css_style}

    /* Rimozione parti nere e tristi: Sidebar e Header coordinati in stile Glam */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #3d1b52 0%, #200a30 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.15);
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Vetro satinato elegante per i container principali */
    div.stVerticalBlockBorderWrapper, div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(255, 255, 255, 0.14) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-radius: 24px !important;
        padding: 28px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35) !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] div {{
        background-color: transparent !important;
    }}

    /* Campi di input ad altissima leggibilità */
    .stTextInput input, .stDateInput input, .stNumberInput input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.8) !important;
        padding: 10px 14px !important;
        color: #1f0b2e !important;
        font-weight: 600 !important;
    }}

    /* Selectbox e menu a tendina leggibili */
    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.8) !important;
        color: #1f0b2e !important;
        font-weight: 600 !important;
    }}

    div[data-baseweb="select"] span {{
        color: #1f0b2e !important;
        font-weight: 600 !important;
    }}

    /* Pulsanti con sfumature Glam ed effetto interattivo */
    div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {{
        background: linear-gradient(135deg, #b070d8 0%, #7b38a0 50%, #9c27b0 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        width: 100% !important;
        padding: 12px 24px !important;
        box-shadow: 0 8px 25px rgba(123, 56, 160, 0.45) !important;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
        background: linear-gradient(135deg, #c48de8 0%, #8e42b8 50%, #ab47bc) !important;
        box-shadow: 0 12px 30px rgba(142, 66, 184, 0.7) !important;
        transform: translateY(-2px);
    }}

    /* Tipografia chiara e raffinata */
    h1, h2, h3, h4 {{
        color: #fce4ec !important;
        font-weight: 700 !important;
        text-align: center;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
    }}

    p, span, label, .stMarkdown, [data-testid="stSidebar"] label {{
        color: #f3e5f5 !important;
        font-weight: 500;
    }}

    /* Tab di navigazione personalizzate */
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.12);
        border-radius: 30px !important;
        color: #f3e5f5;
        font-weight: 600;
        padding: 10px 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        transition: all 0.3s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #b070d8 0%, #7b38a0) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 6px 20px rgba(123, 56, 160, 0.6) !important;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""",
    unsafe_allow_html=True,
)


# Connessione Database Supabase / PostgreSQL
@st.cache_resource
def get_db_engine():
  db_url = st.secrets["supabase"]["db_url"]
  return create_engine(db_url, pool_pre_ping=True)


engine = get_db_engine()


@st.cache_resource
def init_db():
  with engine.begin() as conn:
    conn.execute(
        text("""
            CREATE TABLE IF NOT EXISTS prenotazioni (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                data TEXT NOT NULL,
                ora TEXT NOT NULL,
                trattamento TEXT NOT NULL,
                data_creazione TEXT NOT NULL,
                device_id TEXT,
                stato_presenza TEXT DEFAULT 'Assente',
                codice_fiscale TEXT,
                codice_fiscale_2 TEXT
            )
        """)
    )

    for col, col_type in [
        ("device_id", "TEXT"),
        ("stato_presenza", "TEXT DEFAULT 'Assente'"),
        ("codice_fiscale", "TEXT"),
        ("codice_fiscale_2", "TEXT"),
    ]:
      try:
        conn.execute(
            text(f"ALTER TABLE prenotazioni ADD COLUMN IF NOT EXISTS {col} {col_type}")
        )
      except Exception:
        pass

    conn.execute(
        text("""
            CREATE TABLE IF NOT EXISTS banned_devices (
                device_id TEXT PRIMARY KEY
            )
        """)
    )

    conn.execute(
        text("""
            CREATE TABLE IF NOT EXISTS utenti (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                cognome TEXT NOT NULL,
                codice_fiscale TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                data_registrazione TEXT NOT NULL
            )
        """)
    )


init_db()


def elimina_prenotazioni_passate():
  try:
    local_tz = ZoneInfo("Europe/Rome")
    oggi_str = datetime.now(local_tz).strftime("%Y-%m-%d")
  except Exception:
    oggi_str = datetime.now().strftime("%Y-%m-%d")

  with engine.begin() as conn:
    conn.execute(
        text("DELETE FROM prenotazioni WHERE data < :oggi"), {"oggi": oggi_str}
    )


elimina_prenotazioni_passate()


def hash_password(password, salt=None):
  if salt is None:
    salt = secrets.token_hex(16)
  pwd_hash = hashlib.pbkdf2_hmac(
      "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
  ).hex()
  return salt, pwd_hash


def verifica_password(password, salt, pwd_hash_atteso):
  _, pwd_hash_calcolato = hash_password(password, salt)
  return secrets.compare_digest(pwd_hash_calcolato, pwd_hash_atteso)


def registra_utente(nome, cognome, cf, password):
  salt, pwd_hash = hash_password(password)
  data_reg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  try:
    with engine.begin() as conn:
      res = conn.execute(
          text("SELECT id FROM utenti WHERE codice_fiscale = :cf"),
          {"cf": cf.upper()},
      ).fetchone()
      if res:
        return False, "Esiste già un utente registrato con questo Codice Fiscale."
      conn.execute(
          text("""
                    INSERT INTO utenti (nome, cognome, codice_fiscale, password_salt, password_hash, data_registrazione) 
                    VALUES (:nome, :cognome, :cf, :salt, :pwd_hash, :data_reg)
                """),
          {
              "nome": nome.title(),
              "cognome": cognome.title(),
              "cf": cf.upper(),
              "salt": salt,
              "pwd_hash": pwd_hash,
              "data_reg": data_reg,
          },
      )
    return True, "Registrazione completata con successo!"
  except Exception as e:
    return False, str(e)


def login_utente(nome, cognome, password):
  try:
    with engine.begin() as conn:
      res = conn.execute(
          text("""
                    SELECT id, nome, cognome, codice_fiscale, password_salt, password_hash 
                    FROM utenti 
                    WHERE UPPER(nome) = :nome AND UPPER(cognome) = :cognome
                """),
          {"nome": nome.strip().upper(), "cognome": cognome.strip().upper()},
      ).fetchone()
      if res:
        uid, u_nome, u_cognome, u_cf, salt, pwd_hash = res
        if verifica_password(password, salt, pwd_hash):
          return {
              "id": uid,
              "nome": u_nome,
              "cognome": u_cognome,
              "codice_fiscale": u_cf,
          }, None
      return None, "Credenziali non valide."
  except Exception as e:
    return None, str(e)


def aggiorna_password_utente(nome, cognome, cf, nuova_password):
  try:
    with engine.begin() as conn:
      res = conn.execute(
          text("""
                    SELECT id FROM utenti 
                    WHERE UPPER(nome) = :nome AND UPPER(cognome) = :cognome AND UPPER(codice_fiscale) = :cf
                """),
          {
              "nome": nome.strip().upper(),
              "cognome": cognome.strip().upper(),
              "cf": cf.strip().upper(),
          },
      ).fetchone()
      if not res:
        return False, "Nessun account trovato con i dati inseriti."
      uid = res[0]
      salt, pwd_hash = hash_password(nuova_password)
      conn.execute(
          text(
              "UPDATE utenti SET password_salt = :salt, password_hash ="
              " :pwd_hash WHERE id = :id"
          ),
          {"salt": salt, "pwd_hash": pwd_hash, "id": uid},
      )
    return True, "Password reimpostata con successo!"
  except Exception as e:
    return False, str(e)


def get_orari_per_data(data):
  if isinstance(data, str):
    d = datetime.strptime(data, "%Y-%m-%d").date()
  else:
    d = data
  weekday = d.weekday()
  if weekday == 5:
    return ["09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00"]
  elif weekday == 6:
    return []
  else:
    return [
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
    ]


def get_client_device_id():
  if "device_id_internale" not in st.session_state:
    if "dev_id" in st.query_params and st.query_params["dev_id"].strip():
      st.session_state["device_id_internale"] = (
          f"device_{st.query_params['dev_id']}"
      )
    else:
      unique_id = str(uuid.uuid4()).replace("-", "")[:24]
      st.query_params["dev_id"] = unique_id
      st.session_state["device_id_internale"] = f"device_{unique_id}"
  return st.session_state["device_id_internale"]


def get_current_time_local():
  try:
    local_tz = ZoneInfo("Europe/Rome")
    return datetime.now(local_tz)
  except Exception:
    return datetime.now()


@st.dialog("📜 Regolamento di Lola's Glam House")
def popup_regolamento():
  st.markdown("""
        * ⏱️ **Puntualità:** Si raccomanda di arrivare puntuali all'appuntamento.
        * ⏱️ **Disdette:** Si richiede un preavviso minimo di 24 ore per la cancellazione.
        * ✨ **Trattamenti:** I nostri servizi sono pensati per valorizzare la tua bellezza naturale.
    """)
  if st.button("✨ Ho letto e accetto", use_container_width=True):
    st.session_state["regolamento_accettato"] = True
    st.session_state["mostra_dialog_regolamento"] = False
    st.rerun()


# Catalogo Trattamenti di Lola's Glam House Aggiornato
CATALOGO_SERVIZI = {
    "💅 UNGHIE": ["Mani", "Piedi", "Semipermanente o gel", "Refil", "Ricostruzione"],
    "👁️ CIGLIA": ["Montaggio", "Smontaggio", "Refil"],
    "💇‍♀️ CAPELLI": [
        "Taglio",
        "Colore",
        "Piega",
        "Taglio + Piega",
        "Taglio + Colore + Piega",
        "Colore + Piega",
        "Acconciatura",
        "Meches",
        "Balayage",
        "Permanente",
    ],
    "💆‍♀️ MASSAGGIO": ["Relax", "Anticellulite", "Scrub"],
    "✨ SOPRACCIGLIA": ["Pinzetta"],
    "🪞 CERETTA": [
        "Gambe intere",
        "Metà gambe",
        "Addome",
        "Petto",
        "Inguine",
        "Baffetti",
        "Braccia",
        "Ascelle",
        "Schiena",
        "Total body",
    ],
    "🌸 VISO": [
        "Pulizia viso",
        "Massaggio antirughe",
        "Trattamento viso con spatola ultrasuoni",
    ],
}

logo_path = None
for possible_name in ["logo.png", "logo.PNG", "logo.jpg", "logo.jpeg"]:
  if os.path.exists(possible_name):
    logo_path = possible_name
    break

# --- BARRA LATERALE ADMIN ---
if logo_path:
  st.sidebar.image(logo_path, use_container_width=True)

st.sidebar.title("🔐 Area Admin")
ADMIN_PASSWORD = st.secrets.get("admin_password", "GlamHouse2026")

if "admin_logged_in" not in st.session_state:
  st.session_state["admin_logged_in"] = False

if not st.session_state["admin_logged_in"]:
  admin_pass = st.sidebar.text_input(
      "Password Admin", type="password", key="admin_pwd_input"
  )
  if admin_pass == ADMIN_PASSWORD:
    st.session_state["admin_logged_in"] = True
    st.rerun()
  elif admin_pass != "":
    st.sidebar.error("Password errata!")

if st.session_state["admin_logged_in"]:
  st.sidebar.success("Accesso Admin attivo")
  if st.sidebar.button("🚪 Esci dall'Area Admin"):
    st.session_state["admin_logged_in"] = False
    st.rerun()

# --- VISTA 1: PANNELLO AMMINISTRATORE ---
if st.session_state["admin_logged_in"]:
  st.title("✨ Lola's Glam House - Admin Panel")

  if st.button("🔄 Aggiorna Dati"):
    st.rerun()

  st.markdown("<br>", unsafe_allow_html=True)

  with st.container(border=True):
    st.subheader("📋 Elenco Prenotazioni Attive")
    df = pd.read_sql_query(
        "SELECT id, codice_fiscale, data, ora, trattamento, device_id FROM"
        " prenotazioni ORDER BY data DESC, ora ASC",
        engine,
    )
    if not df.empty:
      st.dataframe(df, use_container_width=True)
    else:
      st.info("Nessuna prenotazione presente.")

  with st.container(border=True):
    st.subheader("🔓 Gestione Chiusure Agenda")
    data_intervallo = st.date_input(
        "Data o Intervallo",
        value=(datetime.today(), datetime.today()),
        min_value=datetime.today(),
    )
    modo_intervallo = st.radio("Ambito", ["Tutta la giornata", "Orario specifico"])

    TUTTI_GLI_ORARI_ADMIN = [
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
    ]
    ora_intervallo = (
        st.selectbox("Orario", TUTTI_GLI_ORARI_ADMIN)
        if modo_intervallo == "Orario specifico"
        else None
    )

    col_b1, col_b2 = st.columns(2)
    with col_b1:
      btn_blocca = st.button("🔒 Blocca")
    with col_b2:
      btn_sblocca = st.button("🔓 Sblocca")

    if btn_blocca or btn_sblocca:
      lista_date = (
          [str(data_intervallo)]
          if not isinstance(data_intervallo, tuple)
          else [str(d) for d in data_intervallo]
      )
      ora_attuale_str = get_current_time_local().strftime("%Y-%m-%d %H:%M")
      with engine.begin() as conn:
        if btn_blocca:
          for d_str in lista_date:
            if modo_intervallo == "Tutta la giornata":
              for h in get_orari_per_data(d_str):
                conn.execute(
                    text(
                        "INSERT INTO prenotazioni (nome, data, ora, trattamento,"
                        " data_creazione, device_id, stato_presenza) VALUES"
                        " (:n, :d, :o, :t, :dc, :di, :sp)"
                    ),
                    {
                        "n": "🔒 CHIUSO",
                        "d": d_str,
                        "o": h,
                        "t": "Chiusura Admin",
                        "dc": ora_attuale_str,
                        "di": "SYSTEM",
                        "sp": "Chiuso",
                    },
                )
            else:
              conn.execute(
                  text(
                      "INSERT INTO prenotazioni (nome, data, ora, trattamento,"
                      " data_creazione, device_id, stato_presenza) VALUES"
                      " (:n, :d, :o, :t, :dc, :di, :sp)"
                  ),
                  {
                      "n": "🔒 CHIUSO",
                      "d": lista_date[0],
                      "o": ora_intervallo,
                      "t": "Chiusura Admin",
                      "dc": ora_attuale_str,
                      "di": "SYSTEM",
                      "sp": "Chiuso",
                  },
              )
          st.success("Blocco applicato!")
        elif btn_sblocca:
          for d_str in lista_date:
            if modo_intervallo == "Tutta la giornata":
              conn.execute(
                  text("DELETE FROM prenotazioni WHERE data = :d"), {"d": d_str}
              )
            else:
              conn.execute(
                  text(
                      "DELETE FROM prenotazioni WHERE data = :d AND ora = :o"
                  ),
                  {"d": d_str, "o": ora_intervallo},
              )
          st.success("Sblocco applicato!")
      st.rerun()

  with st.container(border=True):
    st.subheader("🛡️ Gestione Cancellazioni")
    id_da_eliminare = st.number_input(
        "ID Prenotazione da eliminare", min_value=0, step=1
    )
    if st.button("Elimina Prenotazione"):
      if id_da_eliminare > 0:
        with engine.begin() as conn:
          conn.execute(
              text("DELETE FROM prenotazioni WHERE id = :id"),
              {"id": id_da_eliminare},
          )
        st.success("Eliminata!")
        st.rerun()

  with st.container(border=True):
    st.subheader("👤 Clienti Registrati")
    df_utenti = pd.read_sql_query(
        "SELECT id, nome, cognome, codice_fiscale, data_registrazione FROM"
        " utenti",
        engine,
    )
    if not df_utenti.empty:
      st.dataframe(df_utenti, use_container_width=True)

# --- VISTA 2: PAGINA PRINCIPALE CLIENTE ---
else:
  client_device_id = get_client_device_id()
  with engine.begin() as conn:
    is_banned = conn.execute(
        text("SELECT device_id FROM banned_devices WHERE device_id = :dev_id"),
        {"dev_id": client_device_id},
    ).fetchone()

  if is_banned:
    st.error("⛔ Accesso negato.")
  else:
    if "utente_loggato" not in st.session_state:
      if logo_path:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
          st.image(logo_path, use_container_width=True)

      st.title("✨ Lola's Glam House ✨")
      st.markdown("#### 👤 Accedi al tuo account o registrati")

      tab_login, tab_registrazione = st.tabs(["🔑 Accedi", "📝 Registrati"])

      with tab_login:
        if st.session_state.get("vista_recupero", False):
          st.markdown("##### 🔑 Reimposta Password")
          with st.form("form_recupero"):
            rec_nome = st.text_input("Nome *")
            rec_cognome = st.text_input("Cognome *")
            rec_cf = st.text_input("Codice Fiscale *")
            rec_nuova_pw = st.text_input("Nuova Password *", type="password")
            rec_conf_pw = st.text_input(
                "Conferma Password *", type="password"
            )

            col_r1, col_r2 = st.columns(2)
            with col_r1:
              submit_rec = st.form_submit_button("Aggiorna")
            with col_r2:
              submit_ind = st.form_submit_button("Indietro")

            if submit_ind:
              st.session_state["vista_recupero"] = False
              st.rerun()
            if submit_rec:
              if rec_nuova_pw != rec_conf_pw:
                st.error("Le password non coincidono.")
              else:
                succ, msg = aggiorna_password_utente(
                    rec_nome, rec_cognome, rec_cf, rec_nuova_pw
                )
                if succ:
                  st.success(msg)
                  st.session_state["vista_recupero"] = False
                  st.rerun()
                else:
                  st.error(msg)
        else:
          with st.form("form_login"):
            login_nome = st.text_input("Nome *")
            login_cognome = st.text_input("Cognome *")
            login_password = st.text_input("Password *", type="password")

            col_l1, col_l2 = st.columns(2)
            with col_l1:
              submit_log = st.form_submit_button("Accedi")
            with col_l2:
              submit_rec_click = st.form_submit_button("Password dimenticata?")

            if submit_log:
              utente, err = login_utente(
                  login_nome, login_cognome, login_password
              )
              if utente:
                st.session_state["utente_loggato"] = utente
                st.rerun()
              else:
                st.error(err)
            elif submit_rec_click:
              st.session_state["vista_recupero"] = True
              st.rerun()

      with tab_registrazione:
        with st.form("form_reg"):
          reg_nome = st.text_input("Nome *")
          reg_cognome = st.text_input("Cognome *")
          reg_cf = st.text_input("Codice Fiscale *")
          reg_password = st.text_input("Password *", type="password")
          reg_password_conf = st.text_input(
              "Conferma Password *", type="password"
          )
          submit_reg = st.form_submit_button("Crea Account")

          if submit_reg:
            if reg_password != reg_password_conf:
              st.error("Le password non coincidono.")
            else:
              succ, msg = registra_utente(
                  reg_nome, reg_cognome, reg_cf, reg_password
              )
              if succ:
                st.success(msg)
              else:
                st.error(msg)
      st.stop()

    if logo_path:
      c1, c2, c3 = st.columns([1, 2, 1])
      with c2:
        st.image(logo_path, use_container_width=True)

    st.title("✨ Lola's Glam House ✨")
    st.markdown(
        f"<p style='text-align: center;'>Benvenuta/o, {st.session_state['utente_loggato']['nome']} 💖</p>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📅 Prenota", "ℹ️ Info", "📜 Regolamento"])

    if st.session_state.get("mostra_dialog_regolamento", False):
      popup_regolamento()

    if (
        st.session_state.get("regolamento_accettato", False)
        and "pending_booking" in st.session_state
    ):
      pb = st.session_state["pending_booking"]
      data_creazione_str = get_current_time_local().strftime("%Y-%m-%d %H:%M")
      with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO prenotazioni (nome, data, ora, trattamento,"
                " data_creazione, device_id, stato_presenza, codice_fiscale,"
                " codice_fiscale_2) VALUES (:n, :d, :o, :t, :dc, :di, :sp,"
                " :cf1, :cf2)"
            ),
            {
                "n": pb["nome_completo"],
                "d": str(pb["data_scelta"]),
                "o": pb["ora_scelta"],
                "t": pb["trattamento"],
                "dc": data_creazione_str,
                "di": pb["client_device_id"],
                "sp": "Assente",
                "cf1": pb["cf_principale"],
                "cf2": pb["cf_secondario"],
            },
        )
      st.session_state["booking_success_msg"] = (
          "🎉 Prenotazione confermata con successo!"
      )
      del st.session_state["pending_booking"]
      st.session_state["regolamento_accettato"] = False
      st.rerun()

    with tab1:
      if "booking_success_msg" in st.session_state:
        st.success(st.session_state["booking_success_msg"])
        if st.button("Nuova Prenotazione"):
          del st.session_state["booking_success_msg"]
          st.rerun()
      else:
        with st.container(border=True):
          ul = st.session_state["utente_loggato"]

          categoria_scelta = st.selectbox(
              "Categoria Trattamento *", list(CATALOGO_SERVIZI.keys())
          )
          servizi_disponibili = CATALOGO_SERVIZI[categoria_scelta]
          trattamento_specifico = st.selectbox(
              "Servizio Specifico *", servizi_disponibili
          )

          trattamento_completo = (
              f"{categoria_scelta.split(' ')[1]} - {trattamento_specifico}"
          )

          data_scelta = st.date_input("Data *", min_value=datetime.today())

          orari_disponibili = [h for h in get_orari_per_data(data_scelta)]
          ora_scelta = (
              st.selectbox("Orario *", orari_disponibili)
              if orari_disponibili
              else None
          )

          submitted = st.button("Conferma Prenotazione")
          if submitted:
            if not ora_scelta:
              st.error(
                  "Seleziona un orario valido (giorno chiuso o non disponibile)."
              )
            else:
              st.session_state["pending_booking"] = {
                  "nome_completo": f"{ul['nome']} {ul['cognome']}",
                  "data_scelta": data_scelta,
                  "ora_scelta": ora_scelta,
                  "trattamento": trattamento_completo,
                  "client_device_id": client_device_id,
                  "cf_principale": ul["codice_fiscale"],
                  "cf_secondario": None,
              }
              st.session_state["mostra_dialog_regolamento"] = True
              st.rerun()

    with tab2:
      st.markdown("### Info Studio")
      st.write(
          "Benvenuta nel mondo di Lola's Glam House, dove la cura della persona"
          " incontra l'eleganza e la professionalità."
      )

    with tab3:
      st.markdown("### Regolamento")
      st.write(
          "Consulta i nostri termini di servizio per vivere un'esperienza"
          " rilassante e impeccabile."
      )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Esci"):
      del st.session_state["utente_loggato"]
      st.rerun()
