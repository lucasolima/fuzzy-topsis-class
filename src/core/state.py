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
    """Inicializa as variáveis de sessão necessárias da aplicação usando Data-Driven config."""
    default_states = {
        'alternativas': lambda: load_data('alternativas.json'),
        'next_alt_id': 10,
        'numero_fuzzy_alternativas': lambda: load_data('numero_fuzzy_alternativas.json'),
        'numero_fuzzy_pesos': lambda: load_data('numero_fuzzy_pesos.json'),
        'classes': lambda: load_data('classes.json'),
        'next_fuzzy_alt_id': 1,
        'next_fuzzy_peso_id': 1,
        'next_class_id': 4,
        'criterios': lambda: load_data('criterios.json'),
        'next_cri_id': 7,
        'avaliacoes': dict, # equivalente a iniciar com {} dinamicamente
        'pesos_criterios': dict
    }

    for key, default_value in default_states.items():
        if key not in st.session_state:
            # Se for callable, invocamos a função para pegar o retorno. Isso impede ler json a toa.
            st.session_state[key] = default_value() if callable(default_value) else default_value

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
