import streamlit as st
from src.core.class_state import (
    add_class, 
    update_class_value, 
    delete_class
)

def render_classes():
    st.markdown("---")
    st.subheader("Classes / Perfil de Prioridade (TOPSIS Class)")
    
    st.markdown(
        "As alternativas finalizadas serão classificadas obedecendo às categorias definidas abaixo."
    )

    class_keys = list(st.session_state.classes.keys())
    termos_disponiveis = list(st.session_state.numero_fuzzy_alternativas.keys())
    
    if not class_keys:
        st.info("Nenhuma classe cadastrada. Clique no botão abaixo para adicionar.")
    else:
        # Colunas sem o termo avaliado
        col_desc, col_del = st.columns([9, 1])
        with col_desc: st.write("**Descrição da Classe**")
        
        for cid in class_keys:
            data = st.session_state.classes[cid]
            
            col_desc, col_del = st.columns([9, 1])
            
            with col_desc:
                new_desc = st.text_input(
                    "Descrição Classe", 
                    value=data["descricao"], 
                    key=f"class_desc_{cid}", 
                    label_visibility="collapsed",
                    placeholder="Ex: Alta Prioridade"
                )
                if new_desc != data["descricao"]:
                    update_class_value(cid, "descricao", new_desc)

            with col_del:
                if st.button("❌", key=f"class_del_{cid}", help=f"Excluir {cid}"):
                    delete_class(cid)
                    st.rerun()

    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ Adicionar Classe", type="primary", use_container_width=True):
            add_class()
            st.rerun()
