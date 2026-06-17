import base64
import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

# Garante o carregamento das variáveis de ambiente a partir do .env
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

def get_credentials():
    """Recupera o usuário e senha cadastrados no .env, com fallback para admin/admin."""
    username = os.getenv("APP_USERNAME")
    password = os.getenv("APP_PASSWORD")
    return username, password

def login(username_input, password_input):
    """Valida as credenciais inseridas e atualiza o estado de autenticação."""
    expected_username, expected_password = get_credentials()
    if username_input == expected_username and password_input == expected_password:
        st.session_state.authenticated = True
        st.session_state.auth_error = False
        st.rerun()
    else:
        st.session_state.authenticated = False
        st.session_state.auth_error = True

def logout():
    """Limpa o estado de autenticação e recarrega o app."""
    st.session_state.authenticated = False
    if "auth_error" in st.session_state:
        st.session_state.auth_error = False
    st.rerun()

def get_base64_image(image_path):
    """Lê um arquivo de imagem local e retorna sua representação em Base64 para uso no CSS."""
    try:
        with open(image_path, "rb") as image_file:
            data = image_file.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

def check_auth():
    """
    Verifica se o usuário está autenticado. 
    Retorna True se estiver autenticado, caso contrário renderiza a tela de login e retorna False.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Renderiza a tela de login padrão
    render_login_page()
    return False

def render_login_page():
    # Caminho para o background JPG
    bg_image_path = REPO_ROOT / "assets" / "bg.jpg"
    bg_base64 = get_base64_image(bg_image_path)

    # Oculta a barra lateral padrão do Streamlit na tela de login, define a imagem de fundo e força o form a ter fundo branco
    if bg_base64:
        bg_css = f"""
            <style>
            [data-testid="stSidebar"] {{
                display: none !important;
            }}
            .stApp {{
                background-image: url("data:image/jpg;base64,{bg_base64}") !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
            }}
            
            /* Fundo branco e textos escuros para o formulário de login */
            div[data-testid="stForm"] {{
                background-color: white !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
                padding: 30px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            }}
            div[data-testid="stForm"] p, 
            div[data-testid="stForm"] label, 
            div[data-testid="stForm"] span {{
                color: #1e293b !important;
            }}
            div[data-testid="stForm"] input {{
                color: #1e293b !important;
                background-color: #f8fafc !important;
                border: 1px solid #cbd5e1 !important;
            }}
            
            /* Garante que o ícone do olhinho nativo (SVG/botão interno do input) seja visível */
            div[data-testid="stForm"] div[data-testid="stTextInput"] button,
            div[data-testid="stForm"] div[data-testid="stTextInput"] button svg,
            div[data-testid="stForm"] button[data-testid="InputIconButton"],
            div[data-testid="stForm"] button[data-testid="InputIconButton"] svg {{
                color: #64748b !important;
                fill: currentColor !important;
            }}
            </style>
        """
    else:
        bg_css = """
            <style>
            [data-testid="stSidebar"] {
                display: none !important;
            }
            
            /* Fundo branco e textos escuros para o formulário de login */
            div[data-testid="stForm"] {
                background-color: white !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
                padding: 30px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            }
            div[data-testid="stForm"] p, 
            div[data-testid="stForm"] label, 
            div[data-testid="stForm"] span {
                color: #1e293b !important;
            }
            div[data-testid="stForm"] input {
                color: #1e293b !important;
                background-color: #f8fafc !important;
                border: 1px solid #cbd5e1 !important;
            }
            
            /* Garante que o ícone do olhinho nativo (SVG/botão interno do input) seja visível */
            div[data-testid="stForm"] div[data-testid="stTextInput"] button,
            div[data-testid="stForm"] div[data-testid="stTextInput"] button svg,
            div[data-testid="stForm"] button[data-testid="InputIconButton"],
            div[data-testid="stForm"] button[data-testid="InputIconButton"] svg {
                color: #64748b !important;
                fill: currentColor !important;
            }
            </style>
        """

    st.markdown(bg_css, unsafe_allow_html=True)

    # Cria colunas para centralizar o formulário horizontalmente
    _, col_center, _ = st.columns([1, 2, 1])

    with col_center:
        # Espaçamento vertical para aproximar o conteúdo do centro da tela
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        # Título e Subtítulo centralizados e com cor escura para contraste com fundo claro
        st.markdown("<h1 style='text-align: center; color: #1e293b;'>📊 FTOPSIS Class</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #64748b; margin-bottom: 20px;'>Autenticação requerida</h4>", unsafe_allow_html=True)

        # Formulário de login nativo e centralizado
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Usuário", placeholder="Digite seu usuário", key="auth_username")
            password_input = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="auth_password")
            
            if st.session_state.get("auth_error"):
                st.error("Usuário ou senha incorretos.")
                
            submit_button = st.form_submit_button("Entrar", use_container_width=True)
            if submit_button:
                if not username_input or not password_input:
                    st.session_state.auth_error = True
                    st.warning("Por favor, preencha todos os campos.")
                else:
                    login(username_input, password_input)
