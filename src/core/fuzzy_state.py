import streamlit as st

def add_fuzzy_term(dict_name: str, next_id_key: str, prefix: str = "NOVO"):
    """Adiciona um novo número fuzzy vazio a um determinado dicionário."""
    term_id = f"{prefix}_{st.session_state[next_id_key]}"
    st.session_state[dict_name][term_id] = {
        "descricao": "",
        "lmu": [0.0, 0.0, 0.0]
    }
    st.session_state[next_id_key] += 1

def update_fuzzy_term_key(dict_name: str, old_key: str, new_key: str):
    """Atualiza a chave (Termo) de um número fuzzy em um dicionário específico."""
    if new_key and new_key != old_key and new_key not in st.session_state[dict_name]:
        st.session_state[dict_name][new_key] = st.session_state[dict_name].pop(old_key)

def update_fuzzy_term_value(dict_name: str, key: str, field: str, value):
    """Atualiza um valor específico de um número fuzzy em um dicionário específico."""
    if key in st.session_state[dict_name]:
        if field in ["l", "m", "u"]:
            idx = ["l", "m", "u"].index(field)
            st.session_state[dict_name][key]["lmu"][idx] = value
        else:
            st.session_state[dict_name][key][field] = value

def delete_fuzzy_term(dict_name: str, key: str):
    """Deleta um número fuzzy de um dicionário específico."""
    if key in st.session_state[dict_name]:
        del st.session_state[dict_name][key]