import streamlit as st
import json
import os

def load_data(filename):
    """Carrega dados de um arquivo JSON da pasta data/."""
    # Encontra o caminho absoluto da pasta data baseada na raiz do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(base_dir, "data", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def initialize_state():
    """Inicializa as variáveis de sessão necessárias da aplicação com a estrutura desejada."""
    if 'alternativas' not in st.session_state:
        st.session_state.alternativas = load_data('alternativas.json')
        
    if 'next_alt_id' not in st.session_state:
        st.session_state.next_alt_id = 10

    if 'numero_fuzzy_alternativas' not in st.session_state:
        st.session_state.numero_fuzzy_alternativas = load_data('numero_fuzzy_alternativas.json')
    
    if 'numero_fuzzy_pesos' not in st.session_state:
        st.session_state.numero_fuzzy_pesos = load_data('numero_fuzzy_pesos.json')

    if 'classes' not in st.session_state:
        st.session_state.classes = load_data('classes.json')
    
    if 'next_fuzzy_alt_id' not in st.session_state:
        st.session_state.next_fuzzy_alt_id = 1

    if 'next_fuzzy_peso_id' not in st.session_state:
        st.session_state.next_fuzzy_peso_id = 1

    if 'next_class_id' not in st.session_state:
        st.session_state.next_class_id = 4

    if 'criterios' not in st.session_state:
        st.session_state.criterios = load_data('criterios.json')

    if 'next_cri_id' not in st.session_state:
        st.session_state.next_cri_id = 7

    if 'avaliacoes' not in st.session_state:
        st.session_state.avaliacoes = {}

    if 'pesos_criterios' not in st.session_state:
        st.session_state.pesos_criterios = {}

def add_alternative():
    """Adiciona uma nova alternativa vazia no final do dicionário."""
    alt_id = f"ALT{st.session_state.next_alt_id}"
    st.session_state.alternativas[alt_id] = ""
    st.session_state.next_alt_id += 1

def update_alternative(alt_id: str, new_value: str):
    """Atualiza o valor de uma alternativa existente."""
    st.session_state.alternativas[alt_id] = new_value

def delete_alternative(alt_id: str):
    """Deleta uma alternativa pelo seu identificador (ex: ALT1)."""
    if alt_id in st.session_state.alternativas:
        del st.session_state.alternativas[alt_id]
