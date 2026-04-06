import streamlit as st
from src.core.criteria_state import (
    add_criterion, update_criterion_field, delete_criterion,
    add_criterion_description, update_criterion_description, delete_criterion_description,
    update_criterion_class, sync_classes_in_criteria
)

def render_criteria():
    st.header("Parametrização dos Critérios")
    st.markdown("Cadastre os critérios (Benefício ou Custo), as descrições de valoração e os termos linguísticos mínimos aceitos por classe em relação a este critério.")
    
    # Sincroniza caso classes tenham sido adicionadas/removidas ou renomeadas na primeira aba
    sync_classes_in_criteria()

    terms_alt = list(st.session_state.get("fuzzy_number_alternatives", {}).keys())
    terms_peso = list(st.session_state.get("fuzzy_number_weights", {}).keys())
    
    options_alt = terms_alt if terms_alt else ["(Vazio)"]
    weight_options = terms_peso if terms_peso else ["(Vazio)"]

    criteria = st.session_state.get("criteria", {})
    
    if not criteria:
        st.info("Nenhum critério cadastrado. Clique no botão abaixo para adicionar.")
    else:
        for crit_id, crit_data in criteria.items():
            nome_to_show = crit_data["criterion"] if crit_data["criterion"].strip() else "Novo Critério"
            
            with st.expander(nome_to_show, expanded=False):
                # Campos principais do critério
                col_nome, col_tipo, col_del = st.columns([6, 3, 1])
                
                with col_nome:
                    new_nome = st.text_input(
                        "Nome do Critério", 
                        value=crit_data["criterion"], 
                        key=f"nome_{crit_id}"
                    )
                    if new_nome != crit_data["criterion"]:
                        update_criterion_field(crit_id, "criterion", new_nome)
                        
                with col_tipo:
                    tipos = ["benefício", "custo"]
                    idx_tipo = tipos.index(crit_data["type"]) if crit_data["type"] in tipos else 0
                    new_tipo = st.selectbox(
                        "Tipo", 
                        options=tipos, 
                        index=idx_tipo, 
                        key=f"tipo_{crit_id}"
                    )
                    if new_tipo != crit_data["type"]:
                        update_criterion_field(crit_id, "type", new_tipo)
                        
                with col_del:
                    st.write("") 
                    st.write("") 
                    if st.button("❌", key=f"del_cri_{crit_id}", help=f"Excluir {crit_id}", use_container_width=True):
                        delete_criterion(crit_id)
                        st.rerun()

                st.markdown("---")
                
                # Bloco de Descrições
                st.markdown("#### Descrições de Valoração")
                
                # Headers das descrições
                if len(crit_data["descriptions"]) > 0:
                    hd1, hd2, hd3, hd_del = st.columns([5, 2, 2, 1])
                    with hd1: st.write("**Descrição**")
                    with hd2: st.write("**Termo Alternativa**")
                    with hd3: st.write("**Termo Peso**")

                for i, desc in enumerate(crit_data["descriptions"]):
                    cd1, cd2, cd3, cd_del = st.columns([5, 2, 2, 1])
                    with cd1:
                        n_desc = st.text_input("Descrição", value=desc["description"], key=f"d_desc_{crit_id}_{i}", label_visibility="collapsed")
                        if n_desc != desc["description"]:
                            update_criterion_description(crit_id, i, "description", n_desc)
                            
                    with cd2:
                        t_alt_val = desc["alternative_term"]
                        if t_alt_val not in options_alt and terms_alt:
                            t_alt_val = options_alt[0]
                        idx_alt = options_alt.index(t_alt_val) if t_alt_val in options_alt else 0
                        
                        n_t_alt = st.selectbox("Termo Alt", options=options_alt, index=idx_alt, key=f"d_talt_{crit_id}_{i}", label_visibility="collapsed")
                        if n_t_alt != desc["alternative_term"] and terms_alt:
                            update_criterion_description(crit_id, i, "alternative_term", n_t_alt)
                            
                    with cd3:
                        t_peso_val = desc["weight_term"]
                        if t_peso_val not in weight_options and terms_peso:
                            t_peso_val = weight_options[0]
                        idx_peso = weight_options.index(t_peso_val) if t_peso_val in weight_options else 0
                        
                        n_t_peso = st.selectbox("Termo Peso", options=weight_options, index=idx_peso, key=f"d_tpeso_{crit_id}_{i}", label_visibility="collapsed")
                        if n_t_peso != desc["weight_term"] and terms_peso:
                            update_criterion_description(crit_id, i, "weight_term", n_t_peso)
                            
                    with cd_del:
                        if st.button("🗑️", key=f"del_d_{crit_id}_{i}"):
                            delete_criterion_description(crit_id, i)
                            st.rerun()
                
                col_btn_add_d, _ = st.columns([3, 7])
                with col_btn_add_d:
                    if st.button("➕ Adicionar Descrição", key=f"add_d_{crit_id}"):
                        add_criterion_description(crit_id)
                        st.rerun()

                st.markdown("---")
                
                # Bloco de Classes
                st.markdown("#### Classes (Limiares do Critério)")
                if not crit_data["classes"]:
                    st.info("Não há classes cadastradas na primeira aba.")
                else:
                    ch1, ch2, _ = st.columns([5, 3, 2])
                    with ch1: st.write("**Classe**")
                    with ch2: st.write("**Termo Mínimo (Alternativa)**")
                    
                    for cid, cdata in crit_data["classes"].items():
                        cc1, cc2, _ = st.columns([5, 3, 2])
                        with cc1:
                            st.text_input("Classe", value=cdata["description"], disabled=True, key=f"c_desc_{crit_id}_{cid}", label_visibility="collapsed")
                        with cc2:
                            current_c_alt = cdata["alternative_term"]
                            if current_c_alt not in options_alt and terms_alt:
                                current_c_alt = options_alt[0]
                            idx_calt = options_alt.index(current_c_alt) if current_c_alt in options_alt else 0
                            
                            n_c_alt = st.selectbox("Termo Mínimo", options=options_alt, index=idx_calt, key=f"c_talt_{crit_id}_{cid}", label_visibility="collapsed")
                            if n_c_alt != cdata["alternative_term"] and terms_alt:
                                update_criterion_class(crit_id, cid, "alternative_term", n_c_alt)

    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ Adicionar Critério", type="primary", use_container_width=True):
            add_criterion()
            st.rerun()
