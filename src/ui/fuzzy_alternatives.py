import streamlit as st
from src.core.fuzzy_state import (
    add_fuzzy_term, 
    update_fuzzy_term_key, 
    update_fuzzy_term_value, 
    delete_fuzzy_term
)

def render_fuzzy_config_table(dict_name: str, next_id_key: str, prefix: str, title: str):
    """Função genérica para renderizar a tabela de configurações fuzzy."""
    st.subheader(title)

    fuzzy_keys = list(st.session_state[dict_name].keys())
    
    if not fuzzy_keys:
        st.info(f"Nenhum termo cadastrado em {title}. Clique no botão abaixo para adicionar.")
    else:
        # Cabeçalhos da tabela
        col_term, col_desc, col_l, col_m, col_u, col_del = st.columns([2, 3, 2, 2, 2, 1])
        with col_term: st.write("**Termo**")
        with col_desc: st.write("**Descrição**")
        with col_l: st.write("**l**")
        with col_m: st.write("**m**")
        with col_u: st.write("**u**")
        
        for key in fuzzy_keys:
            data = st.session_state[dict_name][key]
            
            col_term, col_desc, col_l, col_m, col_u, col_del = st.columns([2, 3, 2, 2, 2, 1])
            
            # Usando uma string única por base (dict_name) para não conflitar chaves
            k_base = f"{dict_name}_{key}"

            with col_term:
                new_key = st.text_input(
                    "Termo", 
                    value=key, 
                    key=f"term_{k_base}", 
                    label_visibility="collapsed"
                )
                if new_key != key:
                    update_fuzzy_term_key(dict_name, key, new_key)
            
            with col_desc:
                new_desc = st.text_input(
                    "Descrição", 
                    value=data["descricao"], 
                    key=f"desc_{k_base}", 
                    label_visibility="collapsed"
                )
                if new_desc != data["descricao"]:
                    update_fuzzy_term_value(dict_name, new_key if new_key != key else key, "descricao", new_desc)
            
            with col_l:
                new_l = st.number_input(
                    "l", 
                    min_value=0.0, max_value=10.0, step=0.1, 
                    value=float(data["lmu"][0]), 
                    key=f"l_{k_base}", 
                    label_visibility="collapsed",
                    format="%.1f"
                )
                if new_l != data["lmu"][0]:
                     update_fuzzy_term_value(dict_name, new_key if new_key != key else key, "l", new_l)

            with col_m:
                new_m = st.number_input(
                    "m", 
                    min_value=0.0, max_value=10.0, step=0.1, 
                    value=float(data["lmu"][1]), 
                    key=f"m_{k_base}", 
                    label_visibility="collapsed",
                    format="%.1f"
                )
                if new_m != data["lmu"][1]:
                     update_fuzzy_term_value(dict_name, new_key if new_key != key else key, "m", new_m)

            with col_u:
                new_u = st.number_input(
                    "u", 
                    min_value=0.0, max_value=10.0, step=0.1, 
                    value=float(data["lmu"][2]), 
                    key=f"u_{k_base}", 
                    label_visibility="collapsed",
                    format="%.1f"
                )
                if new_u != data["lmu"][2]:
                     update_fuzzy_term_value(dict_name, new_key if new_key != key else key, "u", new_u)

            with col_del:
                if st.button("❌", key=f"del_{k_base}", help=f"Excluir {key}"):
                    delete_fuzzy_term(dict_name, key)
                    st.rerun()

    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(f"➕ Adicionar Termo ({prefix})", key=f"add_btn_{dict_name}", type="primary", use_container_width=True):
            add_fuzzy_term(dict_name, next_id_key, prefix=prefix)
            st.rerun()

def render_fuzzy_alternatives():
    st.header("Parametrização dos Números Fuzzy e Termos Linguísticos")
    
    st.markdown(
        "Nesta aba, configuramos os termos linguísticos e seus respectivos "
        "números fuzzy triangulares (l, m, u) tanto para **Alternativas** quanto para **Pesos**."
    )

    # Renderiza Bloco 1: Alternativas
    render_fuzzy_config_table(
        dict_name="numero_fuzzy_alternativas", 
        next_id_key="next_fuzzy_alt_id", 
        prefix="ALT", 
        title="Termos Linguísticos (Alternativas)"
    )

    st.markdown("<br><br>", unsafe_allow_html=True) # Espaçamento
    
    # Renderiza Bloco 2: Pesos
    render_fuzzy_config_table(
        dict_name="numero_fuzzy_pesos", 
        next_id_key="next_fuzzy_peso_id", 
        prefix="PESO", 
        title="Termos Linguísticos (Pesos)"
    )
